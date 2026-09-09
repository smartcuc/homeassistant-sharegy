##############################
# energy/api/views_ocpp.py
##############################

import secrets
import datetime
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
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
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            home = Home.objects.first()
            if not home:
                return Response({"wallboxes": []})
        else:
            home = Home.objects.filter(user=user).first() or Home.objects.first()
            if not home:
                return Response({"wallboxes": []})

        try:
            stations = ChargingStation.objects.filter(home=home)
            try:
                host = request.get_host()
            except Exception:
                host = "sharegy.de"
            
            is_sec = False
            try:
                is_sec = request.is_secure() or "https" in request.build_absolute_uri()
            except Exception:
                pass
            protocol = "wss" if is_sec else "ws"

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
                            "start_time": session.start_time.isoformat() if session.start_time else None,
                            "total_energy_kwh": session.total_energy_kwh,
                            "solar_coverage_pct": session.solar_coverage_pct,
                        }

                connector_status = "Gesteckt" if s.status in ["Preparing", "Charging", "SuspendedEV", "SuspendedEVSE"] else ("Reserviert" if s.status == "Reserved" else ("Störung" if s.status == "Faulted" else "Bereit"))
                power_kw_val = getattr(s, "current_power_kw", round((s.active_power_w or 0.0) / 1000.0, 2))

                data.append({
                    "id": str(s.id),
                    "name": s.name,
                    "charge_point_id": s.charge_point_id,
                    "ocpp_url": f"{protocol}://{host}/ocpp/{s.charge_point_id}",
                    "ocpp_version": s.ocpp_version,
                    "vendor": s.vendor or "OCPP Standard",
                    "model": s.model or "EV Charger",
                    "serial_number": s.serial_number,
                    "firmware_version": s.firmware_version,
                    "status": s.status,
                    "error_code": s.error_code,
                    "connector_status": connector_status,
                    "is_online": s.is_online,
                    "is_charging": s.is_charging,
                    "is_discharging_v2g": s.is_discharging_v2g,
                    "last_heartbeat": s.last_heartbeat.isoformat() if s.last_heartbeat else None,
                    "smart_charging_mode": s.smart_charging_mode,
                    "price_threshold_ct": s.price_threshold_ct,
                    "phases": s.phases,
                    "max_current_a": s.max_current_a,
                    "min_current_a": s.min_current_a,
                    "target_current_a": s.target_current_a,
                    "active_power_w": s.active_power_w,
                    "power_kw": power_kw_val,
                    "active_power_kw": power_kw_val,
                    "current_l1": s.current_l1,
                    "current_l2": s.current_l2,
                    "current_l3": s.current_l3,
                    "voltage_v": s.voltage_v,
                    "session_energy_kwh": s.session_energy_kwh,
                    "total_energy_kwh": s.total_energy_kwh,
                    "reservation_id": s.reservation_id,
                    "reserved_id_tag": s.reserved_id_tag,
                    "local_auth_list_version": s.local_auth_list_version,
                    "diagnostics_status": s.diagnostics_status,
                    "last_diagnostics_file": s.last_diagnostics_file,
                    "composite_schedule_data": s.composite_schedule_data,
                    "supports_bidirectional": s.supports_bidirectional,
                    "v2g_mode": s.v2g_mode,
                    "v2g_min_soc_pct": s.v2g_min_soc_pct,
                    "v2g_max_discharge_power_kw": s.v2g_max_discharge_power_kw,
                    "v2g_discharge_power_w": s.v2g_discharge_power_w,
                    "departure_time": s.departure_time.strftime("%H:%M") if s.departure_time else None,
                    "target_departure_soc_pct": s.target_departure_soc_pct,
                    "peak_shaving_threshold_w": s.peak_shaving_threshold_w,
                    "battery_care_mode": s.battery_care_mode,
                    "max_c_rate": s.max_c_rate,
                    "ev_battery_capacity_kwh": s.ev_battery_capacity_kwh,
                    "ev_soc_pct": s.ev_soc_pct,
                    "iso15118_evccid": s.iso15118_evccid,
                    "iso15118_emaid": s.iso15118_emaid,
                    "device_variables": s.device_variables,
                    "active_session": active_session,
                })

            return Response({"wallboxes": data})
        except Exception as e:
            logger.exception("Fehler beim Abrufen der Wallboxen: %s", e)
            return Response({"wallboxes": [], "error": str(e)}, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentifizierung erforderlich."}, status=status.HTTP_401_UNAUTHORIZED)
        home = Home.objects.filter(user=user).first()
        if not home:
            return Response({"error": "Kein Smart Home Profil gefunden."}, status=status.HTTP_400_BAD_REQUEST)

        name = request.data.get("name", "Meine Wallbox").strip()
        vendor = request.data.get("vendor", "").strip()
        model = request.data.get("model", "").strip()
        phases = int(request.data.get("phases", 3))
        max_current_a = float(request.data.get("max_current_a", 16.0))
        smart_charging_mode = request.data.get("smart_charging_mode", "pv_surplus")
        supports_bidirectional = bool(request.data.get("supports_bidirectional", False))
        v2g_mode = request.data.get("v2g_mode", "off")

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
            supports_bidirectional=supports_bidirectional,
            v2g_mode=v2g_mode,
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
        if "min_soc_target_pct" in data:
            station.min_soc_target_pct = int(data["min_soc_target_pct"])
        if "supports_bidirectional" in data:
            station.supports_bidirectional = bool(data["supports_bidirectional"])
        if "v2g_mode" in data:
            if data["v2g_mode"] in dict(ChargingStation.V2G_MODES):
                station.v2g_mode = data["v2g_mode"]
        if "v2g_min_soc_pct" in data:
            station.v2g_min_soc_pct = int(data["v2g_min_soc_pct"])
        if "v2g_max_discharge_power_kw" in data:
            station.v2g_max_discharge_power_kw = float(data["v2g_max_discharge_power_kw"])
        if "departure_time" in data:
            val = str(data["departure_time"]).strip() if data["departure_time"] else None
            if val:
                try:
                    parts = val.split(":")
                    station.departure_time = datetime.time(int(parts[0]), int(parts[1]))
                except (ValueError, IndexError):
                    station.departure_time = None
            else:
                station.departure_time = None
        if "target_departure_soc_pct" in data:
            station.target_departure_soc_pct = int(data["target_departure_soc_pct"])
        if "peak_shaving_threshold_w" in data:
            station.peak_shaving_threshold_w = float(data["peak_shaving_threshold_w"])
        if "battery_care_mode" in data:
            station.battery_care_mode = bool(data["battery_care_mode"])
        if "max_c_rate" in data:
            station.max_c_rate = float(data["max_c_rate"])
        if "ev_battery_capacity_kwh" in data:
            station.ev_battery_capacity_kwh = float(data["ev_battery_capacity_kwh"])
        if "ev_soc_pct" in data:
            station.ev_soc_pct = float(data["ev_soc_pct"])

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
            "supports_bidirectional": station.supports_bidirectional,
            "v2g_mode": station.v2g_mode,
            "v2g_min_soc_pct": station.v2g_min_soc_pct,
            "v2g_max_discharge_power_kw": station.v2g_max_discharge_power_kw,
            "ev_soc_pct": station.ev_soc_pct,
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
            if not tx_id:
                active_sess = ChargingSession.objects.filter(station=station, status="active").order_by("-start_time").first()
                if active_sess:
                    tx_id = active_sess.transaction_id
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {"type": "ocpp_remote_stop", "transaction_id": tx_id or 0}
                )
            return Response({"success": True, "message": f"Stopp-Befehl an {station.name} gesendet."})

        elif action == "unlock":
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {"type": "ocpp_unlock_connector", "connector_id": 1}
                )
            return Response({"success": True, "message": f"Entriegelungs-Befehl an {station.name} gesendet."})

        elif action == "reserve":
            id_tag = request.data.get("id_tag", "RESERVED_USER")
            res_id = int(request.data.get("reservation_id", 1))
            duration_minutes = int(request.data.get("duration_minutes", 120))
            expiry_date = (timezone.now() + timezone.timedelta(minutes=duration_minutes)).isoformat()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {
                        "type": "ocpp_reserve_now",
                        "connector_id": 1,
                        "id_tag": id_tag,
                        "reservation_id": res_id,
                        "expiry_date": expiry_date
                    }
                )
            station.status = "Reserved"
            station.reserved_id_tag = id_tag
            station.reservation_id = res_id
            station.reservation_expiry = timezone.now() + timezone.timedelta(minutes=duration_minutes)
            station.active_power_w = 0.0
            station.target_current_a = 0.0
            station.save(update_fields=["status", "reserved_id_tag", "reservation_id", "reservation_expiry", "active_power_w", "target_current_a"])
            return Response({"success": True, "message": f"Ladesäule {station.name} wurde für {duration_minutes} Minuten reserviert."})

        elif action == "cancel-reserve":
            res_id = station.reservation_id or 1
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {"type": "ocpp_cancel_reservation", "reservation_id": res_id}
                )
            station.status = "Available"
            station.reservation_id = None
            station.reserved_id_tag = ""
            station.reservation_expiry = None
            station.save(update_fields=["status", "reservation_id", "reserved_id_tag", "reservation_expiry"])
            return Response({"success": True, "message": f"Reservierung für {station.name} aufgehoben."})

        elif action == "trigger-message":
            requested_message = request.data.get("requested_message", "StatusNotification")
            connector_id = request.data.get("connector_id")
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {
                        "type": "ocpp_trigger_message",
                        "requested_message": requested_message,
                        "connector_id": connector_id
                    }
                )
            return Response({"success": True, "message": f"TriggerMessage '{requested_message}' an {station.name} gesendet."})

        elif action == "sync-rfid-list":
            tags = ChargingRfidTag.objects.filter(home=home, is_active=True)
            local_list = []
            for t in tags:
                local_list.append({
                    "idTag": t.id_tag,
                    "idTagInfo": {
                        "status": "Accepted",
                        "expiryDate": t.expiry_date.isoformat() if t.expiry_date else None
                    }
                })
            next_version = (station.local_auth_list_version or 0) + 1
            update_type = request.data.get("update_type", "Full")
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {
                        "type": "ocpp_send_local_list",
                        "list_version": next_version,
                        "update_type": update_type,
                        "local_authorization_list": local_list
                    }
                )
            station.local_auth_list_version = next_version
            station.save(update_fields=["local_auth_list_version"])
            return Response({
                "success": True,
                "list_version": next_version,
                "count": len(local_list),
                "message": f"{len(local_list)} RFID-Chips erfolgreich als Version {next_version} an die Wallbox übertragen."
            })

        elif action == "get-local-list-version":
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {"type": "ocpp_get_local_list_version"}
                )
            return Response({"success": True, "message": f"Abfrage der LocalListVersion an {station.name} gesendet."})

        elif action == "get-composite-schedule":
            duration = int(request.data.get("duration", 86400))
            unit = request.data.get("charging_rate_unit", "A")
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {
                        "type": "ocpp_get_composite_schedule",
                        "connector_id": 1,
                        "duration": duration,
                        "charging_rate_unit": unit
                    }
                )
            return Response({"success": True, "message": f"GetCompositeSchedule ({duration}s, {unit}) an {station.name} gesendet."})

        elif action == "get-diagnostics":
            location = request.data.get("location", "https://sharegy.de/api/energy/wallboxes/diagnostics-upload/")
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {
                        "type": "ocpp_get_diagnostics",
                        "location": location,
                        "retries": int(request.data.get("retries", 3)),
                        "retry_interval": int(request.data.get("retry_interval", 30))
                    }
                )
            station.diagnostics_status = "Uploading"
            station.save(update_fields=["diagnostics_status"])
            return Response({"success": True, "message": f"Diagnose-Upload an {location} angefordert."})

        elif action == "set-v2g-mode":
            v2g_mode = request.data.get("v2g_mode", "off")
            min_soc = int(request.data.get("v2g_min_soc_pct", station.v2g_min_soc_pct or 50))
            max_pwr = float(request.data.get("v2g_max_discharge_power_kw", station.v2g_max_discharge_power_kw or 11.0))
            
            station.supports_bidirectional = True
            station.v2g_mode = v2g_mode
            station.v2g_min_soc_pct = min_soc
            station.v2g_max_discharge_power_kw = max_pwr

            if "departure_time" in request.data:
                val = str(request.data["departure_time"]).strip() if request.data["departure_time"] else None
                if val:
                    try:
                        parts = val.split(":")
                        station.departure_time = datetime.time(int(parts[0]), int(parts[1]))
                    except (ValueError, IndexError):
                        station.departure_time = None
                else:
                    station.departure_time = None
            if "target_departure_soc_pct" in request.data:
                station.target_departure_soc_pct = int(request.data["target_departure_soc_pct"])
            if "peak_shaving_threshold_w" in request.data:
                station.peak_shaving_threshold_w = float(request.data["peak_shaving_threshold_w"])
            if "battery_care_mode" in request.data:
                station.battery_care_mode = bool(request.data["battery_care_mode"])
            if "max_c_rate" in request.data:
                station.max_c_rate = float(request.data["max_c_rate"])

            station.save(update_fields=[
                "supports_bidirectional", "v2g_mode", "v2g_min_soc_pct", "v2g_max_discharge_power_kw",
                "departure_time", "target_departure_soc_pct", "peak_shaving_threshold_w", "battery_care_mode", "max_c_rate"
            ])

            # V2G Dispatch berechnen und anwenden
            from energy.services.services_v2g import V2GDispatchEngine
            from energy.ems.services import build_device_signals
            from market.models import SpotPrice

            user = home.user if home else None
            signals = build_device_signals(user) if user else {}
            latest_spot = SpotPrice.objects.filter(timestamp__lte=timezone.now()).order_by("-timestamp").first()
            spot_mwh = (float(latest_spot.price_eur_per_kwh) * 1000.0) if (latest_spot and latest_spot.price_eur_per_kwh is not None) else 80.0

            class HomeMetricDummy:
                pv_power_w = float(signals.get("pv", {}).get("production", 0.0) or 0.0)
                house_power_w = float(signals.get("load", {}).get("consumption", 0.0) or 0.0)
                battery_soc_pct = float(signals.get("battery", {}).get("soc", 100.0) or 100.0)
                battery_power_w = float(signals.get("battery", {}).get("charge", 0.0) or 0.0)

            v2g_res = V2GDispatchEngine.calculate_v2x_dispatch(station, HomeMetricDummy(), spot_mwh)
            V2GDispatchEngine.dispatch_v2x_command(station, v2g_res)

            return Response({
                "success": True,
                "v2g_mode": station.v2g_mode,
                "v2g_min_soc_pct": station.v2g_min_soc_pct,
                "dispatch": v2g_res,
                "message": f"V2G Modus auf '{station.v2g_mode}' gesetzt. ({v2g_res.get('reason')})"
            })

        elif action == "v2g-discharge":
            # Manuelle V2H / V2G Entladung erzwingen
            power_w = float(request.data.get("power_w", 3500.0))
            if power_w > 0:
                power_w = -abs(power_w)
            current_a = round(abs(power_w) / (230.0 * int(station.phases or 3)), 1)

            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {
                        "type": "ocpp_set_v2g_profile",
                        "power_w": power_w,
                        "current_a": current_a,
                        "connector_id": 1
                    }
                )
            station.v2g_discharge_power_w = abs(power_w)
            station.active_power_w = 0.0
            station.target_current_a = current_a
            station.save(update_fields=["v2g_discharge_power_w", "active_power_w", "target_current_a"])
            return Response({
                "success": True,
                "discharge_power_w": abs(power_w),
                "message": f"V2G Entladung mit {abs(power_w):.0f} W an {station.name} gestartet."
            })

        elif action == "get-variables":
            # OCPP 2.0.1 & 2.1 GetVariables
            get_variable_data = request.data.get("get_variable_data", [
                {"component": {"name": "ChargingStation"}, "variable": {"name": "Model"}},
                {"component": {"name": "EVSE"}, "variable": {"name": "AvailabilityState"}},
                {"component": {"name": "ISO15118Ctrlr"}, "variable": {"name": "CertificateInstalled"}},
            ])
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {"type": "ocpp_get_variables", "get_variable_data": get_variable_data}
                )
            return Response({"success": True, "message": f"GetVariables an {station.name} gesendet."})

        elif action == "set-variables":
            # OCPP 2.0.1 & 2.1 SetVariables
            set_variable_data = request.data.get("set_variable_data", [])
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {"type": "ocpp_set_variables", "set_variable_data": set_variable_data}
                )
            return Response({"success": True, "message": f"SetVariables an {station.name} gesendet."})

        elif action == "clear-charging-profile":
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {"type": "ocpp_clear_charging_profile", "connector_id": 1}
                )
            station.target_current_a = 0.0
            station.save(update_fields=["target_current_a"])
            return Response({"success": True, "message": f"Ladeprofil auf {station.name} gelöscht."})

        elif action == "reset":
            reset_type = request.data.get("type", "Soft")
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {"type": "ocpp_reset", "type": reset_type}
                )
            return Response({"success": True, "message": f"Reset-Befehl ({reset_type}) an {station.name} gesendet."})

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
