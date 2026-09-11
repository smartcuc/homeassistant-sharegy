from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import EventLog

User = get_user_model()


class TrackingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="adminuser",
            email="admin@sharegy.de",
            password="testpassword123",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

        # Create sample events
        EventLog.objects.create(name="landing_view", user=self.user, context="global")
        EventLog.objects.create(name="signup_success", user=self.user, context="global")
        EventLog.objects.create(name="login", user=self.user, context="global")

    def test_stats_kpi_endpoint_returns_200(self):
        response = self.client.get("/api/tracking/stats/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("stats", data)
        self.assertIn("daily", data)
        self.assertIn("dau", data)
        self.assertIn("funnel", data)
        self.assertGreaterEqual(data["total_events"], 3)

    def test_funnel_endpoint_returns_200(self):
        response = self.client.get("/api/tracking/funnel/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("steps", data)
