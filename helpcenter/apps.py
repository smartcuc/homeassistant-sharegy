# helpcenter/apps.py

from django.apps import AppConfig


class HelpcenterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "helpcenter"
    verbose_name = "Hilfesystem & Wissensportal"

