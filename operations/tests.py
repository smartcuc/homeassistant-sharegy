from django.test import TestCase, Client
from operations.models import HealthState
from operations.tasks import check_and_create_incident_tickets
from support_desk.models import Ticket, SupportProjectConfig


class SystemStatusHealthCheckTest(TestCase):
    def setUp(self):
        self.client = Client()
        SupportProjectConfig.objects.get_or_create(project_key="sharegy", defaults={"ticket_prefix": "SHAR"})

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

    def test_automatic_incident_ticket_creation_and_resolution(self):
        # 1. Simulate an error in SpotPrice sync
        HealthState.objects.create(
            key="spot_prices",
            status="error",
            value="no spot prices available for 24h",
            details={"age_seconds": 86400},
        )

        # 2. Run Watchdog Triage
        check_and_create_incident_tickets()

        # 3. Verify Ticket was created
        ticket = Ticket.objects.filter(subject__contains="[Auto-Incident: spot_prices]").first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.priority, Ticket.PRIORITY_URGENT)
        self.assertEqual(ticket.category, "infrastructure")
        self.assertEqual(ticket.status, Ticket.STATUS_OPEN)

        # 4. Running again does NOT duplicate the ticket
        check_and_create_incident_tickets()
        count = Ticket.objects.filter(subject__contains="[Auto-Incident: spot_prices]").count()
        self.assertEqual(count, 1)

        # 5. Simulate Recovery to 'ok'
        state = HealthState.objects.get(key="spot_prices")
        state.status = "ok"
        state.value = "latest spot price synced"
        state.save()

        # 6. Run Watchdog Triage again
        check_and_create_incident_tickets()

        # 7. Verify Ticket was auto-resolved
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, Ticket.STATUS_RESOLVED)
        self.assertTrue(ticket.messages.filter(body__contains="Automatische Entwarnung").exists())

