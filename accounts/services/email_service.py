import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def get_user_language(user, override_lang=None):
    """
    Ermittelt die bevorzugte Sprache des Nutzers ('de', 'en', 'pl', 'ro', 'tr', 'ru'). Fallback: 'de'.
    """
    supported = ["de", "en", "pl", "ro", "tr", "ru"]
    if override_lang and str(override_lang).lower() in supported:
        return str(override_lang).lower()

    if hasattr(user, "settings") and getattr(user.settings, "language", None):
        lang = str(user.settings.language).lower()
        if lang in supported:
            return lang

    return "de"


def send_email(template, subject, user, context):
    # ✅ Tenant sauber ermitteln über Membership
    membership = user.memberships.filter(is_active=True).select_related("tenant").first() if hasattr(user, "memberships") else None
    tenant = membership.tenant if membership else None

    # ✅ Fallback
    brand_color = "#4F46E5"
    logo_url = None
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

    I18N = {
        "de": {
            "subject": "Dein Login-Link für Sharegy ⚡",
            "headline": "Willkommen zurück 👋",
            "intro_text": "Hier ist dein persönlicher Einmal-Login-Link für <strong>Sharegy</strong>. Klicke einfach auf den folgenden Button, um dich sicher in dein Konto einzuloggen:",
            "button_text": "🔐 Sicher einloggen",
            "fallback_label": "Alternativer Direktlink:",
            "validity_label": "Gültigkeit:",
            "validity_text": "Dieser Login-Link ist nur 15 Minuten gültig und kann nur einmal verwendet werden.",
            "ignore_text": "Falls du diese Anfrage nicht selbst gestellt hast, kannst du diese E-Mail ignorieren. Dein Account bleibt vollständig geschützt.",
            "plain_intro": "Schön, dass du wieder da bist bei Sharegy.",
            "plain_link_label": "Hier anmelden:",
            "plain_expiry": "Der Link ist 15 Minuten gültig.",
        },
        "en": {
            "subject": "Your magic login link for Sharegy ⚡",
            "headline": "Welcome back 👋",
            "intro_text": "Here is your personal one-time login link for <strong>Sharegy</strong>. Simply click the button below to sign in securely to your account:",
            "button_text": "🔐 Sign in securely",
            "fallback_label": "Alternative direct link:",
            "validity_label": "Validity:",
            "validity_text": "This login link is valid for 15 minutes only and can be used once.",
            "ignore_text": "If you did not request this login link, you can safely ignore this email. Your account remains completely secure.",
            "plain_intro": "Welcome back to Sharegy.",
            "plain_link_label": "Sign in here:",
            "plain_expiry": "This link is valid for 15 minutes.",
        },
        "pl": {
            "subject": "Twój link logowania do Sharegy ⚡",
            "headline": "Witaj ponownie 👋",
            "intro_text": "Oto Twój osobisty jednorazowy link do logowania w <strong>Sharegy</strong>. Kliknij poniższy przycisk, aby bezpiecznie zalogować się na swoje konto:",
            "button_text": "🔐 Zaloguj się bezpiecznie",
            "fallback_label": "Alternatywny link bezpośredni:",
            "validity_label": "Ważność:",
            "validity_text": "Ten link logowania jest ważny przez 15 minut i może być użyty tylko raz.",
            "ignore_text": "Jeśli to nie Ty żądałeś tego linku, możesz zignorować tę wiadomość. Twoje konto pozostaje w pełni bezpieczne.",
            "plain_intro": "Witaj ponownie w Sharegy.",
            "plain_link_label": "Zaloguj się tutaj:",
            "plain_expiry": "Link jest ważny przez 15 minut.",
        },
        "ro": {
            "subject": "Linkul tău de conectare pentru Sharegy ⚡",
            "headline": "Bine ai revenit 👋",
            "intro_text": "Iată linkul tău personal de conectare unică pentru <strong>Sharegy</strong>. Fă clic pe butonul de mai jos pentru a te conecta în siguranță:",
            "button_text": "🔐 Conectează-te în siguranță",
            "fallback_label": "Link direct alternativ:",
            "validity_label": "Valabilitate:",
            "validity_text": "Acest link este valabil timp de 15 minute și poate fi folosit o singură dată.",
            "ignore_text": "Dacă nu ai solicitat acest link, poți ignora acest e-mail. Contul tău rămâne în deplină siguranță.",
            "plain_intro": "Bine ai revenit la Sharegy.",
            "plain_link_label": "Conectează-te aici:",
            "plain_expiry": "Linkul este valabil 15 minute.",
        },
        "tr": {
            "subject": "Sharegy Giriş Bağlantınız ⚡",
            "headline": "Tekrar Hoş Geldiniz 👋",
            "intro_text": "İşte <strong>Sharegy</strong> için kişisel tek seferlik giriş bağlantınız. Hesabınıza güvenli bir şekilde giriş yapmak için aşağıdaki düğmeye tıklayın:",
            "button_text": "🔐 Güvenli Giriş Yap",
            "fallback_label": "Alternatif doğrudan bağlantı:",
            "validity_label": "Geçerlilik:",
            "validity_text": "Bu giriş bağlantısı sadece 15 dakika geçerlidir ve tek seferliktir.",
            "ignore_text": "Bu talebi siz yapmadıysanız bu e-postayı güvenle yok sayabilirsiniz. Hesabınız tamamen güvendedir.",
            "plain_intro": "Sharegy'ye tekrar hoş geldiniz.",
            "plain_link_label": "Buradan giriş yapın:",
            "plain_expiry": "Bağlantı 15 dakika geçerlidir.",
        },
        "ru": {
            "subject": "Ваша ссылка для входа в Sharegy ⚡",
            "headline": "С возвращением 👋",
            "intro_text": "Вот ваша персональная одноразовая ссылка для входа в <strong>Sharegy</strong>. Нажмите кнопку ниже, чтобы безопасно войти в систему:",
            "button_text": "🔐 Безопасный вход",
            "fallback_label": "Прямая ссылка:",
            "validity_label": "Срок действия:",
            "validity_text": "Эта ссылка действительна в течение 15 минут и может быть использована один раз.",
            "ignore_text": "Если вы не запрашивали эту ссылку, просто проигнорируйте письмо. Ваш аккаунт в безопасности.",
            "plain_intro": "С возвращением в Sharegy.",
            "plain_link_label": "Войти здесь:",
            "plain_expiry": "Ссылка действительна 15 минут.",
        },
    }

    t = I18N.get(lang, I18N["de"])
    subject = t["subject"]
    tracking_url = getattr(settings, "TRACKING_BASE_URL", getattr(settings, "BACKEND_URL", "https://api.sharegy.de"))
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "Sharegy <invite@sharegy.cloud>")

    context = {
        "magic_link": link,
        "token": token,
        "tracking_base_url": tracking_url,
        **t,
    }

    html_message = render_to_string("emails/magic_login.html", context)
    plain_message = f"Hallo 👋\n\n{t['plain_intro']}\n\n{t['plain_link_label']}\n{link}\n\n{t['plain_expiry']}\n\nSharegy ⚡\nhttps://sharegy.de"

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


def send_weekly_report_email(user, report_data=None, language=None):
    """
    Sendet den wöchentlichen mehrsprachigen Energie- und Autarkie-Report an den Benutzer.
    """
    lang = get_user_language(user, language)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "Sharegy <invite@sharegy.cloud>")
    user_name = user.first_name or ""

    if report_data is None:
        report_data = {}

    pv_generated_kwh = report_data.get("pv_generated_kwh", 0.0)
    self_consumed_kwh = report_data.get("self_consumed_kwh", 0.0)
    autarky_pct = report_data.get("autarky_pct", 0)
    saved_eur = report_data.get("saved_eur", 0.00)
    grid_feedin_kwh = report_data.get("grid_feedin_kwh", 0.0)
    grid_purchased_kwh = report_data.get("grid_purchased_kwh", 0.0)
    period_str = report_data.get("period_str", "Letzte 7 Tage")
    dashboard_url = report_data.get(
        "dashboard_url",
        getattr(settings, "FRONTEND_URL", "https://sharegy.de") + "/dashboard",
    )

    I18N = {
        "de": {
            "subject": "Dein wöchentlicher Energie- & Autarkie-Report ⚡",
            "headline": "Dein wöchentlicher Energie- & Autarkie-Report",
            "greeting": "Hallo",
            "intro_text": "hier ist deine persönliche Energie-Bilanz der vergangenen Woche im Überblick:",
            "period_label": "Zeitraum",
            "pv_generated_label": "PV-Erzeugung",
            "self_consumption_label": "Eigenverbrauch",
            "autarky_label": "Autarkiegrad",
            "savings_label": "Erzielte Ersparnis",
            "grid_feedin_label": "Netzeinspeisung",
            "grid_purchased_label": "Netzbezug",
            "button_text": "📊 Zum Live-Dashboard",
            "settings_hint": "Du erhältst diese E-Mail, da du den wöchentlichen Energie-Report in deinem Profil aktiviert hast.",
        },
        "en": {
            "subject": "Your weekly energy & autarky report ⚡",
            "headline": "Your Weekly Energy & Autarky Report",
            "greeting": "Hello",
            "intro_text": "here is your personal energy summary for the past week at a glance:",
            "period_label": "Period",
            "pv_generated_label": "Solar Generation",
            "self_consumption_label": "Self-Consumption",
            "autarky_label": "Autarky Rate",
            "savings_label": "Estimated Savings",
            "grid_feedin_label": "Grid Feed-In",
            "grid_purchased_label": "Grid Purchased",
            "button_text": "📊 Open Live Dashboard",
            "settings_hint": "You are receiving this email because the weekly energy report is enabled in your profile.",
        },
        "pl": {
            "subject": "Twój tygodniowy raport energii i autarkii ⚡",
            "headline": "Twój cotygodniowy raport energii i autarkii",
            "greeting": "Cześć",
            "intro_text": "oto Twoje osobiste podsumowanie bilansu energetycznego z minionego tygodnia:",
            "period_label": "Okres",
            "pv_generated_label": "Produkcja solarna",
            "self_consumption_label": "Autokonsumpcja",
            "autarky_label": "Wskaźnik autarkii",
            "savings_label": "Oszczędności",
            "grid_feedin_label": "Oddanie do sieci",
            "grid_purchased_label": "Pobór z sieci",
            "button_text": "📊 Otwórz panel na żywo",
            "settings_hint": "Otrzymujesz tę wiadomość, ponieważ w profilu włączono cotygodniowy raport energii.",
        },
    }

    t = I18N.get(lang, I18N["de"])

    context = {
        "user_name": user_name,
        "pv_generated_kwh": f"{pv_generated_kwh:.1f}" if isinstance(pv_generated_kwh, (int, float)) else str(pv_generated_kwh),
        "self_consumed_kwh": f"{self_consumed_kwh:.1f}" if isinstance(self_consumed_kwh, (int, float)) else str(self_consumed_kwh),
        "autarky_pct": int(autarky_pct) if isinstance(autarky_pct, (int, float)) else str(autarky_pct),
        "saved_eur": f"{saved_eur:.2f}" if isinstance(saved_eur, (int, float)) else str(saved_eur),
        "grid_feedin_kwh": f"{grid_feedin_kwh:.1f}" if isinstance(grid_feedin_kwh, (int, float)) else str(grid_feedin_kwh),
        "grid_purchased_kwh": f"{grid_purchased_kwh:.1f}" if isinstance(grid_purchased_kwh, (int, float)) else str(grid_purchased_kwh),
        "period_str": period_str,
        "dashboard_url": dashboard_url,
        **t,
    }

    text_body = render_to_string("emails/weekly_report.txt", context)
    html_body = render_to_string("emails/weekly_report.html", context)

    msg = EmailMultiAlternatives(t["subject"], text_body, from_email, [user.email])
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)
    logger.info("Sent weekly energy report to %s (Language: %s)", user.email, lang)
    return True


def send_critical_alert_email(user, alert_data, language=None):
    """
    Sendet eine sofortige mehrsprachige E-Mail-Warnung bei kritischen Hardware-Störungen.
    """
    lang = get_user_language(user, language)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "Sharegy <invite@sharegy.cloud>")
    user_name = user.first_name or ""

    alert_title = alert_data.get("title", "Kritische Störung")
    alert_message = alert_data.get("message", "")
    device_name = alert_data.get("device_name", "")
    action_hint = alert_data.get("action_hint", "")
    action_url = alert_data.get(
        "action_url",
        getattr(settings, "FRONTEND_URL", "https://sharegy.de") + "/alerts",
    )

    I18N = {
        "de": {
            "subject_prefix": "🚨 Kritische Warnung",
            "headline": "Kritischer Hardware-Alarm",
            "greeting": "Hallo",
            "intro_text": "unser Überwachungssystem hat soeben eine kritische Störung bei deiner Hardware festgestellt:",
            "severity_badge": "KRITISCHE HARDWARE-WARNUNG",
            "device_label": "Betroffenes Gerät / System",
            "message_label": "Meldung",
            "action_label": "Empfohlene Sofortmaßnahme",
            "button_text": "🛠️ Alarm im System prüfen",
            "settings_hint": "Du erhältst diese Warnung per E-Mail, da kritische Hardware-Alarme in deinem Profil aktiviert sind.",
        },
        "en": {
            "subject_prefix": "🚨 Critical Alert",
            "headline": "Critical Hardware Alert",
            "greeting": "Hello",
            "intro_text": "our monitoring system has detected a critical issue with your energy equipment:",
            "severity_badge": "CRITICAL HARDWARE ALERT",
            "device_label": "Affected Device / System",
            "message_label": "Issue Details",
            "action_label": "Recommended Action",
            "button_text": "🛠️ Check Issue in System",
            "settings_hint": "You are receiving this alert by email because critical hardware alerts are enabled in your profile.",
        },
        "pl": {
            "subject_prefix": "🚨 Alert krytyczny",
            "headline": "Krytyczny alert sprzętowy",
            "greeting": "Cześć",
            "intro_text": "nasz system monitoringu wykrył krytyczną usterkę w Twoim sprzęcie energetycznym:",
            "severity_badge": "KRYTYCZNY ALERT SPRZĘTOWY",
            "device_label": "Urządzenie / System",
            "message_label": "Szczegóły",
            "action_label": "Zalecane działanie",
            "button_text": "🛠️ Sprawdź alert w systemie",
            "settings_hint": "Otrzymujesz to ostrzeżenie e-mailem, ponieważ krytyczne alerty sprzętowe są włączone w Twoim profilu.",
        },
    }

    t = I18N.get(lang, I18N["de"])
    subject = f"{t['subject_prefix']}: {alert_title} – Sharegy"

    context = {
        "user_name": user_name,
        "alert_title": alert_title,
        "alert_message": alert_message,
        "device_name": device_name,
        "action_hint": action_hint,
        "action_url": action_url,
        **t,
    }

    text_body = render_to_string("emails/critical_alert.txt", context)
    html_body = render_to_string("emails/critical_alert.html", context)

    msg = EmailMultiAlternatives(subject, text_body, from_email, [user.email])
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)
    logger.info("Sent critical alert email to %s (Language: %s): %s", user.email, lang, alert_title)
    return True