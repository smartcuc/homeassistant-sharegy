##################
# devices/views.py
##################

import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Device, DeviceMetric
from .models import Home
from .serializers import DeviceSerializer, DeviceCreateSerializer, DeviceStatusSerializer


# ✅ Geräte Liste + Create (EIN Endpoint!)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def device_list(request):

    # ✅ Nur für GET wichtig – NICHT für POST blocken!
    if request.method == "GET":
        home = request.user.homes.first()

        if not home:
            return Response([], status=200)  # ✅ leer statt Fehler

        devices = Device.objects.filter(
            home__user=request.user,
            active=True,
            pending_delete=False,
        )

        return Response(
            DeviceSerializer(devices, many=True).data
        )

    # 🔥 CREATE (NICHT blockieren!)
    if request.method == "POST":

        serializer = DeviceCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        device = serializer.save()

        return Response({
            "id": device.id,
            "identifier": device.identifier,
            "mqtt_token": device.home.mqtt_token,
            "mqtt_username": device.home.mqtt_username,
            "mqtt_password": device.home.mqtt_password,
            "mqtt_host": os.getenv("MQTT_HOST"),
            "mqtt_port": int(os.getenv("MQTT_PORT")),
        }, status=201)

    # 🔹 LIST
    devices = Device.objects.filter(
            home__user=request.user,
            active=True,
            pending_delete=False,
        )

    return Response(
        DeviceSerializer(devices, many=True).data
    )


# ✅ Device Metrics
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_metrics(request, device_id):

    try:
        device = Device.objects.get(id=device_id, home__in=request.user.homes.all())
    except Device.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    metrics = DeviceMetric.objects.filter(device=device).order_by("-timestamp")[:100]

    data = [
        {
            "timestamp": m.timestamp,
            "metric": m.metric_key,
            "value": m.value,
            "unit": m.unit,
        }
        for m in metrics
    ]

    return Response(data)


# ✅ REBUILD MQQT PASSWD
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mqtt_status(request):
    homes = Home.objects.all()

    return Response([
        {
            "user": h.user.id,
            "username": h.mqtt_username,
            "provisioned": h.mqtt_provisioned
        }
        for h in homes
    
    ])


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_status_list(request):

    devices = Device.objects.filter(
        home__in=request.user.homes.all()
    ).select_related("home")

    serializer = DeviceStatusSerializer(devices, many=True)

    return Response(serializer.data)


# ✅ SEND MQTT CONFIG BY MAIL
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_device_config(request):

    device = request.data.get("device")
    email_override = request.data.get("email")

    if not device:
        return Response({"error": "No device data"}, status=400)

    try:
        topic = f"h/{device['mqtt_token']}/{device['identifier']}"

        to_email = email_override or request.user.email

        context = {
            "host": device["mqtt_host"],
            "port": device["mqtt_port"],
            "username": device["mqtt_username"],
            "password": device["mqtt_password"],
            "topic": topic,
        }

        html_content = render_to_string("emails/device_config.html", context)

        text_content = f"""
MQTT Setup:

Host: {context["host"]}
Port: {context["port"]}
User: {context["username"]}
Password: {context["password"]}

Topic:
{context["topic"]}
"""

        email = EmailMultiAlternatives(
            subject=f"Sharegy Setup: {device['identifier']}",
            body=text_content,
            to=[to_email],
        )

        email.attach_alternative(html_content, "text/html")
        email.send()

        return Response({
            "status": "sent",
            "email": to_email
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    