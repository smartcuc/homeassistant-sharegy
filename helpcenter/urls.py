######################
# helpcenter/urls.py
######################

from django.urls import path, include

urlpatterns = [
    path("", include("helpcenter.api.urls")),
]

