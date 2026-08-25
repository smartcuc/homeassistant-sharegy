####################################################
# devices/management/commands/setup_timescaledb.py
####################################################

import os
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Richtet TimescaleDB Hypertables, Kompressions- und Retention-Policies für Telemetrie & Zähler ein."

    def handle(self, *args, **options):
        vendor = connection.vendor
        self.stdout.write(self.style.NOTICE(f"Pruefe Datenbank-Engine ({vendor})..."))

        if vendor != "postgresql":
            self.stdout.write(
                self.style.WARNING(
                    f"Aktuelle Datenbank ist '{vendor}' (nicht PostgreSQL). "
                    "TimescaleDB-Hypertables werden auf PostgreSQL/TimescaleDB Servern (z. B. Live-System) ausgefuehrt. "
                    "Fuer lokale Entwicklung/Tests werden Standard-Tabellen genutzt."
                )
            )
            return

        with connection.cursor() as cursor:
            # 1. Prüfen ob TimescaleDB Extension installiert / verfügbar ist
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
                cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
                self.stdout.write(self.style.SUCCESS("TimescaleDB & pgcrypto Extensions aktiviert."))
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"TimescaleDB Extension konnte nicht initialisiert werden: {e}\n"
                        "Bitte sicherstellen, dass TimescaleDB auf dem PostgreSQL-Server installiert ist."
                    )
                )
                return

            # 2. SQL-Setup-Skript laden und ausführen
            sql_path = os.path.join("db", "sql", "timescaledb_setup.sql")
            if not os.path.exists(sql_path):
                from django.conf import settings
                sql_path = os.path.join(settings.BASE_DIR, "db", "sql", "timescaledb_setup.sql")

            if os.path.exists(sql_path):
                self.stdout.write(self.style.NOTICE(f"Fuehre Setup-Skript aus ({sql_path})..."))
                with open(sql_path, "r", encoding="utf-8") as f:
                    sql_content = f.read()
                
                try:
                    cursor.execute(sql_content)
                    self.stdout.write(
                        self.style.SUCCESS(
                            "TimescaleDB Hypertables, Kompression & Retention Policies erfolgreich eingerichtet!"
                        )
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Fehler bei der TimescaleDB-Ausfuehrung: {e}"))
            else:
                self.stdout.write(self.style.ERROR(f"SQL-Datei nicht gefunden: {sql_path}"))

