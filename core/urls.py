from django.urls import path
from .api_theming import TenantThemingView, PublicTenantDomainLookupView

urlpatterns = [
    path("tenant/theming/", TenantThemingView.as_view(), name="tenant-theming"),
    path("tenant/by-domain/", PublicTenantDomainLookupView.as_view(), name="tenant-by-domain"),
]
