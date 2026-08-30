from django.test import TestCase, Client

class SystemStatusHealthCheckTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_check_endpoint(self):
        response = self.client.get("/api/status/health/", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("services", data)
        self.assertIn("metrics", data)
        self.assertGreaterEqual(len(data["services"]), 4)
        service_ids = [s["id"] for s in data["services"]]
        self.assertIn("database", service_ids)
        self.assertIn("redis", service_ids)
        self.assertIn("websocket_ingest", service_ids)
