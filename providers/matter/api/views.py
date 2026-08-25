from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from devices.models import Home
from providers.matter.models import MatterFabric, MatterNode, MatterCluster, MatterEndpoint
from providers.matter.services.commissioning import commission_matter_node, parse_matter_pairing_code
from providers.matter.services.cluster_engine import (
    process_matter_attribute_report,
    execute_matter_command,
    simulate_matter_telemetry,
)


def _get_user_home(request):
    """Ermittelt das primäre Home des angemeldeten Benutzers."""
    return Home.objects.filter(user=request.user).first()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def matter_status(request):
    """
    Liefert den Status des Sharegy Matter Hubs, die Fabric-ID und alle gekoppelten Knoten.
    """
    home = _get_user_home(request)
    if not home:
        return Response({"error": "Kein Haushalt gefunden."}, status=status.HTTP_404_NOT_FOUND)

    fabric = MatterFabric.get_or_create_for_home(home)
    nodes = MatterNode.objects.filter(fabric=fabric).prefetch_related("endpoints__clusters")

    node_list = []
    for n in nodes:
        clusters_info = []
        for ep in n.endpoints.all():
            for cl in ep.clusters.all():
                clusters_info.append({
                    "endpoint_id": ep.endpoint_id,
                    "cluster_id": hex(cl.cluster_id),
                    "cluster_name": cl.cluster_name,
                    "attributes": cl.attributes,
                })

        node_list.append({
            "id": n.id,
            "node_id": n.node_id,
            "name": n.name,
            "device_type": n.device_type,
            "device_type_id": hex(n.device_type_id),
            "vendor_id": hex(n.vendor_id),
            "product_id": hex(n.product_id),
            "ip_address": n.ip_address,
            "is_online": n.is_online,
            "firmware_version": n.firmware_version,
            "attributes": n.attributes_payload,
            "clusters": clusters_info,
            "last_seen_at": n.last_seen_at.isoformat() if n.last_seen_at else None,
            "device_id": n.device_id,
        })

    return Response({
        "status": "online",
        "fabric_id": hex(fabric.fabric_id),
        "controller_node_id": fabric.controller_node_id,
        "nodes_count": len(node_list),
        "nodes": node_list,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def matter_commission(request):
    """
    Koppelt ein neues Matter 1.3 Endgerät an die Haushalts-Fabric.
    Body:
    {
        "name": "Kaffeemaschine Smart Plug",
        "pairing_code": "MT:Y.K9042C00KA0648G00" oder "34970112332",
        "device_type": "smart_plug",
        "role": "consumer",
        "ip_address": "192.168.1.145" (optional)
    }
    """
    home = _get_user_home(request)
    if not home:
        return Response({"error": "Kein Haushalt gefunden."}, status=status.HTTP_404_NOT_FOUND)

    name = request.data.get("name", "Neues Matter-Gerät").strip()
    pairing_code = request.data.get("pairing_code", "").strip()
    device_type = request.data.get("device_type", "smart_plug")
    role = request.data.get("role")
    ip_address = request.data.get("ip_address")

    if not pairing_code:
        return Response({"error": "Pairing-Code (QR-Code oder 11/21-stelliger Code) erforderlich."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        node = commission_matter_node(
            home=home,
            name=name,
            pairing_code=pairing_code,
            device_type=device_type,
            ip_address=ip_address,
            custom_role=role,
        )

        return Response({
            "status": "commissioned",
            "node_id": node.node_id,
            "name": node.name,
            "device_type": node.device_type,
            "ip_address": node.ip_address,
            "discriminator": node.discriminator,
            "device_id": node.device_id,
        }, status=status.HTTP_201_CREATED)
    except Exception as err:
        return Response({"error": f"Kopplung fehlgeschlagen: {str(err)}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def matter_node_command(request, node_id):
    """
    Sendet einen Steuerbefehl an einen Matter-Knoten (z. B. Toggle, SetOnOff, SetPowerLimit).
    """
    home = _get_user_home(request)
    if not home:
        return Response({"error": "Kein Haushalt gefunden."}, status=status.HTTP_404_NOT_FOUND)

    node = get_object_or_404(MatterNode, fabric__home=home, node_id=node_id)
    command = request.data.get("command", "toggle")
    endpoint_id = int(request.data.get("endpoint_id", 1))
    params = request.data.get("params", {})

    result = execute_matter_command(node, command, endpoint_id=endpoint_id, params=params)
    return Response(result)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def matter_node_delete(request, node_id):
    """
    Entkoppelt ein Matter-Gerät und löscht den Knoten.
    """
    home = _get_user_home(request)
    if not home:
        return Response({"error": "Kein Haushalt gefunden."}, status=status.HTTP_404_NOT_FOUND)

    node = get_object_or_404(MatterNode, fabric__home=home, node_id=node_id)
    dev_name = node.name
    if node.device:
        node.device.delete()
    node.delete()

    return Response({
        "status": "deleted",
        "message": f"Matter-Knoten '{dev_name}' erfolgreich entfernt.",
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def matter_telemetry_report(request):
    """
    Ingestion-Webhook für externe Matter Border Router oder Controller.
    Body:
    {
        "node_id": 100,
        "endpoint_id": 1,
        "cluster_id": 144, // 0x0090
        "attributes": {
            "active_power_w": 2840.5,
            "cumulative_energy_kwh": 45.2
        }
    }
    """
    home = _get_user_home(request)
    if not home:
        return Response({"error": "Kein Haushalt gefunden."}, status=status.HTTP_404_NOT_FOUND)

    node_id = request.data.get("node_id")
    if not node_id:
        return Response({"error": "node_id erforderlich."}, status=status.HTTP_400_BAD_REQUEST)

    node = get_object_or_404(MatterNode, fabric__home=home, node_id=node_id)
    endpoint_id = int(request.data.get("endpoint_id", 1))
    cluster_id_raw = request.data.get("cluster_id", 0x0090)
    cluster_id = int(cluster_id_raw, 16) if isinstance(cluster_id_raw, str) and cluster_id_raw.startswith("0x") else int(cluster_id_raw)
    attributes = request.data.get("attributes", {})

    result = process_matter_attribute_report(
        node=node,
        endpoint_id=endpoint_id,
        cluster_id=cluster_id,
        attributes=attributes,
    )
    return Response(result)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def matter_simulate(request):
    """
    Simuliert Live-Telemetriedaten für alle gekoppelten Matter-Knoten des Haushalts.
    """
    home = _get_user_home(request)
    if not home:
        return Response({"error": "Kein Haushalt gefunden."}, status=status.HTTP_404_NOT_FOUND)

    results = simulate_matter_telemetry(home=home)
    return Response({
        "status": "simulated",
        "updated_nodes": len(results),
        "results": results,
    })

