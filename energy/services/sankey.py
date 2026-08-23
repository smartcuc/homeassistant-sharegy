###########################
# energy/services/sankey.py
###########################

from collections import defaultdict
from devices.models import Device
from devices.services.metrics import get_latest_values


def build_live_sankey(
    user,
    flow,
    signals,
    show_floors=True,
    show_rooms=True,
):
    devices = (
        Device.objects
        .filter(
            home__user=user,
            configured=True,
            active=True,
            pending_delete=False,
        )
        .select_related(
            "config",
            "config__role",
            "config__floor",
            "config__room",
        )
    )

    devices = list(devices)

    values = get_latest_values([device.id for device in devices])

    total_consumption = (
        signals["load"]["consumption"]
        or 0
    )

    nodes = []
    links = []

    known_nodes = set()

    def add_node(node_id, label, node_type):

        if node_id in known_nodes:
            return

        nodes.append({
            "id": node_id,
            "label": label,
            "type": node_type,
        })

        known_nodes.add(node_id)

    #
    # PRODUCER
    #

    add_node(
        "pv",
        "PV",
        "producer",
    )

    add_node(
        "battery",
        "Batterie",
        "producer",
    )

    add_node(
        "grid",
        "Netz",
        "producer",
    )

    #
    # SUM
    #

    add_node(
        "sum",
        "Haus",
        "sum",
    )

    #
    # CONSUMER
    #

    consumers = []

    for device in devices:

        config = getattr(device, "config", None)

        if not config:
            continue

        if (
            not config.metric_definition
            or config.metric_definition.key != "power"
        ):
            continue
        
        role = config.role

        if not role:
            continue

        if role.key != "consumer":
            continue

        if (
            config.generator_type
            and config.generator_type.key == "grid"
        ):
            continue

        node_id = f"device_{device.id}"

        label = (
            config.display_name()
            if config
            else device.identifier
        )

        power = values.get(device.id, 0)

        if power <= 0:
            continue

        add_node(
            node_id,
            label,
            "consumer",
        )

        consumers.append({
            "node_id": node_id,
            "floor": config.floor,
            "room": config.room,
            "power": power,
        })

    #
    # SUM -> FLOOR -> ROOM -> DEVICE
    #
    tracked_consumption = 0

    for consumer in consumers:

        current_target = "sum"

        floor = consumer["floor"]

        if show_floors and floor:

            floor_id = f"floor_{floor.id}"

            add_node(
                floor_id,
                floor.name,
                "floor",
            )

            links.append({
                "source": "sum",
                "target": floor_id,
                "value": consumer["power"],
            })

            current_target = floor_id

        room = consumer["room"]

        if show_rooms and room:

            room_id = f"room_{room.id}"

            add_node(
                room_id,
                room.name,
                "room",
            )

            links.append({
                "source": current_target,
                "target": room_id,
                "value": consumer["power"],
            })

            current_target = room_id

        links.append({
            "source": current_target,
            "target": consumer["node_id"],
            "value": consumer["power"],
        })

        tracked_consumption += consumer["power"]

    if flow.get("pv_to_load", 0) > 0:
        links.append({
            "source": "pv",
            "target": "sum",
            "value": flow["pv_to_load"],
        })

    if flow.get("pv_to_battery", 0) > 0:
        add_node("battery_charge", "Batterieladung", "battery_charge")
        links.append({
            "source": "pv",
            "target": "battery_charge",
            "value": flow["pv_to_battery"],
        })

    if flow.get("pv_to_grid", 0) > 0:
        add_node("grid_export", "Netzeinspeisung", "grid_export")
        links.append({
            "source": "pv",
            "target": "grid_export",
            "value": flow["pv_to_grid"],
        })

    if flow.get("battery_to_load", 0) > 0:
        links.append({
            "source": "battery",
            "target": "sum",
            "value": flow["battery_to_load"],
        })

    if flow.get("grid_to_battery", 0) > 0:
        add_node("battery_charge", "Batterieladung", "battery_charge")
        links.append({
            "source": "grid",
            "target": "battery_charge",
            "value": flow["grid_to_battery"],
        })

    if flow.get("grid_to_load", 0) > 0:
        links.append({
            "source": "grid",
            "target": "sum",
            "value": flow["grid_to_load"],
        })

    incoming_energy = (
        flow.get("pv_to_load", 0)
        + flow.get("battery_to_load", 0)
        + flow.get("grid_to_load", 0)
    )

    untracked = max(
        incoming_energy - tracked_consumption,
        0,
    )  

    if untracked > 0:
        add_node(
            "untracked",
            "Nicht erfasst",
            "untracked",
        )
        links.append({
            "source": "sum",
            "target": "untracked",
            "value": round(untracked, 2),
        })

    # Kanten mit identischem (source, target) zusammenfassen
    aggregated_links = defaultdict(float)
    for link in links:
        key = (link["source"], link["target"])
        aggregated_links[key] += float(link["value"] or 0)

    clean_links = [
        {"source": src, "target": tgt, "value": round(val, 2)}
        for (src, tgt), val in aggregated_links.items()
        if val > 0
    ]

    return {
        "nodes": nodes,
        "links": clean_links,
    }
