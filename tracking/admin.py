from django.contrib import admin
from .models import EventLog


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = (
        "id_short",
        "name",
        "user",
        "tenant",
        "context",
        "source",
        "ip",
        "created_at",
    )
    list_filter = ("context", "name", "tenant", "created_at")
    search_fields = ("name", "user__email", "tenant__name", "source", "ip")
    raw_id_fields = ("user", "tenant")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"

    def id_short(self, obj):
        return str(obj.id)[:8] + "..."
    id_short.short_description = "ID"
