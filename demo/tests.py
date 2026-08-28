################
# demo/tests.py
################

from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from devices.models import Home, Device, DeviceMetric
from demo.models import DemoDeviceMap
from demo.services.cleanup import cleanup_demo_metrics

User = get_user_model()


class DemoCleanupTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="demotester",
            email="demo@sharegy.de",
            password="testpassword123",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Demo Home",
        )
        self.src_device = Device.objects.create(
            home=self.home,
            identifier="SRC-001",
        )
        self.demo_device = Device.objects.create(
            home=self.home,
            identifier="DEMO-001",
        )
        DemoDeviceMap.objects.create(
            source_device=self.src_device,
            demo_device=self.demo_device,
        )

        now = timezone.now()
        # 1. Old metric (35 days old -> should be cleaned up)
        DeviceMetric.objects.create(
            device=self.demo_device,
            metric_key="power",
            unit="W",
            value=250.0,
            timestamp=now - timedelta(days=35),
        )
        # 2. Recent metric (5 days old -> should NOT be cleaned up)
        DeviceMetric.objects.create(
            device=self.demo_device,
            metric_key="power",
            unit="W",
            value=500.0,
            timestamp=now - timedelta(days=5),
        )

    def test_cleanup_demo_metrics(self):
        # Initial count
        self.assertEqual(DeviceMetric.objects.filter(device=self.demo_device).count(), 2)

        # Run cleanup with 28 days retention
        deleted = cleanup_demo_metrics(days=28)
        self.assertEqual(deleted, 1)

        # Verify only recent metric remains
        remaining = DeviceMetric.objects.filter(device=self.demo_device)
        self.assertEqual(remaining.count(), 1)
        self.assertEqual(remaining.first().value, 500.0)
