import random
from django.utils import timezone
from devices.models import DeviceLatestMetric, DeviceMetric1h
from providers.matter.models import MatterNode, MatterCluster, MatterEndpoint


def process_matter_attribute_report(
    node: MatterNode,
    endpoint_id: int,
    cluster_id: int,
    attributes: dict,
) -> dict:
    """
    Verarbeitet einen eingehenden Matter 1.3 Attributbericht.
    Aktualisiert MatterCluster, MatterNode und speichert Telemetriedaten
    in Sharegy (DeviceLatestMetric / DeviceMetric1h).
    """
    now = timezone.now()

    # 1. Endpoint & Cluster finden / aktualisieren
    endpoint, _ = MatterEndpoint.objects.get_or_create(
        node=node,
        endpoint_id=endpoint_id,
        defaults={"name": f"Endpoint {endpoint_id}"},
    )

    cluster_name = MatterCluster.CLUSTER_DEFINITIONS.get(cluster_id, f"Cluster {hex(cluster_id)}")
    cluster, _ = MatterCluster.objects.get_or_create(
        endpoint=endpoint,
        cluster_id=cluster_id,
        defaults={"cluster_name": cluster_name, "attributes": {}},
    )

    cluster.attributes.update(attributes)
    cluster.save(update_fields=["attributes", "updated_at"])

    # 2. Node Payload aktualisieren
    node.attributes_payload.update(attributes)
    node.last_seen_at = now
    node.is_online = True

    # 3. Telemetrie aus Matter 1.3 Clustern extrahieren
    power_w = None
    energy_kwh = None

    # A) Power Measurement (0x0090)
    if "active_power_w" in attributes:
        power_w = float(attributes["active_power_w"])
    elif "active_power_mw" in attributes:
        power_w = float(attributes["active_power_mw"]) / 1000.0

    # B) Energy Measurement (0x0091)
    if "cumulative_energy_kwh" in attributes:
        energy_kwh = float(attributes["cumulative_energy_kwh"])
    elif "cumulative_energy_imported_mwh" in attributes:
        energy_kwh = float(attributes["cumulative_energy_imported_mwh"]) / 1_000_000.0

    # C) On/Off Cluster (0x0006)
    if "on_off" in attributes:
        is_on = bool(attributes["on_off"])
        node.attributes_payload["on_off"] = is_on
        if not is_on:
            power_w = 0.0

    if power_w is not None:
        node.attributes_payload["active_power_w"] = power_w
    if energy_kwh is not None:
        node.attributes_payload["energy_kwh"] = energy_kwh

    node.save(update_fields=["attributes_payload", "last_seen_at", "is_online", "updated_at"])

    # 4. Speichern in Sharegy Device Metriken
    if node.device:
        if power_w is not None:
            DeviceLatestMetric.objects.update_or_create(
                device=node.device,
                metric_key="power",
                defaults={
                    "value": power_w,
                    "unit": "W",
                    "timestamp": now,
                },
            )

        if power_w is not None or energy_kwh is not None:
            bucket_dt = now.replace(minute=0, second=0, microsecond=0)
            avg_w = float(power_w) if power_w is not None else 0.0
            energy_wh = float(energy_kwh) * 1000.0 if energy_kwh is not None else (avg_w * 1.0)

            DeviceMetric1h.objects.update_or_create(
                device=node.device,
                metric_key="power",
                bucket=bucket_dt,
                defaults={
                    "avg": avg_w,
                    "min": avg_w,
                    "max": avg_w,
                    "count": 1,
                    "energy_wh": energy_wh,
                },
            )

    return {
        "status": "success",
        "node_id": node.node_id,
        "endpoint_id": endpoint_id,
        "cluster_id": hex(cluster_id),
        "power_w": power_w,
        "energy_kwh": energy_kwh,
        "timestamp": now.isoformat(),
    }


def execute_matter_command(
    node: MatterNode,
    command: str,
    endpoint_id: int = 1,
    params: dict = None,
) -> dict:
    """
    Führt einen Steuerbefehl auf einem Matter-Knoten aus (z. B. On/Off, Power Limit).
    """
    params = params or {}
    now = timezone.now()

    # 1. On/Off Commands
    if command.lower() in ["toggle", "set_on_off", "turn_on", "turn_off"]:
        current_state = bool(node.attributes_payload.get("on_off", True))
        if command.lower() == "toggle":
            new_state = not current_state
        elif command.lower() in ["turn_on", "on"]:
            new_state = True
        elif command.lower() in ["turn_off", "off"]:
            new_state = False
        else:
            new_state = bool(params.get("on_off", not current_state))

        # Attributbericht simulieren/anwenden
        return process_matter_attribute_report(
            node=node,
            endpoint_id=endpoint_id,
            cluster_id=0x0006,
            attributes={"on_off": new_state},
        )

    # 2. EVSE / Power Limit Command
    if command.lower() in ["set_power_limit", "set_charging_current"]:
        current_limit = int(params.get("current_limit_a", 16))
        power_limit = float(params.get("power_limit_w", current_limit * 230.0 * 3.0))

        return process_matter_attribute_report(
            node=node,
            endpoint_id=endpoint_id,
            cluster_id=0x0099 if node.device_type == "evse" else 0x0098,
            attributes={
                "max_charge_current_a": current_limit,
                "power_adjustment_limit_w": power_limit,
                "active_power_w": power_limit if bool(node.attributes_payload.get("on_off", True)) else 0.0,
            },
        )

    return {
        "status": "error",
        "message": f"Unbekannter Matter Befehl: '{command}'",
    }


def simulate_matter_telemetry(home=None) -> list:
    """
    Simuliert realistische Matter 1.3 Telemetriewerte für gekoppelte Knoten.
    """
    nodes_qs = MatterNode.objects.filter(is_online=True)
    if home:
        nodes_qs = nodes_qs.filter(fabric__home=home)

    results = []
    for node in nodes_qs:
        is_on = bool(node.attributes_payload.get("on_off", True))
        if not is_on:
            power_w = 0.0
        elif node.device_type == "smart_plug":
            power_w = round(random.uniform(40.0, 650.0), 1)
        elif node.device_type == "evse":
            power_w = round(random.uniform(3700.0, 11000.0), 1)
        elif node.device_type == "heatpump":
            power_w = round(random.uniform(800.0, 3200.0), 1)
        elif node.device_type == "solar_inverter":
            power_w = round(random.uniform(500.0, 4500.0), 1)
        else:
            power_w = round(random.uniform(10.0, 200.0), 1)

        prev_energy = float(node.attributes_payload.get("energy_kwh", 10.0))
        new_energy = round(prev_energy + (power_w / 1000.0 * (10.0 / 3600.0)), 4)

        res = process_matter_attribute_report(
            node=node,
            endpoint_id=1,
            cluster_id=0x0090,
            attributes={
                "active_power_w": power_w,
                "active_power_mw": int(power_w * 1000),
                "cumulative_energy_kwh": new_energy,
                "rms_voltage_mv": random.randint(228000, 233000),
                "active_current_ma": int((power_w / 230.0) * 1000),
            },
        )
        results.append(res)

    return results

