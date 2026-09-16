"""
core/resilience.py

Resilienz- und Fehlertoleranz-Framework für externe HTTP- und Cloud-Schnittstellen:
- Circuit-Breaker State Machine (CLOSED, OPEN, HALF_OPEN)
- Exponentieller Backoff mit Jitter
- Standardisierte Connect- und Read-Timeouts
- Schutz vor Worker-Thread-Exhaustion
"""

import time
import logging
from enum import Enum
from typing import Callable, Any, Optional, Dict
import requests

logger = logging.getLogger("sharegy.resilience")

# Standard-Timeouts (Connect: 3.05s, Read: 10s)
DEFAULT_TIMEOUT = (3.05, 10.0)


class CircuitState(Enum):
    CLOSED = "CLOSED"      # Normalbetrieb: Anfragen werden durchgelassen
    OPEN = "OPEN"          # Fehlerzustand: Anfragen werden sofort abgewiesen (Fast-Fail)
    HALF_OPEN = "HALF_OPEN" # Probebetrieb: Einzelne Testanfragen prüfen Erholung


class CircuitBreakerOpenException(Exception):
    """Wird ausgelöst, wenn der Circuit Breaker im Zustand OPEN ist."""
    pass


class CircuitBreaker:
    """
    In-Memory Circuit Breaker zur Kapselung instabiler externer APIs.
    """
    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout_seconds: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.last_state_change = time.time()

    def record_success(self):
        if self.state in (CircuitState.HALF_OPEN, CircuitState.OPEN):
            logger.info(f"[CircuitBreaker:{self.name}] Dienst hat sich erholt -> Zustand wechselt auf CLOSED.")
        self.state = CircuitState.CLOSED
        self.failure_count = 0

    def record_failure(self, error: Exception):
        self.failure_count += 1
        self.last_failure_time = time.time()
        logger.warning(
            f"[CircuitBreaker:{self.name}] Fehler erfasst ({self.failure_count}/{self.failure_threshold}): {error}"
        )
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
            logger.error(
                f"[CircuitBreaker:{self.name}] Fehlerschwelle erreicht -> Zustand wechselt auf OPEN ({self.recovery_timeout_seconds}s Fast-Fail)."
            )

    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            # Prüfen ob Recovery-Timeout abgelaufen ist -> Wechsel in HALF_OPEN
            if time.time() - self.last_state_change >= self.recovery_timeout_seconds:
                logger.info(f"[CircuitBreaker:{self.name}] Recovery-Zeit abgelaufen -> Wechsle in HALF_OPEN.")
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = time.time()
                return True
            return False
        if self.state == CircuitState.HALF_OPEN:
            return True
        return True


# Globales Registry für Circuit Breaker
_CIRCUIT_BREAKERS: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, failure_threshold: int = 5, recovery_timeout_seconds: float = 30.0) -> CircuitBreaker:
    if name not in _CIRCUIT_BREAKERS:
        _CIRCUIT_BREAKERS[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout_seconds=recovery_timeout_seconds
        )
    return _CIRCUIT_BREAKERS[name]


def resilient_http_request(
    method: str,
    url: str,
    circuit_name: str = "default",
    timeout: tuple = DEFAULT_TIMEOUT,
    max_retries: int = 2,
    backoff_factor: float = 0.5,
    **kwargs
) -> requests.Response:
    """
    Führt einen HTTP-Request mit Circuit Breaker, Retries und Timeouts aus.
    """
    cb = get_circuit_breaker(circuit_name)
    if not cb.can_execute():
        raise CircuitBreakerOpenException(
            f"Aufruf an '{circuit_name}' ({url}) blockiert: Circuit Breaker ist OPEN."
        )

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            kwargs.setdefault("timeout", timeout)
            response = requests.request(method, url, **kwargs)
            # HTTP 5xx Statuscodes als Fehler werten
            if response.status_code >= 500:
                response.raise_for_status()
            cb.record_success()
            return response
        except (requests.RequestException, Exception) as exc:
            last_error = exc
            if attempt < max_retries:
                sleep_time = backoff_factor * (2 ** attempt)
                logger.debug(f"[ResilientHTTP:{circuit_name}] Retry {attempt + 1}/{max_retries} nach {sleep_time:.2f}s...")
                time.sleep(sleep_time)
            else:
                cb.record_failure(exc)

    raise last_error or Exception("Unbekannter HTTP-Fehler")
