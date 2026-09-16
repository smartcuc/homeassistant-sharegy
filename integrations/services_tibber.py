#################################
# integrations/services_tibber.py
#################################

import logging
from typing import Optional, Dict, Any, List
import requests
from django.conf import settings
from django.utils.dateparse import parse_datetime

from core.models import IntervalReading
from core.resilience import resilient_http_request, CircuitBreakerOpenException

logger = logging.getLogger("integrations")

TIBBER_API_URL = "https://api.tibber.com/v1-beta/gql"


def get_tibber_homes(token: str) -> dict:
    query = """
    {
      viewer {
        homes {
          id
          appNickname
          address {
            address1
            postalCode
            city
          }
        }
      }
    }
    """
    try:
        resp = resilient_http_request(
            method="POST",
            url=TIBBER_API_URL,
            circuit_name="tibber_api",
            json={"query": query},
            headers=tibber_headers(token),
            timeout=(5.0, 20.0),
            max_retries=2,
        )
        data = resp.json()
        if "errors" in data and data["errors"]:
            return {
                "status": "error",
                "error": data["errors"][0].get("message", "Tibber API-Fehler"),
            }
        homes = data.get("data", {}).get("viewer", {}).get("homes", [])
        formatted = []
        for h in homes:
            addr = h.get("address") or {}
            addr_str = f"{addr.get('address1', '')}, {addr.get('postalCode', '')} {addr.get('city', '')}".strip(" ,")
            formatted.append({
                "id": h.get("id"),
                "name": h.get("appNickname") or addr_str or "Tibber Home",
                "address": addr_str,
            })
        return {"status": "ok", "homes": formatted}
    except CircuitBreakerOpenException:
        logger.warning("[Tibber] Circuit Breaker OPEN -> schnelles Abfangen ohne Blockieren.")
        return {"status": "error", "error": "Tibber API vorübergehend überlastet (Circuit Breaker aktiv)."}
    except requests.exceptions.Timeout:
        logger.warning("Tibber API timeout during get_tibber_homes")
        return {"status": "error", "error": "Tibber Server antwortet nicht rechtzeitig (Timeout)."}
    except Exception as e:
        logger.warning("Tibber API error during get_tibber_homes: %s", e)
        return {"status": "error", "error": str(e)}


def get_tibber_home(token: str) -> dict:
    return get_tibber_homes(token)


def tibber_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def get_tibber_token(user=None) -> Optional[str]:
    """
    DEV: Fallback aus settings/.env
    PROD: später user-spezifisch
    """
    if user:
        token = getattr(user, "tibber_token", None)
        if token:
            return token

    return getattr(settings, "TIBBER_DEFAULT_TOKEN", None)


def fetch_tibber_consumption(home_id: str, token: str, hours: int = 24) -> list:
    query = f"""
    {{
      viewer {{
        home(id: "{home_id}") {{
          consumption(resolution: HOURLY, last: {hours}) {{
            nodes {{
              from
              to
              consumption
            }}
          }}
        }}
      }}
    }}
    """

    try:
        resp = resilient_http_request(
            method="POST",
            url=TIBBER_API_URL,
            circuit_name="tibber_api",
            json={"query": query},
            headers=tibber_headers(token),
            timeout=(5.0, 25.0),
            max_retries=2,
        )
        data = resp.json()
    except CircuitBreakerOpenException:
        logger.warning("[Tibber] Circuit Breaker OPEN bei fetch_tibber_consumption.")
        return []
    except requests.exceptions.Timeout as e:
        logger.warning("Tibber API timeout in fetch_tibber_consumption: %s", e)
        return []
    except requests.exceptions.RequestException as e:
        logger.warning("Tibber API request failed in fetch_tibber_consumption: %s", e)
        return []
    except Exception as e:
        logger.warning("Unerwarteter Fehler bei fetch_tibber_consumption: %s", e)
        return []

    if "errors" in data:
        logger.warning("Tibber API returned errors in consumption: %s", data["errors"])
        return []

    home = data.get("data", {}).get("viewer", {}).get("home")
    if not home or not home.get("consumption"):
        return []

    return home["consumption"].get("nodes", [])


def upsert_tibber_interval_readings(meter, home_id: str, user=None, hours: int = 24, tenant=None) -> dict:
    """
    User-basierter Standard:
    - meter: Pflicht
    - user: optional für user-spezifischen Token
    - tenant: optional; falls nicht gesetzt, wird meter.tenant verwendet (kann None sein)
    """
    token = get_tibber_token(user)

    if not token:
        raise ValueError("No Tibber token available")

    effective_tenant = tenant if tenant is not None else getattr(meter, "tenant", None)

    nodes = fetch_tibber_consumption(
        home_id=home_id,
        token=token,
        hours=hours,
    )

    written = 0
    skipped = 0

    for node in nodes:
        consumption = node.get("consumption")
        if consumption is None:
            skipped += 1
            continue

        ts_start = parse_datetime(node["from"])
        ts_end = parse_datetime(node["to"])

        IntervalReading.objects.update_or_create(
            meter=meter,
            ts_start=ts_start,
            obis_code="1.8.0",
            defaults={
                "tenant": effective_tenant,
                "ts_end": ts_end,
                "value": consumption,
                "unit": "kWh",
                "source": "TIBBER",
            },
        )

        written += 1

    return {
        "status": "ok",
        "written": written,
        "skipped": skipped,
        "total": len(nodes),
    }
