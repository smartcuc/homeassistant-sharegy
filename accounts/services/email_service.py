import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_email(template, subject, user, context):
    
    # ✅ Tenant sauber ermitteln über Membership
    membership = user.memberships.filter(is_active=True).select_related("tenant").first()
    tenant = membership.tenant if membership else None

    # ✅ Fallback (super wichtig!)
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


def send_magic_link_email(user, link, token):
    subject = "Dein Login-Link für Sharegy"
    tracking_url = getattr(settings, "TRACKING_BASE_URL", getattr(settings, "BACKEND_URL", "https://api.sharegy.de"))
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "Sharegy <invite@sharegy.cloud>")

    html_message = render_to_string("emails/magic_login.html", {
        "magic_link": link,
        "token": token,
        "tracking_base_url": tracking_url,
    })

    plain_message = f"Login-Link: {link}"

    logger.info("Sending magic link email to %s via %s (Host: %s:%s)", user.email, from_email, getattr(settings, "EMAIL_HOST", None), getattr(settings, "EMAIL_PORT", None))

    send_mail(
        subject,
        plain_message,
        from_email,
        [user.email],
        html_message=html_message,
    )