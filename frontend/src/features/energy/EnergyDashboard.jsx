/*
# src/features/energy/EnergyDashboard.jsx
*/

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../api/client";
import EnergyOptimizerCard from "./components/EnergyOptimizerCard";
import BatteryForecastCard from "./components/BatteryForecastCard";
import BatteryArbitrageCard from "./components/BatteryArbitrageCard";
import BWWPLoadManagementCard from "./components/BWWPLoadManagementCard";
import WallboxCard from "./components/WallboxCard";
import SimpleDashboardView from "./components/SimpleDashboardView";

import AddWallboxModal from "../devices/components/AddWallboxModal";
import CommunityShareModal from "../community/components/CommunityShareModal";
import CommunityInviteCard from "../community/components/CommunityInviteCard";
import SubmeterTrendModal from "./components/SubmeterTrendModal";
import SubmeterStackedTrendChart from "./components/SubmeterStackedTrendChart";
import DateRangePickerModal from "./components/DateRangePickerModal";
import ExportDropdown from "./components/ExportDropdown";
import GridCo2Card from "../market/components/GridCo2Card";
import { useSubscription } from "../../hooks/useSubscription";
import ProBadge from "../../components/common/ProBadge";
import ProUpgradeModal from "../../components/common/ProUpgradeModal";

export default function EnergyDashboard() {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const [period, setPeriod] = useState("today");
    const [selectedTrendMeter, setSelectedTrendMeter] = useState(null);
    const [isDatePickerOpen, setIsDatePickerOpen] = useState(false);
    const [proModalOpen, setProModalOpen] = useState(false);
    const [shareModalOpen, setShareModalOpen] = useState(false);
    const [addWallboxOpen, setAddWallboxOpen] = useState(false);
    const [proModalFeature, setProModalFeature] = useState({ name: "Pro Feature", desc: "" });
    const [customDates, setCustomDates] = useState({ startDate: null, endDate: null, label: null });
    const [viewMode, setViewMode] = useState(() => {
        try {
            return localStorage.getItem("sharegy_dashboard_view_mode") || "simple";
        } catch {
            return "simple";
        }
    });

    const handleSetViewMode = (mode) => {
        setViewMode(mode);
        try {
            localStorage.setItem("sharegy_dashboard_view_mode", mode);
        } catch (e) {
            console.warn("Could not persist dashboard view mode:", e);
        }
    };

    // Fetch energy balance & submeters
    const balanceQuery = useQuery({
        queryKey: ["energy-balance", period, customDates.startDate, customDates.endDate],
        queryFn: () => {
            let url = `/api/energy/balance/?period=${period}`;
            if (period === "custom" && customDates.startDate) {
                url += `&start_date=${customDates.startDate}&end_date=${customDates.endDate}`;
            }
            return apiFetch(url);
        },
        refetchInterval: 10000,
    });

    const data = balanceQuery.data || {};
    const kpis = data.kpis || {};
    const submeters = data.submeters || [];
    const charts = data.charts || {};
    const breakdown = charts.breakdown || [];
    const timeseries = charts.timeseries || [];
    const insights = data.insights || [];

    const periods = [
        { key: "today", label: t("energy.period_today", "Heute") },
        { key: "7d", label: t("energy.period_7d", "Letzte 7 Tage") },
        { key: "30d", label: t("energy.period_30d", "Letzte 30 Tage"), isProGated: true },
        { key: "year", label: t("energy.period_year", "Dieses Jahr"), isProGated: true },
    ];

    const handlePeriodClick = (p) => {
        if (p.isProGated && !isPro) {
            setProModalFeature({
                name: `Langzeit-Historie (${p.label})`,
                desc: "Unbegrenzte historische Verbrauchsanalysen, Monatsvergleiche und Jahrestrends stehen exklusiv in Sharegy Pro zur Verfügung.",
            });
            setProModalOpen(true);
            return;
        }
        setPeriod(p.key);
        setCustomDates({ startDate: null, endDate: null, label: null });
    };

    const handleCustomDatePickerClick = () => {
        if (!isPro) {
            setProModalFeature({
                name: "Frei wählbarer Analyse-Zeitraum",
                desc: "Benutzerdefinierte Datumsbereiche und historische Langzeit-Filter stehen exklusiv in Sharegy Pro zur Verfügung.",
            });
            setProModalOpen(true);
            return;
        }
        setIsDatePickerOpen(true);
    };

    // Pre-calculate SVG donut slices purely and immutably via reduce
    const donutSlices = useMemo(() => {
        const list = balanceQuery.data?.charts?.breakdown || [];
        const total = list.reduce((acc, item) => acc + item.value, 0) || 1;

        return list.reduce(
            (acc, item) => {
                const percentage = item.value / total;
                const strokeDasharray = `${percentage * 251.2} 251.2`;
                const strokeDashoffset = -acc.accumulated * 251.2;
                return {
                    accumulated: acc.accumulated + percentage,
                    items: [
                        ...acc.items,
                        {
                            ...item,
                            strokeDasharray,
                            strokeDashoffset,
                        },
                    ],
                };
            },
            { accumulated: 0, items: [] }
        ).items;
    }, [balanceQuery.data?.charts?.breakdown]);

    // Calculate max value for timeseries scaling
    const maxBarValue = Math.max(
        ...timeseries.map((pt) => Math.max(pt.pv || 0, pt.load || 0)),
        1
    );

    return (
        <div className="p-6 space-y-6 w-full max-w-full min-w-0">

            {/* =========================================================
                HEADER (MATCHING SOLAR-PROGNOSE STYLE)
            ========================================================= */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <span>⚡</span> {t("energy.title", "Energiebilanz & Analyse")}
                </h1>
                <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
                    {viewMode === "simple" 
                        ? "Die 3 wichtigsten Energiekennzahlen auf einen Blick – einfach, klar und verständlich."
                        : t("energy.subtitle", "Detaillierte Mengen-, Verbrauchs- und Kostenanalyse nach Zeiträumen.")}
                    {period === "custom" && customDates.label && (
                        <span className="ml-2 font-semibold text-indigo-600 bg-indigo-50 dark:bg-indigo-950 px-2 py-0.5 rounded-md">
                            📅 {customDates.label}
                        </span>
                    )}
                </p>
            </div>

            {/* =========================================================
                BUTTONS & CONTROLS ROW DIRECTLY UNDER HEADER
            ========================================================= */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
                <div className="flex flex-wrap items-center gap-2.5">
                    {/* View Mode Toggle: Einfach / Experten */}
                    <div className="inline-flex bg-slate-100 dark:bg-slate-800 p-1 rounded-xl border border-slate-200 dark:border-slate-700 shadow-2xs">
                        <button
                            type="button"
                            onClick={() => handleSetViewMode("simple")}
                            className={`px-3 py-1.5 text-xs font-bold rounded-lg transition cursor-pointer flex items-center gap-1.5 ${
                                viewMode === "simple" 
                                    ? "bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 shadow-xs" 
                                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                            }`}
                        >
                            <span>🟢</span> Einfach
                        </button>
                        <button
                            type="button"
                            onClick={() => handleSetViewMode("expert")}
                            className={`px-3 py-1.5 text-xs font-bold rounded-lg transition cursor-pointer flex items-center gap-1.5 ${
                                viewMode === "expert" 
                                    ? "bg-white dark:bg-slate-900 text-indigo-700 dark:text-indigo-400 shadow-xs" 
                                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                            }`}
                        >
                            <span>⚙️</span> Experten
                        </button>
                    </div>

                    {/* Period Selector Tabs */}
                    <div className="inline-flex bg-slate-100 dark:bg-slate-800 p-1 rounded-xl border border-slate-200 dark:border-slate-700 shadow-2xs">
                        {periods.map((p) => (
                            <button
                                key={p.key}
                                onClick={() => handlePeriodClick(p)}
                                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1.5 ${
                                    period === p.key
                                        ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs font-bold"
                                        : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                                }`}
                            >
                                <span>{p.label}</span>
                                {p.isProGated && !isPro && <ProBadge size="xs" />}
                            </button>
                        ))}
                        <button
                            onClick={handleCustomDatePickerClick}
                            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1.5 ${
                                period === "custom"
                                    ? "bg-indigo-600 text-white shadow-xs font-bold"
                                    : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                            }`}
                            title={t("energy.custom_period_tooltip", "Frei wählbaren Zeitraum einstellen")}
                        >
                            <span>📅</span>
                            <span>{period === "custom" && customDates.label ? customDates.label : t("energy.custom_period", "Zeitraum...")}</span>
                            {!isPro && <ProBadge size="xs" />}
                        </button>
                    </div>
                </div>

                <div className="flex flex-wrap items-center gap-2.5">
                    {/* Multi-Format Export Dropdown (Task 5.15) */}
                    <ExportDropdown
                        period={period}
                        startDate={customDates.startDate}
                        endDate={customDates.endDate}
                    />

                    {/* Community Social Share Button */}
                    <button
                        type="button"
                        onClick={() => setShareModalOpen(true)}
                        className="px-3.5 py-2 rounded-xl text-xs font-bold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition-all shadow-xs flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
                        title="Erfolge & Autarkie mit Nachbarn und Social Media teilen"
                    >
                        <span>📢</span>
                        <span>{t("community.share_stats", "Erfolge teilen")}</span>
                    </button>
                </div>
            </div>

            {/* SIMPLE VIEW BRANCH */}
            {viewMode === "simple" ? (
                <SimpleDashboardView
                    balanceData={data}
                    onSwitchToExpert={() => handleSetViewMode("expert")}
                    onOpenWallbox={() => setAddWallboxOpen(true)}
                />
            ) : (
                <>

            {/* =========================================================
                KPI HIGHLIGHTS
            ========================================================= */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
                {/* PV Generation */}
                <div className="p-4 bg-amber-50/70 border border-amber-200/80 rounded-2xl shadow-2xs">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-amber-700">
                        ☀️ {t("energy.solar_production", "Erzeugung")}
                    </div>
                    <div className="text-2xl font-extrabold text-gray-900 mt-1.5">
                        {Number(kpis.pv_generation_kwh || 0).toLocaleString("de-DE", { maximumFractionDigits: 1 })}{" "}
                        <span className="text-xs font-semibold text-gray-500">kWh</span>
                    </div>
                    <div className="text-[11px] text-amber-800/80 mt-1 font-medium">
                        Direkt: {Number(kpis.direct_consumption_kwh || 0).toFixed(1)} kWh
                    </div>
                </div>

                {/* House Consumption */}
                <div className="p-4 bg-blue-50/70 border border-blue-200/80 rounded-2xl shadow-2xs">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-blue-700">
                        🏠 {t("energy.household_load", "Verbrauch")}
                    </div>
                    <div className="text-2xl font-extrabold text-gray-900 mt-1.5">
                        {Number(kpis.house_consumption_kwh || 0).toLocaleString(undefined, { maximumFractionDigits: 1 })}{" "}
                        <span className="text-xs font-semibold text-gray-500">kWh</span>
                    </div>
                    <div className="text-[11px] text-blue-800/80 mt-1 font-medium">
                        {t("energy_kpis.grid_import_kwh", { val: Number(kpis.grid_import_kwh || 0).toFixed(1), defaultValue: `Netzbezug: ${Number(kpis.grid_import_kwh || 0).toFixed(1)} kWh` })}
                    </div>
                </div>

                {/* Autarky Rate */}
                <div className="p-4 bg-emerald-50/70 border border-emerald-200/80 rounded-2xl shadow-2xs">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-700">
                        🛡️ {t("energy.autarky", "Autarkiegrad")}
                    </div>
                    <div className="text-2xl font-extrabold text-emerald-700 mt-1.5">
                        {Number(kpis.autarky_rate || 0).toFixed(0)} %
                    </div>
                    <div className="text-[11px] text-emerald-800/80 mt-1 font-medium">
                        {t("energy_kpis.grid_independent", "Netzunabhängig")}
                    </div>
                </div>

                {/* Self Consumption Rate */}
                <div className="p-4 bg-purple-50/70 border border-purple-200/80 rounded-2xl shadow-2xs">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-purple-700">
                        🔄 {t("energy.self_consumption", "Eigenverbrauch")}
                    </div>
                    <div className="text-2xl font-extrabold text-purple-700 mt-1.5">
                        {Number(kpis.self_consumption_rate || 0).toFixed(0)} %
                    </div>
                    <div className="text-[11px] text-purple-800/80 mt-1 font-medium">
                        {t("energy.pv_utilization", "PV-Nutzungsgrad")}
                    </div>
                </div>

                {/* Financial Benefit */}
                <div className="p-4 bg-indigo-50/70 border border-indigo-200/80 rounded-2xl shadow-2xs">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-indigo-700">
                        💶 {t("energy.net_benefit", "Finanzvorteil")}
                    </div>
                    <div className="text-2xl font-extrabold text-indigo-900 mt-1.5">
                        {Number(kpis.net_benefit_eur || 0) >= 0 ? "+" : ""}
                        {Number(kpis.net_benefit_eur || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €
                    </div>
                    <div className="text-[11px] text-indigo-800/80 mt-1 font-medium truncate" title={kpis.tariff_label}>
                        {t("energy_kpis.savings_label", { val: Number(kpis.savings_eur || 0).toFixed(2), defaultValue: `Ersparnis: ${Number(kpis.savings_eur || 0).toFixed(2)} €` })} · <span className="font-semibold">{kpis.tariff_label || "Standard"}</span>
                    </div>
                </div>

                {/* CO2 Saved */}
                <div className="p-4 bg-teal-50/70 border border-teal-200/80 rounded-2xl shadow-2xs">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-teal-700">
                        🌿 {t("energy.co2_saved", "CO₂ vermieden")}
                    </div>
                    <div className="text-2xl font-extrabold text-teal-900 mt-1.5">
                        {Number(kpis.co2_saved_kg || 0).toLocaleString(undefined, { maximumFractionDigits: 1 })}{" "}
                        <span className="text-xs font-semibold text-gray-500">kg</span>
                    </div>
                    <div className="text-[11px] text-teal-800/80 mt-1 font-medium">
                        {t("energy_kpis.eco_balance", "Ökobilanz")}
                    </div>
                </div>
            </div>

            {/* =========================================================
                ANALYTICS & IMPACT BENCHMARKS
            ========================================================= */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 bg-slate-50/80 border border-slate-200/80 rounded-2xl p-3.5 shadow-2xs">
                <div className="flex items-center gap-2.5">
                    <span className="text-xl p-2 bg-white rounded-xl shadow-2xs">⚡</span>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-gray-500">{t("energy.pv_peak_power", "PV Spitzenleistung")}</div>
                        <div className="text-sm font-black text-gray-900 font-mono">{kpis.peak_pv_kw || 0} kW</div>
                    </div>
                </div>

                <div className="flex items-center gap-2.5">
                    <span className="text-xl p-2 bg-white rounded-xl shadow-2xs">📈</span>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-gray-500">{t("energy.max_load_peak", "Max. Lastspitze")}</div>
                        <div className="text-sm font-black text-gray-900 font-mono">{kpis.peak_load_kw || 0} kW</div>
                    </div>
                </div>

                <div className="flex items-center gap-2.5">
                    <span className="text-xl p-2 bg-white rounded-xl shadow-2xs">☀️</span>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-gray-500">{t("energy_kpis.avg_gen_day", "Ø Erzeugung / Tag")}</div>
                        <div className="text-sm font-black text-gray-900 font-mono">{kpis.daily_avg_generation_kwh || 0} kWh</div>
                    </div>
                </div>

                <div className="flex items-center gap-2.5">
                    <span className="text-xl p-2 bg-white rounded-xl shadow-2xs">🏠</span>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-gray-500">{t("energy_kpis.avg_load_day", "Ø Bedarf / Tag")}</div>
                        <div className="text-sm font-black text-gray-900 font-mono">{kpis.daily_avg_consumption_kwh || 0} kWh</div>
                    </div>
                </div>

                <div className="flex items-center gap-2.5">
                    <span className="text-xl p-2 bg-white rounded-xl shadow-2xs">🚗</span>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-gray-500">{t("energy.ev_range_km", "Solar-Fahrleistung")}</div>
                        <div className="text-sm font-black text-emerald-700 font-mono">+{kpis.ev_km_equivalent || 0} km</div>
                    </div>
                </div>

                <div className="flex items-center gap-2.5">
                    <span className="text-xl p-2 bg-white rounded-xl shadow-2xs">🌳</span>
                    <div>
                        <div className="text-[10px] uppercase font-bold text-gray-500">{t("energy.tree_offset", "Baum-Kompensation")}</div>
                        <div className="text-sm font-black text-teal-700 font-mono">{t("energy_kpis.trees_count", { count: kpis.trees_equivalent || 0, defaultValue: `${kpis.trees_equivalent || 0} Bäume` })}</div>
                    </div>
                </div>
            </div>

            {/* =========================================================
                COMMUNITY & ENERGY SHARING INVITE BANNER (TASK 2)
            ========================================================= */}
            <CommunityInviteCard
                onOpenShareModal={() => setShareModalOpen(true)}
                kpis={kpis}
            />

            {/* =========================================================
                INSIGHTS NOTIFICATION
            ========================================================= */}
            {insights.length > 0 && (
                <div className="p-4 bg-linear-to-r from-indigo-50/80 to-purple-50/80 border border-indigo-100 rounded-2xl text-xs text-indigo-950 space-y-1.5 shadow-2xs">
                    {insights.map((text, i) => (
                        <div key={i} className="flex items-center gap-2">
                            <span className="text-indigo-600 text-sm">💡</span>
                            <span className="font-medium">{text}</span>
                        </div>
                    ))}
                </div>
            )}

            {/* =========================================================
                SMART ENERGY OPTIMIZER (1H, 2H, 4H BESTE LADEZEITEN)
            ========================================================= */}
            <EnergyOptimizerCard />

            {/* =========================================================
                BWWP & WÄRMEPUMPEN LASTMANAGEMENT (SG-READY)
            ========================================================= */}
            <BWWPLoadManagementCard />

            {/* =========================================================
                BATTERIE- & SOC-PROGNOSE (TASK 5.3)
            ========================================================= */}
            <BatteryForecastCard />


            {/* =========================================================
                VIRTUELLE ZÄHLER & SUB-METERING
            ========================================================= */}
            <div className="space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div>
                        <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                            <span>🧮</span> {t("energy.submeters_title", "Virtuelle Zähler & Sub-Metering")}
                        </h2>
                        <p className="text-xs text-gray-500 mt-0.5">
                            {t("energy.submeters_subtitle", "Aufschlüsselung des gesamten Hausverbrauchs nach Verbrauchern. Klicke auf eine Kachel für Zeitreihen- & Trend-Analysen.")}
                        </p>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold px-2.5 py-1 bg-slate-100 text-slate-700 rounded-lg">
                            {submeters.length} {submeters.length === 1 ? "Verbraucher" : "Verbraucher"}
                        </span>
                    </div>
                </div>

                {/* Submeters Grid */}
                {submeters.length === 0 ? (
                    <div className="bg-slate-50/60 border border-dashed border-slate-300 rounded-2xl p-6 text-center space-y-2">
                        <span className="text-2xl">🔌</span>
                        <div className="font-bold text-gray-800 text-sm">
                            {t("energy.no_submeters", "Keine Einzelverbraucher konfiguriert")}
                        </div>
                        <p className="text-xs text-gray-500 max-w-md mx-auto">
                            {t("energy.no_submeters_desc", "Füge unter 'Geräte' smarte Steckdosen, Wallboxen oder Wärmepumpen-Sensoren hinzu, um Verbräuche hier separat aufzuschlüsseln.")}
                        </p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {submeters.map((meter) => (
                            <div
                                key={meter.id}
                                onClick={() => setSelectedTrendMeter(meter)}
                                className={`p-5 rounded-2xl border transition shadow-2xs cursor-pointer group hover:scale-[1.01] ${meter.is_residual
                                    ? "bg-slate-50/70 border-dashed border-slate-300 hover:border-slate-400 hover:shadow-xs"
                                    : "bg-white border-gray-200 hover:border-indigo-300 hover:shadow-md"
                                    }`}
                                title={t("submeters.click_to_open_trends", "Klick: Historische Zeitreihen & Trends öffnen")}
                            >
                                {/* Meter Header */}
                                <div className="flex items-center justify-between gap-2">
                                    <div className="flex items-center gap-2.5 min-w-0">
                                        <span className="text-2xl shrink-0 p-2 bg-slate-100 group-hover:bg-indigo-50 rounded-xl transition">
                                            {meter.icon}
                                        </span>
                                        <div className="min-w-0">
                                            <div className="font-bold text-sm text-gray-900 group-hover:text-indigo-600 transition truncate">
                                                {meter.name}
                                            </div>
                                            <div className="text-[11px] text-gray-400 capitalize">{meter.category}</div>
                                        </div>
                                    </div>
                                    <span
                                        className="px-2.5 py-1 rounded-full text-xs font-bold text-white shrink-0 shadow-2xs"
                                        style={{ backgroundColor: meter.color }}
                                    >
                                        {meter.share_pct} %
                                    </span>
                                </div>

                                {/* Consumption & Costs */}
                                <div className="mt-4 flex items-baseline justify-between border-b border-gray-100 pb-3">
                                    <div>
                                        <div className="text-2xl font-black text-gray-900 font-mono">
                                            {Number(meter.consumption_kwh).toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}{" "}
                                            <span className="text-xs font-normal text-gray-500">kWh</span>
                                        </div>
                                        <div className="text-[11px] text-gray-400">{t("submeters.period_consumption", "Verbrauch im Zeitraum")}</div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-sm font-bold text-gray-800 font-mono">
                                            {Number(meter.cost_eur || 0).toFixed(2)} €
                                        </div>
                                        <div className="text-[11px] text-emerald-600 font-medium">
                                            -{Number(meter.savings_eur || 0).toFixed(2)} € Solar
                                        </div>
                                    </div>
                                </div>

                                {/* Solar vs. Grid Coverage Bar */}
                                <div className="mt-3 space-y-1.5">
                                    <div className="flex justify-between text-[11px] font-medium">
                                        <span className="text-emerald-700 flex items-center gap-1">
                                            <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
                                            {t("energy.solar_share", "Solarstrom")}: {meter.solar_share_pct.toFixed(0)}%
                                        </span>
                                        <span className="text-slate-500 flex items-center gap-1">
                                            <span className="w-2 h-2 rounded-full bg-slate-400 inline-block" />
                                            {t("energy.grid_share", "Netzstrom")}: {(100 - meter.solar_share_pct).toFixed(0)}%
                                        </span>
                                    </div>

                                    <div className="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden flex">
                                        <div
                                            className="bg-emerald-500 h-full transition-all duration-500"
                                            style={{ width: `${meter.solar_share_pct}%` }}
                                            title={`Solarstrom: ${meter.solar_share_pct}%`}
                                        />
                                        <div
                                            className="bg-slate-400 h-full transition-all duration-500"
                                            style={{ width: `${100 - meter.solar_share_pct}%` }}
                                            title={`Netzstrom: ${100 - meter.solar_share_pct}%`}
                                        />
                                    </div>
                                </div>

                                {/* Footer Link / Action Prompt */}
                                <div className="mt-3 pt-2 border-t border-gray-100 flex items-center justify-between text-[11px] text-indigo-600 font-semibold opacity-0 group-hover:opacity-100 transition">
                                    <span>📈 Trends & Historie anzeigen</span>
                                    <span className="group-hover:translate-x-1 transition">→</span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Gestapelte historische Trendanalyse aller Zähler */}
                <SubmeterStackedTrendChart
                    period={period}
                    onSelectMeter={(m) => setSelectedTrendMeter(m)}
                />
            </div>

            {/* =========================================================
                CHARTS SECTION: BREAKDOWN (DONUT) & GENERATION VS LOAD
            ========================================================= */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 1. Verbrauchsaufteilung (Donut + Legend) */}
                <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-xs space-y-4">
                    <h3 className="font-bold text-base text-gray-900 flex items-center gap-2">
                        <span>📊</span> {t("energy.breakdown_title", "Verbrauchsaufteilung")}
                    </h3>

                    {breakdown.length === 0 ? (
                        <div className="py-12 text-center text-gray-400 text-xs font-medium bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
                            {t("energy.no_breakdown_data", "Keine Verbrauchsaufteilung im gewählten Zeitraum")}
                        </div>
                    ) : (
                        <div className="flex flex-col sm:flex-row items-center gap-6">
                            {/* Custom SVG Donut */}
                            <div className="relative w-44 h-44 shrink-0 flex items-center justify-center">
                                <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                                    {donutSlices.map((item, idx) => (
                                        <circle
                                            key={idx}
                                            cx="50"
                                            cy="50"
                                            r="40"
                                            fill="transparent"
                                            stroke={item.color}
                                            strokeWidth="16"
                                            strokeDasharray={item.strokeDasharray}
                                            strokeDashoffset={item.strokeDashoffset}
                                            className="transition-all duration-500 hover:opacity-80"
                                        />
                                    ))}
                                </svg>
                                <div className="absolute text-center">
                                    <div className="text-xs text-gray-400 font-semibold uppercase">{t("energy_kpis.total_uppercase", "Gesamt")}</div>
                                    <div className="text-base font-black text-gray-900 font-mono">
                                        {Number(kpis.house_consumption_kwh || 0).toFixed(1)}
                                    </div>
                                    <div className="text-[10px] text-gray-500">kWh</div>
                                </div>
                            </div>

                            {/* Legend */}
                            <div className="flex-1 w-full space-y-2">
                                {breakdown.map((item, idx) => {
                                    const total = breakdown.reduce((acc, b) => acc + b.value, 0) || 1;
                                    const pct = ((item.value / total) * 100).toFixed(1);

                                    return (
                                        <div key={idx} className="flex items-center justify-between text-xs">
                                            <div className="flex items-center gap-2 truncate">
                                                <span className="w-3 h-3 rounded-md shrink-0" style={{ backgroundColor: item.color }} />
                                                <span className="font-medium text-gray-700 truncate">{item.name}</span>
                                            </div>
                                            <div className="font-mono font-bold text-gray-900 shrink-0 ml-2">
                                                {Number(item.value).toFixed(1)} kWh <span className="text-gray-400 font-normal">({pct}%)</span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </div>

                {/* 2. Energetische Mengenbilanz (In & Out Flussmatrix) */}
                <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-xs space-y-4">
                    <h3 className="font-bold text-base text-gray-900 flex items-center gap-2">
                        <span>🔄</span> {t("energy.energy_balance", "Mengenbilanz (kWh)")}
                    </h3>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                        {/* Erzeugung Matrix */}
                        <div className="p-3.5 bg-amber-50/60 border border-amber-100 rounded-xl space-y-2">
                            <div className="font-bold text-amber-900 border-b border-amber-200/60 pb-1">
                                ☀️ {t("energy.pv", "PV-Erzeugung")} ({Number(kpis.pv_generation_kwh || 0).toFixed(1)} kWh)
                            </div>
                            <div className="flex justify-between text-gray-700">
                                <span>🏠 {t("energy.direct_consumption", "Direktverbrauch")}:</span>
                                <span className="font-mono font-bold">{Number(kpis.direct_consumption_kwh || 0).toFixed(1)} kWh</span>
                            </div>
                            <div className="flex justify-between text-gray-700">
                                <span>🔋 {t("energy.into_battery", "In Batterie")}:</span>
                                <span className="font-mono font-bold">{Number(kpis.battery_charge_kwh || 0).toFixed(1)} kWh</span>
                            </div>
                            <div className="flex justify-between text-gray-700">
                                <span>🔌 {t("energy.grid_export", "Netzeinspeisung")}:</span>
                                <span className="font-mono font-bold">{Number(kpis.grid_export_kwh || 0).toFixed(1)} kWh</span>
                            </div>
                        </div>

                        {/* Verbrauch Matrix */}
                        <div className="p-3.5 bg-blue-50/60 border border-blue-100 rounded-xl space-y-2">
                            <div className="font-bold text-blue-900 border-b border-blue-200/60 pb-1">
                                🏠 {t("energy.load", "Hausbedarf")} ({Number(kpis.house_consumption_kwh || 0).toFixed(1)} kWh)
                            </div>
                            <div className="flex justify-between text-gray-700">
                                <span>☀️ {t("energy.from_pv_direct", "Aus PV-Direkt")}:</span>
                                <span className="font-mono font-bold">{Number(kpis.direct_consumption_kwh || 0).toFixed(1)} kWh</span>
                            </div>
                            <div className="flex justify-between text-gray-700">
                                <span>🔋 {t("energy.from_battery", "Aus Batterie")}:</span>
                                <span className="font-mono font-bold">{Number(kpis.battery_discharge_kwh || 0).toFixed(1)} kWh</span>
                            </div>
                            <div className="flex justify-between text-gray-700">
                                <span>🔌 {t("energy.from_grid", "Aus Stromnetz")}:</span>
                                <span className="font-mono font-bold">{Number(kpis.grid_import_kwh || 0).toFixed(1)} kWh</span>
                            </div>
                        </div>
                    </div>

                    {/* Monetary summary strip */}
                    <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs">
                        <span className="text-gray-600 font-medium">{t("energy.cost_summary_period", "Kostenbilanz im Zeitraum:")}</span>
                        <div className="flex items-center gap-4 font-mono font-semibold">
                            <span className="text-emerald-700">+{Number(kpis.savings_eur || 0).toFixed(2)} € {t("energy.savings_short", "Ersparnis")}</span>
                            <span className="text-amber-700">{t("energy_kpis.feed_in_rev", { val: Number(kpis.feed_in_revenue_eur || 0).toFixed(2), defaultValue: `+${Number(kpis.feed_in_revenue_eur || 0).toFixed(2)} € Einspeisung` })}</span>
                            <span className="text-rose-700">-{Number(kpis.grid_costs_eur || 0).toFixed(2)} € {t("energy.grid_costs_short", "Netzkosten")}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* =========================================================
                TIMELINE BARS: ERZEUGUNG VS. VERBRAUCH
            ========================================================= */}
            <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                    <h3 className="font-bold text-base text-gray-900 flex items-center gap-2">
                        <span>📈</span> {t("energy.generation_vs_load", "Erzeugung vs. Verbrauch")} ({data?.period_label || period})
                    </h3>
                    <div className="flex items-center gap-4 text-xs font-semibold">
                        <div className="flex items-center gap-1.5 text-amber-700">
                            <span className="w-3 h-3 rounded-xs bg-amber-400" /> ☀️ {t("energy.pv_kwh", "Erzeugung (kWh)")}
                        </div>
                        <div className="flex items-center gap-1.5 text-blue-700">
                            <span className="w-3 h-3 rounded-xs bg-blue-500" /> {t("energy_kpis.load_kwh", "🏠 Verbrauch (kWh)")}
                        </div>
                    </div>
                </div>

                {/* Visual Bar Columns */}
                {timeseries.length === 0 ? (
                    <div className="py-12 text-center text-gray-400 text-xs font-medium bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
                        {t("energy.no_timeseries_data", "Keine Zeitreihendaten für diesen Zeitraum erfasst")}
                    </div>
                ) : (
                    <div className="pt-6 pb-2">
                        <div className="h-48 flex items-end justify-between gap-2 border-b border-gray-200 pb-2">
                            {timeseries.map((pt, idx) => {
                                const pvHeight = (pt.pv / maxBarValue) * 100;
                                const loadHeight = (pt.load / maxBarValue) * 100;

                                return (
                                    <div key={idx} className="flex-1 flex flex-col items-center gap-1 h-full justify-end group">
                                        <div className="w-full flex items-end justify-center gap-1 h-full">
                                            {/* PV Bar */}
                                            <div
                                                className="w-1/2 max-w-[24px] bg-amber-400 rounded-t-sm transition-all duration-300 group-hover:bg-amber-500"
                                                style={{ height: `${Math.max(pvHeight, 2)}%` }}
                                                title={`${t("energy.production", "Erzeugung")}: ${pt.pv} kWh`}
                                            />
                                            {/* Load Bar */}
                                            <div
                                                className="w-1/2 max-w-[24px] bg-blue-500 rounded-t-sm transition-all duration-300 group-hover:bg-blue-600"
                                                style={{ height: `${Math.max(loadHeight, 2)}%` }}
                                                title={`${t("energy.consumption", "Verbrauch")}: ${pt.load} kWh`}
                                            />
                                        </div>
                                        <span className="text-[10px] text-gray-400 font-mono mt-1 whitespace-nowrap truncate w-full text-center">
                                            {pt.time}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>

            {/* =========================================================
                E-AUTO & WALLBOX SMART-CHARGING (OCPP 1.6-J)
            ========================================================= */}
            <div className="mb-6">
                <WallboxCard onOpenAddModal={() => setAddWallboxOpen(true)} />
            </div>

            {/* =========================================================
                BATTERY ARBITRAGE & GRID CO2 SIGNAL (TASK 5.16 & 5.17)
            ========================================================= */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <BatteryArbitrageCard />
                <GridCo2Card />
            </div>
            </>
            )}

            {/* =========================================================
                COMMUNITY SOCIAL SHARE MODAL
            ========================================================= */}
            <CommunityShareModal
                isOpen={shareModalOpen}
                onClose={() => setShareModalOpen(false)}
                kpis={kpis}
            />

            {/* =========================================================
                WALLBOX VERBINDEN MODAL (OCPP 1.6-J)
            ========================================================= */}
            <AddWallboxModal
                isOpen={addWallboxOpen}
                onClose={() => setAddWallboxOpen(false)}
            />

            {/* =========================================================
                SUBMETER TREND & HISTORY MODAL (TASK 5.14)
            ========================================================= */}
            <SubmeterTrendModal
                meter={selectedTrendMeter}
                isOpen={Boolean(selectedTrendMeter)}
                onClose={() => setSelectedTrendMeter(null)}
                defaultPeriod={period}
            />

            {/* =========================================================
                CUSTOM DATE RANGE PICKER MODAL (TASK 5.15)
            ========================================================= */}
            <DateRangePickerModal
                isOpen={isDatePickerOpen}
                onClose={() => setIsDatePickerOpen(false)}
                initialStart={customDates.startDate}
                initialEnd={customDates.endDate}
                onApply={(res) => {
                    setPeriod("custom");
                    setCustomDates({
                        startDate: res.startDate,
                        endDate: res.endDate,
                        label: res.label,
                    });
                }}
            />

            {/* =========================================================
                PRO UPGRADE DIALOG
            ========================================================= */}
            <ProUpgradeModal
                open={proModalOpen}
                onClose={() => setProModalOpen(false)}
                featureName={proModalFeature.name}
                featureDesc={proModalFeature.desc}
            />
        </div>
    );
}
