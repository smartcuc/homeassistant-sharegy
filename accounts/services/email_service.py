import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def get_user_language(user, override_lang=None):
    """
    Ermittelt die bevorzugte Sprache des Nutzers ('de', 'en', 'pl'). Fallback: 'de'.
    """
    if override_lang and str(override_lang).lower() in ["de", "en", "pl"]:
        return str(override_lang).lower()

    if hasattr(user, "settings") and getattr(user.settings, "language", None):
        lang = str(user.settings.language).lower()
        if lang in ["de", "en", "pl"]:
            return lang

    return "de"


def send_email(template, subject, user, context):
    # ✅ Tenant sauber ermitteln über Membership
    membership = user.memberships.filter(is_active=True).select_related("tenant").first()
    tenant = membership.tenant if membership else None

    # ✅ Fallback
    brand_color = "#00C48C"
    logo_url = "https://sharegy.de/logo.png"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "Sharegy <invite@sharegy.cloud>")

    if tenant:
        brand_color = tenant.primary_color or brand_color
        logo_url = tenant.logo_url or logo_url
        from_email = tenant.email_from or from_email

    # ✅ Template Context
    context.update({
        "tenant": tenant,
        "brand_color": brand_color,
        "logo_url": logo_url,
        "user": user,
    })

    # ✅ Templates rendern
    text = render_to_string(f"emails/{template}.txt", context)
    html = render_to_string(f"emails/{template}.html", context)

    # ✅ Mail bauen
    email = EmailMultiAlternatives(
        subject,
        text,
        from_email,
        [user.email],
    )

    email.attach_alternative(html, "text/html")
    email.send()


def send_magic_link_email(user, link, token, language=None):
    lang = get_user_language(user, language)

    subjects = {
        "de": "Dein Login-Link für Sharegy ⚡",
        "en": "Your magic login link for Sharegy ⚡",
        "pl": "Twój link logowania do Sharegy ⚡",
    }
    subject = subjects.get(lang, subjects["de"])
    tracking_url = getattr(settings, "TRACKING_BASE_URL", getattr(settings, "BACKEND_URL", "https://api.sharegy.de"))
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "Sharegy <invite@sharegy.cloud>")

    html_message = render_to_string("emails/magic_login.html", {
        "magic_link": link,
        "token": token,
        "tracking_base_url": tracking_url,
    })

    plain_message = f"Login-Link: {link}"

    logger.info("Sending magic link email to %s via %s (Language: %s)", user.email, from_email, lang)

    send_mail(
        subject,
        plain_message,
        from_email,
        [user.email],
        html_message=html_message,
    )


def send_email_change_request_email(user, new_email, confirm_link, language=None):
    """
    Sendet die mehrsprachige Verifizierungs-E-Mail an die NEUE E-Mail-Adresse.
    """
    lang = get_user_language(user, language)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "Sharegy <invite@sharegy.cloud>")
    user_name = user.first_name or ""

    I18N = {
        "de": {
            "subject": "Bestätige deine neue E-Mail-Adresse für Sharegy ⚡",
            "headline": "Bestätige deine neue E-Mail-Adresse",
            "greeting": "Hallo",
            "intro_text": "du hast eine Änderung deiner E-Mail-Adresse für deinen Sharegy-Account angefordert.",
            "new_email_label": "Neue E-Mail-Adresse",
            "confirm_instruction": "Klicke auf folgenden Link, um deine neue E-Mail-Adresse zu bestätigen:",
            "button_text": "✉️ Neue E-Mail-Adresse bestätigen",
            "expiry_notice": "Der Bestätigungslink ist aus Sicherheitsgründen 30 Minuten gültig.",
            "ignore_notice": "Falls du diese Änderung nicht selbst angefordert hast, kannst du diese E-Mail ignorieren. Dein Account bleibt unverändert.",
        },
        "en": {
            "subject": "Confirm your new email address for Sharegy ⚡",
            "headline": "Confirm your new email address",
            "greeting": "Hello",
            "intro_text": "you requested a change of your email address for your Sharegy account.",
            "new_email_label": "New email address",
            "confirm_instruction": "Click the following link to confirm your new email address:",
            "button_text": "✉️ Confirm new email address",
            "expiry_notice": "For security reasons, this confirmation link is valid for 30 minutes.",
            "ignore_notice": "If you did not request this change, you can safely ignore this email. Your account remains unchanged.",
        },
        "pl": {
            "subject": "Potwierdź swój nowy adres e-mail w Sharegy ⚡",
            "headline": "Potwierdź swój nowy adres e-mail",
            "greeting": "Cześć",
            "intro_text": "zgłoszono prośbę o zmianę adresu e-mail dla Twojego konta Sharegy.",
            "new_email_label": "Nowy adres e-mail",
            "confirm_instruction": "Kliknij poniższy link, aby potwierdzić swój nowy adres e-mail:",
            "button_text": "✉️ Potwierdź nowy adres e-mail",
            "expiry_notice": "Ze względów bezpieczeństwa link potwierdzający jest ważny przez 30 minut.",
            "ignore_notice": "Jeśli to nie Ty zgłosiłeś tę zmianę, możesz zignorować tę wiadomość. Twoje konto pozostanie bez zmian.",
        },
    }

    t = I18N.get(lang, I18N["de"])

    context = {
        "user_name": user_name,
        "new_email": new_email,
        "confirm_link": confirm_link,
        **t,
    }

    text_body = render_to_string("emails/email_change.txt", context)
    html_body = render_to_string("emails/email_change.html", context)

    msg = EmailMultiAlternatives(t["subject"], text_body, from_email, [new_email])
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)
    logger.info("Sent email change confirmation to %s (Language: %s)", new_email, lang)


def send_email_change_alert_email(user, new_email, language=None):
    """
    Sendet die mehrsprachige Sicherheits-Warnung an die ALTE/bisherige E-Mail-Adresse.
    """
    lang = get_user_language(user, language)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "Sharegy <invite@sharegy.cloud>")
    user_name = user.first_name or ""

    I18N = {
        "de": {
            "subject": "Sicherheitshinweis: E-Mail-Änderung für deinen Sharegy-Account angefordert 🛡️",
            "headline": "Sicherheitshinweis: E-Mail-Änderung angefordert",
            "greeting": "Hallo",
            "alert_intro": "für deinen Sharegy-Account wurde soeben eine Änderung der primären E-Mail-Adresse angefordert:",
            "old_email_label": "Bisherige E-Mail-Adresse",
            "new_email_label": "Neu angeforderte Adresse",
            "alert_info": "Eine Bestätigungs-E-Mail mit einem 30-minütigen Freigabelink wurde an die neue Adresse gesendet. Erst nach Klick auf diesen Link wird die Änderung wirksam.",
            "alert_warning_title": "Warst du das nicht?",
            "alert_warning_text": "Falls du diese Änderung nicht selbst veranlasst hast, kontaktiere bitte unverzüglich unseren Support oder ändere sofort dein Passwort.",
        },
        "en": {
            "subject": "Security Alert: Email change requested for your Sharegy account 🛡️",
            "headline": "Security Alert: Email change requested",
            "greeting": "Hello",
            "alert_intro": "a change of the primary email address was requested for your Sharegy account:",
            "old_email_label": "Current email address",
            "new_email_label": "Requested new email address",
            "alert_info": "A confirmation email with a 30-minute verification link was sent to the new address. The change only takes effect once the link is clicked.",
            "alert_warning_title": "Wasn't you?",
            "alert_warning_text": "If you did not initiate this change, please contact our support immediately or change your password.",
        },
        "pl": {
            "subject": "Powiadomienie o bezpieczeństwie: Żądanie zmiany adresu e-mail w Sharegy 🛡️",
            "headline": "Powiadomienie o bezpieczeństwie: Zmiana adresu e-mail",
            "greeting": "Cześć",
            "alert_intro": "dla Twojego konta Sharegy zgłoszono zmianę głównego adresu e-mail:",
            "old_email_label": "Dotychczasowy adres e-mail",
            "new_email_label": "Nowy wnioskowany adres",
            "alert_info": "Wiadomość z 30-minutowym linkiem weryfikacyjnym została wysłana na nowy adres. Zmiana wejdzie w życie dopiero po kliknięciu w link.",
            "alert_warning_title": "To nie Ty?",
            "alert_warning_text": "Jeśli nie zlecałeś tej zmiany, skontaktuj się niezwłocznie z naszym wsparciem lub zmień hasło.",
        },
    }

    t = I18N.get(lang, I18N["de"])

    context = {
        "user_name": user_name,
        "old_email": user.email,
        "new_email": new_email,
        **t,
    }

    text_body = render_to_string("emails/email_change_security_alert.txt", context)
    html_body = render_to_string("emails/email_change_security_alert.html", context)

    msg = EmailMultiAlternatives(t["subject"], text_body, from_email, [user.email])
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=True)
    logger.info("Sent email change security alert to %s (Language: %s)", user.email, lang)