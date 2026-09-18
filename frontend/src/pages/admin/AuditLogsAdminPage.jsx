import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../api/client";
import {
  ShieldCheck,
  ShieldAlert,
  Search,
  Download,
  Filter,
  RefreshCw,
  FileText,
  Clock,
  User,
  Activity,
  AlertTriangle,
  Info,
  CheckCircle2,
  X,
  ExternalLink,
  Code,
  Zap,
} from "lucide-react";
import AdminPageHeader from "../../components/admin/AdminPageHeader";
import KpiCard from "../../components/admin/KpiCard";
import useModalDismiss from "../../hooks/useModalDismiss";

export default function AuditLogsAdminPage() {
  const { t } = useTranslation();
  const [severityFilter, setSeverityFilter] = useState("all");
  const [actionFilter, setActionFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedLog, setSelectedLog] = useState(null);

  useModalDismiss(Boolean(selectedLog), () => setSelectedLog(null));

  // 1. Fetch Audit Logs
  const logsQuery = useQuery({
    queryKey: ["admin-audit-logs", severityFilter, actionFilter, searchQuery],
    queryFn: async () => {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      const params = new URLSearchParams();
      if (severityFilter !== "all") params.append("severity", severityFilter);
      if (actionFilter !== "all") params.append("action", actionFilter);
      if (searchQuery.trim()) params.append("search", searchQuery.trim());

      return apiFetch(`/api/core/audit-logs/?${params.toString()}`, {
        headers: { Authorization: token ? `Bearer ${token}` : "" },
      });
    },
    refetchInterval: 20000,
  });

  // 2. Fetch Audit Stats
  const statsQuery = useQuery({
    queryKey: ["admin-audit-stats"],
    queryFn: async () => {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      return apiFetch("/api/core/audit-logs/stats/", {
        headers: { Authorization: token ? `Bearer ${token}` : "" },
      });
    },
    refetchInterval: 30000,
  });

  const logs = logsQuery.data?.results || [];
  const stats = statsQuery.data || {};

  const handleExportCsv = () => {
    const token = localStorage.getItem("token") || sessionStorage.getItem("token");
    window.open(`/api/core/audit-logs/export/?auth=${encodeURIComponent(token || "")}`, "_blank");
  };

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case "critical":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-black bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-500/20">
            <ShieldAlert className="w-3 h-3" /> Kritisch
          </span>
        );
      case "security":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-black bg-purple-500/10 text-purple-700 dark:text-purple-400 border border-purple-500/20">
            <ShieldCheck className="w-3 h-3" /> Sicherheit
          </span>
        );
      case "warning":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-black bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-3 h-3" /> Warnung
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
            <Info className="w-3 h-3" /> Info
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 animate-fade-in p-6 max-w-7xl mx-auto">
      {/* SaaS Enterprise Standard Header */}
      <AdminPageHeader
        icon="🔒"
        title="Enterprise Audit Trail & Revisionsprotokoll"
        subtitle="Vollständige, manipulationssichere Aufzeichnung aller administrativen, steuerungs- und sicherheitsrelevanten Aktionen (ISO 27001 / SOC 2 & EnWG § 14a Nachweisführung)."
        badge="Revisionssicher & DSGVO-Konform"
        badgeColor="emerald"
        actions={
          <button
            type="button"
            onClick={handleExportCsv}
            className="px-4 py-2 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-100 rounded-xl text-xs font-bold border border-slate-200 dark:border-slate-700 shadow-xs flex items-center gap-1.5 transition cursor-pointer"
          >
            <Download className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span>CSV-Export (Audit Report)</span>
          </button>
        }
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          icon="🛡️"
          title="Gesamt-Ereignisse"
          value={stats.total_events ?? logs.length}
          subtitle="Protokollierte Aktionen"
          tone="emerald"
        />
        <KpiCard
          icon="🚨"
          title="Sicherheits- & Kritisch"
          value={(stats.security_events || 0) + (stats.critical_events || 0)}
          subtitle="KRITIS- & BNetzA-Relevanz"
          tone="purple"
        />
        <KpiCard
          icon="⚡"
          title="§ 14a & VPP Aktionen"
          value={(stats.dimming_events || 0) + (stats.dispatch_events || 0)}
          subtitle="Dimm- & Dispatch-Impulse"
          tone="amber"
        />
        <KpiCard
          icon="⏱️"
          title="Letzter Prüfnachweis"
          value={stats.last_audit_timestamp ? new Date(stats.last_audit_timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "Live"}
          subtitle="Audit-Status: Validiert"
          tone="blue"
        />
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        <div className="flex-1 relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Suchen nach Akteur (E-Mail), Ressource, IP-Adresse oder Aktions-Schlüssel..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-medium text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-emerald-500/30"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-500 dark:text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <span>Schweregrad:</span>
          </div>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-bold text-slate-800 dark:text-slate-200"
          >
            <option value="all">Alle Schweregrade</option>
            <option value="info">Info</option>
            <option value="warning">Warnung</option>
            <option value="security">Sicherheit</option>
            <option value="critical">Kritisch</option>
          </select>

          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-bold text-slate-800 dark:text-slate-200"
          >
            <option value="all">Alle Aktions-Typen</option>
            <option value="DIMMING_TRIGGER">⚡ § 14a Dimm-Befehl</option>
            <option value="DISPATCH_EXECUTE">🚀 VPP Dispatch</option>
            <option value="SECURITY_CONFIG">🔒 Sicherheitskonfiguration</option>
            <option value="EICHRECHT_VERIFY">⚖️ Eichrechtsprüfung</option>
            <option value="CREATE">➕ Ressourcenerstellung</option>
            <option value="UPDATE">✏️ Ressourcenänderung</option>
            <option value="DELETE">🗑️ Löschung</option>
          </select>

          <button
            type="button"
            onClick={() => logsQuery.refetch()}
            className="p-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-xl transition cursor-pointer"
            title="Aktualisieren"
          >
            <RefreshCw className={`w-4 h-4 ${logsQuery.isFetching ? "animate-spin text-emerald-600" : ""}`} />
          </button>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50/75 dark:bg-slate-950/75 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider">
                <th className="py-3.5 px-5">Zeitstempel (UTC)</th>
                <th className="py-3.5 px-5">Schweregrad</th>
                <th className="py-3.5 px-5">Aktion & Ressource</th>
                <th className="py-3.5 px-5">Akteur</th>
                <th className="py-3.5 px-5">IP-Adresse</th>
                <th className="py-3.5 px-5 text-right">Details & Diff</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-medium">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="py-12 text-center text-slate-400">
                    <ShieldCheck className="w-8 h-8 mx-auto mb-2 text-slate-300 dark:text-slate-600" />
                    Keine Audit-Ereignisse mit den gewählten Filtern gefunden.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr
                    key={log.id}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition cursor-pointer"
                    onClick={() => setSelectedLog(log)}
                  >
                    <td className="py-3.5 px-5 whitespace-nowrap text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                      {new Date(log.created_at).toLocaleString("de-DE", {
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                      })}
                    </td>
                    <td className="py-3.5 px-5 whitespace-nowrap">
                      {getSeverityBadge(log.severity)}
                    </td>
                    <td className="py-3.5 px-5">
                      <div className="font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                        <span>{log.action}</span>
                      </div>
                      <div className="text-[11px] text-slate-500 dark:text-slate-400">
                        {log.resource_type}: <strong className="text-slate-700 dark:text-slate-200">{log.resource_name || log.resource_id || "–"}</strong>
                      </div>
                    </td>
                    <td className="py-3.5 px-5 whitespace-nowrap">
                      <div className="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                        <User className="w-3.5 h-3.5 text-slate-400" />
                        <span>{log.actor_email}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-5 whitespace-nowrap font-mono text-[11px] text-slate-500">
                      {log.ip_address}
                    </td>
                    <td className="py-3.5 px-5 text-right whitespace-nowrap">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedLog(log);
                        }}
                        className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg text-xs font-bold transition inline-flex items-center gap-1 cursor-pointer"
                      >
                        <Code className="w-3.5 h-3.5 text-indigo-500" />
                        <span>Diff</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Audit Detail & Diff Modal */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-fade-in">
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl max-w-2xl w-full p-6 space-y-5 overflow-hidden">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xl">🔒</span>
                  <h3 className="text-lg font-black text-slate-900 dark:text-white">
                    Audit-Eintrag Details
                  </h3>
                  {getSeverityBadge(selectedLog.severity)}
                </div>
                <p className="text-xs text-slate-500 font-mono">
                  Audit-ID: {selectedLog.id}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedLog(null)}
                className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-white rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs bg-slate-50 dark:bg-slate-950 p-3.5 rounded-2xl border border-slate-200/80 dark:border-slate-800">
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Aktion & Ressource</span>
                <strong className="text-slate-900 dark:text-white">{selectedLog.action}</strong> ({selectedLog.resource_type})
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Akteur & IP</span>
                <strong className="text-slate-900 dark:text-white">{selectedLog.actor_email}</strong> ({selectedLog.ip_address})
              </div>
              <div className="col-span-2">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Ressourcen-ID & Name</span>
                <span className="text-slate-800 dark:text-slate-200 font-mono">{selectedLog.resource_id} • {selectedLog.resource_name}</span>
              </div>
            </div>

            {/* Change Diff JSON */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-slate-700 dark:text-slate-300">
                <span className="flex items-center gap-1.5">
                  <Code className="w-4 h-4 text-indigo-500" />
                  <span>Protokollierte Änderungen (Diff Payload):</span>
                </span>
              </div>
              <pre className="p-4 bg-slate-950 text-emerald-400 rounded-2xl text-[11px] font-mono overflow-x-auto max-h-56 border border-slate-800">
                {JSON.stringify(selectedLog.changes, null, 2)}
              </pre>
            </div>

            {/* Metadata JSON */}
            {selectedLog.metadata && Object.keys(selectedLog.metadata).length > 0 && (
              <div className="space-y-2">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                  Zusätzlicher Audit-Kontext & Metadaten:
                </span>
                <pre className="p-3 bg-slate-950 text-sky-400 rounded-2xl text-[11px] font-mono overflow-x-auto max-h-36 border border-slate-800">
                  {JSON.stringify(selectedLog.metadata, null, 2)}
                </pre>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                type="button"
                onClick={() => setSelectedLog(null)}
                className="px-5 py-2.5 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl text-xs font-bold hover:bg-slate-800 dark:hover:bg-slate-100 transition cursor-pointer"
              >
                Schließen
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
