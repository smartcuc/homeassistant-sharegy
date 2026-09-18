"""
core/idempotency.py

Idempotency-Engine für schreibende API-Mutations (Billing, VPP, Device-Switching, Settlements):
- Header: 'X-Idempotency-Key' oder 'Idempotency-Key'
- Verhindert doppelte Buchungen, Stripe Checkout Sessions oder wiederholte Schaltimpulse bei Netzschwankungen
- Replay identischer Anfragen mit identischem HTTP Statuscode, Body und 'X-Idempotency-Replay: true'
- Erkennt Payload-Konflikte (gleicher Key, anderer Payload -> 422 Unprocessable Entity)
- Verhindert Race Conditions (in-flight Requests -> 409 Conflict)
"""

import hashlib
import json
import logging
import time
from typing import Optional, Tuple, Any, Dict
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response as DRFResponse

logger = logging.getLogger("sharegy.idempotency")

# Standard-Gültigkeitsdauer für Idempotency-Keys (24 Stunden)
DEFAULT_IDEMPOTENCY_TIMEOUT = getattr(settings, "IDEMPOTENCY_TIMEOUT", 86400)
# Lock-Timeout für in Bearbeitung befindliche Anfragen (60 Sekunden)
IDEMPOTENCY_LOCK_TIMEOUT = getattr(settings, "IDEMPOTENCY_LOCK_TIMEOUT", 60)

HEADER_NAMES = ("HTTP_X_IDEMPOTENCY_KEY", "HTTP_IDEMPOTENCY_KEY")


def get_idempotency_key(request) -> Optional[str]:
    """
    Extrahiert den Idempotency-Key aus den Request-Headern.
    """
    if not hasattr(request, "META"):
        return None
    for header in HEADER_NAMES:
        val = request.META.get(header)
        if val:
            cleaned = str(val).strip()
            if 1 <= len(cleaned) <= 128:
                return cleaned
    return None


def compute_request_hash(request) -> str:
    """
    Erzeugt einen SHA-256 Hash aus HTTP-Methode, Pfad, Query-Parametern und Body.
    Damit wird sichergestellt, dass derselbe Key nicht versehentlich mit abweichenden
    Parametern wiederverwendet wird.
    """
    hasher = hashlib.sha256()
    hasher.update(request.method.upper().encode("utf-8"))
    hasher.update(request.path.encode("utf-8"))
    
    # Query String
    query_str = getattr(request, "META", {}).get("QUERY_STRING", "")
    hasher.update(query_str.encode("utf-8"))
    
    # Request Body
    try:
        if hasattr(request, "_body"):
            body = request._body
        elif hasattr(request, "body"):
            body = request.body
        else:
            body = b""
        hasher.update(body)
    except Exception:
        # Fallback falls Body bereits gestreamt oder unlesbar
        hasher.update(b"")

    return hasher.hexdigest()


def build_cache_key(user_identifier: str, path: str, idempotency_key: str) -> str:
    """
    Erzeugt einen eindeutigen Cache-Schlüssel für die Idempotenz-Prüfung.
    """
    path_hash = hashlib.md5(path.encode("utf-8")).hexdigest()[:10]
    return f"idempotency:{user_identifier}:{path_hash}:{idempotency_key}"


def get_user_identifier(request) -> str:
    """
    Ermittelt den Benutzer oder IP-Identifier für anonyme Requests.
    """
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        return f"u_{user.id}"
    
    # Anonym: IP-Adresse aus X-Forwarded-For oder Remote-Addr
    meta = getattr(request, "META", {})
    x_forwarded_for = meta.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = meta.get("REMOTE_ADDR", "anon")
    return f"ip_{hashlib.md5(ip.encode('utf-8')).hexdigest()[:12]}"


def check_idempotency(request, key: Optional[str] = None) -> Tuple[Optional[HttpResponse], Optional[str]]:
    """
    Prüft, ob für diesen Request ein Idempotency-Key vorliegt und ob bereits ein Ergebnis
    gespeichert oder die Operation gerade in Ausführung ist.

    Rückgabe: (response, cache_key)
    - Wenn response nicht None ist: Sofort an den Client zurückliefern (Short-Circuit)
    - Wenn response None ist: Request normal ausführen und danach 'store_idempotency_response' aufrufen.
    """
    if key is None:
        key = get_idempotency_key(request)

    if not key:
        return None, None

    user_id = get_user_identifier(request)
    cache_key = build_cache_key(user_id, request.path, key)
    req_hash = compute_request_hash(request)

    try:
        cached_entry = cache.get(cache_key)
    except Exception as e:
        logger.warning(f"[Idempotency] Cache-Lese-Fehler: {e}")
        return None, None

    if cached_entry:
        status = cached_entry.get("status")
        stored_hash = cached_entry.get("request_hash")

        # 1. Konflikt: Gleicher Key mit verändertem Request-Body
        if stored_hash and stored_hash != req_hash:
            logger.warning(
                f"[Idempotency] Key '{key}' für Pfad '{request.path}' mit abweichender Payload wiederverwendet."
            )
            conflict_res = JsonResponse(
                {
                    "error": "Idempotency-Key wurde bereits mit abweichendem Request-Payload verwendet.",
                    "code": "IDEMPOTENCY_PAYLOAD_MISMATCH",
                },
                status=422,
            )
            conflict_res["X-Idempotency-Key"] = key
            conflict_res["X-Idempotency-Replay"] = "true"
            return conflict_res, cache_key

        # 2. In Bearbeitung (Lock): Zweiter Request während der erste noch läuft
        if status == "IN_PROGRESS":
            logger.info(f"[Idempotency] Request mit Key '{key}' ist bereits in Bearbeitung (409 Conflict).")
            in_prog_res = JsonResponse(
                {
                    "error": "Operation mit diesem Idempotency-Key wird bereits ausgeführt.",
                    "code": "IDEMPOTENCY_IN_PROGRESS",
                },
                status=409,
            )
            in_prog_res["X-Idempotency-Key"] = key
            in_prog_res["Retry-After"] = "2"
            return in_prog_res, cache_key

        # 3. Abgeschlossen: Gespeichertes Ergebnis zurückgeben (Replay)
        if status == "COMPLETED":
            logger.info(f"[Idempotency] Cache-HIT: Replay für Key '{key}' auf '{request.path}'.")
            data = cached_entry.get("response_data")
            resp_status = cached_entry.get("response_status", 200)
            content_type = cached_entry.get("content_type", "application/json")

            if content_type == "application/json" or isinstance(data, (dict, list)):
                replay_res = HttpResponse(
                    json.dumps(data) if not isinstance(data, str) else data,
                    status=resp_status,
                    content_type="application/json",
                )
            else:
                replay_res = HttpResponse(
                    data or "",
                    status=resp_status,
                    content_type=content_type,
                )

            replay_res["X-Idempotency-Key"] = key
            replay_res["X-Idempotency-Replay"] = "true"
            replay_res["X-Cache-Lookup"] = "HIT"
            return replay_res, cache_key

    # Kein Cache-Eintrag vorhanden -> Status 'IN_PROGRESS' registrieren (Lock)
    try:
        cache.set(
            cache_key,
            {
                "status": "IN_PROGRESS",
                "request_hash": req_hash,
                "created_at": time.time(),
                "path": request.path,
                "method": request.method,
            },
            timeout=IDEMPOTENCY_LOCK_TIMEOUT,
        )
    except Exception as e:
        logger.warning(f"[Idempotency] Cache-Set-Fehler (IN_PROGRESS): {e}")

    return None, cache_key


def store_idempotency_response(
    request,
    response: HttpResponse,
    cache_key: Optional[str] = None,
    timeout: int = DEFAULT_IDEMPOTENCY_TIMEOUT,
) -> HttpResponse:
    """
    Speichert das Response-Ergebnis im Cache für zukünftige Replays.
    5xx-Serverfehler werden nicht dauerhaft gespeichert, damit Clients den Request wiederholen können.
    """
    key = get_idempotency_key(request)
    if not key:
        return response

    if cache_key is None:
        user_id = get_user_identifier(request)
        cache_key = build_cache_key(user_id, request.path, key)

    response["X-Idempotency-Key"] = key
    if "X-Idempotency-Replay" not in response:
        response["X-Idempotency-Replay"] = "false"

    # Serverfehler (>= 500) nicht dauerhaft cachen -> Lock freigeben
    if response.status_code >= 500:
        clear_idempotency_key(cache_key)
        return response

    req_hash = compute_request_hash(request)
    
    # Response-Body extrahieren
    resp_data = None
    content_type = response.get("Content-Type", "application/json")
    
    try:
        if isinstance(response, JsonResponse):
            resp_data = json.loads(response.content.decode("utf-8"))
        elif hasattr(response, "data") and isinstance(response.data, (dict, list)):
            resp_data = response.data
        elif hasattr(response, "content"):
            raw_content = response.content.decode("utf-8")
            try:
                resp_data = json.loads(raw_content)
            except Exception:
                resp_data = raw_content
    except Exception as e:
        logger.debug(f"[Idempotency] Response serialization fallback: {e}")
        resp_data = getattr(response, "content", b"").decode("utf-8", errors="ignore")

    try:
        cache.set(
            cache_key,
            {
                "status": "COMPLETED",
                "request_hash": req_hash,
                "response_status": response.status_code,
                "response_data": resp_data,
                "content_type": content_type,
                "completed_at": time.time(),
            },
            timeout=timeout,
        )
        logger.debug(f"[Idempotency] Response für Key '{key}' erfolgreich gecached (TTL={timeout}s).")
    except Exception as e:
        logger.warning(f"[Idempotency] Cache-Set-Fehler (COMPLETED): {e}")

    return response


def clear_idempotency_key(cache_key: Optional[str]) -> None:
    """
    Entfernt einen Idempotency-Eintrag (z.B. bei Server-Exceptions oder Abbruch).
    """
    if not cache_key:
        return
    try:
        cache.delete(cache_key)
    except Exception as e:
        logger.warning(f"[Idempotency] Cache-Delete-Fehler: {e}")


def idempotent_mutation(required: bool = False, timeout: int = DEFAULT_IDEMPOTENCY_TIMEOUT):
    """
    Dekorator für Views, die Idempotenz erzwingen oder optional unterstützen sollen.

    Verwendung:
        @api_view(["POST"])
        @idempotent_mutation(required=True)
        def my_mutation_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Nur schreibende Methoden behandeln
            if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
                return view_func(request, *args, **kwargs)

            key = get_idempotency_key(request)
            if required and not key:
                return JsonResponse(
                    {
                        "error": "Der HTTP-Header 'X-Idempotency-Key' ist für diesen Endpunkt erforderlich.",
                        "code": "IDEMPOTENCY_KEY_REQUIRED",
                    },
                    status=400,
                )

            if not key:
                return view_func(request, *args, **kwargs)

            replay_resp, cache_key = check_idempotency(request, key=key)
            if replay_resp is not None:
                return replay_resp

            try:
                response = view_func(request, *args, **kwargs)
                return store_idempotency_response(request, response, cache_key=cache_key, timeout=timeout)
            except Exception:
                clear_idempotency_key(cache_key)
                raise

        return _wrapped_view
    return decorator
