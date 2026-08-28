#####################
# helpcenter/urls.py
#####################
from django.urls import path, include

urlpatterns = [
    path("", include("support_desk.api.urls_help")),
]
