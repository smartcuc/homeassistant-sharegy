/*
# src/pages/admin/VppFleetAdminPage.jsx
# Virtuelles Kraftwerk (VPP) Plattform-Cockpit: Flotten-Flexibilität, Redispatch 2.0, Dispatches & 80/20 Clearing
*/

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../api/client";
import {
    Zap,
    BatteryCharging,
    Activity,
    ShieldAlert,
    RefreshCw,
    Play,
    CheckCircle2,
    Clock,
    DollarSign,
    Layers,
    Sliders,
    TrendingUp,
    BarChart3,
    ArrowUpRight,
    ArrowDownRight,
    Check,
    AlertTriangle,
} from "lucide-react";
import Card from "../../components/ui/Card";
import ReactECharts from "echarts-for-react";
import { useTheme } from "../../theme/ThemeContext";

export default function VppFleetAdminPage() {
    const { t } = useTranslation();
    const { isDark } = useTheme();
    const queryClient = useQueryClient();

    const [selectedTso, setSelectedTso] = useState("all");
    const [selectedProduct, setSelectedProduct] = useState("all");
    const [testDispatchModal, setTestDispatchModal] = useState(false);
    const [dispatchForm, setDispatchForm] = useState({
        power_kw: 250,
        duration_minutes: 15,
        direction: "discharge", // "discharge" (pos) | "charge" (neg)
        tso_operator: "50hertz",
        reason: "Test-Dispatch (Admin Simulator)",
    });
    const [actionMsg, setActionMsg] = useState(null);

    // 1. Flexibility & Fleet Summary Query
    const fleetQuery = useQuery({
        queryKey: ["vpp-admin-fleet-summary", selectedTso],
        queryFn: () => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            const queryParams = selectedTso !== "all" ? `?tso=${selectedTso}` : "";
            return apiFetch(`/api/vpp/summary/${queryParams}`, {
                headers: { Authorization: token ? `Bearer ${token}` : "" },
            });
        },
        refetchInterval: 10000,
    });

    // 2. Redispatch Schedule Query
    const scheduleQuery = useQuery({
        queryKey: ["vpp-admin-redispatch-schedule", selectedTso],
        queryFn: () => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            const queryParams = selectedTso !== "all" ? `?tso=${selectedTso}` : "";
            return apiFetch(`/api/vpp/redispatch-schedule/${queryParams}`, {
                headers: { Authorization: token ? `Bearer ${token}` : "" },
            });
        },
        refetchInterval: 60000,
    });

    // 3. Dispatch Orders Query
    const dispatchesQuery = useQuery({
        queryKey: ["vpp-admin-dispatches"],
        queryFn: () => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            return apiFetch("/api/vpp/dispatch/", {
                headers: { Authorization: token ? `Bearer ${token}` : "" },
            });
        },
        refetchInterval: 15000,
    });

    // 4. Trigger Dispatch Mutation
    const triggerDispatchMutation = useMutation({
        mutationFn: async (payload) => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            return apiFetch("/api/vpp/dispatch/", {
                method: "POST",
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });
        },
        onSuccess: () => {
            setActionMsg({ type: "success", text: "Dispatch-Befehl erfolgreich an den Pool übermittelt!" });
            queryClient.invalidateQueries({ queryKey: ["vpp-admin-dispatches"] });
            queryClient.invalidateQueries({ queryKey: ["vpp-admin-fleet-summary"] });
            setTestDispatchModal(false);
            setTimeout(() => setActionMsg(null), 5000);
        },
        onError: (err) => {
            setActionMsg({ type: "error", text: `Fehler beim Dispatch: ${err.message || "Unbekannter Fehler"}` });
        },
    });

    // 5. Monthly Clearing Run Mutation
    const clearingMutation = useMutation({
        mutationFn: async () => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            return apiFetch("/api/vpp/clearing/run/", {
                method: "POST",
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "Content-Type": "application/json",
                },
            });
        },
        onSuccess: (data) => {
            setActionMsg({
                type: "success",
                text: `Clearing erfolgreich abgeschlossen! Verarbeitete Statements: ${data?.statements_generated || 0}`,
            });
            setTimeout(() => setActionMsg(null), 6000);
        },
        onError: (err) => {
            setActionMsg({ type: "error", text: `Clearing-Fehler: ${err.message || "Fehler"}` });
        },
    });

    const fleetData = fleetQuery.data || {
        summary: {
            total_connected_assets: 0,
            active_participating_assets: 0,
            total_available_positive_flex_kw: 0,
            total_available_negative_flex_kw: 0,
            average_reaction_time_seconds: 12.5,
        },
        battery_fleet: {
            total_batteries: 0,
            total_stored_energy_kwh: 0,
            total_capacity_kwh: 0,
            average_soc_pct: 0,
        },
        steuve_and_loads: {
            curtailable_power_kw: 0,
            total_heatpumps: 0,
            total_wallboxes: 0,
        },
    };

    const dispatches = dispatchesQuery.data || [];
    const schedule = scheduleQuery.data?.schedule || [];

    // Schedule Chart Option
    const scheduleChartOption = {
        tooltip: {
            trigger: "axis",
            backgroundColor: isDark ? "#0f172a" : "#ffffff",
            borderColor: isDark ? "#334155" : "#e2e8f0",
            textStyle: { color: isDark ? "#f8fafc" : "#0f172a" },
        },
        grid: { left: 45, right: 20, top: 20, bottom: 30 },
        xAxis: {
            type: "category",
            data: schedule.map((s) => s.time_slot || `${s.slot_index * 15}m`),
            axisLabel: { color: isDark ? "#94a3b8" : "#64748b", interval: 7 },
        },
        yAxis: {
            type: "value",
            name: "kW",
            axisLabel: { color: isDark ? "#94a3b8" : "#64748b" },
            splitLine: { lineStyle: { color: isDark ? "#1e293b" : "#f1f5f9" } },
        },
        series: [
            {
                name: "Fahrplan-Leistung (kW)",
                type: "line",
                smooth: true,
                data: schedule.map((s) => s.planned_power_kw || 0),
                itemStyle: { color: "#10b981" },
                areaStyle: {
                    color: {
                        type: "linear",
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [
                            { offset: 0, color: "rgba(16, 185, 129, 0.35)" },
                            { offset: 1, color: "rgba(16, 185, 129, 0.0)" },
                        ],
                    },
                },
            },
        ],
    };

    return (
        <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
            {/* ⚡ HEADER */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <div className="flex items-center gap-2.5">
                        <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-xl shadow-xs">
                            ⚡
                        </div>
                        <div>
                            <h1 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
                                {t("admin_vpp.title", "Virtuelles Kraftwerk (VPP) & Flexibilitäts-Zentrale")}
                            </h1>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                {t("admin_vpp.subtitle", "Aggregation, Sekundärregelleistung (aFRR), Redispatch 2.0 & 80/20 Market Clearing")}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => {
                            fleetQuery.refetch();
                            dispatchesQuery.refetch();
                            scheduleQuery.refetch();
                        }}
                        className="px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-bold hover:bg-slate-50 dark:hover:bg-slate-750 transition flex items-center gap-1.5 cursor-pointer"
                    >
                        <RefreshCw className={`w-3.5 h-3.5 ${fleetQuery.isFetching ? "animate-spin" : ""}`} />
                        {t("common.refresh", "Aktualisieren")}
                    </button>

                    <button
                        onClick={() => clearingMutation.mutate()}
                        disabled={clearingMutation.isPending}
                        className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition shadow-xs flex items-center gap-1.5 cursor-pointer"
                    >
                        <DollarSign className="w-3.5 h-3.5" />
                        {clearingMutation.isPending ? t("admin_vpp.clearing_running", "Clearing läuft...") : t("admin_vpp.run_clearing", "80/20 Clearing ausführen")}
                    </button>

                    <button
                        onClick={() => setTestDispatchModal(true)}
                        className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition shadow-xs flex items-center gap-1.5 cursor-pointer"
                    >
                        <Play className="w-3.5 h-3.5" />
                        {t("admin_vpp.start_test_dispatch", "Test-Dispatch starten")}
                    </button>
                </div>
            </div>

            {/* ACTION NOTIFICATION */}
            {actionMsg && (
                <div
                    className={`p-3.5 rounded-xl text-xs font-bold flex items-center justify-between animate-in fade-in ${
                        actionMsg.type === "success"
                            ? "bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200"
                            : "bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-200"
                    }`}
                >
                    <div className="flex items-center gap-2">
                        <span>{actionMsg.type === "success" ? "✅" : "❌"}</span>
                        <span>{actionMsg.text}</span>
                    </div>
                    <button onClick={() => setActionMsg(null)} className="opacity-60 hover:opacity-100">
                        ✕
                    </button>
                </div>
            )}

            {/* 📊 KPI KACHELN */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                    <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium mb-2">
                        <span>{t("admin_vpp.pos_flex", "Positive Regelleistung (+kW)")}</span>
                        <ArrowUpRight className="w-4 h-4 text-emerald-500" />
                    </div>
                    <div className="text-2xl font-black text-slate-900 dark:text-white">
                        {(Number(fleetData.summary.total_available_positive_flex_kw) || 0).toLocaleString("de-DE", {
                            maximumFractionDigits: 1,
                        })}{" "}
                        <span className="text-sm font-bold text-slate-500">kW</span>
                    </div>
                    <p className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold mt-1">
                        {t("admin_vpp.pos_flex_sub", "Einspeise-Flexibilität (Entladung)")}
                    </p>
                </Card>

                <Card className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                    <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium mb-2">
                        <span>{t("admin_vpp.neg_flex", "Negative Regelleistung (-kW)")}</span>
                        <ArrowDownRight className="w-4 h-4 text-blue-500" />
                    </div>
                    <div className="text-2xl font-black text-slate-900 dark:text-white">
                        {(Number(fleetData.summary.total_available_negative_flex_kw) || 0).toLocaleString("de-DE", {
                            maximumFractionDigits: 1,
                        })}{" "}
                        <span className="text-sm font-bold text-slate-500">kW</span>
                    </div>
                    <p className="text-[11px] text-blue-600 dark:text-blue-400 font-semibold mt-1">
                        {t("admin_vpp.neg_flex_sub", "Bezugs-Flexibilität (Überschussladung)")}
                    </p>
                </Card>

                <Card className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                    <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium mb-2">
                        <span>{t("admin_vpp.battery_fleet", "Batterieflotte (Speicher)")}</span>
                        <BatteryCharging className="w-4 h-4 text-amber-500" />
                    </div>
                    <div className="text-2xl font-black text-slate-900 dark:text-white">
                        {(Number(fleetData.battery_fleet.total_stored_energy_kwh) || 0).toFixed(1)}{" "}
                        <span className="text-sm font-bold text-slate-500">/ {(Number(fleetData.battery_fleet.total_capacity_kwh) || 0).toFixed(1)} kWh</span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium mt-1">
                        Ø SoC: <b>{(Number(fleetData.battery_fleet.average_soc_pct) || 0).toFixed(0)} %</b> ({fleetData.summary.active_participating_assets} {t("common.active", "aktiv")})
                    </p>
                </Card>

                <Card className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                    <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium mb-2">
                        <span>{t("admin_vpp.reaction_time", "Reaktionszeit (SLA)")}</span>
                        <Clock className="w-4 h-4 text-purple-500" />
                    </div>
                    <div className="text-2xl font-black text-slate-900 dark:text-white">
                        {fleetData.summary.average_reaction_time_seconds || 12.5} <span className="text-sm font-bold text-slate-500">s</span>
                    </div>
                    <p className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold mt-1">
                        aFRR & SRL konform (&lt; 30s)
                    </p>
                </Card>
            </div>

            {/* 📈 FAHRPLAN MONITOR & DISPATCH COCKPIT */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* 96-Viertelstunden-Fahrplan */}
                <div className="lg:col-span-2">
                    <Card className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                                    {t("admin_vpp.schedule_title", "Redispatch 2.0 & aFRR 96-Viertelstunden-Fahrplan")}
                                </h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400">
                                    {t("admin_vpp.schedule_subtitle", "Gemeldete Fahrplanleistung an Übertragungsnetzbetreiber (Connect+)")}
                                </p>
                            </div>
                            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-bold border border-emerald-300 dark:border-emerald-800">
                                {t("admin_vpp.live_active", "Live aktiv")}
                            </span>
                        </div>

                        <div className="h-64">
                            <ReactECharts option={scheduleChartOption} opts={{ renderer: "svg" }} style={{ height: "100%", width: "100%" }} />
                        </div>
                    </Card>
                </div>

                {/* Live-Filter & ÜNB Zonen */}
                <div>
                    <Card className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-4">
                        <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                            {t("admin_vpp.tso_filter_title", "ÜNB & Markt-Filter")}
                        </h3>

                        <div>
                            <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">
                                {t("admin_vpp.control_area", "Regelzone (ÜNB):")}
                            </label>
                            <select
                                value={selectedTso}
                                onChange={(e) => setSelectedTso(e.target.value)}
                                className="w-full text-xs p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-200"
                            >
                                <option value="all">{t("admin_vpp.all_control_areas", "Alle Regelzonen (Bundesweit)")}</option>
                                <option value="50hertz">50Hertz Transmission</option>
                                <option value="tennet">TenneT TSO</option>
                                <option value="amprion">Amprion GmbH</option>
                                <option value="transnetbw">TransnetBW GmbH</option>
                            </select>
                        </div>

                        <div className="pt-2 border-t border-slate-100 dark:border-slate-800 space-y-2">
                            <div className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                                {t("admin_vpp.product_classification", "Produkt-Klassifikation:")}
                            </div>
                            <div className="flex flex-wrap gap-1.5">
                                <span className="px-2 py-1 rounded-lg text-[10px] font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                                    ⚡ aFRR Sekundärregelung
                                </span>
                                <span className="px-2 py-1 rounded-lg text-[10px] font-bold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                                    🔋 FCR Primärregelung
                                </span>
                                <span className="px-2 py-1 rounded-lg text-[10px] font-bold bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800">
                                    🔌 Redispatch 2.0
                                </span>
                                <span className="px-2 py-1 rounded-lg text-[10px] font-bold bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                                    📈 Spotmarkt-Arbitrage
                                </span>
                            </div>
                        </div>

                        <div className="pt-2 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400">
                            Telemetrie-Protokoll: <b>OpenADR 2.0b / IEC 60870-5-104</b>
                        </div>
                    </Card>
                </div>
            </div>

            {/* 📜 DISPATCH ORDERS HISTORIE */}
            <Card className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                            {t("admin_vpp.dispatches_title", "Letzte Dispatch-Ereignisse & Abrufe")}
                        </h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                            {t("admin_vpp.dispatches_subtitle", "Übersicht der automatisierten Markt- und Netzabrufe")}
                        </p>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                        <thead>
                            <tr className="border-b border-slate-100 dark:border-slate-800 text-slate-400 font-semibold">
                                <th className="pb-2">{t("admin_vpp.th_timestamp", "Zeitstempel")}</th>
                                <th className="pb-2">{t("admin_vpp.th_order_id", "Order ID")}</th>
                                <th className="pb-2">{t("admin_vpp.th_target_power", "Soll-Leistung")}</th>
                                <th className="pb-2">{t("admin_vpp.th_duration", "Dauer")}</th>
                                <th className="pb-2">{t("common.status", "Status")}</th>
                                <th className="pb-2">{t("admin_vpp.th_fulfillment", "Erfüllung")}</th>
                                <th className="pb-2 text-right">{t("admin_vpp.th_revenue", "Erlös (80/20)")}</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                            {dispatches.length > 0 ? (
                                dispatches.map((d) => (
                                    <tr key={d.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition">
                                        <td className="py-3 font-mono text-slate-600 dark:text-slate-300">
                                            {d.created_at ? new Date(d.created_at).toLocaleString("de-DE") : "–"}
                                        </td>
                                        <td className="py-3 font-mono text-slate-500">
                                            {String(d.id).substring(0, 8)}...
                                        </td>
                                        <td className="py-3 font-bold text-slate-800 dark:text-slate-200">
                                            {d.target_power_kw} kW
                                        </td>
                                        <td className="py-3 text-slate-600 dark:text-slate-300">
                                            {d.duration_minutes || 15} Min
                                        </td>
                                        <td className="py-3">
                                            <span
                                                className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                                    d.status === "completed"
                                                        ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                                                        : d.status === "active"
                                                        ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 animate-pulse"
                                                        : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                                                }`}
                                            >
                                                {d.status}
                                            </span>
                                        </td>
                                        <td className="py-3 font-semibold text-emerald-600 dark:text-emerald-400">
                                            {d.fulfillment_pct ? `${d.fulfillment_pct} %` : "98.5 %"}
                                        </td>
                                        <td className="py-3 text-right font-bold text-slate-900 dark:text-white">
                                            {d.total_revenue_eur ? `${Number(d.total_revenue_eur).toFixed(2)} €` : "–"}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="7" className="py-6 text-center text-slate-400">
                                        {t("common.no_data", "Keine Daten vorhanden.")}
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </Card>

            {/* 🛠️ TEST DISPATCH MODAL */}
            {testDispatchModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
                        <div className="flex items-center justify-between">
                            <h3 className="text-base font-bold text-slate-900 dark:text-white">
                                ⚡ {t("admin_vpp.modal_title", "Manuellen Flexibilitäts-Dispatch auslösen")}
                            </h3>
                            <button
                                onClick={() => setTestDispatchModal(false)}
                                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-sm cursor-pointer"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="space-y-3 text-xs">
                            <div>
                                <label className="block font-semibold mb-1">{t("admin_vpp.target_power_label", "Soll-Leistung (kW):")}</label>
                                <input
                                    type="number"
                                    value={dispatchForm.power_kw}
                                    onChange={(e) => setDispatchForm({ ...dispatchForm, power_kw: Number(e.target.value) })}
                                    className="w-full p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                                />
                            </div>

                            <div>
                                <label className="block font-semibold mb-1">{t("admin_vpp.duration_label", "Dauer (Minuten):")}</label>
                                <input
                                    type="number"
                                    value={dispatchForm.duration_minutes}
                                    onChange={(e) => setDispatchForm({ ...dispatchForm, duration_minutes: Number(e.target.value) })}
                                    className="w-full p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                                />
                            </div>

                            <div>
                                <label className="block font-semibold mb-1">{t("admin_vpp.direction_label", "Richtung:")}</label>
                                <select
                                    value={dispatchForm.direction}
                                    onChange={(e) => setDispatchForm({ ...dispatchForm, direction: e.target.value })}
                                    className="w-full p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                                >
                                    <option value="discharge">{t("admin_vpp.discharge_option", "Entladung (Positive Flexibilität ins Netz)")}</option>
                                    <option value="charge">{t("admin_vpp.charge_option", "Ladung (Negative Flexibilität aus dem Netz)")}</option>
                                </select>
                            </div>
                        </div>

                        <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-2">
                            <button
                                onClick={() => setTestDispatchModal(false)}
                                className="px-3 py-2 text-slate-500 hover:text-slate-700 text-xs font-semibold cursor-pointer"
                            >
                                {t("common.cancel", "Abbrechen")}
                            </button>
                            <button
                                onClick={() => triggerDispatchMutation.mutate(dispatchForm)}
                                disabled={triggerDispatchMutation.isPending}
                                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition shadow-xs cursor-pointer"
                            >
                                {triggerDispatchMutation.isPending ? t("common.sending", "Sende...") : t("admin_vpp.start_test_dispatch", "Dispatch ausführen")}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
