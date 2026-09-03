###############################################
# devices/management/commands/mqtt_reconcile.py
###############################################

from django.core.management.base import BaseCommand
from devices.models import Home
from devices.tasks import provision_home, mqtt_cmd
import subprocess


class Command(BaseCommand):
    help = "Reconcile MQTT users, roles and ACLs with database"

    # ---------------------------------------------------------
    # ✅ CLI OPTIONS
    # ---------------------------------------------------------
    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not modify anything, only print actions"
        )

        parser.add_argument(
            "--only-broken",
            action="store_true",
            help="Only process already provisioned homes"
        )

    # ---------------------------------------------------------
    # ✅ HELPER: COMMAND RUN
    # ---------------------------------------------------------
    def run_cmd(self, *args, dry_run=False):
        if dry_run:
            self.stdout.write(f"[DRY] dynsec {' '.join(args[1:])}")
            return None

        return subprocess.run(
            mqtt_cmd(*args),
            capture_output=True,
            text=True
        )

    # ---------------------------------------------------------
    # ✅ HELPER: ACL CLEANUP
    # ---------------------------------------------------------
    def cleanup_wrong_acls(self, username, role_output, expected_pub, expected_sub, dry_run):

        lines = role_output.splitlines()

        for line in lines:
            line = line.strip()

            # Beispiel:
            # publishClientSend : allow : home/... (priority: 0)

            if "publishClientSend" in line and expected_pub not in line:

                topic = line.split(":")[2].split("(")[0].strip()

                if topic:
                    self.stdout.write(f"[WARN] removing wrong publish ACL: {topic}")

                    self.run_cmd(
                        "dynsec", "removeRoleACL",
                        username,
                        "publishClientSend",
                        topic,
                        dry_run=dry_run
                    )

            if "subscribePattern" in line and expected_sub not in line:

                topic = line.split(":")[2].split("(")[0].strip()

                if topic:
                    self.stdout.write(f"[WARN] removing wrong subscribe ACL: {topic}")

                    self.run_cmd(
                        "dynsec", "removeRoleACL",
                        username,
                        "subscribePattern",
                        topic,
                        dry_run=dry_run
                    )

    # ---------------------------------------------------------
    # MAIN LOGIC
    # ---------------------------------------------------------
    def handle(self, *args, **options):

        dry_run = options["dry_run"]
        only_broken = options["only_broken"]

        homes = Home.objects.all()

        if only_broken:
            homes = homes.filter(mqtt_provisioned=True)

        self.stdout.write(f"Checking {homes.count()} homes...\n")

        for home in homes:
            username = home.mqtt_username
            token = str(home.mqtt_token)

            self.stdout.write(f"--- {username} ---")

            # =====================================================
            # 1. CLIENT CHECK
            # =====================================================
            client_res = self.run_cmd(
                "dynsec", "getClient", username,
                dry_run=dry_run
            )

            if not client_res or client_res.returncode != 0:
                self.stdout.write("[ERROR] Client missing -> reprovision")

                if not dry_run:
                    provision_home.delay(home.id)

                continue

            self.stdout.write("[OK] Client OK")

            # =====================================================
            # 2. ROLE CHECK
            # =====================================================
            role_res = self.run_cmd(
                "dynsec", "getRole", username,
                dry_run=dry_run
            )

            if not role_res or role_res.returncode != 0:
                self.stdout.write("[ERROR] Role missing -> reprovision")

                if not dry_run:
                    provision_home.delay(home.id)

                continue

            self.stdout.write("[OK] Role OK")

            role_output = role_res.stdout

            # =====================================================
            # 3. ROLE BINDING CHECK
            # =====================================================
            if username not in client_res.stdout:
                self.stdout.write("[ERROR] Role not assigned -> reprovision")

                if not dry_run:
                    provision_home.delay(home.id)

                continue

            self.stdout.write("[OK] Role binding OK")

            # =====================================================
            # 4. EXPECTED ACLs
            # =====================================================
            expected_publish = f"h/{token}/#"
            expected_subscribe = f"h/{token}/#"

            # =====================================================
            # CLEANUP FALSCHER ACLs
            # =====================================================
            self.cleanup_wrong_acls(
                username,
                role_output,
                expected_publish,
                expected_subscribe,
                dry_run=dry_run
            )

            # =====================================================
            # CHECK publish ACL
            # =====================================================
            if expected_publish not in role_output:
                self.stdout.write("[ERROR] publish ACL missing -> fixing")

                self.run_cmd(
                    "dynsec", "addRoleACL",
                    username,
                    "publishClientSend",
                    expected_publish,
                    "allow",
                    dry_run=dry_run
                )
            else:
                self.stdout.write("[OK] publish ACL OK")

            # =====================================================
            # CHECK subscribe ACL
            # =====================================================
            if expected_subscribe not in role_output:
                self.stdout.write("[ERROR] subscribe ACL missing -> fixing")

                self.run_cmd(
                    "dynsec", "addRoleACL",
                    username,
                    "subscribePattern",
                    expected_subscribe,
                    "allow",
                    dry_run=dry_run
                )
            else:
                self.stdout.write("[OK] subscribe ACL OK")

            self.stdout.write("[OK] fully reconciled\n")

        self.stdout.write("[OK] MQTT reconcile done")