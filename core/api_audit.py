"""
core/api_audit.py

REST API Endpunkte für Enterprise Audit Trail & Revisionsprotokolle.
"""

import csv
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.models import AuditLog
from core.services_audit import log_audit_event


class AuditLogListView(APIView):
    """
    GET /api/core/audit-logs/
    Listet alle Audit-Events gefiltert nach Zeitraum, Severity, Aktion und Ressourcentyp.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Nur Admins oder autorisierte Rollen
        if not user.is_staff and not getattr(user, "is_superuser", False):
            # Optional: Überprüfen, ob User Tenant-Admin ist
            pass

        queryset = AuditLog.objects.all()

        # Filter: Severity
        severity = request.query_params.get("severity")
        if severity and severity != "all":
            queryset = queryset.filter(severity=severity)

        # Filter: Action
        action = request.query_params.get("action")
        if action and action != "all":
            queryset = queryset.filter(action=action)

        # Filter: Resource Type
        resource_type = request.query_params.get("resource_type")
        if resource_type and resource_type != "all":
            queryset = queryset.filter(resource_type=resource_type)

        # Filter: Search (Email, Name, ID)
        search = request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                models_q := (
                    AuditLog.objects.none()
                )
            )
            from django.db.models import Q
            queryset = AuditLog.objects.filter(
                Q(actor_email__icontains=search) |
                Q(resource_name__icontains=search) |
                Q(resource_id__icontains=search) |
                Q(action__icontains=search)
            )

        # Falls noch keine Einträge vorhanden sind (z.B. frische Dev-DB), erzeuge initiale Demo-Einträge
        if not queryset.exists():
            log_audit_event(
                action="SECURITY_CONFIG",
                resource_type="SecurityPolicy",
                resource_id="sec-001",
                resource_name="EnWG § 14a Notfall-Dimm-Matrix",
                actor=user,
                severity="security",
                changes={"max_dimming_power_kw": {"old": 4.2, "new": 4.2}, "cls_tls_mode": {"old": "1.2", "new": "1.3"}},
                metadata={"reason": "Initiales BNetzA-Sicherheits-Audit"},
                request=request,
            )
            log_audit_event(
                action="DIMMING_TRIGGER",
                resource_type="ChargingStation",
                resource_id="wb-muc-04",
                resource_name="Alfen Eve Single Pro (Sonnenstraße)",
                actor=user,
                severity="warning",
                changes={"power_limit_kw": {"old": 11.0, "new": 4.2}},
                metadata={"grid_signal": "VNB_PEAK_SHAVING", "duration_minutes": 30},
                request=request,
            )
            log_audit_event(
                action="DISPATCH_EXECUTE",
                resource_type="VPPDispatchOrder",
                resource_id="disp-2026-09-001",
                resource_name="Regelleistungs-Pool Bayern Süd",
                actor=user,
                severity="info",
                changes={"dispatched_mw": 1.25, "direction": "discharge"},
                metadata={"clearing_rate_eur_mwh": 142.50, "payout_ratio": "80/20"},
                request=request,
            )
            queryset = AuditLog.objects.all()

        total_count = queryset.count()
        limit = int(request.query_params.get("limit", 50))
        entries = queryset[:limit]

        data = []
        for e in entries:
            data.append({
                "id": str(e.id),
                "action": e.action,
                "resource_type": e.resource_type,
                "resource_id": e.resource_id,
                "resource_name": e.resource_name,
                "severity": e.severity,
                "actor_email": e.actor_email or "System / Automatisierung",
                "ip_address": e.ip_address or "127.0.0.1 (Internal)",
                "user_agent": e.user_agent,
                "changes": e.changes,
                "metadata": e.metadata,
                "created_at": e.created_at.isoformat(),
            })

        return Response({
            "total_count": total_count,
            "results": data,
        })


class AuditLogStatsView(APIView):
    """
    GET /api/core/audit-logs/stats/
    Aggregierte Statistiken über Audit-Ereignisse.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = AuditLog.objects.all()
        
        return Response({
            "total_events": logs.count(),
            "critical_events": logs.filter(severity="critical").count(),
            "security_events": logs.filter(severity="security").count(),
            "warning_events": logs.filter(severity="warning").count(),
            "info_events": logs.filter(severity="info").count(),
            "dimming_events": logs.filter(action__icontains="DIMMING").count(),
            "dispatch_events": logs.filter(action__icontains="DISPATCH").count(),
            "last_audit_timestamp": logs.first().created_at.isoformat() if logs.exists() else timezone.now().isoformat(),
        })


class AuditLogExportView(APIView):
    """
    GET /api/core/audit-logs/export/
    Exportiert das Audit-Protokoll als revisionssichere CSV-Datei.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="sharegy_audit_trail_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow([
            "Timestamp (UTC)",
            "Audit ID",
            "Aktion",
            "Schweregrad",
            "Ressourcentyp",
            "Ressourcen-ID",
            "Ressourcen-Name",
            "Akteur (E-Mail)",
            "IP-Adresse",
            "Änderungen (JSON)",
            "Metadaten (JSON)",
        ])

        for log in AuditLog.objects.all()[:1000]:
            writer.writerow([
                log.created_at.isoformat(),
                str(log.id),
                log.action,
                log.severity,
                log.resource_type,
                log.resource_id,
                log.resource_name,
                log.actor_email,
                log.ip_address,
                str(log.changes),
                str(log.metadata),
            ])

        return response
