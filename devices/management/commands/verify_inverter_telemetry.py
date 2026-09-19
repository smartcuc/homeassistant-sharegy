from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from devices.models import Device, DeviceMetric, DeviceLatestMetric
from datetime import timedelta
import json

User = get_user_model()

class Command(BaseCommand):
    help = "Diagnostik & Verifikation für Closed-Beta Inverter- und Hardware-Paten"

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, help="E-Mail-Adresse des Beta-Testers")
        parser.add_argument("--device-id", type=str, help="Spezifische Geräte-ID prüfen")
        parser.add_argument("--hours", type=int, default=6, help="Prüffenster in Stunden (Standard: 6)")

    def handle(self, *args, **options):
        email = options.get("email")
        device_id = options.get("device_id")
        hours = options.get("hours") or 6
        now = timezone.now()
        since = now - timedelta(hours=hours)

        self.stdout.write(self.style.MIGRATE_HEADING("\n" + "="*70))
        self.stdout.write(self.style.MIGRATE_HEADING(" 🔍 SHAREGY INVERTER & HARDWARE-PATEN DIAGNOSTIC INSPECTOR"))
        self.stdout.write(self.style.MIGRATE_HEADING("="*70 + "\n"))

        devices_qs = Device.objects.all()

        if email:
            try:
                user = User.objects.get(email__iexact=email.strip())
                self.stdout.write(f"👤 Prüfe Beta-Tester: {self.style.SUCCESS(user.email)} (ID: {user.id})")
                # Find devices via user or home
                devices_qs = devices_qs.filter(home__user=user)
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"❌ Kein Benutzer mit E-Mail '{email}' gefunden."))
                return

        if device_id:
            devices_qs = devices_qs.filter(id=device_id)

        count = devices_qs.count()
        if count == 0:
            self.stdout.write(self.style.WARNING("⚠️ Keine Geräte für die angegebenen Filterkriterien gefunden."))
            self.stdout.write("  -> Der Tester hat möglicherweise noch kein Gerät über den Wizard angelegt.")
            return

        self.stdout.write(f"📋 Gefundene Geräte zur Analyse: {self.style.SUCCESS(str(count))}\n")

        for dev in devices_qs:
            self.stdout.write(self.style.HTTP_INFO(f"--- Gerät: {dev.name} (Typ: {dev.device_type}, Hersteller/Integration: {dev.integration_type}) ---"))
            self.stdout.write(f"   • Device-ID: {dev.id}")
            self.stdout.write(f"   • Angelegt am: {dev.created_at.strftime('%Y-%m-%d %H:%M:%S UTC') if dev.created_at else 'Unbekannt'}")
            
            # 1. Config / Credentials Check
            has_credentials = bool(dev.credentials or dev.connection_params)
            self.stdout.write(f"   • Zugangsdaten hinterlegt: {'🟢 JA' if has_credentials else '🔴 NEIN (Fehlen)'}")
            
            # 2. Latest Snapshot Check
            latest = DeviceLatestMetric.objects.filter(device=dev).first()
            if latest and latest.timestamp:
                age_minutes = int((now - latest.timestamp).total_seconds() / 60)
                age_str = f"vor {age_minutes} Minuten" if age_minutes > 0 else "gerade eben (< 1 Min)"
                self.stdout.write(f"   • Letzter Snapshot (`DeviceLatestMetric`): {latest.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')} ({age_str})")
                self.stdout.write(f"     - Leistung (W): {latest.power_w or 0:.1f} W")
                self.stdout.write(f"     - Energie (kWh): {latest.energy_kwh or 0:.2f} kWh")
                if latest.voltage_v:
                    self.stdout.write(f"     - Spannung (V): {latest.voltage_v:.1f} V")
                if latest.current_a:
                    self.stdout.write(f"     - Strom (A): {latest.current_a:.2f} A")
            else:
                self.stdout.write("   • Letzter Snapshot: ⚠️ Noch kein Snapshot in `DeviceLatestMetric` vorhanden.")

            # 3. Time-Series Metric Stream Check
            metrics_count = DeviceMetric.objects.filter(device=dev, timestamp__gte=since).count()
            earliest_metric = DeviceMetric.objects.filter(device=dev, timestamp__gte=since).order_by('timestamp').first()
            latest_metric = DeviceMetric.objects.filter(device=dev, timestamp__gte=since).order_by('-timestamp').first()

            self.stdout.write(f"   • Empfangene Zeitreihen-Messpunkte (letzte {hours}h): {metrics_count}")
            
            # 4. Plausibility & Verification Decision
            if metrics_count > 0 and latest and (now - latest.timestamp).total_seconds() < 3600:
                status_badge = self.style.SUCCESS("🟢 VERIFIED & STREAMING (Tester hat erfolgreich Daten gesendet)")
                diagnosis = "Schnittstelle funktioniert einwandfrei. Live-Telemetrie fließt stabil in die Datenbank."
            elif metrics_count > 0:
                status_badge = self.style.WARNING("🟡 HISTORICAL DATA PRESENT (Verbindung aktuell unterbrochen)")
                diagnosis = f"Daten wurden gesendet, aber der letzte Messpunkt ist älter als 60 Minuten ({latest.timestamp if latest else 'N/A'})."
            elif has_credentials:
                status_badge = self.style.WARNING("🟡 CONFIGURED BUT NO METRICS (Warten auf ersten Ingest)")
                diagnosis = "Zugangsdaten sind hinterlegt, aber es sind noch keine Messwerte in TimescaleDB eingegangen. Prüfen Sie Webhook-URL, Token-Gültigkeit oder Poller."
            else:
                status_badge = self.style.ERROR("🔴 NOT CONFIGURED (Tester hat noch keine Daten eingegeben)")
                diagnosis = "Der Tester hat das Gerät angelegt, aber keine Zugangsdaten hinterlegt."

            self.stdout.write(f"\n   📊 Gesamt-Ergebnis: {status_badge}")
            self.stdout.write(f"   💡 Diagnose: {diagnosis}\n")

        self.stdout.write(self.style.MIGRATE_HEADING("="*70 + "\n"))
