###################
# producer/admin.py
###################

from django.contrib import admin

from producer.models import (
    GeneratorSystem,
    GeneratorString,
    GeneratorType,
    Orientation,
    StorageSystem,
)


class GeneratorStringInline(admin.TabularInline):
    model = GeneratorString

    extra = 1

    fields = (
        "name",
        "module_count",
        "peak_power_kwp",
        "orientation",
        "tilt_deg",
        "shading_percent",
    )


@admin.register(GeneratorType)
class GeneratorTypeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "key",
        "sort_order",
        "active",
    )

    list_filter = ("active",)


@admin.register(Orientation)
class OrientationAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "key",
        "azimuth_deg",
        "sort_order",
        "active",
    )

    list_filter = ("active",)


@admin.register(GeneratorSystem)
class GeneratorSystemAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "home",
        "generator_type",
        "peak_power_kw",
        "active",
    )

    list_filter = (
        "generator_type",
        "active",
    )

    inlines = [
        GeneratorStringInline,
    ]


@admin.register(StorageSystem)
class StorageSystemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "home",
        "capacity_kwh",
        "max_charge_power_kw",
        "max_discharge_power_kw",
        "min_soc_reserve_pct",
        "primary_device",
        "active",
    )
    list_filter = ("active", "is_auto_detected")
    search_fields = ("name", "home__name")
