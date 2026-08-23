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
