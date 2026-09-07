"""
energy/api/views_fuel_radar.py

REST API Endpunkte für das Mobilitäts- & Spritpreis-Radar (Tankerkönig / MTS-K).
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from devices.models import Home
from energy.services.tankerkoenig import fetch_fuel_radar_data

logger = logging.getLogger(__name__)


def _get_home_for_request(request):
    """Ermittelt das Home des authentifizierten Benutzers."""
    user = request.user
    if not user or not user.is_authenticated:
        return None
    home_id = request.query_params.get("home_id")
    if home_id:
        return Home.objects.filter(id=home_id, user=user).first()
    return Home.objects.filter(user=user).first() or Home.objects.first()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fuel_radar_view(request):
    """
    GET /api/energy/fuel-radar/
    Liefert die günstigsten Tankstellen im Umkreis, 100km-EV-Kostenvergleich und Tankempfehlungen.
    Parameter:
    - radius_km: float (Standard 5.0, min 1.0, max 25.0)
    - fuel_type: str ("all", "e10", "e5", "diesel")
    - lat: float (optional)
    - lng: float (optional)
    """
    home = _get_home_for_request(request)
    if not home:
        return Response({"error": "Kein Home gefunden."}, status=404)

    radius_km = float(request.query_params.get("radius_km", 5.0))
    fuel_type = request.query_params.get("fuel_type", "all")
    custom_lat = request.query_params.get("lat")
    custom_lng = request.query_params.get("lng")

    data = fetch_fuel_radar_data(
        home,
        radius_km=radius_km,
        fuel_type=fuel_type,
        custom_lat=custom_lat,
        custom_lng=custom_lng,
    )
    return Response(data)
