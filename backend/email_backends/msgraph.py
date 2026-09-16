import base64
import email.utils
import logging
import time
import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMultiAlternatives

logger = logging.getLogger(__name__)


class MSGraphEmailBackend(BaseEmailBackend):
    """
    Microsoft Graph API Email Backend für Django.
    Versendet E-Mails über die offizielle Microsoft Graph REST-API (/users/{sender}/sendMail)
    mittels OAuth2 Client-Credentials-Grant (M365 / Entra ID).
    """

    _cached_token = None
    _token_expires_at = 0

    def __init__(
        self,
        tenant_id=None,
        client_id=None,
        client_secret=None,
        default_sender=None,
        fail_silently=False,
        **kwargs,
    ):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.tenant_id = tenant_id or getattr(settings, "MS_GRAPH_TENANT_ID", None)
        self.client_id = client_id or getattr(settings, "MS_GRAPH_CLIENT_ID", None)
        self.client_secret = client_secret or getattr(settings, "MS_GRAPH_CLIENT_SECRET", None)
        self.default_sender = default_sender or getattr(settings, "MS_GRAPH_DEFAULT_SENDER", getattr(settings, "DEFAULT_FROM_EMAIL", "info@smartevo.de"))

    def _get_access_token(self):
        """Holt ein Bearer-Token per Client Credentials Grant oder nutzt den Cache."""
        now = time.time()
        if self._cached_token and now < (self._token_expires_at - 60):
            return self._cached_token

        if not self.tenant_id or not self.client_id or not self.client_secret:
            raise ValueError(
                "Microsoft Graph API credentials missing. Please set MS_GRAPH_TENANT_ID, "
                "MS_GRAPH_CLIENT_ID, and MS_GRAPH_CLIENT_SECRET in settings or environment."
            )

        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }

        resp = requests.post(token_url, data=data, timeout=10)
        if resp.status_code != 200:
            logger.error("MS Graph Token Error (%s): %s", resp.status_code, resp.text)
            resp.raise_for_status()

        token_data = resp.json()
        self._cached_token = token_data["access_token"]
        expires_in = int(token_data.get("expires_in", 3600))
        self._token_expires_at = now + expires_in
        return self._cached_token

    def _extract_email_address(self, raw_address):
        """Extrahiert die reine E-Mail-Adresse aus Strings wie 'smartEvo <info@smartevo.de>'."""
        if not raw_address:
            return self._clean_default_sender()
        name, addr = email.utils.parseaddr(raw_address)
        return addr or self._clean_default_sender()

    def _clean_default_sender(self):
        name, addr = email.utils.parseaddr(self.default_sender)
        return addr or "info@smartevo.de"

    def _build_graph_payload(self, message):
        """Wandelt ein Django EmailMessage-Objekt in ein Microsoft Graph API JSON-Payload um."""
        # 1. HTML & Text ermitteln
        html_body = None
        text_body = message.body

        if isinstance(message, EmailMultiAlternatives):
            for content, mimetype in message.alternatives:
                if mimetype == "text/html":
                    html_body = content
                    break

        body_content = html_body if html_body is not None else text_body
        content_type = "HTML" if html_body is not None else "Text"

        # 2. Absender (Name & Adresse) ermitteln
        from_raw = message.from_email or self.default_sender
        from_name, from_addr = email.utils.parseaddr(from_raw)
        from_addr = from_addr or self._clean_default_sender()
        from_payload = {"emailAddress": {"address": from_addr}}
        if from_name:
            from_payload["emailAddress"]["name"] = from_name

        # 3. Empfänger formatieren
        def format_recipients(addr_list):
            recipients = []
            for addr in addr_list or []:
                clean_addr = self._extract_email_address(addr)
                if clean_addr:
                    recipients.append({"emailAddress": {"address": clean_addr}})
            return recipients

        save_to_sent = "true" if getattr(settings, "MS_GRAPH_SAVE_TO_SENT", False) else "false"

        payload = {
            "message": {
                "subject": message.subject or "(Kein Betreff)",
                "from": from_payload,
                "body": {
                    "contentType": content_type,
                    "content": body_content or "",
                },
                "toRecipients": format_recipients(message.to),
                "ccRecipients": format_recipients(message.cc),
                "bccRecipients": format_recipients(message.bcc),
            },
            "saveToSentItems": save_to_sent,
        }

        # 4. Reply-To
        if message.reply_to:
            payload["message"]["replyTo"] = format_recipients(message.reply_to)

        # 4. Anhänge
        attachments = []
        for att in getattr(message, "attachments", []):
            if isinstance(att, tuple):
                filename, content, mimetype = att
                if isinstance(content, str):
                    content = content.encode("utf-8")
                b64_content = base64.b64encode(content).decode("ascii")
                attachments.append({
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": filename,
                    "contentType": mimetype or "application/octet-stream",
                    "contentBytes": b64_content,
                })
        if attachments:
            payload["message"]["attachments"] = attachments

        return payload

    def send_messages(self, email_messages):
        """Versendet eine Liste von E-Mails über die Microsoft Graph API."""
        if not email_messages:
            return 0

        sent_count = 0
        try:
            token = self._get_access_token()
        except Exception as e:
            logger.exception("Fehler beim Abrufen des MS Graph Tokens: %s", e)
            if not self.fail_silently:
                raise
            return 0

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        for msg in email_messages:
            sender = self._extract_email_address(msg.from_email)
            send_url = f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail"
            payload = self._build_graph_payload(msg)

            try:
                resp = requests.post(send_url, json=payload, headers=headers, timeout=15)
                if resp.status_code in (200, 202):
                    sent_count += 1
                    logger.info("MS Graph Mail erfolgreich versendet an %s (Absender: %s)", msg.to, sender)
                else:
                    logger.error(
                        "MS Graph Mail Fehler (%s) beim Versand an %s via %s: %s",
                        resp.status_code,
                        msg.to,
                        sender,
                        resp.text,
                    )
                    if not self.fail_silently:
                        resp.raise_for_status()
            except Exception as e:
                logger.exception("Ausnahmefehler beim MS Graph Mailversand an %s: %s", msg.to, e)
                if not self.fail_silently:
                    raise

        return sent_count
