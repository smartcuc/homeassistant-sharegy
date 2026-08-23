import logging
from datetime import UTC, datetime

from django.utils import timezone
from django.core.cache import cache

from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from devices.models import (
    Device,
    DeviceMetric,
    DeviceLatestMetric,
    DeviceConfig,
    DeviceResource,
    Home,
    MetricDefinition,
)
from devices.services.metrics import should_record_metric
from devices.services.ingest import ingest_metric_payload

from .parser import get_attr

logger = logging.getLogger("django")


@api_view(["POST"])
@permission_classes([AllowAny])
def otlp_metrics(request):
    created = 0
    resource_metrics = request.data.get("resourceMetrics", [])

    for resource_metric in resource_metrics:
        resource = resource_metric.get("resource", {})
        attributes = resource.get("attributes", [])
        resource_attributes = {}

        for attr in attributes:
            key = attr.get("key")
            value = get_attr([attr], key)
            if key and value is not None:
                resource_attributes[key] = value

        resource_attributes.pop("home.token", None)
        device_id = get_attr(attributes, "device.id")
        token = get_attr(attributes, "home.token")

        if not device_id or not token:
            continue

        try:
            home = Home.objects.get(mqtt_token=token)
        except Home.DoesNotExist:
            logger.warning(
                "otlp.invalid_token",
                extra={
                    "token": token,
                    "device": device_id,
                },
            )
            continue

        device, _ = Device.objects.get_or_create(
            home=home,
            identifier=device_id,
        )

        device.last_seen = timezone.now()
        device.save(update_fields=["last_seen"])

        resource_obj, _ = DeviceResource.objects.get_or_create(
            device=device,
        )

        if resource_obj.attributes != resource_attributes:
            resource_obj.attributes = resource_attributes
            resource_obj.save(update_fields=["attributes"])

        config, _ = DeviceConfig.objects.get_or_create(
            device=device,
            defaults={
                "home": home,
                "name": device.identifier,
            },
        )

        for scope_metric in resource_metric.get("scopeMetrics", []):
            for metric in scope_metric.get("metrics", []):
                metric_name = metric.get("name")
                if not metric_name:
                    continue

                metric_unit = metric.get("unit", "")
                metric_definition, _ = MetricDefinition.objects.get_or_create(
                    key=metric_name,
                    defaults={
                        "name": metric_name,
                        "unit": metric_unit,
                    },
                )
                if not metric_unit and metric_definition.unit:
                    metric_unit = metric_definition.unit

                # Auto-Assign Lead-Metric für EMS-Wirkleistung
                if not config.metric_definition:
                    if metric_name in ["power", "active_power", "p_total", "W", "val", "value"] or not config.metric_definition:
                        config.metric_definition = metric_definition
                        config.save(update_fields=["metric_definition"])

                datapoints_container = metric.get("gauge") or metric.get("sum")
                if not datapoints_container:
                    continue

                for point in datapoints_container.get("dataPoints", []):
                    value = point.get("asDouble")
                    if value is None:
                        value = point.get("asInt")
                    if value is None:
                        continue

                    float_val = float(value)
                    metric_key = str(metric_name)

                    ns = point.get("timeUnixNano")
                    if ns is not None:
                        timestamp = datetime.fromtimestamp(
                            int(ns) / 1_000_000_000,
                            tz=UTC,
                        )
                    else:
                        timestamp = timezone.now()

                    res = ingest_metric_payload(
                        device=device,
                        metrics={metric_name: float_val},
                        timestamp=timestamp,
                        source="otel",
                        meta=resource_attributes,
                        unit_map={metric_name: metric_unit},
                    )
                    created += res.get("created_metrics", 0)

    return Response(
        {
            "status": "ok",
            "created": created,
        }
    )
