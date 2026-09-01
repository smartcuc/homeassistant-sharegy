from django.contrib import admin
from .models import UserPreference


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "key", "updated_at")
    list_filter = ("key",)
    search_fields = ("user__email", "key")
    raw_id_fields = ("user",)
    readonly_fields = ("updated_at",)
