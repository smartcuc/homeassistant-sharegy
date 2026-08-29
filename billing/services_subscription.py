################################
# billing/services_subscription.py
################################

import uuid
from decimal import Decimal
from datetime import date, timedelta
from io import BytesIO

from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from billing.models import EMSSubscription, EMSInvoice
from accounts.models import UserProfile


# ==========================================
# 💎 PLANS & PRICING CONFIGURATION
# ==========================================

PLANS_CONFIG = {
    "free": {
        "id": "free",
        "name": "Sharegy Free",
        "category": "free",
        "price_gross_eur": Decimal("0.00"),
        "billing_interval": "month",
        "features": [
            "Live-Sankey Energiefluss & 24h-Historie",
            "Basis-Wetter- & Solarprognose (24h)",
            "Home Assistant & Matter 1.3 Hub",
            "Residual-Zähler & Grundlastmessung",
            "Standard-Web-Cockpit",
        ],
    },
    "pro_monthly": {
        "id": "pro_monthly",
        "name": "Sharegy Pro",
        "category": "pro",
        "price_gross_eur": Decimal("4.99"),
        "billing_interval": "month",
        "popular": True,
        "features": [
            "48h-Prognose-Trio (PV + Last + Speicher-SoC)",
            "Multi-Dauer Börsenstrom-Optimizer (1h, 2h, 4h)",
            "Batterie-Arbitrage & Grid-Charging Simulator",
            "Live CO₂-Grid-Signal & Grünstrom-Index (36h)",
            "Proaktive AI-Alarmzentrale (8 Erkennungsregeln)",
            "Unbegrenzte Historie & Submeter-Trends",
            "Multi-Format Daten-Export (Excel, PDF, CSV, JSON)",
        ],
    },
    "pro_yearly": {
        "id": "pro_yearly",
        "name": "Sharegy Pro (Jahresabo)",
        "category": "pro",
        "price_gross_eur": Decimal("49.99"),
        "price_monthly_equivalent": Decimal("4.17"),
        "billing_interval": "year",
        "discount_pct": 17,
        "features": [
            "Alle Pro-Features inklusive",
            "2 Monate kostenlos (17% Ersparnis)",
            "Prioritäts-Support & Feature-Early-Access",
        ],
    },
    "landlord_monthly": {
        "id": "landlord_monthly",
        "name": "Vermieter & Quartiere",
        "category": "landlord",
        "price_gross_eur": Decimal("14.99"),
        "billing_interval": "month",
        "features": [
            "Alle Pro-Features für alle Wohneinheiten",
            "Multi-Home & Unterzähler-Abrechnung",
            "Mieterstrom-Berichte & Steuer-PDFs",
            "Quartiers-Clearing & P2P-Export",
        ],
    },
    "landlord_yearly": {
        "id": "landlord_yearly",
        "name": "Vermieter & Quartiere (Jahresabo)",
        "category": "landlord",
        "price_gross_eur": Decimal("149.99"),
        "price_monthly_equivalent": Decimal("12.50"),
        "billing_interval": "year",
        "discount_pct": 17,
        "features": [
            "Alle Vermieter-Features inklusive",
            "2 Monate kostenlos (17% Ersparnis)",
            "Dedizierter Enterprise-Support",
        ],
    },
}


def get_or_create_subscription(user):
    """
    Holt das Abonnement des Benutzers oder initialisiert den Free-Plan.
    """
    sub, created = EMSSubscription.objects.get_or_create(
        user=user,
        defaults={
            "plan": EMSSubscription.PLAN_FREE,
            "status": EMSSubscription.STATUS_ACTIVE,
            "current_period_start": timezone.now(),
            "payment_method": "stripe",
        },
    )
    return sub


def get_subscription_overview(user):
    """
    Gibt vollständige Abrechnungs- und Abonnement-Daten für das Frontend zurück.
    """
    sub = get_or_create_subscription(user)
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Invoices abrufen
    invoices = list(
        sub.invoices.all().values(
            "id",
            "invoice_number",
            "plan_name",
            "amount_gross_eur",
            "status",
            "paid_at",
            "created_at",
            "period_start",
            "period_end",
        )
    )

    # Falls keine Rechnungen existieren und User Pro ist -> Demo-Rechnung erzeugen
    if not invoices and sub.is_pro_active:
        seed_demo_invoices(user)
        invoices = list(
            sub.invoices.all().values(
                "id",
                "invoice_number",
                "plan_name",
                "amount_gross_eur",
                "status",
                "paid_at",
                "created_at",
                "period_start",
                "period_end",
            )
        )

    current_plan_config = PLANS_CONFIG.get(sub.plan, PLANS_CONFIG["free"])

    return {
        "subscription": {
            "id": str(sub.id),
            "plan": sub.plan,
            "plan_name": current_plan_config["name"],
            "status": sub.status,
            "is_pro": sub.is_pro_active,
            "is_landlord": sub.is_landlord_active,
            "current_period_start": sub.current_period_start.isoformat() if sub.current_period_start else None,
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
            "cancel_at_period_end": sub.cancel_at_period_end,
            "payment_method": sub.payment_method,
            "payment_method_brand": sub.payment_method_brand or "visa",
            "payment_method_last4": sub.payment_method_last4 or "4242",
            "entitlements": sub.entitlements,
        },
        "billing_address": {
            "billing_name": profile.billing_name or f"{user.first_name} {user.last_name}".strip() or user.username,
            "customer_type": profile.customer_type,
            "company_name": profile.company_name,
            "vat_id": profile.vat_id,
            "street": profile.street,
            "house_number": profile.house_number,
            "postal_code": profile.postal_code,
            "city": profile.city,
            "country": profile.country,
            "email": user.email,
        },
        "available_plans": PLANS_CONFIG,
        "invoices": invoices,
    }


def update_billing_address(user, data):
    """
    Aktualisiert die Rechnungsadresse im Benutzerprofil.
    """
    profile, _ = UserProfile.objects.get_or_create(user=user)

    profile.billing_name = data.get("billing_name", profile.billing_name)
    profile.customer_type = data.get("customer_type", profile.customer_type)
    profile.company_name = data.get("company_name", profile.company_name)
    profile.vat_id = data.get("vat_id", profile.vat_id)
    profile.street = data.get("street", profile.street)
    profile.house_number = data.get("house_number", profile.house_number)
    profile.postal_code = data.get("postal_code", profile.postal_code)
    profile.city = data.get("city", profile.city)
    profile.country = data.get("country", profile.country)

    profile.save()
    return profile


DISPOSABLE_EMAIL_DOMAINS = {
    "mailinator.com", "trashmail.com", "tempmail.com", "guerrillamail.com",
    "sharklasers.com", "10minutemail.com", "yopmail.com", "temp-mail.org",
    "dispostable.com", "getairmail.com", "throwawaymail.com",
}


def validate_upgrade_eligibility(user, terms_accepted=True, request_meta=None):
    """
    Prüft vor dem Wechsel auf einen Pro-/Bezahlplan:
    1. Gültige E-Mail-Adresse (keine Wegwerf-Mail).
    2. Dokumentierte Zustimmung zu den AGBs.
    """
    import re
    from accounts.models import UserTermsConsent

    email = (user.email or "").strip().lower()
    if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("Für ein Pro-Abonnement ist eine gültige E-Mail-Adresse erforderlich.")

    domain = email.split("@")[-1]
    if domain in DISPOSABLE_EMAIL_DOMAINS:
        raise ValueError("Wegwerf-E-Mail-Adressen sind für Pro-Abonnements nicht zugelassen. Bitte hinterlege eine dauerhafte E-Mail-Adresse.")

    if not terms_accepted:
        raise ValueError("Bitte bestätige die AGB und Datenschutzbestimmungen, um das Abonnement abzuschließen.")

    # AGB-Zustimmung rechtssicher protokollieren
    ip = None
    ua = ""
    if request_meta:
        ip = request_meta.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request_meta.get("REMOTE_ADDR")
        ua = request_meta.get("HTTP_USER_AGENT", "")[:500]

    UserTermsConsent.objects.create(
        user=user,
        terms_version="2026-08",
        privacy_version="2026-08",
        consent_type=UserTermsConsent.CONSENT_UPGRADE_PRO,
        ip_address=ip if ip and len(ip) <= 45 else None,
        user_agent=ua,
    )


def change_subscription_plan(user, new_plan_id, payment_method="Kreditkarte (via Stripe)", terms_accepted=True, request_meta=None):
    """
    Upgraded oder Downgraded das Abonnement und erzeugt bei Bezahlplänen eine Rechnung.
    """
    if new_plan_id not in PLANS_CONFIG:
        raise ValueError(f"Ungültiger Plan: {new_plan_id}")

    # Wenn Upgrade auf Bezahlplan (Pro / Landlord): Validierung durchführen
    if new_plan_id != EMSSubscription.PLAN_FREE:
        validate_upgrade_eligibility(user, terms_accepted=terms_accepted, request_meta=request_meta)

    sub = get_or_create_subscription(user)
    plan_info = PLANS_CONFIG[new_plan_id]

    now = timezone.now()
    if plan_info["billing_interval"] == "year":
        period_end = now + timedelta(days=365)
    else:
        period_end = now + timedelta(days=30)

    sub.plan = new_plan_id
    sub.status = EMSSubscription.STATUS_ACTIVE
    sub.current_period_start = now
    sub.current_period_end = period_end
    sub.cancel_at_period_end = False
    sub.payment_method = "stripe"
    if not sub.payment_method_brand:
        sub.payment_method_brand = "visa"
        sub.payment_method_last4 = "4242"
    sub.save()

    # Wenn bezahlter Plan: Rechnung anlegen
    gross = plan_info["price_gross_eur"]
    if gross > 0:
        create_invoice_for_subscription(
            subscription=sub,
            plan_id=new_plan_id,
            payment_method=payment_method,
            period_start=now.date(),
            period_end=period_end.date(),
        )

    return sub


def validate_coupon_code(code, user=None):
    """
    Prüft einen Gutscheincode auf Gültigkeit und berechnet den Rabatt/Vorteil.
    """
    from billing.models import Coupon, CouponRedemption

    clean_code = (code or "").strip().upper()
    if not clean_code:
        raise ValueError("Bitte gib einen Gutscheincode ein.")

    coupon = Coupon.objects.filter(code=clean_code).first()
    if not coupon:
        raise ValueError(f"Gutscheincode '{clean_code}' ist ungültig oder existiert nicht.")

    if not coupon.is_valid:
        raise ValueError(f"Gutscheincode '{clean_code}' ist abgelaufen oder hat das Einlösungslimit erreicht.")

    if user and CouponRedemption.objects.filter(coupon=coupon, user=user).exists():
        raise ValueError(f"Du hast den Gutscheincode '{clean_code}' bereits eingelöst.")

    return {
        "valid": True,
        "code": coupon.code,
        "description": coupon.description or (
            f"{coupon.duration_months} Monate Pro kostenlos"
            if coupon.discount_type == Coupon.TYPE_FREE_MONTHS
            else f"{coupon.discount_value}% Rabatt"
        ),
        "discount_type": coupon.discount_type,
        "discount_value": float(coupon.discount_value),
        "free_plan": coupon.free_plan,
        "duration_months": coupon.duration_months,
    }


def redeem_coupon_code(code, user, terms_accepted=True, request_meta=None):
    """
    Löst einen Gutschein ein und schaltet das entsprechende Abonnement frei.
    """
    from billing.models import Coupon, CouponRedemption

    coupon_info = validate_coupon_code(code, user=user)
    coupon = Coupon.objects.get(code=coupon_info["code"])

    # E-Mail & AGB prüfen
    validate_upgrade_eligibility(user, terms_accepted=terms_accepted, request_meta=request_meta)

    sub = get_or_create_subscription(user)
    now = timezone.now()

    # Freischaltung durchführen
    if coupon.discount_type == Coupon.TYPE_FREE_MONTHS or (coupon.discount_type == Coupon.TYPE_PERCENT and coupon.discount_value >= Decimal("100.00")):
        duration_days = coupon.duration_months * 30
        sub.plan = coupon.free_plan or EMSSubscription.PLAN_PRO_MONTHLY
        sub.status = EMSSubscription.STATUS_ACTIVE
        sub.current_period_start = now
        sub.current_period_end = now + timedelta(days=duration_days)
        sub.cancel_at_period_end = False
        sub.payment_method = "coupon"
        sub.payment_method_brand = "promo"
        sub.payment_method_last4 = coupon.code[:4]
        sub.save()

    # Redemption speichern
    CouponRedemption.objects.create(
        coupon=coupon,
        user=user,
        subscription=sub,
        applied_discount=coupon_info["description"],
    )

    coupon.redemptions_count += 1
    coupon.save(update_fields=["redemptions_count"])

    return sub



def cancel_subscription(user, at_period_end=True):
    """
    Kündigt das Abonnement zum Ende des aktuellen Abrechnungszeitraums.
    """
    sub = get_or_create_subscription(user)
    if at_period_end:
        sub.cancel_at_period_end = True
    else:
        sub.plan = EMSSubscription.PLAN_FREE
        sub.status = EMSSubscription.STATUS_CANCELED
        sub.cancel_at_period_end = False
    sub.save()
    return sub


def reactivate_subscription(user):
    """
    Reaktiviert ein zum Periodenende gekündigtes Abonnement.
    """
    sub = get_or_create_subscription(user)
    sub.cancel_at_period_end = False
    sub.status = EMSSubscription.STATUS_ACTIVE
    sub.save()
    return sub


def create_invoice_for_subscription(subscription, plan_id, payment_method, period_start=None, period_end=None):
    """
    Erstellt einen EMSInvoice-Datensatz mit Rechnungsnummer und MwSt.-Berechnung.
    """
    plan_info = PLANS_CONFIG.get(plan_id, PLANS_CONFIG["pro_monthly"])
    user = subscription.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    gross = plan_info["price_gross_eur"]
    tax_rate = Decimal("19.00")
    net = (gross / Decimal("1.19")).quantize(Decimal("0.01"))
    tax = gross - net

    now = timezone.now()
    if not period_start:
        period_start = now.date()
    if not period_end:
        period_end = (now + timedelta(days=30 if plan_info["billing_interval"] == "month" else 365)).date()

    # Fortlaufende Rechnungsnummer z. B. SHG-2026-080123
    seq = EMSInvoice.objects.filter(created_at__year=now.year).count() + 1
    invoice_number = f"SHG-{now.year}-{seq:05d}"

    recipient = profile.billing_name or f"{user.first_name} {user.last_name}".strip() or user.username
    street = f"{profile.street} {profile.house_number}".strip() or "Musterstraße 1"
    postal = profile.postal_code or "10115"
    city = profile.city or "Berlin"
    country = profile.country or "DE"

    invoice = EMSInvoice.objects.create(
        invoice_number=invoice_number,
        user=user,
        subscription=subscription,
        plan_name=plan_info["name"],
        amount_net_eur=net,
        tax_eur=tax,
        amount_gross_eur=gross,
        tax_rate_pct=tax_rate,
        period_start=period_start,
        period_end=period_end,
        status=EMSInvoice.STATUS_PAID,
        payment_method=payment_method,
        paid_at=now,
        recipient_name=recipient,
        company_name=profile.company_name,
        street_and_number=street,
        postal_code=postal,
        city=city,
        country=country,
        vat_id=profile.vat_id,
    )
    return invoice


def seed_demo_invoices(user):
    """
    Erzeugt 2 realistische Demo-Rechnungen für Tests und Preview.
    """
    sub = get_or_create_subscription(user)
    today = date.today()

    # Rechnung vorletzter Monat
    create_invoice_for_subscription(
        subscription=sub,
        plan_id="pro_monthly",
        payment_method="Kreditkarte (•••• 4242)",
        period_start=today - timedelta(days=60),
        period_end=today - timedelta(days=30),
    )

    # Rechnung aktueller Monat
    create_invoice_for_subscription(
        subscription=sub,
        plan_id="pro_monthly",
        payment_method="Kreditkarte (•••• 4242)",
        period_start=today - timedelta(days=30),
        period_end=today,
    )


def generate_invoice_pdf(invoice):
    """
    Erstellt ein professionelles, A4-PDF-Dokument der Rechnung via ReportLab.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    normal_style.fontSize = 9
    normal_style.leading = 13
    normal_style.textColor = colors.HexColor("#1F2937")

    bold_style = ParagraphStyle(
        "BoldText",
        parent=normal_style,
        fontName="Helvetica-Bold",
    )

    title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#111827"),
        fontName="Helvetica-Bold",
    )

    story = []

    # 1. Header (Logo & Firmendaten)
    header_data = [
        [
            Paragraph("<b>Sharegy Energy Management</b><br/>Sharegy Cloud GmbH<br/>Energieallee 42<br/>10115 Berlin", normal_style),
            Paragraph(f"<font size='14' color='#059669'><b>RECHNUNG</b></font><br/><b>Rechnungs-Nr.:</b> {invoice.invoice_number}<br/><b>Datum:</b> {invoice.created_at.strftime('%d.%m.%Y')}<br/><b>Status:</b> Bezahlt (via Stripe)", normal_style),
        ]
    ]
    header_table = Table(header_data, colWidths=[270, 245])
    header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(header_table)
    story.append(Spacer(1, 20))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E5E7EB"), spaceAfter=15))

    # 2. Empfängerdaten
    recipient_lines = [
        f"<b>{invoice.recipient_name}</b>",
    ]
    if invoice.company_name:
        recipient_lines.append(invoice.company_name)
    if invoice.street_and_number:
        recipient_lines.append(invoice.street_and_number)
    recipient_lines.append(f"{invoice.postal_code} {invoice.city}".strip())
    if invoice.country:
        recipient_lines.append(f"Land: {invoice.country}")
    if invoice.vat_id:
        recipient_lines.append(f"USt-IdNr.: {invoice.vat_id}")

    customer_table = Table(
        [
            [Paragraph("<b>Rechnungsempfänger:</b><br/>" + "<br/>".join(recipient_lines), normal_style),
             Paragraph(f"<b>Leistungszeitraum:</b><br/>{invoice.period_start.strftime('%d.%m.%Y')} bis {invoice.period_end.strftime('%d.%m.%Y')}<br/><br/><b>Zahlungsart:</b> {invoice.payment_method}", normal_style)]
        ],
        colWidths=[270, 245],
    )
    customer_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(customer_table)
    story.append(Spacer(1, 25))

    # 3. Positionstabelle
    pos_data = [
        [
            Paragraph("<b>Pos.</b>", bold_style),
            Paragraph("<b>Beschreibung</b>", bold_style),
            Paragraph("<b>Zeitraum</b>", bold_style),
            Paragraph("<b>Netto</b>", bold_style),
            Paragraph("<b>MwSt.</b>", bold_style),
            Paragraph("<b>Gesamt</b>", bold_style),
        ],
        [
            Paragraph("1", normal_style),
            Paragraph(f"<b>{invoice.plan_name}</b><br/>SaaS-Abonnement Home Energy Management System", normal_style),
            Paragraph(f"{invoice.period_start.strftime('%d.%m.%Y')} - {invoice.period_end.strftime('%d.%m.%Y')}", normal_style),
            Paragraph(f"{invoice.amount_net_eur} €", normal_style),
            Paragraph(f"{invoice.tax_rate_pct}%", normal_style),
            Paragraph(f"<b>{invoice.amount_gross_eur} €</b>", normal_style),
        ]
    ]

    pos_table = Table(pos_data, colWidths=[35, 195, 110, 55, 50, 70])
    pos_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
                ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
            ]
        )
    )
    story.append(pos_table)
    story.append(Spacer(1, 15))

    # 4. Summenblock
    summary_data = [
        ["Nettobetrag:", f"{invoice.amount_net_eur} €"],
        [f"zzgl. 19% MwSt.:", f"{invoice.tax_eur} €"],
        ["Gesamtbetrag (Brutto):", f"{invoice.amount_gross_eur} €"],
    ]
    summary_table = Table(summary_data, colWidths=[445, 70])
    summary_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#111827")),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 30))

    # 5. Footer & Danke
    story.append(Paragraph("Der Gesamtbetrag wurde erfolgreich über das hinterlegte Zahlungsmittel beglichen. Vielen Dank für dein Vertrauen in Sharegy!", normal_style))
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#9CA3AF"), spaceAfter=10))
    story.append(Paragraph("<font size='7' color='#6B7280'>Sharegy Cloud GmbH • Geschäftsführer: Smart EMS • HRB 123456 Berlin • USt-IdNr: DE345678901 • Bank: Solaris SE • IBAN: DE89370400440532013000 • BIC: SOLADED1XXX</font>", normal_style))

    doc.build(story)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Rechnung_{invoice.invoice_number}.pdf"'
    return response
