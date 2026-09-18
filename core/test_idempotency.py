"""
core/test_idempotency.py

Unit- und Integrationstests für die Idempotency-Engine und Middleware.
"""

import json
from unittest.mock import MagicMock
from django.test import TestCase, RequestFactory
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from rest_framework.test import APIRequestFactory

from core.idempotency import (
    get_idempotency_key,
    compute_request_hash,
    check_idempotency,
    store_idempotency_response,
    clear_idempotency_key,
    idempotent_mutation,
)
from core.middleware import IdempotencyMiddleware


class IdempotencyEngineTests(TestCase):
    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()

    def tearDown(self):
        cache.clear()

    def test_get_idempotency_key_headers(self):
        req1 = self.factory.post("/api/billing/checkout/", HTTP_X_IDEMPOTENCY_KEY="key-123-abc")
        self.assertEqual(get_idempotency_key(req1), "key-123-abc")

        req2 = self.factory.post("/api/vpp/dispatch/", HTTP_IDEMPOTENCY_KEY="key-456-def")
        self.assertEqual(get_idempotency_key(req2), "key-456-def")

        req_none = self.factory.post("/api/devices/1/switch/")
        self.assertIsNone(get_idempotency_key(req_none))

    def test_compute_request_hash_differentiates_payloads(self):
        req1 = self.factory.post(
            "/api/devices/1/switch/",
            data=json.dumps({"state": "on"}),
            content_type="application/json",
        )
        req2 = self.factory.post(
            "/api/devices/1/switch/",
            data=json.dumps({"state": "off"}),
            content_type="application/json",
        )
        hash1 = compute_request_hash(req1)
        hash2 = compute_request_hash(req2)
        self.assertNotEqual(hash1, hash2)

    def test_full_idempotent_flow_success_and_replay(self):
        call_count = 0

        def dummy_view(request):
            nonlocal call_count
            call_count += 1
            return JsonResponse({"status": "switched", "call": call_count}, status=200)

        # 1. Erster Request mit Key
        req1 = self.factory.post(
            "/api/devices/42/switch/",
            data=json.dumps({"state": "on"}),
            content_type="application/json",
            HTTP_X_IDEMPOTENCY_KEY="switch-token-001",
        )

        middleware = IdempotencyMiddleware(dummy_view)
        res1 = middleware(req1)

        self.assertEqual(res1.status_code, 200)
        self.assertEqual(call_count, 1)
        self.assertEqual(res1["X-Idempotency-Key"], "switch-token-001")
        self.assertEqual(res1["X-Idempotency-Replay"], "false")
        data1 = json.loads(res1.content.decode("utf-8"))
        self.assertEqual(data1["status"], "switched")
        self.assertEqual(data1["call"], 1)

        # 2. Zweiter Request mit EXAKT dem gleichen Key und Body (z.B. nach Netzwerk-Timeout / Retry)
        req2 = self.factory.post(
            "/api/devices/42/switch/",
            data=json.dumps({"state": "on"}),
            content_type="application/json",
            HTTP_X_IDEMPOTENCY_KEY="switch-token-001",
        )

        res2 = middleware(req2)

        self.assertEqual(res2.status_code, 200)
        # WICHTIG: View darf NICHT noch einmal ausgeführt worden sein!
        self.assertEqual(call_count, 1)
        self.assertEqual(res2["X-Idempotency-Key"], "switch-token-001")
        self.assertEqual(res2["X-Idempotency-Replay"], "true")
        self.assertEqual(res2["X-Cache-Lookup"], "HIT")
        data2 = json.loads(res2.content.decode("utf-8"))
        self.assertEqual(data2["status"], "switched")
        self.assertEqual(data2["call"], 1)

    def test_payload_mismatch_returns_422(self):
        def dummy_view(request):
            return JsonResponse({"ok": True})

        middleware = IdempotencyMiddleware(dummy_view)

        # 1. Erster Request
        req1 = self.factory.post(
            "/api/vpp/dispatch/",
            data=json.dumps({"power_kw": 50.0}),
            content_type="application/json",
            HTTP_X_IDEMPOTENCY_KEY="vpp-dispatch-100",
        )
        res1 = middleware(req1)
        self.assertEqual(res1.status_code, 200)

        # 2. Zweiter Request mit gleichem Key aber verändertem Payload
        req2 = self.factory.post(
            "/api/vpp/dispatch/",
            data=json.dumps({"power_kw": 120.0}),
            content_type="application/json",
            HTTP_X_IDEMPOTENCY_KEY="vpp-dispatch-100",
        )
        res2 = middleware(req2)
        self.assertEqual(res2.status_code, 422)
        data2 = json.loads(res2.content.decode("utf-8"))
        self.assertEqual(data2["code"], "IDEMPOTENCY_PAYLOAD_MISMATCH")

    def test_in_progress_returns_409_conflict(self):
        # 1. Lock manuell setzen (als ob ein Request gerade läuft)
        req = self.factory.post(
            "/api/billing/settlement/",
            data=json.dumps({"period": "2026-09"}),
            content_type="application/json",
            HTTP_X_IDEMPOTENCY_KEY="settle-key-55",
        )

        # Simuliere check_idempotency setzt IN_PROGRESS
        replay_resp, cache_key = check_idempotency(req)
        self.assertIsNone(replay_resp)
        self.assertIsNotNone(cache_key)

        # 2. Zweiter Request während IN_PROGRESS aktiv ist
        replay_resp2, _ = check_idempotency(req)
        self.assertIsNotNone(replay_resp2)
        self.assertEqual(replay_resp2.status_code, 409)
        self.assertEqual(replay_resp2["Retry-After"], "2")
        data = json.loads(replay_resp2.content.decode("utf-8"))
        self.assertEqual(data["code"], "IDEMPOTENCY_IN_PROGRESS")

    def test_decorator_enforce_required_key(self):
        @idempotent_mutation(required=True)
        def strictly_idempotent_view(request):
            return JsonResponse({"processed": True})

        # Ohne Header -> 400 Bad Request
        req_bad = self.factory.post("/api/billing/charge/")
        res_bad = strictly_idempotent_view(req_bad)
        self.assertEqual(res_bad.status_code, 400)
        self.assertEqual(json.loads(res_bad.content.decode("utf-8"))["code"], "IDEMPOTENCY_KEY_REQUIRED")

        # Mit Header -> 200 OK
        req_good = self.factory.post(
            "/api/billing/charge/",
            HTTP_X_IDEMPOTENCY_KEY="charge-key-999",
        )
        res_good = strictly_idempotent_view(req_good)
        self.assertEqual(res_good.status_code, 200)
