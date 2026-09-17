import { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import ReactECharts from "echarts-for-react";
import { KpiCard } from "../../components/admin/KpiCard";
import { apiFetch } from "../../api/client";
import AdminPageHeader from "../../components/admin/AdminPageHeader";

export default function AdminDashboard() {
    const { t } = useTranslation();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    const isDark = typeof document !== "undefined" && document.documentElement.classList.contains("dark");

    function fetchStats() {
        setLoading(true);
        apiFetch("/api/stats/dashboard/")
            .then((d) => {
                setData(d);
                setLoading(false);
            })
            .catch((err) => {
                console.error(err);
                setLoading(false);
            });
    }

    useEffect(() => {
        fetchStats();
    }, []);

    const chartOption = useMemo(() => {
        if (!data || !data.funnel) return null;
        const funnel = [
            { name: t("admin.funnel_total", "Total Links"), value: data.funnel.total || 0, color: "#6366f1" },
            { name: t("admin.funnel_opened", "Opened"), value: data.funnel.opened || 0, color: "#3b82f6" },
            { name: t("admin.funnel_clicked", "Clicked"), value: data.funnel.clicked || 0, color: "#10b981" },
            { name: t("admin.funnel_logins", "Logins"), value: data.funnel.used || 0, color: "#8b5cf6" },
        ];

        return {
            tooltip: {
                trigger: "axis",
                axisPointer: { type: "shadow" },
                backgroundColor: isDark ? "#0f172a" : "rgba(255, 255, 255, 0.95)",
                borderColor: isDark ? "#334155" : "#e2e8f0",
                textStyle: { color: isDark ? "#f8fafc" : "#1e293b", fontSize: 12 },
            },
            grid: {
                left: "3%",
                right: "3%",
                bottom: "5%",
                top: "10%",
                containLabel: true,
            },
            xAxis: {
                type: "category",
                data: funnel.map((f) => f.name),
                axisLabel: { color: isDark ? "#94a3b8" : "#64748b", fontSize: 12, fontWeight: "bold" },
                axisLine: { lineStyle: { color: isDark ? "#334155" : "#cbd5e1" } },
            },
            yAxis: {
                type: "value",
                axisLabel: { color: isDark ? "#94a3b8" : "#94a3b8", fontSize: 11 },
                splitLine: { lineStyle: { color: isDark ? "#1e293b" : "#f1f5f9", type: "dashed" } },
            },
            series: [
                {
                    type: "bar",
                    data: funnel.map((f) => ({
                        value: f.value,
                        itemStyle: { color: f.color, borderRadius: [6, 6, 0, 0] },
                    })),
                    barWidth: "40%",
                },
            ],
        };
    }, [data, t, isDark]);

    const interfaceChartOption = useMemo(() => {
        if (!data || !data.interface_stats || !data.interface_stats.interfaces) return null;
        const ifaces = data.interface_stats.interfaces;
        const colorPalette = ["#0284c7", "#ea580c", "#f59e0b", "#10b981", "#8b5cf6"];

        const filtered = ifaces.filter(i => (i.total_configured > 0 || i.active_24h > 0));
        const chartData = filtered.length > 0 ? filtered : ifaces;

        return {
            tooltip: {
                trigger: "item",
                formatter: "{b}: {c} Haushalte ({d}%)",
                backgroundColor: isDark ? "#0f172a" : "rgba(255, 255, 255, 0.95)",
                borderColor: isDark ? "#334155" : "#e2e8f0",
                textStyle: { color: isDark ? "#f8fafc" : "#1e293b", fontSize: 12 },
            },
            legend: {
                bottom: "0%",
                left: "center",
                textStyle: { color: isDark ? "#94a3b8" : "#64748b", fontSize: 11 },
            },
            series: [
                {
                    name: "Schnittstellen",
                    type: "pie",
                    radius: ["42%", "72%"],
                    avoidLabelOverlap: false,
                    itemStyle: {
                        borderRadius: 8,
                        borderColor: isDark ? "#0f172a" : "#fff",
                        borderWidth: 2,
                    },
                    label: {
                        show: false,
                    },
                    data: chartData.map((item, idx) => ({
                        value: item.total_configured || item.active_24h || 0,
                        name: item.name,
                        itemStyle: { color: colorPalette[idx % colorPalette.length] },
                    })),
                },
            ],
        };
    }, [data, t, isDark]);

    if (loading && !data) {
        return (
            <div className="p-12 max-w-7xl mx-auto flex items-center justify-center text-slate-400 text-sm animate-pulse">
                {t("common.loading", "Lade Admin-Dashboard…")}
            </div>
        );
    }

    const funnelData = data?.funnel || { total: 0, opened: 0, clicked: 0, used: 0 };
    const ifaceStats = data?.interface_stats || { interfaces: [], total_homes: 0, total_telemetry_homes: 0 };

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6 animate-fade-in">
            {/* UNIFIED ADMIN HEADER */}
            <AdminPageHeader
                icon="🛡️"
                iconBg="bg-indigo-500/10 border-indigo-500/20 text-indigo-600 dark:text-indigo-400"
                title={t("admin.title", "Admin & Conversion Center")}
                subtitle={t("admin.subtitle", "Übersicht über Nutzer-Onboarding, Magic-Link-Konvertierung, Live-Aktivitäten und Systemstatus.")}
                badge={t("admin.badge_staff", "Staff Portal")}
                badgeColor="indigo"
                manualLink="/app/help/admin-communities-portfolio-guide"
                manualLabel={t("nav.manual", "Handbuch")}
                actions={
                    <>
                        <Link
                            to="/app/admin/tracking"
                            className="px-3.5 py-2 bg-indigo-50 dark:bg-indigo-950/40 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 font-bold text-xs rounded-xl border border-indigo-200 dark:border-indigo-800/80 transition flex items-center gap-1.5 shadow-xs"
                        >
                            <span>📈</span>
                            <span>{t("admin.event_tracking", "Event-Tracking")}</span>
                        </Link>
                        <button
                            onClick={fetchStats}
                            className="p-2.5 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 rounded-xl transition cursor-pointer shadow-xs"
                            title={t("common.refresh", "Aktualisieren")}
                        >
                            <span className={loading ? "animate-spin inline-block text-xs" : "text-xs"}>🔄</span>
                        </button>
                        <a
                            href="/admin/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-3.5 py-2 bg-slate-900 dark:bg-slate-800 hover:bg-black dark:hover:bg-slate-700 text-white font-bold text-xs rounded-xl transition flex items-center gap-1.5 shadow-xs"
                        >
                            <span>⚙️</span>
                            <span>Django Admin</span>
                            <span className="text-[10px]">↗</span>
                        </a>
                    </>
                }
            />

            {/* KPI Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <KpiCard title={t("admin.kpi_generated_links", "🔗 Generierte Links")} value={funnelData.total} icon="🔗" />
                <KpiCard title={t("admin.kpi_emails_opened", "📬 E-Mail Geöffnet")} value={funnelData.opened} icon="📬" />
                <KpiCard title={t("admin.kpi_links_clicked", "🖱️ Link Geklickt")} value={funnelData.clicked} icon="🖱️" />
                <KpiCard title={t("admin.kpi_logins_success", "✅ Erfolgreiche Logins")} value={funnelData.used} icon="✅" />
            </div>

            {/* INTERFACE & ADAPTER ECOSYSTEM ANALYTICS */}
            <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-4">
                    <div>
                        <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <span>📡</span> {t("admin.interface_analytics_title", "Schnittstellen & Adapter-Nutzung (Ecosystem Analytics)")}
                        </h2>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            {t("admin.interface_analytics_sub", "Welche Schnittstellen und Zentralen (Home Assistant, ioBroker, Shelly, Cloud-WR) werden von aktiven Nutzern verwendet?")}
                        </p>
                    </div>
                    <span className="text-xs font-mono px-3 py-1 bg-slate-100 dark:bg-slate-800 rounded-full text-slate-700 dark:text-slate-300 font-semibold self-start sm:self-auto border border-slate-200 dark:border-slate-700">
                        {ifaceStats.total_telemetry_homes} / {ifaceStats.total_homes} {t("admin.homes_with_telemetry", "Haushalte aktiv")}
                    </span>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
                    {/* Donut Chart */}
                    <div className="lg:col-span-5 h-64 w-full">
                        {interfaceChartOption ? (
                            <ReactECharts
                                option={interfaceChartOption}
                                style={{ height: "100%", width: "100%" }}
                                notMerge={true}
                                lazyUpdate={true}
                            />
                        ) : (
                            <div className="h-full flex items-center justify-center text-slate-400 text-xs">
                                {t("admin.no_interface_data", "Keine Schnittstellendaten")}
                            </div>
                        )}
                    </div>

                    {/* Table / Breakdown */}
                    <div className="lg:col-span-7 space-y-3">
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-xs">
                                <thead>
                                    <tr className="border-b border-slate-100 dark:border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                                        <th className="pb-2 font-medium">{t("admin.interface_name", "Schnittstelle")}</th>
                                        <th className="pb-2 text-center font-medium">{t("admin.active_24h", "Aktiv (24h)")}</th>
                                        <th className="pb-2 text-center font-medium">{t("admin.active_7d", "Aktiv (7d)")}</th>
                                        <th className="pb-2 text-right font-medium">{t("admin.share", "Anteil")}</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-50 dark:divide-slate-800">
                                    {ifaceStats.interfaces?.map((item) => (
                                        <tr key={item.key} className="hover:bg-slate-50 dark:hover:bg-slate-800/60 transition">
                                            <td className="py-2.5 font-bold text-slate-900 dark:text-slate-200 flex items-center gap-2">
                                                <span>
                                                    {item.key === "homeassistant" ? "🏠" :
                                                     item.key === "iobroker" ? "🔵" :
                                                     item.key === "shelly_wss" ? "⚡" :
                                                     item.key === "cloud_inverter" ? "☁️" : "📡"}
                                                </span>
                                                <span>{item.name}</span>
                                            </td>
                                            <td className="py-2.5 text-center font-mono font-semibold text-emerald-600 dark:text-emerald-400">
                                                {item.active_24h}
                                            </td>
                                            <td className="py-2.5 text-center font-mono text-slate-600 dark:text-slate-400">
                                                {item.active_7d}
                                            </td>
                                            <td className="py-2.5 text-right font-mono font-bold text-indigo-600 dark:text-indigo-400">
                                                {item.percentage}%
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        {/* Strategic Insight Alert */}
                        <div className="p-3.5 bg-gradient-to-r from-indigo-50/70 via-sky-50/50 to-white dark:from-indigo-950/40 dark:via-slate-900 dark:to-slate-900 rounded-2xl border border-indigo-100/80 dark:border-indigo-900/60 flex items-start gap-2.5 text-xs text-indigo-950 dark:text-indigo-200">
                            <span className="text-base shrink-0">💡</span>
                            <div>
                                <span className="font-bold">{t("admin.strategic_insight_title", "Entwicklungs-Fokus & Roadmap:")} </span>
                                <span>{ifaceStats.recommendation || t("admin.strategic_insight_default", "Ermöglicht gezielte Optimierung für die populärsten Zentralen im Kundenkreis.")}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Conversion Chart */}
            <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <span>📊</span> {t("admin.onboarding_funnel", "Onboarding & Conversion Funnel")}
                    </h2>
                    <span className="text-xs text-slate-400 font-mono">Magic Link Conversion Rate</span>
                </div>

                <div className="h-72 w-full">
                    {chartOption ? (
                        <ReactECharts
                            option={chartOption}
                            style={{ height: "100%", width: "100%" }}
                            notMerge={true}
                            lazyUpdate={true}
                        />
                    ) : (
                        <div className="h-full flex items-center justify-center text-slate-400 text-xs">
                            {t("admin.no_funnel_data", "Keine Trichterdaten vorhanden")}
                        </div>
                    )}
                </div>
            </div>

            {/* LIVE LOGINS & ACTIVITY */}
            <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                    <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <span>⚡</span> {t("admin.live_user_activity", "Live Benutzer-Aktivität")}
                    </h2>
                    <span className="text-xs text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" /> Live Feed
                    </span>
                </div>

                <div className="space-y-2">
                    {data?.live_logins && data.live_logins.length > 0 ? (
                        data.live_logins.map((l, i) => (
                            <div
                                key={i}
                                className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl text-xs text-slate-700 dark:text-slate-300 transition"
                            >
                                <div className="flex items-center gap-2">
                                    <span>👤</span>
                                    <span className="font-semibold text-slate-900 dark:text-white">{l.user}</span>
                                    <span className="text-slate-400 dark:text-slate-500">{t("admin.logged_in_success", "hat sich erfolgreich eingeloggt")}</span>
                                </div>
                                <span className="font-mono text-slate-400 dark:text-slate-500">{l.timestamp}</span>
                            </div>
                        ))
                    ) : (
                        <div className="text-xs text-slate-400 dark:text-slate-500 py-4 text-center">
                            {t("admin.no_recent_logins", "Keine aktuellen Logins verzeichnet.")}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
