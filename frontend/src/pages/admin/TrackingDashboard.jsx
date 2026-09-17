/*
# src/pages/admin/TrackingDashboard.jsx
*/

import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import ReactECharts from "echarts-for-react";
import { apiFetch } from "../../api/client";
import AdminPageHeader from "../../components/admin/AdminPageHeader";

function formatStats(stats) {
    const map = {};
    stats.forEach((s) => {
        map[s.event] = s.count;
    });
    return map;
}

export default function TrackingDashboard() {
    const { t } = useTranslation();
    const { data, isLoading } = useQuery({
        queryKey: ["tracking"],
        queryFn: () => apiFetch("/api/tracking/stats/"),
        staleTime: 30_000,
    });

    const stats = data?.stats || [];
    const map = formatStats(stats);

    const funnel = [
        { key: "landing_view", label: t("tracking.landing_view", "Landing Page Aufruf"), icon: "🌐" },
        { key: "signup_click", label: t("tracking.signup_click", "Registrierung geklickt"), icon: "📝" },
        { key: "magic_link_requested", label: t("tracking.magic_link_requested", "Magic-Link angefordert"), icon: "✉️" },
        { key: "email_open", label: t("tracking.email_open", "E-Mail geöffnet"), icon: "📬" },
        { key: "magic_link_click", label: t("tracking.magic_link_click", "Link angeklickt"), icon: "🖱️" },
        { key: "magic_login_success", label: t("tracking.magic_login_success", "Erfolgreich eingeloggt"), icon: "🔑" },
        { key: "dashboard_open", label: t("tracking.dashboard_open", "Dashboard geöffnet"), icon: "🏠" },
    ];

    const chartOption = useMemo(() => {
        const dailyList = data?.daily || [];
        if (!dailyList || dailyList.length === 0) return null;
        return {
            tooltip: {
                trigger: "axis",
                backgroundColor: "rgba(255, 255, 255, 0.95)",
                borderColor: "#e2e8f0",
                textStyle: { color: "#1e293b", fontSize: 12 },
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
                data: dailyList.map((d) => d.date),
                axisLabel: { color: "#94a3b8", fontSize: 11 },
                axisLine: { lineStyle: { color: "#cbd5e1" } },
            },
            yAxis: {
                type: "value",
                axisLabel: { color: "#94a3b8", fontSize: 11 },
                splitLine: { lineStyle: { color: "#f1f5f9", type: "dashed" } },
            },
            series: [
                {
                    name: "Events",
                    type: "line",
                    smooth: true,
                    showSymbol: true,
                    symbolSize: 6,
                    itemStyle: { color: "#6366f1" },
                    lineStyle: { width: 2.5, color: "#6366f1" },
                    areaStyle: {
                        color: {
                            type: "linear",
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: "rgba(99, 102, 241, 0.35)" },
                                { offset: 1, color: "rgba(99, 102, 241, 0.0)" },
                            ],
                        },
                    },
                    data: dailyList.map((d) => d.count),
                },
            ],
        };
    }, [data]);

    if (isLoading) {
        return (
            <div className="p-8 max-w-7xl mx-auto flex items-center justify-center text-slate-400 text-sm animate-pulse">
                {t("common.loading", "Lade Tracking- und Eventdaten…")}
            </div>
        );
    }

    const totalEventsCount = stats.reduce((acc, curr) => acc + (curr.count || 0), 0);

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* Unified SaaS-Enterprise Header */}
            <AdminPageHeader
                icon="📈"
                iconBg="bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 border-purple-100 dark:border-purple-900/50"
                title={t("tracking.title", "Event-Tracking & Telemetrie-Analytics")}
                subtitle={t("tracking.subtitle", "Detaillierte Erfassung von Nutzerinteraktionen, Feature-Nutzung und Registrierungstrichter.")}
                badge={`${totalEventsCount.toLocaleString()} ${t("tracking.total_events", "Gesamt-Events")}`}
                badgeColor="purple"
                actions={
                    <>
                        <Link
                            to="/app/admin/dashboard"
                            className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-semibold text-xs rounded-xl transition flex items-center gap-1.5"
                        >
                            <span>📊</span> {t("admin.title", "Admin Dashboard")}
                        </Link>
                        <a
                            href="/admin/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-3.5 py-1.5 bg-slate-900 hover:bg-black dark:bg-indigo-600 dark:hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl transition flex items-center gap-1.5 shadow-xs"
                        >
                            <span>⚙️</span> Django Admin <span>↗</span>
                        </a>
                    </>
                }
            />

            {/* 7-Tage Timeline Chart */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <span>📅</span> {t("tracking.chart_title", "Event-Aktivität (Letzte 7 Tage)")}
                    </h2>
                    <span className="text-xs text-slate-400 font-mono">{t("tracking.chart_subtitle", "Tägliche Interaktionen")}</span>
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
                            {t("tracking.no_data_7_days", "Keine Daten für die letzten 7 Tage")}
                        </div>
                    )}
                </div>
            </div>

            {/* Grid: Conversion Funnel & Top Events */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Conversion Funnel */}
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs space-y-4">
                    <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                        <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <span>🎯</span> {t("tracking.funnel_title", "User Funnel Schritte")}
                        </h2>
                        <span className="text-xs text-slate-400">Step-by-Step Conversion</span>
                    </div>

                    <div className="space-y-4 pt-1">
                        {funnel.map((item, i) => {
                            const value = map[item.key] || 0;
                            const prev = i === 0 ? value : (map[funnel[i - 1].key] || 1);
                            const percent = i === 0 ? 100 : Math.min(100, Math.round((value / Math.max(prev, 1)) * 100));

                            return (
                                <div key={item.key} className="space-y-1.5">
                                    <div className="flex justify-between text-xs font-semibold text-slate-700 dark:text-slate-300">
                                        <span className="flex items-center gap-1.5">
                                            <span>{item.icon}</span> {item.label}
                                        </span>
                                        <span className="font-mono text-slate-500 dark:text-slate-400">
                                            {value} <span className="text-indigo-600 dark:text-indigo-400 font-bold">({percent}%)</span>
                                        </span>
                                    </div>

                                    <div className="h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full transition-all duration-500"
                                            style={{ width: `${percent}%` }}
                                        />
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Top Events Table */}
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs space-y-4">
                    <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                        <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <span>🔥</span> {t("tracking.top_events_title", "Häufigste Event-Typen")}
                        </h2>
                        <span className="text-xs text-slate-400">Top 10 Events</span>
                    </div>

                    <div className="divide-y divide-slate-100 dark:divide-slate-800">
                        {stats
                            .sort((a, b) => b.count - a.count)
                            .slice(0, 10)
                            .map((item, idx) => (
                                <div
                                    key={item.event}
                                    className="flex items-center justify-between py-2.5 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/50 px-2 rounded-lg transition"
                                >
                                    <div className="flex items-center gap-2 truncate">
                                        <span className="font-bold text-slate-400 font-mono w-4">#{idx + 1}</span>
                                        <span className="font-mono text-slate-800 dark:text-slate-200 truncate">{item.event}</span>
                                    </div>
                                    <span className="font-bold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/60 px-2.5 py-0.5 rounded-full font-mono text-[11px] border border-indigo-100 dark:border-indigo-900/50">
                                        {item.count}
                                    </span>
                                </div>
                            ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
