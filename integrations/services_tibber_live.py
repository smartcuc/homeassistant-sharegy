######################################
# integrations/services_tibber_live.py
######################################

import asyncio
import json
import random
import websockets
import requests
import logging

from django.utils.dateparse import parse_datetime
from django.core.cache import cache

from integrations.live_state import LIVE_STATE

logger = logging.getLogger("integrations")

LAST_EVENT_TS = {}

GRAPHQL_HTTP_URL = "https://api.tibber.com/v1-beta/gql"


# ✅ WebSocket URL dynamisch holen (einmal)
def get_ws_url(token):
    query = """
    {
      viewer {
        websocketSubscriptionUrl
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Django/ESWES 1.0",
    }

    try:
        resp = requests.post(GRAPHQL_HTTP_URL, json={"query": query}, headers=headers, timeout=(10, 25))
        data = resp.json()
        return data.get("data", {}).get("viewer", {}).get("websocketSubscriptionUrl")
    except Exception as e:
        logger.warning("Could not fetch Tibber websocketSubscriptionUrl: %s", e)
        return None



# ✅ EIN einzelner Stream (keine DB Writes)
async def tibber_live_stream_multi(token, meters):

    ws_url = get_ws_url(token)

    async with websockets.connect(
        ws_url,
        subprotocols=["graphql-transport-ws"],
        additional_headers={"Authorization": f"Bearer {token}"},
    ) as ws:

        # ✅ INIT
        await ws.send(json.dumps({"type": "connection_init"}))

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if data.get("type") == "connection_ack":
                print("✅ Tibber ACK")
                break

        # ✅ MULTI SUBSCRIBE
        for idx, meter in enumerate(meters):
            query = f"""
            subscription {{
              liveMeasurement(homeId: "{meter.tibber_home_id}") {{
                timestamp
                power
              }}
            }}
            """

            await ws.send(
                json.dumps(
                    {"id": str(idx), "type": "subscribe", "payload": {"query": query}}
                )
            )

        print(f"⚡ Subscribed to {len(meters)} meters")

        # ✅ LOOP
        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if data.get("type") != "next":
                continue

            sub_id = data["id"]
            meter = meters[int(sub_id)]

            measurement = data["payload"]["data"]["liveMeasurement"]

            ts = parse_datetime(measurement["timestamp"])

            cache.set(f"energy:last_event:{meter.id}", ts.isoformat(), timeout=None)

            # ✅ NEU: Meter IDs speichern
            meter_ids = cache.get("energy:meters") or []

            if str(meter.id) not in meter_ids:
                meter_ids.append(str(meter.id))
                cache.set("energy:meters", meter_ids, timeout=None)

            LAST_EVENT_TS[str(meter.id)] = ts

            power = measurement["power"] or 0

            cache.set(f"energy:last_power:{meter.id}", power, timeout=None)

            LIVE_STATE[str(meter.id)] = {
                "provider": "tibber",
                "power": power,
                "timestamp": ts.isoformat(),
            }

            short_id = str(meter.id).split("-")[0]
            logger.debug(f"⚡ {short_id} → {power} W")


# ✅ Reconnect + Backoff


async def tibber_live_stream_forever(token, meters):

    while True:
        try:
            await tibber_live_stream_multi(token, meters)

        except Exception as e:
            print("⚠️ Stream Fehler:", e)

            delay = random.uniform(5, 30)
            print(f"🔄 Reconnect in {delay:.1f}s")

            await asyncio.sleep(delay)
