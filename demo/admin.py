from django.contrib import admin
from .models import DemoDeviceMap, DemoDeviceSimulation


@admin.register(DemoDeviceMap)
class DemoDeviceMapAdmin(admin.ModelAdmin):
    list_display = ("id", "source_device", "demo_device", "created_at")
    raw_id_fields = ("source_device", "demo_device")
    search_fields = ("source_device__name", "demo_device__name")
    list_filter = ("created_at",)


@admin.register(DemoDeviceSimulation)
class DemoDeviceSimulationAdmin(admin.ModelAdmin):
    list_display = ("id", "device", "hidden_until")
    raw_id_fields = ("device",)
    search_fields = ("device__name",)
    list_filter = ("hidden_until",)

