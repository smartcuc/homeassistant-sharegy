########################
# producer/api/views.py
########################

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from producer.models import GeneratorSystem, GeneratorString, GeneratorType,  Orientation


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generator_list(request):

    home = request.user.homes.first()

    if not home:
        return Response([])

    systems = (
        GeneratorSystem.objects.filter(
            home=home,
            active=True,
        )
        .prefetch_related(
            "strings",
            "generator_type",
        )
        .order_by("name")
    )

    data = []

    for system in systems:

        strings = []

        for string in system.strings.all():

            strings.append(
                {
                    "id": str(string.id),
                    "name": string.name,
                    "module_count": string.module_count,
                    "peak_power_kwp": float(string.peak_power_kwp),
                    "orientation": string.orientation.name if string.orientation else "-",
                    "orientation_key": string.orientation.key if string.orientation else None,
                    "orientation_id": string.orientation.id if string.orientation else None,
                    "tilt_deg": string.tilt_deg,
                    "shading_percent": float(string.shading_percent),
                }
            )

        data.append(
            {
                "id": str(system.id),
                "generator_type_id": (
                    system.generator_type.id if system.generator_type else None
                ),
                "device_id": (system.device.id if system.device else None),
                "name": system.name,
                "type": (system.generator_type.key if system.generator_type else None),
                "type_label": (
                    system.generator_type.name
                    if system.generator_type
                    else "Nicht konfiguriert"
                ),
                "needs_configuration": system.needs_configuration,
                "peak_power_kw": (
                    float(system.peak_power_kw)
                    if system.peak_power_kw is not None
                    else None
                ),
                "inverter_power_kw": (
                    float(system.inverter_power_kw)
                    if system.inverter_power_kw
                    else None
                ),
                "battery_capacity_kwh": (
                    float(system.battery_capacity_kwh)
                    if system.battery_capacity_kwh
                    else None
                ),
                "string_count": system.string_count,
                "total_string_power_kwp": system.total_string_power_kwp,
                "strings": strings,
            }
        )

    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generator_create(request):

    home = request.user.homes.first()

    if not home:
        return Response(
            {"detail": "Kein Home gefunden."},
            status=400,
        )

    generator_type = None

    if request.data.get("generator_type"):

        generator_type = GeneratorType.objects.get(
            id=request.data["generator_type"]
        )

    system = GeneratorSystem.objects.create(
        home=home,
        generator_type=generator_type,
        name=request.data.get("name"),
        peak_power_kw=request.data.get("peak_power_kw"),
        inverter_power_kw=request.data.get("inverter_power_kw"),
        battery_capacity_kwh=request.data.get("battery_capacity_kwh"),
    )

    return Response(
        {
            "id": str(system.id),
        }
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def generator_delete(request, generator_id):

    generator = GeneratorSystem.objects.get(
        id=generator_id,
        home=request.user.homes.first(),
    )

    generator.delete()

    return Response(
        {
            "success": True,
        }
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def generator_update(
    request,
    generator_id,
):

    generator = GeneratorSystem.objects.get(
        id=generator_id,
        home=request.user.homes.first(),
    )

    if "name" in request.data:
        generator.name = request.data["name"]

    if "peak_power_kw" in request.data:
        generator.peak_power_kw = request.data["peak_power_kw"]

    if "inverter_power_kw" in request.data:
        generator.inverter_power_kw = request.data["inverter_power_kw"]

    if "battery_capacity_kwh" in request.data:
        generator.battery_capacity_kwh = request.data["battery_capacity_kwh"]

    if "generator_type" in request.data:

        generator.generator_type = GeneratorType.objects.get(
            id=request.data["generator_type"]
        )

    generator.save()

    return Response(
        {
            "success": True,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def string_create(request):

    generator = GeneratorSystem.objects.get(id=request.data["generator_id"])
    orientation = Orientation.objects.get(id=request.data["orientation_id"]
    )

    string = GeneratorString.objects.create(
        generator=generator,
        name=request.data["name"],
        module_count=request.data["module_count"],
        peak_power_kwp=request.data["peak_power_kwp"],
        orientation=orientation,
        tilt_deg=request.data["tilt_deg"],
        shading_percent=request.data.get(
            "shading_percent",
            0,
        ),
    )

    return Response(
        {
            "id": str(string.id),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generator_type_list(request):

    data = []

    for item in GeneratorType.objects.filter(
        active=True,
    ):

        data.append(
            {
                "id": item.id,
                "key": item.key,
                "name": item.name,
            }
        )

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def orientation_list(request):

    data = []

    for item in Orientation.objects.filter(
        active=True,
    ):

        data.append(
            {
                "id": item.id,
                "key": item.key,
                "name": item.name,
                "azimuth_deg": item.azimuth_deg,
            }
        )

    return Response(data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def string_delete(
    request,
    string_id,
):

    string = GeneratorString.objects.get(id=string_id)

    string.delete()

    return Response(
        {
            "success": True,
        }
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def string_update(
    request,
    string_id,
):

    string = GeneratorString.objects.get(id=string_id)

    if "name" in request.data:
        string.name = request.data["name"]

    if "module_count" in request.data:
        string.module_count = request.data["module_count"]

    if "peak_power_kwp" in request.data:
        string.peak_power_kwp = request.data["peak_power_kwp"]

    if "orientation_id" in request.data:

        string.orientation = Orientation.objects.get(id=request.data["orientation_id"])

    if "tilt_deg" in request.data:
        string.tilt_deg = request.data["tilt_deg"]

    if "shading_percent" in request.data:
        string.shading_percent = request.data["shading_percent"]

    string.save()

    return Response(
        {
            "success": True,
        }
    )


# ============================================================
# ✅ STORAGE SYSTEM (BATTERIESPEICHER) APIS
# ============================================================

from producer.models import StorageSystem
from devices.models import Device, DeviceLatestMetric
from django.db.models import Q


def serialize_storage_system(storage):
    live_soc = storage.get_live_soc()
    live_power = storage.get_live_power()
    capacity = float(storage.capacity_kwh)
    current_stored_kwh = round((live_soc / 100.0) * capacity, 2) if (live_soc is not None) else None

    # Status bestimmen
    status = "idle"
    if live_power is not None:
        if live_power > 50:
            status = "charging"
        elif live_power < -50:
            status = "discharging"
        elif live_soc is not None and live_soc >= float(storage.max_soc_pct) - 2.0:
            status = "full"
        elif live_soc is not None and live_soc <= float(storage.min_soc_reserve_pct) + 2.0:
            status = "empty_reserve"

    def get_dev_info(dev):
        if not dev:
            return None, None
        name = dev.config.name if hasattr(dev, "config") and dev.config and dev.config.name else dev.identifier
        return str(dev.id), name

    p_id, p_name = get_dev_info(storage.primary_device)
    soc_id, soc_name = get_dev_info(storage.soc_device)
    pwr_id, pwr_name = get_dev_info(storage.power_device)
    curr_id, curr_name = get_dev_info(storage.current_device)
    volt_id, volt_name = get_dev_info(storage.voltage_device)
    cin_id, cin_name = get_dev_info(storage.charge_energy_device)
    cout_id, cout_name = get_dev_info(storage.discharge_energy_device)

    return {
        "id": str(storage.id),
        "name": storage.name,
        "capacity_kwh": capacity,
        "max_charge_power_kw": float(storage.max_charge_power_kw),
        "max_discharge_power_kw": float(storage.max_discharge_power_kw),
        "min_soc_reserve_pct": float(storage.min_soc_reserve_pct),
        "max_soc_pct": float(storage.max_soc_pct),
        "charge_efficiency_pct": float(storage.charge_efficiency_pct),
        "discharge_efficiency_pct": float(storage.discharge_efficiency_pct),
        "active": storage.active,
        "is_auto_detected": storage.is_auto_detected,
        # Live Metrics
        "live_soc_pct": live_soc,
        "live_power_w": live_power,
        "current_stored_kwh": current_stored_kwh,
        "status": status,
        # Mapped Signals
        "primary_device": {"id": p_id, "name": p_name} if p_id else None,
        "soc_device": {"id": soc_id, "name": soc_name, "metric_key": storage.soc_metric_key} if soc_id else None,
        "power_device": {"id": pwr_id, "name": pwr_name, "metric_key": storage.power_metric_key} if pwr_id else None,
        "current_device": {"id": curr_id, "name": curr_name, "metric_key": storage.current_metric_key} if curr_id else None,
        "voltage_device": {"id": volt_id, "name": volt_name, "metric_key": storage.voltage_metric_key} if volt_id else None,
        "charge_energy_device": {"id": cin_id, "name": cin_name, "metric_key": storage.charge_energy_metric_key} if cin_id else None,
        "discharge_energy_device": {"id": cout_id, "name": cout_name, "metric_key": storage.discharge_energy_metric_key} if cout_id else None,
        "created_at": storage.created_at.isoformat(),
        "updated_at": storage.updated_at.isoformat(),
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def storage_list(request):
    home = request.user.homes.first()
    if not home:
        return Response([])

    storages = list(StorageSystem.objects.filter(home=home).select_related(
        "primary_device", "soc_device", "power_device", "current_device", "voltage_device", "charge_energy_device", "discharge_energy_device"
    ).order_by("created_at"))

    # 1. Strikte Konsolidierung: Ein Haushalt besitzt im UI genau 1 logisches Batteriesystem
    if len(storages) > 1:
        primary = storages[0]
        for duplicate in storages[1:]:
            # Übernehme fehlende Bindungen aus dem Duplikat in das primäre System
            if not primary.soc_device and duplicate.soc_device:
                primary.soc_device = duplicate.soc_device
                primary.soc_metric_key = duplicate.soc_metric_key
            if not primary.power_device and duplicate.power_device:
                primary.power_device = duplicate.power_device
                primary.power_metric_key = duplicate.power_metric_key
            if not primary.current_device and (duplicate.current_device or duplicate.primary_device):
                primary.current_device = duplicate.current_device or duplicate.primary_device
                primary.current_metric_key = duplicate.current_metric_key or "battery_current"
            if not primary.voltage_device and duplicate.voltage_device:
                primary.voltage_device = duplicate.voltage_device
                primary.voltage_metric_key = duplicate.voltage_metric_key
            if duplicate.capacity_kwh and float(duplicate.capacity_kwh) > float(primary.capacity_kwh or 0):
                primary.capacity_kwh = duplicate.capacity_kwh
            duplicate.delete()
        primary.save()
        storages = [primary]

    # 2. Auto-Creation & Wiring: Falls noch kein Speicher existiert oder Sensoren unvollständig sind
    if not storages:
        home_devs = list(Device.objects.filter(home=home, pending_delete=False))
        has_battery_devs = any(
            (getattr(d.config.role, "key", "") if getattr(d, "config", None) and d.config.role else "").lower() in ["battery", "storage", "akku"]
            or any(k in (getattr(d.config, "name", None) or d.identifier or "").lower() for k in ["battery", "batterie", "speicher", "soc"])
            for d in home_devs
        )
        if has_battery_devs:
            storage = StorageSystem.objects.create(
                home=home,
                name="Hausspeicher",
                capacity_kwh=10.0,
                max_charge_power_kw=5.0,
                max_discharge_power_kw=5.0,
                is_auto_detected=True,
            )
            storages = [storage]

    if storages:
        storage = storages[0]
        home_devs = list(Device.objects.filter(home=home, pending_delete=False))
        updated = False

        for d in home_devs:
            d_name = (getattr(d.config, "name", None) or d.identifier or "").lower()
            role_key = (getattr(d.config.role, "key", "") if getattr(d, "config", None) and d.config.role else "").lower()
            mdef = getattr(d.config, "metric_definition", None) if getattr(d, "config", None) else None
            unit = (mdef.unit or "").strip().lower() if mdef else ""
            m_key = (mdef.key or "").strip().lower() if mdef else ""

            is_current = unit in ["a", "ma"] or m_key in ["current", "battery_current"] or any(k in d_name for k in ["_current", "stromstärke", "battery_current"])
            is_soc = unit in ["%"] or m_key in ["soc", "battery_soc", "battery_level"] or any(k in d_name for k in ["_soc", "ladestand", "battery_soc", "battery_level"])
            is_voltage = unit in ["v", "mv"] or m_key in ["voltage", "battery_voltage"] or any(k in d_name for k in ["_voltage", "spannung", "battery_voltage"])
            is_power = (unit in ["w", "kw"] or m_key in ["power", "battery_power", "active_power"] or any(k in d_name for k in ["power", "leistung", "battery_power"])) and not is_current

            if is_soc and not storage.soc_device:
                storage.soc_device = d
                storage.soc_metric_key = m_key or "soc"
                updated = True
            elif is_current and not storage.current_device:
                storage.current_device = d
                storage.current_metric_key = m_key or "battery_current"
                updated = True
            elif is_power and not storage.power_device:
                storage.power_device = d
                storage.power_metric_key = m_key or "power"
                updated = True
            elif is_voltage and not storage.voltage_device:
                storage.voltage_device = d
                storage.voltage_metric_key = m_key or "battery_voltage"
                updated = True

        if updated:
            storage.save()

    return Response([serialize_storage_system(s) for s in storages])


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def storage_create(request):
    home = request.user.homes.first()
    if not home:
        return Response({"error": "No home found"}, status=400)

    data = request.data
    storage = StorageSystem.objects.create(
        home=home,
        name=data.get("name", "Hausspeicher"),
        capacity_kwh=data.get("capacity_kwh", 10.0),
        max_charge_power_kw=data.get("max_charge_power_kw", 5.0),
        max_discharge_power_kw=data.get("max_discharge_power_kw", 5.0),
        min_soc_reserve_pct=data.get("min_soc_reserve_pct", 10.0),
        max_soc_pct=data.get("max_soc_pct", 100.0),
        charge_efficiency_pct=data.get("charge_efficiency_pct", 95.0),
        discharge_efficiency_pct=data.get("discharge_efficiency_pct", 95.0),
        soc_metric_key=data.get("soc_metric_key", "soc"),
        power_metric_key=data.get("power_metric_key", "power"),
        current_metric_key=data.get("current_metric_key", "battery_current"),
        voltage_metric_key=data.get("voltage_metric_key", "battery_voltage"),
        charge_energy_metric_key=data.get("charge_energy_metric_key", "energy_in"),
        discharge_energy_metric_key=data.get("discharge_energy_metric_key", "energy_out"),
        active=data.get("active", True),
    )

    # Devices verknüpfen
    if data.get("primary_device_id"):
        storage.primary_device = Device.objects.filter(id=data["primary_device_id"], home=home).first()
    if data.get("soc_device_id"):
        storage.soc_device = Device.objects.filter(id=data["soc_device_id"], home=home).first()
    if data.get("power_device_id"):
        storage.power_device = Device.objects.filter(id=data["power_device_id"], home=home).first()
    if data.get("current_device_id"):
        storage.current_device = Device.objects.filter(id=data["current_device_id"], home=home).first()
    if data.get("voltage_device_id"):
        storage.voltage_device = Device.objects.filter(id=data["voltage_device_id"], home=home).first()
    if data.get("charge_energy_device_id"):
        storage.charge_energy_device = Device.objects.filter(id=data["charge_energy_device_id"], home=home).first()
    if data.get("discharge_energy_device_id"):
        storage.discharge_energy_device = Device.objects.filter(id=data["discharge_energy_device_id"], home=home).first()

    storage.save()
    return Response(serialize_storage_system(storage), status=201)


@api_view(["PATCH", "PUT"])
@permission_classes([IsAuthenticated])
def storage_update(request, storage_id):
    home = request.user.homes.first()
    try:
        storage = StorageSystem.objects.get(id=storage_id, home=home)
    except StorageSystem.DoesNotExist:
        return Response({"error": "Storage system not found"}, status=404)

    data = request.data
    for field in [
        "name", "capacity_kwh", "max_charge_power_kw", "max_discharge_power_kw",
        "min_soc_reserve_pct", "max_soc_pct", "charge_efficiency_pct",
        "discharge_efficiency_pct", "soc_metric_key", "power_metric_key",
        "current_metric_key", "voltage_metric_key",
        "charge_energy_metric_key", "discharge_energy_metric_key", "active"
    ]:
        if field in data:
            setattr(storage, field, data[field])

    # Devices updaten (auch null erlaubt)
    if "primary_device_id" in data:
        p_id = data["primary_device_id"]
        storage.primary_device = Device.objects.filter(id=p_id, home=home).first() if p_id else None
    if "soc_device_id" in data:
        soc_id = data["soc_device_id"]
        storage.soc_device = Device.objects.filter(id=soc_id, home=home).first() if soc_id else None
    if "power_device_id" in data:
        pwr_id = data["power_device_id"]
        storage.power_device = Device.objects.filter(id=pwr_id, home=home).first() if pwr_id else None
    if "current_device_id" in data:
        c_id = data["current_device_id"]
        storage.current_device = Device.objects.filter(id=c_id, home=home).first() if c_id else None
    if "voltage_device_id" in data:
        v_id = data["voltage_device_id"]
        storage.voltage_device = Device.objects.filter(id=v_id, home=home).first() if v_id else None
    if "charge_energy_device_id" in data:
        cin_id = data["charge_energy_device_id"]
        storage.charge_energy_device = Device.objects.filter(id=cin_id, home=home).first() if cin_id else None
    if "discharge_energy_device_id" in data:
        cout_id = data["discharge_energy_device_id"]
        storage.discharge_energy_device = Device.objects.filter(id=cout_id, home=home).first() if cout_id else None

    storage.save()
    return Response(serialize_storage_system(storage))


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def storage_delete(request, storage_id):
    home = request.user.homes.first()
    try:
        storage = StorageSystem.objects.get(id=storage_id, home=home)
    except StorageSystem.DoesNotExist:
        return Response({"error": "Storage system not found"}, status=404)

    storage.delete()
    return Response({"success": True})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def storage_detect(request):
    """
    Scannt alle Geräte des Haushalts nach Speicher-Metriken (SoC, Ladeleistung, Batteriestrom)
    und liefert intelligente Vorschläge zur 1-Klick-Übernahme.
    """
    home = request.user.homes.first()
    if not home:
        return Response({"candidates": [], "devices": []})

    devices = Device.objects.filter(home=home, active=True, pending_delete=False)
    candidates = []
    device_options = []

    for dev in devices:
        name = dev.config.name if hasattr(dev, "config") and dev.config and dev.config.name else dev.identifier
        role = dev.config.role.key if (hasattr(dev, "config") and dev.config and dev.config.role) else ""

        # Vorhandene Metriken abfragen
        metrics = list(DeviceLatestMetric.objects.filter(device=dev).values_list("metric_key", flat=True))

        has_soc = any(k in ["soc", "battery_soc", "state_of_charge", "battery_level"] for k in metrics)
        has_power = any(k in ["power", "battery_power", "battery_w", "power_w"] for k in metrics)
        has_current = any(k in ["battery_current", "current"] for k in metrics)
        has_voltage = any(k in ["battery_voltage", "voltage"] for k in metrics)
        has_energy = any(k in ["energy_in", "energy_out", "total_charge", "total_discharge"] for k in metrics)

        # Reine Stromsensoren sind KEIN eigenständiger Speicher-Kandidat
        is_pure_current = has_current and not has_power and not has_soc

        is_candidate = not is_pure_current and (
            role in ["battery", "storage", "akku"]
            or ("battery" in dev.identifier.lower() and not "current" in dev.identifier.lower())
            or has_soc
            or has_power
        )

        dev_data = {
            "id": str(dev.id),
            "name": name,
            "identifier": dev.identifier,
            "role": role,
            "metrics": metrics,
            "has_soc": has_soc,
            "has_power": has_power,
            "has_current": has_current,
            "has_voltage": has_voltage,
            "has_energy": has_energy,
        }
        device_options.append(dev_data)

        if is_candidate:
            soc_key = "soc" if "soc" in metrics else ("battery_soc" if "battery_soc" in metrics else ("battery_level" if "battery_level" in metrics else "value"))
            pwr_key = "battery_power" if "battery_power" in metrics else ("power" if "power" in metrics else "value")
            curr_key = "battery_current" if "battery_current" in metrics else ("current" if "current" in metrics else "")

            candidates.append({
                "device": dev_data,
                "suggested_name": f"{name} (Speicher)",
                "suggested_soc_metric": soc_key,
                "suggested_power_metric": pwr_key,
                "suggested_current_metric": curr_key,
                "confidence": "high" if has_soc and has_power else ("medium" if has_soc or role in ["battery", "storage"] else "low"),
            })

    return Response({
        "candidates": candidates,
        "devices": device_options,
    })

