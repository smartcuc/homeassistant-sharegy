/*
# src/pages/admin/AdminDashboard.jsx
*/

import { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import ReactECharts from "echarts-for-react";
import { KpiCard } from "../../components/admin/KpiCard";

export default function AdminDashboard() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch("/api/stats/dashboard/", {
            credentials: "include",
        })
            .then((res) => res.json())
            .then((d) => {
                setData(d);
                setLoading(false);
            })
            .catch((err) => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    const chartOption = useMemo(() => {
        if (!data || !data.funnel) return null;
        const funnel = [
            { name: "Total Links", value: data.funnel.total || 0, color: "#6366f1" },
            { name: "Opened", value: data.funnel.opened || 0, color: "#3b82f6" },
            { name: "Clicked", value: data.funnel.clicked || 0, color: "#10b981" },
            { name: "Logins", value: data.funnel.used || 0, color: "#8b5cf6" },
        ];

        return {
            tooltip: {
                trigger: "axis",
                axisPointer: { type: "shadow" },
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
                data: funnel.map((f) => f.name),
                axisLabel: { color: "#64748b", fontSize: 12, fontWeight: "bold" },
                axisLine: { lineStyle: { color: "#cbd5e1" } },
            },
            yAxis: {
                type: "value",
                axisLabel: { color: "#94a3b8", fontSize: 11 },
                splitLine: { lineStyle: { color: "#f1f5f9", type: "dashed" } },
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
    }, [data]);

    if (loading) {
        return (
            <div className="p-8 max-w-7xl mx-auto flex items-center justify-center text-gray-400 text-sm animate-pulse">
                Lade Admin-Dashboard…
            </div>
        );
    }

    const funnelData = data?.funnel || { total: 0, opened: 0, clicked: 0, used: 0 };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-gray-200 rounded-3xl p-6 shadow-xs">
                <div>
                    <div className="flex items-center gap-2.5">
                        <span className="text-2xl">🛡️</span>
                        <h1 className="text-2xl font-black text-gray-900 tracking-tight">Admin & Conversion Center</h1>
                        <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-100">
                            Staff Portal
                        </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                        Übersicht über Nutzer-Onboarding, Magic-Link-Konvertierung, Live-Aktivitäten und Systemstatus.
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    <Link
                        to="/app/admin/tracking"
                        className="px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold text-xs rounded-xl transition flex items-center gap-1.5"
                    >
                        <span>📈</span> Event-Tracking
                    </Link>
                    <a
                        href="/admin/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2 bg-slate-900 hover:bg-black text-white font-semibold text-xs rounded-xl transition flex items-center gap-1.5 shadow-xs"
                    >
                        <span>⚙️</span> Django Admin <span>↗</span>
                    </a>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <KpiCard title="🔗 Generierte Links" value={funnelData.total} />
                <KpiCard title="📬 E-Mail Geöffnet" value={funnelData.opened} />
                <KpiCard title="🖱️ Link Geklickt" value={funnelData.clicked} />
                <KpiCard title="✅ Erfolgreiche Logins" value={funnelData.used} />
            </div>

            {/* Main Chart */}
            <div className="bg-white border border-gray-200 rounded-3xl p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
                        <span>📊</span> Onboarding & Conversion Funnel
                    </h2>
                    <span className="text-xs text-gray-400 font-mono">Magic Link Conversion Rate</span>
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
                        <div className="h-full flex items-center justify-center text-gray-400 text-xs">
                            Keine Trichterdaten vorhanden
                        </div>
                    )}
                </div>
            </div>

            {/* LIVE LOGINS & ACTIVITY */}
            <div className="bg-white border border-gray-200 rounded-3xl p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between border-b border-gray-100 pb-3">
                    <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
                        <span>⚡</span> Live Benutzer-Aktivität
                    </h2>
                    <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" /> Live Feed
                    </span>
                </div>

                <div className="space-y-2">
                    {data?.live_logins && data.live_logins.length > 0 ? (
                        data.live_logins.map((l, i) => (
                            <div
                                key={i}
                                className="flex items-center justify-between p-3 bg-slate-50 hover:bg-slate-100 rounded-xl text-xs text-gray-700 transition"
                            >
                                <div className="flex items-center gap-2">
                                    <span>👤</span>
                                    <span className="font-semibold text-gray-900">{l.user}</span>
                                    <span className="text-gray-400">hat sich erfolgreich eingeloggt</span>
                                </div>
                                <span className="font-mono text-gray-400">{l.timestamp}</span>
                            </div>
                        ))
                    ) : (
                        <div className="text-xs text-gray-400 py-4 text-center">
                            Keine aktuellen Logins verzeichnet.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
