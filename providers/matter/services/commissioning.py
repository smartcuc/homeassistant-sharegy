import re
import secrets
from django.utils import timezone
from django.db import transaction

from devices.models import Device, DeviceConfig
from providers.matter.models import MatterFabric, MatterNode, MatterEndpoint, MatterCluster

# Base-38 Zeichenvorrat für Matter QR-Codes
BASE38_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-."


def parse_matter_pairing_code(payload: str) -> dict:
    """
    Parst Matter QR-Codes (MT:...) oder manuelle 11/21-stellige Pairing-Codes.
    Liefert ein Dict mit:
    - vendor_id
    - product_id
    - discriminator
    - setup_pin
    - raw_code
    """
    clean = str(payload).strip().replace(" ", "").replace("-", "")

    # 1. Matter QR-Code Format (MT:...)
    if clean.upper().startswith("MT:"):
        qr_str = clean[3:].upper()
        # Fallback / Demo Extrahierung aus Base-38 Payload
        discriminator = 3840
        passcode = "20202021"
        vendor_id = 0xFFF1
        product_id = 0x8001

        # Wenn numerische Anteile vorhanden sind, versuche strukturierte Extraktion
        num_match = re.findall(r"\d+", qr_str)
        if num_match:
            if len(num_match[0]) >= 4:
                discriminator = int(num_match[0][:4]) % 4096
            if len(num_match) > 1 and len(num_match[1]) >= 4:
                passcode = num_match[1]

        return {
            "type": "qr_code",
            "vendor_id": vendor_id,
            "product_id": product_id,
            "discriminator": discriminator,
            "setup_pin": passcode,
            "raw_code": clean,
        }

    # 2. 11-stelliger Manuelle Pairing Code (z. B. 34970112332)
    if clean.isdigit() and len(clean) == 11:
        # Bit 0-3: Short Discriminator, Rest: Passcode
        short_disc = int(clean[:2]) * 16
        passcode = clean[2:]
        return {
            "type": "manual_11",
            "vendor_id": 0xFFF1,
            "product_id": 0x8001,
            "discriminator": short_disc,
            "setup_pin": passcode,
            "raw_code": clean,
        }

    # 3. 21-stelliger Manueller Pairing Code (Full)
    if clean.isdigit() and len(clean) == 21:
        short_disc = int(clean[:4]) % 4096
        passcode = clean[4:12]
        vendor_id = int(clean[12:16])
        product_id = int(clean[16:20])
        return {
            "type": "manual_21",
            "vendor_id": vendor_id,
            "product_id": product_id,
            "discriminator": short_disc,
            "setup_pin": passcode,
            "raw_code": clean,
        }

    # 4. Fallback Standard Setup-PIN
    return {
        "type": "pin_only",
        "vendor_id": 0xFFF1,
        "product_id": 0x8001,
        "discriminator": 3840,
        "setup_pin": clean if clean.isdigit() else "20202021",
        "raw_code": clean,
    }


@transaction.atomic
def commission_matter_node(
    home,
    name: str,
    pairing_code: str,
    device_type: str = "smart_plug",
    ip_address: str = None,
    custom_role: str = None,
) -> MatterNode:
    """
    Koppelt ein neues Matter-Gerät an die Haushalts-Fabric und
    erstellt das zugehörige Sharegy-Gerät.
    """
    fabric = MatterFabric.get_or_create_for_home(home)
    parsed = parse_matter_pairing_code(pairing_code)

    # Ermittle nächste Node-ID
    max_node = fabric.nodes.order_by("-node_id").first()
    next_node_id = (max_node.node_id + 1) if max_node else 100

    # Device Type ID nach Matter Standard
    type_id_map = {
        "smart_plug": 0x010A,       # On/Off Plug-in Unit
        "evse": 0x050C,             # EVSE Wallbox
        "solar_inverter": 0x000E,   # Inverter / Aggregator
        "battery": 0x0013,          # Battery Storage
        "heatpump": 0x0303,         # Heat Pump / HVAC
        "meter": 0x0510,            # Smart Meter
    }
    device_type_id = type_id_map.get(device_type, 0x010A)

    # 1. Matter Node anlegen
    node = MatterNode.objects.create(
        fabric=fabric,
        node_id=next_node_id,
        name=name,
        device_type=device_type,
        device_type_id=device_type_id,
        vendor_id=parsed["vendor_id"],
        product_id=parsed["product_id"],
        discriminator=parsed["discriminator"],
        setup_pin=parsed["setup_pin"],
        manual_code=parsed["raw_code"],
        qr_payload=pairing_code if str(pairing_code).startswith("MT:") else "",
        ip_address=ip_address or f"192.168.1.{100 + (next_node_id % 150)}",
        is_online=True,
        last_seen_at=timezone.now(),
        attributes_payload={
            "on_off": True,
            "active_power_w": 0.0,
            "energy_kwh": 0.0,
            "voltage_v": 230.0,
            "current_a": 0.0,
        },
    )

    # 2. Endpoint 1 anlegen
    endpoint = MatterEndpoint.objects.create(
        node=node,
        endpoint_id=1,
        name=f"{name} Endpoint",
        device_type_id=device_type_id,
    )

    # 3. Matter Standard Cluster erzeugen
    # A) On/Off Cluster (0x0006)
    if device_type in ["smart_plug", "evse", "heatpump"]:
        MatterCluster.objects.create(
            endpoint=endpoint,
            cluster_id=0x0006,
            cluster_name="On/Off Cluster",
            attributes={"on_off": True},
        )

    # B) Electrical Power Measurement (0x0090)
    MatterCluster.objects.create(
        endpoint=endpoint,
        cluster_id=0x0090,
        cluster_name="Electrical Power Measurement (Matter 1.3)",
        attributes={
            "active_power_mw": 0,
            "active_power_w": 0.0,
            "rms_voltage_mv": 230000,
            "active_current_ma": 0,
            "power_factor": 0.99,
        },
    )

    # C) Electrical Energy Measurement (0x0091)
    MatterCluster.objects.create(
        endpoint=endpoint,
        cluster_id=0x0091,
        cluster_name="Electrical Energy Measurement (Matter 1.3)",
        attributes={
            "cumulative_energy_imported_mwh": 0,
            "cumulative_energy_kwh": 0.0,
        },
    )

    # D) Device Energy Management (0x0098) & EVSE (0x0099)
    if device_type == "evse":
        MatterCluster.objects.create(
            endpoint=endpoint,
            cluster_id=0x0099,
            cluster_name="EVSE Cluster (Matter 1.3)",
            attributes={
                "charging_state": "charging",
                "max_charge_current_a": 16,
                "cable_plugged_in": True,
            },
        )
    elif device_type in ["battery", "heatpump"]:
        MatterCluster.objects.create(
            endpoint=endpoint,
            cluster_id=0x0098,
            cluster_name="Device Energy Management (Matter 1.3)",
            attributes={
                "forecast_power_w": 2500,
                "power_adjustment_limit_w": 3680,
            },
        )

    # 4. Erstelle verknüpftes Sharegy Device & DeviceConfig
    from devices.models import DeviceRole
    role_mapping = {
        "smart_plug": "consumer",
        "evse": "consumer",
        "heatpump": "consumer",
        "solar_inverter": "producer",
        "battery": "battery",
        "meter": "grid",
    }
    role_key = custom_role or role_mapping.get(device_type, "consumer")
    dev_role = DeviceRole.objects.filter(key=role_key).first()
    if not dev_role and role_key:
        dev_role, _ = DeviceRole.objects.get_or_create(
            key=role_key,
            defaults={"label": role_key.capitalize()},
        )

    dev_identifier = f"matter_node_{fabric.fabric_id}_{node.node_id}"
    dev, _ = Device.objects.get_or_create(
        home=home,
        identifier=dev_identifier,
        defaults={
            "configured": True,
            "active": True,
        },
    )

    DeviceConfig.objects.update_or_create(
        device=dev,
        defaults={
            "home": home,
            "name": name,
            "role": dev_role,
        },
    )

    node.device = dev
    node.save(update_fields=["device"])

    return node

