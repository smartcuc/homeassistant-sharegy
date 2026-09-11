#######################
# tracking/analytics.py
#######################

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import EventLog
from .constants import FUNNEL_STEPS

User = get_user_model()


# ============================================================
# ✅ HELPERS
# ============================================================

def _base_queryset(tenant=None, context="global"):
    if context == "tenant" and tenant:
        return EventLog.objects.filter(tenant=tenant)
    if tenant:
        return EventLog.objects.filter(tenant=tenant)
    if context == "global":
        return EventLog.objects.all()
    return EventLog.objects.all()


def _unique_users(queryset):
    return (
        queryset
        .filter(user__isnull=False)
        .values("user")
        .distinct()
        .count()
    )


# ============================================================
# ✅ KPIs
# ============================================================

def get_kpis(tenant=None, context="global", days=7):
    now = timezone.now()

    base_qs = _base_queryset(tenant, context)

    # ✅ Zeitfenster (wichtig!)
    window_start = now - timedelta(days=days)
    window_qs = base_qs.filter(created_at__gte=window_start)

    # ✅ DAU = letzte 24h (bewusst unabhängig vom Fenster)
    dau = _unique_users(
        base_qs.filter(created_at__gte=now - timedelta(days=1))
    )

    # ✅ Funnel (nur im Zeitfenster!)
    landing_users = _unique_users(
        window_qs.filter(name="landing_view")
    )

    signup_users = _unique_users(
        window_qs.filter(name="signup_success")
    )

    login_users = _unique_users(
        window_qs.filter(name="login")
    )

    return {
        "dau": dau,
        "conversion_landing_signup": round(
            (signup_users / landing_users * 100) if landing_users else 0, 2
        ),
        "conversion_signup_login": round(
            (login_users / signup_users * 100) if signup_users else 0, 2
        ),
        "window_days": days,
    }


# ============================================================
# ✅ FUNNEL
# ============================================================

def get_funnel(tenant=None, context="global", days=7):
    now = timezone.now()

    base_qs = _base_queryset(tenant, context)

    # ✅ Zeitfenster
    window_qs = base_qs.filter(
        created_at__gte=now - timedelta(days=days)
    )

    steps = []

    for label, event_name in FUNNEL_STEPS:
        qs = window_qs.filter(name=event_name)

        count = _unique_users(qs)

        steps.append({
            "label": label,
            "count": count
        })

    return {
        "steps": steps,
        "window_days": days
    }

