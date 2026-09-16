"""
core/test_resilience.py

Unit-Tests für das Resilienz- und Circuit-Breaker-Modul.
"""

from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase
import requests

from core.resilience import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerOpenException,
    resilient_http_request,
    get_circuit_breaker,
)


class CircuitBreakerTests(SimpleTestCase):
    def test_circuit_breaker_transitions(self):
        cb = CircuitBreaker(name="test_cb", failure_threshold=2, recovery_timeout_seconds=60.0)
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertTrue(cb.can_execute())

        # Fehler 1
        cb.record_failure(Exception("Timeout 1"))
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertTrue(cb.can_execute())

        # Fehler 2 -> Schwelle erreicht -> OPEN
        cb.record_failure(Exception("Timeout 2"))
        self.assertEqual(cb.state, CircuitState.OPEN)
        self.assertFalse(cb.can_execute())

        # Nach Erholung
        cb.record_success()
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertTrue(cb.can_execute())

    @patch("requests.request")
    def test_resilient_http_request_success(self, mock_request):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "ok"}
        mock_request.return_value = mock_resp

        resp = resilient_http_request("GET", "https://api.example.com/health", circuit_name="mock_test")
        self.assertEqual(resp.status_code, 200)
