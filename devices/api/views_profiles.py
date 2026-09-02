"""
devices/api/views_profiles.py

REST-API Endpoints für deklarative Hersteller-Cloud-Profile (Sungrow iSolarCloud, SolarEdge, Fronius).
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from devices.models import Device, DeviceConfig, CloudDeviceIntegration, Home
from devices.services_profile_runner import (
    list_available_profiles,
    load_profile,
    test_cloud_credentials,
    execute_cloud_poll,
)

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_cloud_profiles_view(request):
    """
    Liefert alle verfügbaren Hersteller-Profile mit Metadaten und Formularfeldern.
    """
    profiles = list_available_profiles()
    return Response({
        "status": "success",
        "profiles": profiles,
        "count": len(profiles),
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def test_cloud_connection_view(request):
    """
    Testet die eingegebenen Zugangsdaten für ein Profil live oder im Simulator.
    Payload: { profile_id: "sungrow_isolarcloud", credentials: { appkey, user_account, ... } }
    """
    profile_id = request.data.get("profile_id")
    credentials = request.data.get("credentials") or {}

    if not profile_id:
        return Response(
            {"status": "error", "message": "Parameter 'profile_id' ist erforderlich."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        result = test_cloud_credentials(profile_id, credentials)
        return Response(result)
    except Exception as e:
        logger.warning("Cloud credentials test failed: %s", e)
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def integrate_cloud_device_view(request):
    """
    Erstellt ein neues Cloud-Gerät oder verknüpft ein bestehendes Gerät mit einem Cloud-Profil.
    Payload: {
        home_id: ...,
        name: "Sungrow SH10RT",
        profile_id: "sungrow_isolarcloud",
        credentials: { appkey, user_account, user_password, ps_id },
        polling_interval: 60
    }
    """
    user = request.user
    home_id = request.data.get("home_id")
    name = request.data.get("name") or "Cloud-Wechselrichter"
    profile_id = request.data.get("profile_id")
    credentials = request.data.get("credentials") or {}
    interval = int(request.data.get("polling_interval", 60))

    if not profile_id:
        return Response({"status": "error", "message": "profile_id ist erforderlich."}, status=400)

    # Home finden oder erstes Home des Users nutzen
    home = None
    if home_id:
        home = Home.objects.filter(id=home_id, user=user).first()
    if not home:
        home = Home.objects.filter(user=user).first()

    if not home:
        return Response({"status": "error", "message": "Kein gültiges Gebäude (Home) gefunden."}, status=400)

    try:
        profile = load_profile(profile_id)
    except Exception as e:
        return Response({"status": "error", "message": f"Ungültiges Profil: {e}"}, status=400)

    identifier = f"cloud-{profile_id}-{home.id}"[:64]

    # Gerät anlegen oder aktualisieren
    device, created = Device.objects.get_or_create(
        home=home,
        identifier=identifier,
        defaults={"configured": True, "active": True},
    )

    # DeviceConfig
    config, _ = DeviceConfig.objects.get_or_create(
        device=device,
        defaults={"home": home, "name": name},
    )
    if not config.name:
        config.name = name
        config.save(update_fields=["name"])

    # CloudDeviceIntegration
    integration, int_created = CloudDeviceIntegration.objects.get_or_create(
        device=device,
        defaults={
            "profile_id": profile_id,
            "credentials": credentials,
            "polling_interval_seconds": interval,
            "is_active": True,
            "last_status": CloudDeviceIntegration.STATUS_PENDING,
        },
    )
    if not int_created:
        integration.profile_id = profile_id
        integration.credentials = credentials
        integration.polling_interval_seconds = interval
        integration.is_active = True
        integration.save()

    # Direkt einen ersten Sync durchführen
    poll_res = execute_cloud_poll(integration)

    return Response({
        "status": "success",
        "message": f"Gerät '{name}' erfolgreich mit {profile.get('name')} verknüpft!",
        "device_id": device.id,
        "integration_id": str(integration.id),
        "poll_result": poll_res,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def poll_cloud_device_now_view(request, device_id):
    """
    Triggert eine manuelle Sofort-Abfrage der Cloud-Daten für ein Gerät.
    """
    integration = CloudDeviceIntegration.objects.filter(
        device__id=device_id,
        device__home__user=request.user,
    ).first()

    if not integration:
        return Response(
            {"status": "error", "message": "Keine Cloud-Integration für dieses Gerät gefunden."},
            status=status.HTTP_404_NOT_FOUND,
        )

    res = execute_cloud_poll(integration)
    return Response(res)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cloud_integration_status_view(request, device_id):
    """
    Liefert den aktuellen Kopplungs- und Polling-Status einer Cloud-Integration.
    """
    integration = CloudDeviceIntegration.objects.filter(
        device__id=device_id,
        device__home__user=request.user,
    ).first()

    if not integration:
        return Response(
            {"status": "error", "message": "Keine Cloud-Integration für dieses Gerät gefunden."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response({
        "status": "success",
        "integration_id": str(integration.id),
        "profile_id": integration.profile_id,
        "is_active": integration.is_active,
        "last_status": integration.last_status,
        "last_polled_at": integration.last_polled_at.isoformat() if integration.last_polled_at else None,
        "last_error_message": integration.last_error_message,
        "polling_interval_seconds": integration.polling_interval_seconds,
    })
