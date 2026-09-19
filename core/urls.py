from django.urls import path
from .api_theming import TenantThemingView, PublicTenantDomainLookupView
from .api_audit import AuditLogListView, AuditLogStatsView, AuditLogExportView

urlpatterns = [
    path("tenant/theming/", TenantThemingView.as_view(), name="tenant-theming"),
    path("tenant/by-domain/", PublicTenantDomainLookupView.as_view(), name="tenant-by-domain"),
    
    # 🔒 Enterprise Audit Trail & Revisionsprotokolle
    path("audit-logs/", AuditLogListView.as_view(), name="audit-logs-list"),
    path("audit-logs/stats/", AuditLogStatsView.as_view(), name="audit-logs-stats"),
    path("audit-logs/export/", AuditLogExportView.as_view(), name="audit-logs-export"),

    # 📁 Zentraler Dokumenten- & Export-Manager (Download Hub)
    path("documents/", __import__("core.api_documents", fromlist=["documents_catalog_view"]).documents_catalog_view, name="documents-catalog"),
    path("documents/generate/", __import__("core.api_documents", fromlist=["document_generate_view"]).document_generate_view, name="documents-generate"),
]

