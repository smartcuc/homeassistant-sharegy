"""
devices/api/views_self_test.py

REST-API Endpoints für den 1-Klick Hardware-Selbsttest.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from devices.models import Device
from devices.services_self_test import run_device_self_test


@api_view(["POST", "GET"])
@permission_classes([AllowAny])
def device_self_test_view(request, device_id):
    """
    Führt den 1-Klick Hardware-Selbsttest für ein spezifisches Gerät aus.
    POST/GET /api/devices/<device_id>/self-test/
    """
    credentials = request.data.get("credentials") if request.method == "POST" else None
    try:
        device = Device.objects.get(id=device_id)
    except Device.DoesNotExist:
        # Fallback simulation if device doesn't exist yet
        res = run_device_self_test(device=None, device_id=device_id, credentials=credentials)
        return Response(res, status=status.HTTP_200_OK)

    res = run_device_self_test(device=device, credentials=credentials)
    return Response(res, status=status.HTTP_200_OK)


@api_view(["POST", "GET"])
@permission_classes([AllowAny])
def device_self_test_simulate_view(request):
    """
    Führt einen 1-Klick Hardware-Selbsttest für Onboarding / Setup-Assistenten aus.
    POST/GET /api/devices/self-test/simulate/
    """
    profile_id = request.data.get("profile_id") or request.GET.get("profile_id") or "sungrow_isolarcloud"
    credentials = request.data.get("credentials") if request.method == "POST" else None
    res = run_device_self_test(device=None, mock_profile_id=profile_id, credentials=credentials)
    return Response(res, status=status.HTTP_200_OK)
