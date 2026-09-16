from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from backend.email_backends.msgraph import MSGraphEmailBackend


class Command(BaseCommand):
    help = "Send a test transactional email via Microsoft Graph API"

    def add_arguments(self, parser):
        parser.add_argument("recipient", type=str, help="Recipient email address")
        parser.add_argument("--sender", type=str, default=None, help="Sender email address (default: MS_GRAPH_DEFAULT_SENDER or info@smartevo.de)")

    def handle(self, *args, **options):
        recipient = options["recipient"]
        sender = options["sender"] or getattr(settings, "MS_GRAPH_DEFAULT_SENDER", "info@smartevo.de")

        self.stdout.write(f"Testing Microsoft Graph Email Delivery...")
        self.stdout.write(f"  Sender: {sender}")
        self.stdout.write(f"  Recipient: {recipient}")
        self.stdout.write(f"  Tenant ID: {getattr(settings, 'MS_GRAPH_TENANT_ID', 'not set')}")
        self.stdout.write(f"  Client ID: {getattr(settings, 'MS_GRAPH_CLIENT_ID', 'not set')}")

        subject = "⚡ smartEvo / Sharegy Microsoft Graph Zustellbarkeitstest"
        text_content = (
            "Hallo,\n\n"
            "Diese E-Mail wurde erfolgreich über die offizielle Microsoft Graph API direkt aus dem "
            "Microsoft 365 Exchange Online Postfach versendet.\n\n"
            "Status: Zustellung 100% verifiziert!"
        )
        html_content = (
            "<div style='font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; rounded: 16px;'>"
            "<h2 style='color: #062F32;'>⚡ smartEvo & Sharegy Zustellbarkeits-Test</h2>"
            "<p style='color: #334155; font-size: 15px;'>Hallo,</p>"
            "<p style='color: #334155; font-size: 15px;'>Diese E-Mail wurde erfolgreich über die offizielle <strong>Microsoft Graph API</strong> direkt aus eurem <strong>Microsoft 365 Exchange Online</strong> Postfach versendet.</p>"
            "<div style='background-color: #ecfdf5; border-left: 4px solid #10b981; padding: 12px; margin: 16px 0;'>"
            "<strong style='color: #065f46;'>✓ Status: 100% Zustellung im Posteingang verifiziert!</strong>"
            "</div>"
            "<p style='color: #64748b; font-size: 12px;'>Versendet via MS Graph API • Keine Third-Party-Kosten</p>"
            "</div>"
        )

        try:
            backend = MSGraphEmailBackend()
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=sender,
                to=[recipient],
            )
            msg.attach_alternative(html_content, "text/html")
            
            result = backend.send_messages([msg])
            if result > 0:
                self.stdout.write(self.style.SUCCESS(f"✓ E-Mail erfolgreich über Microsoft Graph an {recipient} versendet!"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ Versand fehlgeschlagen (0 gesendet)."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Fehler beim Microsoft Graph Versand: {e}"))
