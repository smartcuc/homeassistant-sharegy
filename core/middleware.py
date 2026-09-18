########################
# core/middleware.py
########################
import logging
import uuid

from .logging_context import request_id_var
from .idempotency import (
    get_idempotency_key,
    check_idempotency,
    store_idempotency_response,
    clear_idempotency_key,
)

logger = logging.getLogger(__name__)


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        token = request_id_var.set(rid)

        try:
            response = self.get_response(request)
            response["X-Request-Id"] = rid
            return response
        finally:
            request_id_var.reset(token)


class IdempotencyMiddleware:
    """
    Automatisches Idempotenz-Handling für schreibende HTTP-Mutations (POST, PUT, PATCH, DELETE).
    Greift ein, sobald der Client den Header 'X-Idempotency-Key' oder 'Idempotency-Key' mitsendet:
    - Verhindert doppelte Lastschalt-Befehle (Relais, Inverter, VPP Dispatches)
    - Verhindert doppelte Abrechnungsbuchungen (Stripe Checkout Sessions, Abrechnungsläufe)
    - Replayt im Erfolgsfall das exakte Resultat mit 'X-Idempotency-Replay: true'
    - Weist gleichzeitige Requests ab (409 Conflict)
    - Erkennt Payload-Abweichungen (422 Unprocessable Entity)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Nur schreibende API-Mutations prüfen
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return self.get_response(request)

        key = get_idempotency_key(request)
        if not key:
            return self.get_response(request)

        # 1. Idempotenz prüfen (Cache-Hit / Conflict / Lock)
        replay_resp, cache_key = check_idempotency(request, key=key)
        if replay_resp is not None:
            return replay_resp

        # 2. Request ausführen
        try:
            response = self.get_response(request)
            return store_idempotency_response(request, response, cache_key=cache_key)
        except Exception:
            # Bei Fehlern Lock freigeben
            clear_idempotency_key(cache_key)
            raise
