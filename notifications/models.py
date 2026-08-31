########################
# notifications/models.py
########################

import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class DeviceSubscription(models.Model):
    """
    Speichert Push-Registrierungen (Browser Web-Push, iOS, Android).
    """
    DEVICE_WEB_PUSH = "web_push"
    DEVICE_IOS = "ios"
    DEVICE_ANDROID = "android"

    DEVICE_TYPE_CHOICES = [
        (DEVICE_WEB_PUSH, "Web-Push (Safari / Chrome / Firefox)"),
        (DEVICE_IOS, "iOS (Apple APNs)"),
        (DEVICE_ANDROID, "Android (Google FCM)"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="device_subscriptions",
    )

    home = models.ForeignKey(
        "devices.Home",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="device_subscriptions",
    )

    device_type = models.CharField(
        max_length=32,
        choices=DEVICE_TYPE_CHOICES,
        default=DEVICE_WEB_PUSH,
    )

    # W3C Web-Push Daten
    endpoint = models.URLField(max_length=1024, blank=True, default="")
    p256dh_key = models.CharField(max_length=255, blank=True, default="")
    auth_key = models.CharField(max_length=255, blank=True, default="")

    # Native FCM / APNs Token
    fcm_token = models.CharField(max_length=1024, blank=True, default="")

    device_name = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="z. B. 'iPhone 15 Pro', 'Pixel 8', 'Chrome auf Windows'",
    )

    user_agent = models.CharField(max_length=512, blank=True, default="")
    is_active = models.BooleanField(default=True, db_index=True)

    # 🛡️ Audit & Sicherheit
    registered_ip = models.GenericIPAddressField(null=True, blank=True, help_text="IP-Adresse bei Aktivierung")
    unregistered_ip = models.GenericIPAddressField(null=True, blank=True, help_text="IP-Adresse bei Deaktivierung")
    unregistered_at = models.DateTimeField(null=True, blank=True, help_text="Zeitpunkt der Deaktivierung")

    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["home", "is_active"]),
            models.Index(fields=["endpoint"]),
        ]

    def __str__(self):
        name = self.device_name or self.device_type
        return f"{self.user.email} - {name} ({'Aktiv' if self.is_active else 'Inaktiv'})"


class NotificationPreference(models.Model):
    """
    Benutzerspezifische Präferenzen für Push-Alarme & Ruhezeiten (Quiet Hours).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )

    push_enabled = models.BooleanField(
        default=True,
        help_text="Globale Push-Aktivierung für diesen Account",
    )

    # 🌙 Ruhezeiten (Quiet Hours)
    quiet_hours_enabled = models.BooleanField(
        default=False,
        help_text="Benachrichtigungen zu bestimmten Uhrzeiten stummschalten",
    )
    quiet_hours_start = models.TimeField(
        default="22:00:00",
        help_text="Beginn der Nachtruhe (z. B. 22:00)",
    )
    quiet_hours_end = models.TimeField(
        default="07:00:00",
        help_text="Ende der Nachtruhe (z. B. 07:00)",
    )
    allow_critical_in_quiet_hours = models.BooleanField(
        default=True,
        help_text="Kritische Notfall-Alarme (z. B. Speicher leer, Frost) trotz Ruhezeit zustellen",
    )

    # 🎯 Alarm-Kategorien Filter
    notify_battery = models.BooleanField(default=True, help_text="Speicher-Notreserve & Entlade-Warnungen")
    notify_leakage = models.BooleanField(default=True, help_text="Nachtverbrauch & Dauerlast-Leckagen")
    notify_pv = models.BooleanField(default=True, help_text="PV-Ausfall & Ertragsanomalien")
    notify_prices = models.BooleanField(default=True, help_text="Börsenstrom-Negativpreise & Preis-Peaks")
    notify_device_status = models.BooleanField(default=True, help_text="Geräte-Offline & Signal-Verlust")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification Preferences for {self.user.email}"
