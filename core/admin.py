################################
# core/admin.py
################################

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import OuterRef, Subquery, DateTimeField
from django_celery_results.models import TaskResult

from core.models import (
    Meter,
    IntervalReading,
    AggregatedReading,
    BalanceSlot,
    MeterRegister,
    Tenant,  
)


# ============================================================
# ✅ CELERY TASKS
# ============================================================


# ✅ erst deregistrieren
admin.site.unregister(TaskResult)

@admin.register(TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    list_display = (
        "task_id",
        "task_name",
        "status",
        "date_done",
    )
    search_fields = ("task_id", "task_name")
    list_filter = ("status",)
    readonly_fields = ("result", "traceback")


# ============================================================
# 🔥 METER ADMIN (DEBUG + PERFORMANCE)
# ============================================================

@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):

    fields = (
        "serial_number",
        "tenant",
        "owner_user",
        "owner_membership",
        "meter_type",
        "integration_type",
        "tibber_home_id",
        "last_tibber_sync",
    )

    readonly_fields = ("last_tibber_sync",)

    list_display = (
        "id",
        "serial_number",
        "tenant",
        "owner_user",
        "owner_membership",
        "meter_type",
        "integration_type",
        "last_reading",
        "delay_minutes",
        "status_colored",
    )

    list_filter = (
        "meter_type",
        "tenant",
        "integration_type",
    )

    search_fields = ("serial_number", "tibber_home_id", "owner_user__email", "owner_user__username")

    raw_id_fields = ("tenant", "owner_user", "owner_membership")
    list_select_related = ("tenant", "owner_user", "owner_membership")

    ordering = ("serial_number",)

    # ✅ Performance: latest reading als Subquery
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        latest_reading = (
            IntervalReading.objects.filter(meter=OuterRef("pk"))
            .order_by("-ts_start")
            .values("ts_start")[:1]
        )

        return qs.annotate(
            last_reading_ts=Subquery(
                latest_reading,
                output_field=DateTimeField(),
            )
        )

    def last_reading(self, obj):
        return obj.last_reading_ts
    last_reading.short_description = "Last Reading"

    def delay_minutes(self, obj):
        if not obj.last_reading_ts:
            return None

        delta = timezone.now() - obj.last_reading_ts
        return int(delta.total_seconds() / 60)
    delay_minutes.short_description = "Delay (min)"

    def status_colored(self, obj):
        if not obj.last_reading_ts:
            return mark_safe("<span style='color:gray;'>no_data</span>")

        delay = self.delay_minutes(obj)

        if delay < 60:
            return mark_safe("<b style='color:green;'>ok</b>")
        elif delay < 180:
            return mark_safe("<b style='color:orange;'>delayed</b>")
        else:
            return mark_safe("<b style='color:red;'>stale</b>")


# ============================================================
# ✅ METER REGISTER
# ============================================================

@admin.register(MeterRegister)
class MeterRegisterAdmin(admin.ModelAdmin):
    list_display = ("id", "meter", "obis_code", "description")
    search_fields = ("meter__serial_number", "obis_code", "description")
    raw_id_fields = ("meter",)



# ============================================================
# ✅ INTERVAL READING (RAW DATA)
# ============================================================

@admin.register(IntervalReading)
class IntervalReadingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "meter",
        "ts_start",
        "obis_code",
        "value",
        "unit",
        "source",
    )
    list_filter = ("tenant", "obis_code", "unit", "source")
    search_fields = ("meter__serial_number", "obis_code")
    raw_id_fields = ("tenant", "meter")
    ordering = ("-ts_start",)


# ============================================================
# ✅ AGGREGATED READING (INTERMEDIATE)
# ============================================================

@admin.register(AggregatedReading)
class AggregatedReadingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "meter",
        "period_start",
        "obis_code",
        "value",
    )
    list_filter = ("tenant", "obis_code")
    search_fields = ("meter__serial_number", "obis_code")
    raw_id_fields = ("tenant", "meter")
    ordering = ("-period_start",)


# ============================================================
# 💎 BALANCE SLOT (DEIN GOLD!)
# ============================================================

@admin.register(BalanceSlot)
class BalanceSlotAdmin(admin.ModelAdmin):

    list_display = (
        "period_start",
        "meter",
        "consumption_kwh",
        "generation_kwh",
        "self_consumption_kwh",
        "grid_import_kwh",
        "grid_export_kwh",
    )

    list_filter = (
        "meter",
    )

    search_fields = (
        "meter__serial_number",
    )

    raw_id_fields = ("meter", "tenant")

    ordering = ("-period_start",)

    date_hierarchy = "period_start"

    # ✅ Optional: schnelle Übersicht
    def has_add_permission(self, request):
        return False  # Balance wird nur berechnet

    def has_delete_permission(self, request, obj=None):
        return False


from accounts.models import TenantMembership


class TenantMembershipInline(admin.TabularInline):
    model = TenantMembership
    extra = 1
    raw_id_fields = ("user",)
    fields = ("user", "role", "is_active", "created_at")
    readonly_fields = ("created_at",)


# ============================================================
# ✅TENANT ANLEGEN
# ============================================================

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_public", "primary_color")
    search_fields = ("name", "slug")
    fieldsets = (
        ("Stammdaten", {"fields": ("name", "slug", "is_public")}),
        ("Geokoordinaten", {"fields": ("latitude", "longitude")}),
        ("Theme & Farben", {"fields": ("primary_color", "secondary_color", "button_color")}),
    )
    inlines = [TenantMembershipInline]


from core.models import MemberEnergyProfile


@admin.register(MemberEnergyProfile)
class MemberEnergyProfileAdmin(admin.ModelAdmin):
    list_display = ("member", "energy_role", "grid_connection_id", "created_at")
    list_filter = ("energy_role",)
    search_fields = ("member__user__email", "grid_connection_id")
    raw_id_fields = ("member",)




