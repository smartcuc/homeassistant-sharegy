##############################
# energy/api/views_ocpp.py
##############################

import secrets
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from devices.models import Home
from devices.models_ocpp import ChargingStation, ChargingSession, ChargingRfidTag
from energy.services.services_smart_charging import (
    calculate_smart_charging_current,
    dispatch_wallbox_charging_profile
)

logger = logging.getLogger("django")


class WallboxListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        home = Home.objects.filter(user=user).first()
        if not home:
            return Response({"wallboxes": []})

        stations = ChargingStation.objects.filter(home=home)
        host = request.get_host()
        protocol = "wss" if request.is_secure() or "https" in request.build_absolute_uri() else "ws"

        data = []
        for s in stations:
            active_session = None
            if s.active_transaction_id:
                session = ChargingSession.objects.filter(
                    station=s,
                    transaction_id=s.active_transaction_id,
                    status="active"
                ).first()
                if session:
                    active_session = {
                        "transaction_id": session.transaction_id,
                        "id_tag": session.id_tag,
                        "start_time": session.start_time.isoformat(),
                        "total_energy_kwh": session.total_energy_kwh,
                        "solar_coverage_pct": session.solar_coverage_pct,
                    }

            data.append({
                "id": str(s.id),
                "name": s.name,
                "charge_point_id": s.charge_point_id,
                "ocpp_url": f"{protocol}://{host}/ocpp/{s.charge_point_id}",
                "vendor": s.vendor or "OCPP Standard",
                "model": s.model or "EV Charger",
                "serial_number": s.serial_number,
                "firmware_version": s.firmware_version,
                "status": s.status,
                "is_online": s.is_online,
                "is_charging": s.is_charging,
                "last_heartbeat": s.last_heartbeat.isoformat() if s.last_heartbeat else None,
                "smart_charging_mode": s.smart_charging_mode,
                "price_threshold_ct": s.price_threshold_ct,
                "phases": s.phases,
                "max_current_a": s.max_current_a,
                "min_current_a": s.min_current_a,
                "target_current_a": s.target_current_a,
                "active_power_w": s.active_power_w,
                "power_kw": s.current_power_kw,
                "current_l1": s.current_l1,
                "current_l2": s.current_l2,
                "current_l3": s.current_l3,
                "voltage_v": s.voltage_v,
                "session_energy_kwh": s.session_energy_kwh,
                "total_energy_kwh": s.total_energy_kwh,
                "active_session": active_session,
            })

        return Response({"wallboxes": data})

    def post(self, request):
        user = request.user
        home = Home.objects.filter(user=user).first()
        if not home:
            return Response({"error": "Kein Smart Home Profil gefunden."}, status=status.HTTP_400_BAD_REQUEST)

        name = request.data.get("name", "Meine Wallbox").strip()
        vendor = request.data.get("vendor", "").strip()
        model = request.data.get("model", "").strip()
        phases = int(request.data.get("phases", 3))
        max_current_a = float(request.data.get("max_current_a", 16.0))
        smart_charging_mode = request.data.get("smart_charging_mode", "pv_surplus")

        # Eindeutige Kennung generieren
        charge_point_id = f"WB-{secrets.token_hex(4).upper()}"

        station = ChargingStation.objects.create(
            home=home,
            charge_point_id=charge_point_id,
            name=name,
            vendor=vendor,
            model=model,
            phases=phases,
            max_current_a=max_current_a,
            smart_charging_mode=smart_charging_mode,
            is_online=False
        )

        host = request.get_host()
        protocol = "wss" if request.is_secure() or "https" in request.build_absolute_uri() else "ws"
        ocpp_url = f"{protocol}://{host}/ocpp/{station.charge_point_id}"

        return Response({
            "success": True,
            "id": str(station.id),
            "charge_point_id": station.charge_point_id,
            "name": station.name,
            "ocpp_url": ocpp_url,
            "message": f"Wallbox erfolgreich registriert. Trage {ocpp_url} in deiner Wallbox-Konfiguration ein."
        }, status=status.HTTP_201_CREATED)


class WallboxDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        user = request.user
        home = Home.objects.filter(user=user).first()
        return get_object_or_404(ChargingStation, id=pk, home=home)

    def patch(self, request, pk):
        station = self.get_object(request, pk)
        data = request.data

        if "name" in data:
            station.name = str(data["name"]).strip()
        if "smart_charging_mode" in data:
            if data["smart_charging_mode"] in dict(ChargingStation.CHARGING_MODES):
                station.smart_charging_mode = data["smart_charging_mode"]
        if "price_threshold_ct" in data:
            station.price_threshold_ct = float(data["price_threshold_ct"])
        if "max_current_a" in data:
            station.max_current_a = float(data["max_current_a"])
        if "min_current_a" in data:
            station.min_current_a = float(data["min_current_a"])
        if "phases" in data:
            station.phases = int(data["phases"])

        station.save()

        # Sofort Ladestrom neu berechnen und anpassen
        from energy.ems.services import build_device_signals
        from market.models import SpotPrice

        user = station.home.user if station.home else None
        signals = build_device_signals(user) if user else {}
        pv_power_w = float(signals.get("pv", {}).get("production", 0.0) or 0.0)
        load_power_w = float(signals.get("load", {}).get("consumption", 0.0) or 0.0)
        battery_charge_w = float(signals.get("battery", {}).get("charge", 0.0) or 0.0)

        latest_spot = SpotPrice.objects.filter(timestamp__lte=timezone.now()).order_by("-timestamp").first()
        spot_price_ct = float(latest_spot.price_ct_kwh) if latest_spot else 20.0

        target_a = calculate_smart_charging_current(
            station=station,
            pv_power_w=pv_power_w,
            load_power_w=load_power_w,
            battery_charge_w=battery_charge_w,
            spot_price_ct=spot_price_ct
        )
        dispatch_res = dispatch_wallbox_charging_profile(station, target_a)

        return Response({
            "success": True,
            "id": str(station.id),
            "smart_charging_mode": station.smart_charging_mode,
            "target_current_a": station.target_current_a,
            "dispatch": dispatch_res
        })

    def delete(self, request, pk):
        station = self.get_object(request, pk)
        station.delete()
        return Response({"success": True, "message": "Wallbox gelöscht."})


class WallboxRemoteActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, action):
        user = request.user
        home = Home.objects.filter(user=user).first()
        station = get_object_or_404(ChargingStation, id=pk, home=home)
        channel_layer = get_channel_layer()

        if action == "remote-start":
            id_tag = request.data.get("id_tag", "APP_USER")
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {"type": "ocpp_remote_start", "connector_id": 1, "id_tag": id_tag}
                )
            return Response({"success": True, "message": f"Start-Befehl an {station.name} gesendet."})

        elif action == "remote-stop":
            tx_id = station.active_transaction_id
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {"type": "ocpp_remote_stop", "transaction_id": tx_id}
                )
            return Response({"success": True, "message": f"Stopp-Befehl an {station.name} gesendet."})

        elif action == "unlock":
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {"type": "ocpp_unlock_connector", "connector_id": 1}
                )
            return Response({"success": True, "message": f"Entriegelungs-Befehl an {station.name} gesendet."})

        elif action == "dispatch-now":
            from energy.ems.services import build_device_signals
            from market.models import SpotPrice

            user = home.user if home else None
            signals = build_device_signals(user) if user else {}
            pv_power_w = float(signals.get("pv", {}).get("production", 0.0) or 0.0)
            load_power_w = float(signals.get("load", {}).get("consumption", 0.0) or 0.0)
            battery_charge_w = float(signals.get("battery", {}).get("charge", 0.0) or 0.0)

            latest_spot = SpotPrice.objects.filter(timestamp__lte=timezone.now()).order_by("-timestamp").first()
            spot_price_ct = float(latest_spot.price_ct_kwh) if latest_spot else 20.0

            target_a = calculate_smart_charging_current(
                station=station,
                pv_power_w=pv_power_w,
                load_power_w=load_power_w,
                battery_charge_w=battery_charge_w,
                spot_price_ct=spot_price_ct
            )
            dispatch_res = dispatch_wallbox_charging_profile(station, target_a)
            return Response({
                "success": True,
                "target_current_a": target_a,
                "dispatch": dispatch_res
            })

        return Response({"error": f"Unbekannte Aktion '{action}'."}, status=status.HTTP_400_BAD_REQUEST)


class WallboxSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        home = Home.objects.filter(user=user).first()
        station = get_object_or_404(ChargingStation, id=pk, home=home)

        sessions = ChargingSession.objects.filter(station=station).order_by("-start_time")[:30]
        data = [
            {
                "id": str(sess.id),
                "transaction_id": sess.transaction_id,
                "id_tag": sess.id_tag,
                "user_email": sess.user.email if sess.user else "Gast / RFID",
                "start_time": sess.start_time.isoformat(),
                "stop_time": sess.stop_time.isoformat() if sess.stop_time else None,
                "total_energy_kwh": sess.total_energy_kwh,
                "solar_energy_kwh": sess.solar_energy_kwh,
                "grid_energy_kwh": sess.grid_energy_kwh,
                "solar_coverage_pct": sess.solar_coverage_pct,
                "cost_eur": float(sess.cost_eur),
                "stop_reason": sess.stop_reason,
                "status": sess.status,
            }
            for sess in sessions
        ]

        return Response({"sessions": data})
