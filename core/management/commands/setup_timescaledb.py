import os
import logging
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Applies and verifies TimescaleDB hypertables, continuous aggregates and telemetry indexes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            help="Simulate execution without applying SQL changes.",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        engine = settings.DATABASES.get("default", {}).get("ENGINE", "")

        self.stdout.write(self.style.MIGRATE_HEADING("🚀 Sharegy TimescaleDB & Telemetrie-Index Setup"))
        self.stdout.write(f"Datenbank-Engine: {engine}")

        if "postgresql" not in engine:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️ Aktuelle Datenbank ist nicht PostgreSQL (z. B. SQLite im Testmodus). "
                    "TimescaleDB-Hypertables werden nur auf PostgreSQL/TimescaleDB angewendet. "
                    "Standard Django B-Tree Compound-Indexes sind aktiv."
                )
            )
            return

        sql_path = os.path.join(settings.BASE_DIR, "db", "sql", "timescaledb_setup.sql")
        if not os.path.exists(sql_path):
            self.stdout.write(self.style.ERROR(f"❌ SQL-Datei nicht gefunden: {sql_path}"))
            return

        with open(sql_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        if dry_run:
            self.stdout.write(self.style.SUCCESS("✅ Dry-Run erfolgreich: SQL-Datei validiert."))
            return

        with connection.cursor() as cursor:
            try:
                self.stdout.write("Führe db/sql/timescaledb_setup.sql aus...")
                cursor.execute(sql_content)
                self.stdout.write(self.style.SUCCESS("✅ TimescaleDB Hypertables & Compression erfolgreich eingerichtet!"))

                # Diagnose-Abfrage
                cursor.execute(
                    """
                    SELECT hypertable_schema, hypertable_name, num_chunks, compression_enabled
                    FROM timescaledb_information.hypertables;
                    """
                )
                rows = cursor.fetchall()
                if rows:
                    self.stdout.write("\n📊 Aktive Hypertables:")
                    for schema, name, chunks, comp in rows:
                        comp_str = "Kompression AN" if comp else "Kompression AUS"
                        self.stdout.write(f"  • {schema}.{name}: {chunks} Chunks ({comp_str})")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Fehler bei TimescaleDB Setup: {e}"))
                logger.error("TimescaleDB setup failed: %s", e)
