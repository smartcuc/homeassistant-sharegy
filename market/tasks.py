#################
# market/tasks.py
#################

import logging
import requests
from decimal import Decimal
from datetime import timezone as dt_timezone

from celery import shared_task
from django.utils import timezone
from django.core.cache import cache

from market.models import SpotPrice
from market.tasks_analysis import compute_daily_spot_summary

logger = logging.getLogger(__name__)


def unix_to_dt(ts):
    return timezone.datetime.fromtimestamp(ts, tz=dt_timezone.utc)


def fetch_spot_prices_smard():
    """
    Holt 15-Minuten Spotpreise direkt von der SMARD-Schnittstelle der Bundesnetzagentur.
    """
    index_url = "https://www.smard.de/app/chart_data/4169/DE-LU/index_quarterhour.json"
    index_response = requests.get(index_url, timeout=15)
    index_response.raise_for_status()

    timestamps = index_response.json().get("timestamps", [])
    if not timestamps:
        return {"status": "error", "count": 0}

    latest_timestamp = timestamps[-1]
    data_url = (
        f"https://www.smard.de/app/chart_data/4169/DE-LU/"
        f"4169_DE-LU_quarterhour_{latest_timestamp}.json"
    )

    response = requests.get(data_url, timeout=15)
    response.raise_for_status()
    data = response.json()

    objs = []
    for ts_ms, price_mwh in data.get("series", []):
        if price_mwh is None:
            continue

        dt = timezone.datetime.fromtimestamp(ts_ms / 1000, tz=dt_timezone.utc)
        price_kwh = Decimal(str(price_mwh)) / Decimal("1000")

        objs.append(
            SpotPrice(
                timestamp=dt,
                price_eur_per_kwh=price_kwh,
                source="smard",
            )
        )

    if objs:
        SpotPrice.objects.bulk_create(
            objs,
            update_conflicts=True,
            unique_fields=["timestamp", "source"],
            update_fields=["price_eur_per_kwh"],
        )

    count = len(objs)
    cache.set("spot:last_update", timezone.now().isoformat(), timeout=None)
    cache.set("spot:last_count", count, timeout=None)
    cache.set("spot:last_success", True, timeout=None)

    return {"status": "ok", "source": "smard", "count": count}


@shared_task
def fetch_spot_prices():
    """
    Holt Spotpreise primär von Energy-Charts (Fraunhofer ISE).
    Falls nicht erreichbar oder unvollständig, greift automatisch SMARD als Fallback.
    """
    url = "https://api.energy-charts.info/price"
    start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timezone.timedelta(days=2)

    params = {
        "bzn": "DE-LU",
        "start": int(start.timestamp()),
        "end": int(end.timestamp()),
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        timestamps = data.get("unix_seconds", [])
        prices = data.get("price", [])

        objs = []
        for ts, price_mwh in zip(timestamps, prices):
            if price_mwh is None:
                continue

            dt = unix_to_dt(ts)
            price_kwh = Decimal(str(price_mwh)) / Decimal("1000")

            objs.append(
                SpotPrice(
                    timestamp=dt,
                    price_eur_per_kwh=price_kwh,
                    source="energy-charts",
                )
            )

        if objs:
            SpotPrice.objects.bulk_create(
                objs,
                update_conflicts=True,
                unique_fields=["timestamp", "source"],
                update_fields=["price_eur_per_kwh"],
            )

        count = len(objs)
        cache.set("spot:last_update", timezone.now().isoformat(), timeout=None)
        cache.set("spot:last_count", count, timeout=None)
        cache.set("spot:last_success", True, timeout=None)

        return {"status": "ok", "source": "energy-charts", "count": count}

    except Exception as e:
        logger.warning("Energy-Charts Abruf fehlgeschlagen (%s), versuche SMARD Fallback", e)
        return fetch_spot_prices_smard()


@shared_task(bind=True, max_retries=16)
def fetch_spot_prices_retry(self):
    """
    Intelligenter Day-Ahead Abruf:
    Prüft, ob für MORGEN bereits vollständige Preisdaten in der DB vorliegen.
    Falls ja: Sofortige Beendigung in <1ms ohne externe API-Last.
    Falls nein: Versucht Energy-Charts -> SMARD und plant sanften Retry.
    """
    now = timezone.now()
    tomorrow = (now + timezone.timedelta(days=1)).date()
    cache_key = f"spot:tomorrow_synced_{tomorrow.isoformat()}"

    # 1. Schnelle Cache-Prüfung: Wurde morgen heute bereits erfolgreich synchronisiert?
    if cache.get(cache_key):
        return {"status": "already_synced", "date": str(tomorrow)}

    # 2. DB-Prüfung: Liegen bereits >= 24 Stundenpreise für morgen vor?
    tomorrow_start = timezone.make_aware(timezone.datetime.combine(tomorrow, timezone.datetime.min.time()))
    tomorrow_end = tomorrow_start + timezone.timedelta(days=1)
    tomorrow_count = SpotPrice.objects.filter(
        timestamp__gte=tomorrow_start,
        timestamp__lt=tomorrow_end,
    ).count()

    if tomorrow_count >= 24:
        cache.set(cache_key, True, timeout=86400)
        cache.set("spot:ready", True, timeout=None)
        compute_daily_spot_summary.delay()
        return {"status": "already_complete_in_db", "count": tomorrow_count}

    # 3. Externe Abfrage ausführen
    try:
        result = fetch_spot_prices()

        # Nach dem Abruf erneut prüfen, ob der morgige Tag da ist
        tomorrow_count_after = SpotPrice.objects.filter(
            timestamp__gte=tomorrow_start,
            timestamp__lt=tomorrow_end,
        ).count()

        if tomorrow_count_after >= 24:
            cache.set(cache_key, True, timeout=86400)
            cache.set("spot:ready", True, timeout=None)
            compute_daily_spot_summary.delay()
            return {
                "status": "ok",
                "source": result.get("source"),
                "tomorrow_points": tomorrow_count_after,
            }

        # Falls nach 13:00 Uhr noch keine Daten für morgen vorliegen: Retry in 15 Min
        if now.hour >= 13:
            raise Exception(f"Börsenpreise für morgen ({tomorrow}) noch nicht publiziert ({tomorrow_count_after} Werte)")

        return result

    except Exception as e:
        cache.set("spot:last_success", False, timeout=None)
        logger.info("Spotpreis-Sync Retry geplant (%s)", e)
        # Retry alle 15 Minuten (900 Sekunden)
        raise self.retry(countdown=900, exc=e)
