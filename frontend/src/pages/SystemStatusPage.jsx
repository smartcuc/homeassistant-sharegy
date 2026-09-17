import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../api/client";
import Card from "../components/ui/Card";
import { useUser } from "../hooks/useUser";
import { trackEvent } from "../tracking/ga";

export default function SystemStatusPage() {
    const { t } = useTranslation();
    const { user } = useUser();
    const queryClient = useQueryClient();

    // Störungsmeldungs-Modal / Formular State
    const [showTicketModal, setShowTicketModal] = useState(false);
    const [ticketCategory, setTicketCategory] = useState("telemetry_stream");
    const [ticketSubject, setTicketSubject] = useState("");
    const [ticketDescription, setTicketDescription] = useState("");
    const [attachDiagnostics, setAttachDiagnostics] = useState(true);
    const [ticketResult, setTicketResult] = useState(null);

    // 1. Health Query (aktualisiert sich alle 15 Sekunden)
    const { data: healthData, isLoading, refetch, isFetching } = useQuery({
        queryKey: ["systemHealthStatus"],
        queryFn: () => apiFetch("/api/status/health/"),
        refetchInterval: 15000,
    });

    // 2. Ticket Erstellung Mutation
    const createTicketMutation = useMutation({
        mutationFn: (payload) =>
            apiFetch("/api/support/tickets/", {
                method: "POST",
                body: JSON.stringify(payload),
            }),
        onSuccess: (res) => {
            trackEvent("incident_reported", "support", ticketCategory);
            setTicketResult({
                type: "success",
                message: t("system_status.incident_submitted", { id: res.ticket_number || res.id?.slice(0, 8), defaultValue: `✅ Störungsmeldung erfolgreich übermittelt! Ticket-ID: #${res.ticket_number || res.id?.slice(0, 8)}` }),
            });
            setTicketSubject("");
            setTicketDescription("");
            queryClient.invalidateQueries(["alerts-list"]);
        },
        onError: (err) => {
            setTicketResult({
                type: "error",
                message: t("system_status.incident_error", { msg: err.message, defaultValue: `Fehler beim Senden der Störungsmeldung: ${err.message}` }),
            });
        },
    });

    const handleTicketSubmit = (e) => {
        e.preventDefault();
        if (!ticketSubject.trim() || !ticketDescription.trim()) return;

        let fullDesc = ticketDescription;
        if (attachDiagnostics && healthData) {
            fullDesc += `\n\n--- 🔍 Automatische System-Diagnose ---\n`;
            fullDesc += `• Timestamp: ${new Date().toISOString()}\n`;
            fullDesc += `• System-Status: ${healthData.status} (${healthData.status_label})\n`;
            fullDesc += `• DB-Latenz: ${healthData.services?.find(s => s.id === "database")?.latency_ms} ms\n`;
            fullDesc += `• Browser: ${navigator.userAgent}\n`;
        }

        createTicketMutation.mutate({
            subject: `[Systemstatus-Report] ${ticketSubject}`,
            description: fullDesc,
            category: ticketCategory,
            priority: "medium",
            project_key: "sharegy",
        });
    };

    const isAllOperational = healthData?.status === "operational";

    // Berechtigungs-Prüfung: Nur HEMS-Admins und Sharegy-Sysadmins
    const isSysAdmin = Boolean(user?.is_staff || user?.is_superuser || user?.is_platform_admin || user?.platform_role === "system_admin");
    const isHemsAdmin = Boolean(isSysAdmin || user?.memberships?.some((m) => ["admin", "user_admin", "owner"].includes(m.role)) || user?.is_admin || user?.usage_mode === "landlord");
    const canViewServerHardware = isSysAdmin || isHemsAdmin;

    const visibleServices = (healthData?.services || []).filter(
        (srv) => srv.id !== "server_resources" || canViewServerHardware
    );

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* TOP HEADER */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                        <span className="relative flex h-4 w-4">
                            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                                isAllOperational ? "bg-emerald-400" : "bg-amber-400"
                            }`}></span>
                            <span className={`relative inline-flex rounded-full h-4 w-4 ${
                                isAllOperational ? "bg-emerald-500" : "bg-amber-500"
                            }`}></span>
                        </span>
                        <span>{t("system_status.title", "Systemstatus & Live-Infrastruktur")}</span>
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">
                        {t("system_status.subtitle", "Echtzeit-Überwachung aller Dienste, Datenbanken, Ingest-Pipelines und APIs.")}
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => refetch()}
                        disabled={isFetching}
                        className="px-3.5 py-2 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 text-gray-700 dark:text-gray-200 text-xs font-bold rounded-xl hover:bg-gray-50 transition shadow-xs flex items-center gap-1.5 cursor-pointer"
                    >
                        <span className={isFetching ? "animate-spin" : ""}>🔄</span>
                        <span>{isFetching ? t("system_status.refreshing", "Aktualisiere...") : t("system_status.check_now", "Jetzt prüfen")}</span>
                    </button>
                    <button
                        onClick={() => setShowTicketModal(true)}
                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl transition shadow-xs flex items-center gap-2 cursor-pointer"
                    >
                        <span>🚨</span>
                        <span>{t("system_status.report_incident", "Störung melden")}</span>
                    </button>
                </div>
            </div>

            {/* HERO STATUS BANNER */}
            <div className={`p-6 rounded-3xl border shadow-md transition ${
                isAllOperational
                    ? "bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-100 dark:from-emerald-950/40 dark:to-slate-900 border-emerald-300 dark:border-emerald-800 text-emerald-950 dark:text-emerald-200"
                    : "bg-gradient-to-r from-amber-50 via-orange-50 to-amber-100 dark:from-amber-950/40 dark:to-slate-900 border-amber-300 dark:border-amber-800 text-amber-950 dark:text-amber-200"
            }`}>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center text-2xl shadow-inner ${
                            isAllOperational ? "bg-emerald-500 text-white" : "bg-amber-500 text-white"
                        }`}>
                            {isAllOperational ? "✓" : "!"}
                        </div>
                        <div>
                            <div className="text-xl font-extrabold flex items-center gap-2">
                                <span>{isAllOperational ? t("system_status.all_operational", "Alle Systeme operativ") : healthData?.status === "degraded" ? t("system_status.capacity_warning", "Kapazitäts-Warnung") : (healthData?.status_label || t("system_status.degraded", "Teilweise beeinträchtigt"))}</span>
                            </div>
                            <div className="text-xs opacity-80 mt-0.5">
                                {t("system_status.last_check", "Letzte Überprüfung:")} {healthData?.timestamp ? new Date(healthData.timestamp).toLocaleTimeString() : t("system_status.just_now", "vor wenigen Sekunden")} • {t("system_status.version", "Version:")} {healthData?.version || "3.2.0-beta"}
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-6 border-t md:border-t-0 md:border-l border-emerald-200 dark:border-emerald-800/60 pt-4 md:pt-0 md:pl-6">
                        <div>
                            <div className="text-[10px] uppercase font-bold tracking-wider opacity-70">{t("system_status.uptime_30d", "Uptime (30 Tage)")}</div>
                            <div className="text-2xl font-extrabold text-emerald-700 dark:text-emerald-400">
                                {healthData?.overall_uptime_pct || "99.98"} %
                            </div>
                        </div>
                        <div>
                            <div className="text-[10px] uppercase font-bold tracking-wider opacity-70">{t("system_status.active_devices", "Aktive Geräte")}</div>
                            <div className="text-2xl font-extrabold text-gray-900 dark:text-white">
                                {healthData?.metrics?.active_devices ?? 0}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* SERVICES GRID */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {visibleServices.map((srv) => {
                    const isSrvOk = srv.status === "operational";
                    return (
                        <div
                            key={srv.id}
                            className="p-5 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-2xl shadow-xs hover:border-indigo-200 transition flex flex-col justify-between"
                        >
                            <div>
                                <div className="flex items-center justify-between gap-2 mb-2">
                                    <h3 className="font-bold text-sm text-gray-900 dark:text-white truncate">
                                        {srv.name}
                                    </h3>
                                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase shrink-0 ${
                                        isSrvOk
                                            ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                                            : "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
                                    }`}>
                                        {isSrvOk ? t("system_status.online", "Online 🟢") : t("system_status.incident", "Störung 🔴")}
                                    </span>
                                </div>
                                <p className="text-xs text-gray-500 leading-relaxed min-h-[36px]">
                                    {srv.details}
                                </p>
                            </div>

                            <div className="mt-4 pt-3 border-t border-gray-100 dark:border-slate-800 flex items-center justify-between text-[11px] text-gray-400">
                                <span>{t("system_status.latency", "Latenz:")}</span>
                                <span className="font-mono font-bold text-gray-700 dark:text-gray-300">
                                    {srv.latency_ms} ms
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* 🖥️ HARDWARE- & KAPAZITÄTS-WÄCHTER (AUFRÜST-RADAR) */}
            {canViewServerHardware && healthData?.metrics?.server_hardware && (
                <div className="p-6 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-3xl shadow-xs space-y-4">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-gray-100 dark:border-slate-800">
                        <div className="flex items-center gap-2.5">
                            <span className="text-xl">🖥️</span>
                            <div>
                                <h2 className="text-sm font-bold text-gray-900 dark:text-white">
                                    {t("system_status.server_capacity_title", "Server-Kapazität & Hardware-Auslastung")}
                                </h2>
                                <p className="text-xs text-gray-500">
                                    {t("system_status.server_capacity_desc", "Proaktiver Aufrüst-Wächter zur Erkennung von Performance-Engpässen.")}
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-2">
                            <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${
                                healthData.metrics.server_hardware.upgrade_recommended
                                    ? "bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-300"
                                    : "bg-emerald-100 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-300"
                            }`}>
                                <span>{healthData.metrics.server_hardware.upgrade_recommended ? t("system_status.upgrade_recommended", "⚠️ Upgrade empfohlen") : t("system_status.buffer_sufficient", "✅ Ausreichend Puffer")}</span>
                            </span>
                        </div>
                    </div>

                    {/* HARDWARE PROGRESS BARS */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-1">
                        {/* CPU */}
                        <div className="space-y-2">
                            <div className="flex justify-between text-xs font-bold text-gray-700 dark:text-gray-300">
                                <span>{t("system_status.cpu_utilization", { count: healthData.metrics.server_hardware.cpu_count, defaultValue: `CPU-Auslastung (${healthData.metrics.server_hardware.cpu_count} vCPUs)` })}</span>
                                <span className="font-mono">{healthData.metrics.server_hardware.cpu_used_pct}%</span>
                            </div>
                            <div className="w-full h-2.5 bg-gray-100 dark:bg-slate-800 rounded-full overflow-hidden">
                                <div
                                    className={`h-full rounded-full transition-all duration-500 ${
                                        healthData.metrics.server_hardware.cpu_used_pct > 80
                                            ? "bg-rose-500"
                                            : healthData.metrics.server_hardware.cpu_used_pct > 60
                                            ? "bg-amber-500"
                                            : "bg-indigo-600"
                                    }`}
                                    style={{ width: `${Math.min(100, healthData.metrics.server_hardware.cpu_used_pct)}%` }}
                                ></div>
                            </div>
                            <div className="text-[11px] text-gray-400">
                                {t("system_status.load_avg", "Load Avg:")} <span className="font-mono">{healthData.metrics.server_hardware.load1}</span>
                            </div>
                        </div>

                        {/* RAM */}
                        <div className="space-y-2">
                            <div className="flex justify-between text-xs font-bold text-gray-700 dark:text-gray-300">
                                <span>{t("system_status.ram_memory", { gb: Math.round(healthData.metrics.server_hardware.ram_total_mb / 1024), defaultValue: `RAM-Speicher (${Math.round(healthData.metrics.server_hardware.ram_total_mb / 1024)} GB)` })}</span>
                                <span className="font-mono">{healthData.metrics.server_hardware.ram_used_pct}%</span>
                            </div>
                            <div className="w-full h-2.5 bg-gray-100 dark:bg-slate-800 rounded-full overflow-hidden">
                                <div
                                    className={`h-full rounded-full transition-all duration-500 ${
                                        healthData.metrics.server_hardware.ram_used_pct > 85
                                            ? "bg-rose-500"
                                            : healthData.metrics.server_hardware.ram_used_pct > 70
                                            ? "bg-amber-500"
                                            : "bg-emerald-500"
                                    }`}
                                    style={{ width: `${Math.min(100, healthData.metrics.server_hardware.ram_used_pct)}%` }}
                                ></div>
                            </div>
                            <div className="text-[11px] text-gray-400">
                                {t("system_status.free", "Frei:")} <span className="font-mono">{Math.round(healthData.metrics.server_hardware.ram_available_mb / 1024 * 10) / 10} GB</span>
                            </div>
                        </div>

                        {/* DISK */}
                        <div className="space-y-2">
                            <div className="flex justify-between text-xs font-bold text-gray-700 dark:text-gray-300">
                                <span>{t("system_status.ssd_storage", { gb: healthData.metrics.server_hardware.disk_total_gb, defaultValue: `SSD-Speicher (${healthData.metrics.server_hardware.disk_total_gb} GB)` })}</span>
                                <span className="font-mono">{healthData.metrics.server_hardware.disk_used_pct}%</span>
                            </div>
                            <div className="w-full h-2.5 bg-gray-100 dark:bg-slate-800 rounded-full overflow-hidden">
                                <div
                                    className={`h-full rounded-full transition-all duration-500 ${
                                        healthData.metrics.server_hardware.disk_used_pct > 85
                                            ? "bg-rose-500"
                                            : healthData.metrics.server_hardware.disk_used_pct > 75
                                            ? "bg-amber-500"
                                            : "bg-teal-500"
                                    }`}
                                    style={{ width: `${Math.min(100, healthData.metrics.server_hardware.disk_used_pct)}%` }}
                                ></div>
                            </div>
                            <div className="text-[11px] text-gray-400">
                                {t("system_status.free", "Frei:")} <span className="font-mono">{healthData.metrics.server_hardware.disk_free_gb} GB</span>
                            </div>
                        </div>
                    </div>

                    {/* ADVISOR BANNER */}
                    <div className="p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-gray-100 dark:border-slate-800 flex items-center justify-between text-xs text-gray-600 dark:text-gray-300">
                        <div className="flex items-center gap-2">
                            <span>💡</span>
                            <span><strong>{t("system_status.recommendation", "Empfehlung:")}</strong> {healthData.metrics.server_hardware.recommended_hardware}</span>
                        </div>
                        <span className="text-[11px] text-gray-400">
                            {t("system_status.active_db_conns", "Aktive DB-Verbindungen:")} <strong className="text-gray-700 dark:text-gray-200 font-mono">{healthData.metrics.server_hardware.db_active_connections}</strong>
                        </span>
                    </div>
                </div>
            )}

            {/* LIVE TELEMETRIE & PERFORMANCE KACHELN */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-950 flex items-center justify-center text-lg text-indigo-600">
                            ⚡
                        </div>
                        <div>
                            <div className="text-[11px] font-bold text-gray-400 uppercase">{t("system_status.ingest_throughput", "Ingest-Durchsatz")}</div>
                            <div className="text-lg font-bold text-gray-900 dark:text-white">
                                {healthData?.metrics?.ingest_throughput_msg_sec || 48.5} {t("system_status.msg_per_sec", "Msg / Sekunde")}
                            </div>
                        </div>
                    </div>
                </Card>

                <Card>
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950 flex items-center justify-center text-lg text-emerald-600">
                            ⏱️
                        </div>
                        <div>
                            <div className="text-[11px] font-bold text-gray-400 uppercase">{t("system_status.avg_api_latency", "Durchschn. API-Latenz")}</div>
                            <div className="text-lg font-bold text-gray-900 dark:text-white">
                                {healthData?.metrics?.avg_api_latency_ms || 12.4} ms
                            </div>
                        </div>
                    </div>
                </Card>

                <Card>
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-950 flex items-center justify-center text-lg text-amber-600">
                            🛡️
                        </div>
                        <div>
                            <div className="text-[11px] font-bold text-gray-400 uppercase">{t("system_status.incidents_30d", "Störungen (30 Tage)")}</div>
                            <div className="text-lg font-bold text-gray-900 dark:text-white">
                                {healthData?.metrics?.incident_count_30d ? `${healthData.metrics.incident_count_30d} Vorfälle` : t("system_status.no_open_incidents", "0 ungelöste Vorfälle")}
                            </div>
                        </div>
                    </div>
                </Card>
            </div>

            {/* MODAL: STÖRUNGSMELDUNG / TICKET ERSTELLUNG */}
            {showTicketModal && (
                <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4">
                    <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-3xl shadow-2xl max-w-lg w-full p-6 animate-in fade-in zoom-in-95">
                        <div className="flex items-center justify-between pb-4 border-b border-gray-100 dark:border-slate-800">
                            <div className="flex items-center gap-2">
                                <span className="text-xl">🚨</span>
                                <h3 className="font-bold text-base text-gray-900 dark:text-white">
                                    {t("system_status.modal_report_title", "Störung oder Problem melden")}
                                </h3>
                            </div>
                            <button
                                onClick={() => {
                                    setShowTicketModal(false);
                                    setTicketResult(null);
                                }}
                                className="text-gray-400 hover:text-gray-600 text-lg cursor-pointer"
                            >
                                ✕
                            </button>
                        </div>

                        {ticketResult ? (
                            <div className="py-6 space-y-4">
                                <div className={`p-4 rounded-2xl text-xs font-bold ${
                                    ticketResult.type === "success"
                                        ? "bg-emerald-50 text-emerald-900 border border-emerald-200"
                                        : "bg-rose-50 text-rose-900 border border-rose-200"
                                }`}>
                                    {ticketResult.message}
                                </div>
                                <button
                                    onClick={() => {
                                        setShowTicketModal(false);
                                        setTicketResult(null);
                                    }}
                                    className="w-full py-2.5 bg-gray-900 hover:bg-black text-white text-xs font-bold rounded-xl transition cursor-pointer"
                                >
                                    {t("common.close", "Schließen")}
                                </button>
                            </div>
                        ) : (
                            <form onSubmit={handleTicketSubmit} className="mt-4 space-y-4">
                                <div>
                                    <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">
                                        {t("system_status.incident_category", "Kategorie der Störung")}
                                    </label>
                                    <select
                                        value={ticketCategory}
                                        onChange={(e) => setTicketCategory(e.target.value)}
                                        className="w-full text-xs font-semibold p-2.5 rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-200"
                                    >
                                        <option value="telemetry_stream">{t("system_status.cat_telemetry_stream", "Live-Telemetrie & Zählerstände (Verzögerte Werte / Offline)")}</option>
                                        <option value="inverter_storage">{t("system_status.cat_inverter_storage", "Wechselrichter & Batteriespeicher (Modbus TCP / Cloud-API)")}</option>
                                        <option value="wallbox_ocpp">{t("system_status.cat_wallbox_ocpp", "Wallbox & E-Mobilität (OCPP-Gateway / Überschussladen)")}</option>
                                        <option value="market_tariffs">{t("system_status.cat_market_tariffs", "Dynamische Stromtarife & Börsenpreise (EPEX Spot Feed)")}</option>
                                        <option value="grid_curtailment">{t("system_status.cat_grid_curtailment", "§ 14a EnWG Dimmung & Netzsteuerung (CLS / SMGW)")}</option>
                                        <option value="energy_sharing">{t("system_status.cat_energy_sharing", "Energy Sharing & Quartiersbilanzierung (§ 42b EnWG)")}</option>
                                        <option value="platform_api">{t("system_status.cat_platform_api", "Plattform, Login & WebSockets (Allgemeine Störung)")}</option>
                                        <option value="other">{t("system_status.cat_other", "Sonstiges technisches Infrastruktur-Problem")}</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">
                                        {t("system_status.subject_label", "Kurzer Betreff")}
                                    </label>
                                    <input
                                        type="text"
                                        required
                                        placeholder={t("system_status.subject_placeholder", "z. B. Shelly Pro 3EM sendet seit 10 Minuten keine Werte")}
                                        value={ticketSubject}
                                        onChange={(e) => setTicketSubject(e.target.value)}
                                        className="w-full text-xs p-2.5 rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-indigo-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">
                                        {t("system_status.desc_label", "Problembeschreibung")}
                                    </label>
                                    <textarea
                                        required
                                        rows={4}
                                        placeholder={t("system_status.desc_placeholder", "Beschreibe kurz, was genau passiert ist und bei welchem Gerät/Menü...")}
                                        value={ticketDescription}
                                        onChange={(e) => setTicketDescription(e.target.value)}
                                        className="w-full text-xs p-2.5 rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-indigo-500"
                                    />
                                </div>

                                <div className="flex items-center gap-2">
                                    <input
                                        type="checkbox"
                                        id="attach_diag"
                                        checked={attachDiagnostics}
                                        onChange={(e) => setAttachDiagnostics(e.target.checked)}
                                        className="rounded text-indigo-600 cursor-pointer"
                                    />
                                    <label htmlFor="attach_diag" className="text-xs text-gray-500 cursor-pointer">
                                        {t("system_status.attach_diag", "Aktuelle System- & Latenzdiagnose automatisch anhängen")}
                                    </label>
                                </div>

                                <div className="flex items-center justify-end gap-2 pt-2">
                                    <button
                                        type="button"
                                        onClick={() => setShowTicketModal(false)}
                                        className="px-4 py-2 text-xs font-bold text-gray-500 hover:text-gray-700 transition cursor-pointer"
                                    >
                                        {t("common.cancel", "Abbrechen")}
                                    </button>
                                    <button
                                        type="submit"
                                        disabled={createTicketMutation.isLoading}
                                        className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl transition shadow-xs cursor-pointer"
                                    >
                                        {createTicketMutation.isLoading ? t("system_status.submitting_incident", "Sende Störungsmeldung...") : t("system_status.submit_incident", "Störung absenden →")}
                                    </button>
                                </div>
                            </form>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
