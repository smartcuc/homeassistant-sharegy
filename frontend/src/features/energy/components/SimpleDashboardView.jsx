/*
# frontend/src/features/energy/components/SimpleDashboardView.jsx
# Einfach-Modus: Verständliche, intuitive Energiebilanz mit 100% echten Live- und Periodenwerten
*/

import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { 
    Sun, 
    Home, 
    Battery, 
    Zap, 
    TrendingUp, 
    ShieldCheck, 
    ArrowUpRight, 
    ArrowDownRight, 
    Leaf, 
    Lightbulb, 
    Sparkles, 
    Car, 
    Sliders 
} from "lucide-react";

export default function SimpleDashboardView({ 
    balanceData = {}, 
    liveData = {},
    period = "today",
    periodLabel = "Heute",
    onSwitchToExpert,
    onOpenWallbox,
}) {
    const { t } = useTranslation();

    // 1. Perioden-KPIs (Echte Aggregatwerte für den ausgewählten Zeitraum)
    const kpis = balanceData.kpis || {};
    const submeters = balanceData.submeters || [];
    const insights = balanceData.insights || [];

    const autarkyRate = Math.round(Number(kpis.autarky_rate ?? kpis.autarky_pct ?? 0));
    const selfConsumptionRate = Math.round(Number(kpis.self_consumption_rate ?? kpis.self_consumption_pct ?? 0));
    const savingsEur = Number(kpis.savings_eur ?? 0);
    const netBenefitEur = Number(kpis.net_benefit_eur ?? savingsEur);
    const co2SavedKg = Number(kpis.co2_saved_kg ?? (kpis.solar_supplied_kwh ? kpis.solar_supplied_kwh * 0.4 : 0));
    
    const pvGenerationKwh = Number(kpis.pv_generation_kwh ?? 0);
    const houseConsumptionKwh = Number(kpis.house_consumption_kwh ?? 0);
    const gridImportKwh = Number(kpis.grid_import_kwh ?? 0);
    const gridExportKwh = Number(kpis.grid_export_kwh ?? 0);
    const batteryChargeKwh = Number(kpis.battery_charge_kwh ?? 0);
    const batteryDischargeKwh = Number(kpis.battery_discharge_kwh ?? 0);

    // 2. Echtzeit Live-Werte (Aus Live-Stream / Dashboard-Me)
    const liveKpis = liveData.kpis || {};
    const solarPowerW = Math.round(Number(liveData.pv_power_w ?? liveKpis.pv ?? liveKpis.pv_power_w ?? 0));
    const homePowerW = Math.round(Number(liveData.load_power_w ?? liveKpis.load ?? liveKpis.load_power_w ?? 0));
    const gridPowerW = Math.round(Number(liveData.grid_power_w ?? liveKpis.grid ?? liveKpis.grid_power_w ?? 0)); // negativ = Einspeisung, positiv = Bezug
    const batteryPowerW = Math.round(Number(liveData.battery_power_w ?? liveKpis.battery ?? liveKpis.battery_power_w ?? 0)); // negativ = Entladen, positiv = Laden
    const batterySocPct = liveData.battery_soc_pct !== undefined && liveData.battery_soc_pct !== null
        ? Math.round(Number(liveData.battery_soc_pct))
        : (liveKpis.battery_soc_pct !== undefined ? Math.round(Number(liveKpis.battery_soc_pct)) : null);

    // 3. Formatierungshilfen
    const formatPower = (watts) => {
        const abs = Math.abs(watts);
        if (abs >= 1000) {
            return `${(watts / 1000).toFixed(2)} kW`;
        }
        return `${Math.round(watts)} W`;
    };

    const formatKwh = (val) => {
        return Number(val || 0).toLocaleString("de-DE", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    };

    // 4. Klartext-Status ermitteln (Basiert auf den 100% echten Live-Werten)
    const statusText = useMemo(() => {
        if (solarPowerW > 200 && gridPowerW <= 20) {
            const surplusW = Math.abs(Math.min(0, gridPowerW));
            return {
                badge: "🟢 100% Sonnenstrom",
                badgeClass: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-900/50",
                headline: "Dein Haushalt läuft aktuell autark über die Solaranlage.",
                subline: surplusW > 50 
                    ? `Die PV erzeugt ${formatPower(solarPowerW)}. Überschuss von ${formatPower(surplusW)} fließt ins Netz bzw. in den Speicher.`
                    : `Die Solaranlage deckt deinen aktuellen Hausverbrauch von ${formatPower(homePowerW)} ab.`,
            };
        }
        if (batteryPowerW < -100 && solarPowerW <= 200) {
            return {
                badge: "🔋 Speicher-Versorgung",
                badgeClass: "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200 dark:border-amber-900/50",
                headline: "Dein Haushalt wird aus dem Batteriespeicher versorgt.",
                subline: batterySocPct !== null 
                    ? `Akkustand liegt bei ${batterySocPct}%. Entladeleistung: ${formatPower(Math.abs(batteryPowerW))}.`
                    : `Aktuelle Entladeleistung: ${formatPower(Math.abs(batteryPowerW))}.`,
            };
        }
        if (gridPowerW > 100) {
            return {
                badge: "⚡ Netzbezug aktiv",
                badgeClass: "bg-sky-100 text-sky-800 dark:bg-sky-950/60 dark:text-sky-300 border-sky-200 dark:border-sky-900/50",
                headline: "Aktuell wird Strom aus dem öffentlichen Netz bezogen.",
                subline: `Netzbezug: ${formatPower(gridPowerW)} · Optimiertes Lastmanagement aktiv.`,
            };
        }
        if (gridPowerW < -100) {
            return {
                badge: "📤 Netzeinspeisung",
                badgeClass: "bg-teal-100 text-teal-800 dark:bg-teal-950/60 dark:text-teal-300 border-teal-200 dark:border-teal-900/50",
                headline: "Solarüberschuss wird ins Stromnetz eingespeist.",
                subline: `Einspeisung: ${formatPower(Math.abs(gridPowerW))} zu deinem garantierten Vergütungstarif.`,
            };
        }
        return {
            badge: "✨ Ausgeglichener Betrieb",
            badgeClass: "bg-indigo-100 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300 border-indigo-200 dark:border-indigo-900/50",
            headline: "Energiemanagement läuft im optimalen Gleichgewicht.",
            subline: "Erzeugung, Speichernutzung und Hausverbrauch sind optimal austariert.",
        };
    }, [solarPowerW, homePowerW, gridPowerW, batteryPowerW, batterySocPct]);

    return (
        <div className="space-y-6">
            {/* =========================================================
                1. DREI HERO HIGHLIGHT-KARTEN
            ========================================================= */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                
                {/* 1. AUTARKIEGRAD IM ZEITRAUM */}
                <div className="bg-white dark:bg-slate-900 rounded-3xl p-5 sm:p-6 border border-slate-200/90 dark:border-slate-800 shadow-xs relative overflow-hidden flex flex-col justify-between group hover:border-emerald-400 dark:hover:border-emerald-500/50 transition-all">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                            <ShieldCheck className="w-4 h-4 text-emerald-500" />
                            Autarkie ({periodLabel})
                        </span>
                        <span className="w-8 h-8 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-sm font-bold border border-emerald-200 dark:border-emerald-900/50">
                            🛡️
                        </span>
                    </div>

                    <div className="my-4">
                        <div className="flex items-baseline gap-2.5">
                            <span className="text-4xl sm:text-5xl font-black text-slate-900 dark:text-white tracking-tight font-mono">
                                {autarkyRate}%
                            </span>
                            <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${
                                autarkyRate >= 75 
                                    ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800" 
                                    : autarkyRate >= 40 
                                        ? "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800" 
                                        : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700"
                            }`}>
                                {autarkyRate >= 75 ? "Exzellent" : autarkyRate >= 40 ? "Gut" : "Basis"}
                            </span>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5 leading-relaxed">
                            {autarkyRate}% deines Strombedarfs stammten direkt aus deiner eigenen Solaranlage & Speicher.
                        </p>
                    </div>

                    <div className="w-full bg-slate-100 dark:bg-slate-800 h-2.5 rounded-full overflow-hidden">
                        <div 
                            className="bg-emerald-500 h-full rounded-full transition-all duration-700" 
                            style={{ width: `${Math.min(100, Math.max(0, autarkyRate))}%` }}
                        />
                    </div>
                </div>

                {/* 2. FINANZVORTEIL & ERSPARNIS */}
                <div className="bg-white dark:bg-slate-900 rounded-3xl p-5 sm:p-6 border border-slate-200/90 dark:border-slate-800 shadow-xs relative overflow-hidden flex flex-col justify-between group hover:border-amber-400 dark:hover:border-amber-500/50 transition-all">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                            <TrendingUp className="w-4 h-4 text-amber-500" />
                            Finanzvorteil ({periodLabel})
                        </span>
                        <span className="w-8 h-8 rounded-full bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center text-sm font-bold border border-amber-200 dark:border-amber-900/50">
                            💶
                        </span>
                    </div>

                    <div className="my-4">
                        <div className="flex items-baseline gap-2">
                            <span className="text-4xl sm:text-5xl font-black text-slate-900 dark:text-white tracking-tight font-mono">
                                {netBenefitEur >= 0 ? "+" : ""}{netBenefitEur.toFixed(2)} €
                            </span>
                            <span className="text-xs font-bold text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/60 px-2 py-0.5 rounded-full border border-amber-200 dark:border-amber-900/50">
                                Eingespart
                            </span>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5 leading-relaxed">
                            Vermiedene Stromkosten durch Eigenverbrauch zzgl. Einspeisevergütung.
                        </p>
                    </div>

                    <div className="text-[11px] text-slate-500 dark:text-slate-400 font-medium flex items-center justify-between pt-1 border-t border-slate-100 dark:border-slate-800">
                        <span className="flex items-center gap-1">
                            <Leaf className="w-3.5 h-3.5 text-emerald-500" />
                            CO₂ vermieden: <strong className="text-slate-700 dark:text-slate-300">{formatKwh(co2SavedKg)} kg</strong>
                        </span>
                        <span>
                            Eigenverbrauch: <strong className="text-slate-700 dark:text-slate-300">{selfConsumptionRate}%</strong>
                        </span>
                    </div>
                </div>

                {/* 3. AKTUELLER ECHTZEIT-STATUS */}
                <div className="bg-white dark:bg-slate-900 rounded-3xl p-5 sm:p-6 border border-slate-200/90 dark:border-slate-800 shadow-xs relative overflow-hidden flex flex-col justify-between group hover:border-indigo-400 dark:hover:border-indigo-500/50 transition-all">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                            <Zap className="w-4 h-4 text-indigo-500" />
                            Echtzeit-Zustand
                        </span>
                        <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${statusText.badgeClass}`}>
                            {statusText.badge}
                        </span>
                    </div>

                    <div className="my-3 space-y-1.5">
                        <h3 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white leading-snug">
                            {statusText.headline}
                        </h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                            {statusText.subline}
                        </p>
                    </div>

                    <div className="pt-2.5 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
                        <span>
                            Live Solar: <strong className="font-mono text-slate-900 dark:text-white">{formatPower(solarPowerW)}</strong>
                        </span>
                        {batterySocPct !== null && (
                            <span>
                                Akku: <strong className="font-mono text-slate-900 dark:text-white">{batterySocPct}%</strong>
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {/* =========================================================
                2. LIVE ENERGIEFLUSS-KACHELN (ECHTZEIT-ÜBERSICHT)
            ========================================================= */}
            <div className="bg-white dark:bg-slate-900 rounded-3xl p-5 sm:p-6 border border-slate-200/90 dark:border-slate-800 shadow-xs space-y-6">
                <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                        <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <span className="relative flex h-2.5 w-2.5">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                            </span>
                            Live Energiefluss deiner Anlage
                        </h2>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            Echtzeit-Messwerte aller Hauptkomponenten im aktuellen Moment.
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={onSwitchToExpert}
                        className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/60 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 px-3.5 py-2 rounded-xl border border-indigo-200 dark:border-indigo-900/50 transition cursor-pointer flex items-center gap-1.5 shadow-2xs"
                    >
                        <Sliders className="w-3.5 h-3.5" />
                        Experten-Ansicht öffnen
                    </button>
                </div>

                {/* 4 INTERAKTIVE LIVE CARDS */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5 sm:gap-4">
                    
                    {/* ☀️ PHOTOVOLTAIK */}
                    <div className="p-4 sm:p-5 rounded-2xl bg-amber-50/60 dark:bg-amber-950/25 border border-amber-200/80 dark:border-amber-900/40 flex flex-col justify-between">
                        <div className="flex items-center justify-between mb-2">
                            <div className="w-9 h-9 rounded-xl bg-amber-400 dark:bg-amber-500 text-white flex items-center justify-center text-lg shadow-2xs">
                                ☀️
                            </div>
                            <span className="text-[10px] font-bold uppercase tracking-wider text-amber-800 dark:text-amber-300 bg-amber-100/80 dark:bg-amber-900/50 px-2 py-0.5 rounded-md">
                                Erzeugung
                            </span>
                        </div>
                        <div>
                            <span className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-amber-100 font-mono tracking-tight">
                                {formatPower(solarPowerW)}
                            </span>
                            <div className="text-xs text-amber-800 dark:text-amber-300 font-semibold mt-1 flex items-center justify-between">
                                <span>{solarPowerW > 20 ? "Aktiv" : "Ruhend"}</span>
                                <span className="text-slate-500 dark:text-slate-400 font-normal">
                                    Gesamt: {formatKwh(pvGenerationKwh)} kWh
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* 🏠 HAUSVERBRAUCH */}
                    <div className="p-4 sm:p-5 rounded-2xl bg-rose-50/60 dark:bg-rose-950/25 border border-rose-200/80 dark:border-rose-900/40 flex flex-col justify-between">
                        <div className="flex items-center justify-between mb-2">
                            <div className="w-9 h-9 rounded-xl bg-rose-500 text-white flex items-center justify-center text-lg shadow-2xs">
                                🏠
                            </div>
                            <span className="text-[10px] font-bold uppercase tracking-wider text-rose-800 dark:text-rose-300 bg-rose-100/80 dark:bg-rose-900/50 px-2 py-0.5 rounded-md">
                                Haushalt
                            </span>
                        </div>
                        <div>
                            <span className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-rose-100 font-mono tracking-tight">
                                {formatPower(homePowerW)}
                            </span>
                            <div className="text-xs text-rose-800 dark:text-rose-300 font-semibold mt-1 flex items-center justify-between">
                                <span>Bedarf</span>
                                <span className="text-slate-500 dark:text-slate-400 font-normal">
                                    Gesamt: {formatKwh(houseConsumptionKwh)} kWh
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* 🔋 BATTERIESPEICHER */}
                    <div className="p-4 sm:p-5 rounded-2xl bg-emerald-50/60 dark:bg-emerald-950/25 border border-emerald-200/80 dark:border-emerald-900/40 flex flex-col justify-between">
                        <div className="flex items-center justify-between mb-2">
                            <div className="w-9 h-9 rounded-xl bg-emerald-500 text-white flex items-center justify-center text-lg shadow-2xs">
                                🔋
                            </div>
                            <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 dark:text-emerald-300 bg-emerald-100/80 dark:bg-emerald-900/50 px-2 py-0.5 rounded-md font-mono">
                                {batterySocPct !== null ? `${batterySocPct}% SoC` : "Speicher"}
                            </span>
                        </div>
                        <div>
                            <span className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-emerald-100 font-mono tracking-tight">
                                {formatPower(Math.abs(batteryPowerW))}
                            </span>
                            <div className="text-xs text-emerald-800 dark:text-emerald-300 font-semibold mt-1 flex items-center justify-between">
                                <span>{batteryPowerW > 100 ? "⚡ Lädt" : batteryPowerW < -100 ? "🏠 Entlädt" : "Standby"}</span>
                                <span className="text-slate-500 dark:text-slate-400 font-normal">
                                    Ladung: {formatKwh(batteryChargeKwh)} kWh
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* ⚡ STROMNETZ */}
                    <div className={`p-4 sm:p-5 rounded-2xl border flex flex-col justify-between ${
                        gridPowerW <= 0 
                            ? "bg-sky-50/60 dark:bg-sky-950/25 border-sky-200/80 dark:border-sky-900/40" 
                            : "bg-purple-50/60 dark:bg-purple-950/25 border-purple-200/80 dark:border-purple-900/40"
                    }`}>
                        <div className="flex items-center justify-between mb-2">
                            <div className={`w-9 h-9 rounded-xl text-white flex items-center justify-center text-lg shadow-2xs ${
                                gridPowerW <= 0 ? "bg-sky-500" : "bg-purple-600"
                            }`}>
                                ⚡
                            </div>
                            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md ${
                                gridPowerW <= 0 
                                    ? "bg-sky-100/80 dark:bg-sky-900/50 text-sky-800 dark:text-sky-300" 
                                    : "bg-purple-100/80 dark:bg-purple-900/50 text-purple-800 dark:text-purple-300"
                            }`}>
                                {gridPowerW <= 0 ? "Einspeisung" : "Netzbezug"}
                            </span>
                        </div>
                        <div>
                            <span className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white font-mono tracking-tight">
                                {gridPowerW < 0 ? `+${formatPower(Math.abs(gridPowerW))}` : formatPower(gridPowerW)}
                            </span>
                            <div className="text-xs font-semibold mt-1 flex items-center justify-between">
                                <span className={gridPowerW <= 0 ? "text-sky-700 dark:text-sky-300" : "text-purple-700 dark:text-purple-300"}>
                                    {gridPowerW <= 0 ? "📤 Einspeisen" : "📥 Bezug"}
                                </span>
                                <span className="text-slate-500 dark:text-slate-400 font-normal">
                                    {gridPowerW <= 0 ? `${formatKwh(gridExportKwh)} kWh` : `${formatKwh(gridImportKwh)} kWh`}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* =========================================================
                    3. BILANZ-GEGENÜBERSTELLUNG & SUBMETER (TOP VERBRAUCHER)
                ========================================================= */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 pt-2">
                    
                    {/* LINKE SPALTE: PERIODEN-BILANZ */}
                    <div className="p-4 sm:p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-800 space-y-4">
                        <div className="flex items-center justify-between">
                            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                <span>📊</span> Gesamtenergie im Zeitraum ({periodLabel})
                            </h3>
                            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 font-mono">
                                kWh-Bilanz
                            </span>
                        </div>

                        <div className="space-y-2.5">
                            {/* Erzeugung */}
                            <div className="flex items-center justify-between text-xs">
                                <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
                                    <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" />
                                    Solarerzeugung gesamt
                                </span>
                                <span className="font-bold font-mono text-slate-900 dark:text-white">
                                    {formatKwh(pvGenerationKwh)} kWh
                                </span>
                            </div>

                            {/* Hausverbrauch */}
                            <div className="flex items-center justify-between text-xs">
                                <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
                                    <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block" />
                                    Gesamter Hausverbrauch
                                </span>
                                <span className="font-bold font-mono text-slate-900 dark:text-white">
                                    {formatKwh(houseConsumptionKwh)} kWh
                                </span>
                            </div>

                            {/* Netzbezug */}
                            <div className="flex items-center justify-between text-xs">
                                <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
                                    <span className="w-2.5 h-2.5 rounded-full bg-purple-500 inline-block" />
                                    Netzstrom bezogen
                                </span>
                                <span className="font-bold font-mono text-slate-900 dark:text-white">
                                    {formatKwh(gridImportKwh)} kWh
                                </span>
                            </div>

                            {/* Netzeinspeisung */}
                            <div className="flex items-center justify-between text-xs">
                                <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
                                    <span className="w-2.5 h-2.5 rounded-full bg-sky-500 inline-block" />
                                    Solarstrom eingespeist
                                </span>
                                <span className="font-bold font-mono text-slate-900 dark:text-white">
                                    {formatKwh(gridExportKwh)} kWh
                                </span>
                            </div>
                        </div>

                        {/* Visuelle Aufteilung */}
                        {houseConsumptionKwh > 0 && (
                            <div className="pt-2 border-t border-slate-200/80 dark:border-slate-700/60">
                                <div className="flex justify-between text-[11px] font-semibold text-slate-500 dark:text-slate-400 mb-1">
                                    <span>Deckung des Verbrauchs:</span>
                                    <span>{autarkyRate}% Solar & Akku · {Math.max(0, 100 - autarkyRate)}% Netz</span>
                                </div>
                                <div className="w-full h-3 rounded-full bg-slate-200 dark:bg-slate-700 flex overflow-hidden">
                                    <div 
                                        className="bg-emerald-500 h-full transition-all duration-500" 
                                        style={{ width: `${Math.min(100, autarkyRate)}%` }}
                                        title={`Solaranteil: ${autarkyRate}%`}
                                    />
                                    <div 
                                        className="bg-purple-500 h-full transition-all duration-500" 
                                        style={{ width: `${Math.max(0, 100 - autarkyRate)}%` }}
                                        title={`Netzanteil: ${Math.max(0, 100 - autarkyRate)}%`}
                                    />
                                </div>
                            </div>
                        )}
                    </div>

                    {/* RECHTE SPALTE: TOP VERBRAUCHER */}
                    <div className="p-4 sm:p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-800 flex flex-col justify-between">
                        <div>
                            <div className="flex items-center justify-between mb-3">
                                <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                    <span>🔌</span> Größte Stromverbraucher
                                </h3>
                                <Link 
                                    to="/app/devices" 
                                    className="text-[11px] font-bold text-indigo-600 dark:text-indigo-400 hover:underline"
                                >
                                    Geräte verwalten &rarr;
                                </Link>
                            </div>

                            {submeters.length > 0 ? (
                                <div className="space-y-2">
                                    {submeters.slice(0, 4).map((sub) => (
                                        <div 
                                            key={sub.id} 
                                            className="flex items-center justify-between p-2 rounded-xl bg-white dark:bg-slate-850 border border-slate-200/60 dark:border-slate-700/60 shadow-2xs"
                                        >
                                            <div className="flex items-center gap-2 min-w-0">
                                                <span className="text-base shrink-0">{sub.icon || "⚡"}</span>
                                                <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate">
                                                    {sub.name}
                                                </span>
                                            </div>
                                            <div className="flex items-center gap-3 shrink-0">
                                                <span className="text-xs font-mono font-bold text-slate-900 dark:text-white">
                                                    {formatKwh(sub.consumption_kwh)} kWh
                                                </span>
                                                <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 min-w-[40px] text-right font-mono">
                                                    {sub.share_pct}%
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="py-6 text-center text-xs text-slate-500 dark:text-slate-400">
                                    Noch keine Einzelgeräte erfasst. Verbinde deine Wallbox, Wärmepumpe oder Schaltsteckdosen.
                                </div>
                            )}
                        </div>

                        {/* INSIGHTS FOOTER */}
                        {insights.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-slate-200/80 dark:border-slate-700/60 flex items-start gap-2 text-xs text-indigo-950 dark:text-indigo-200">
                                <Sparkles className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
                                <span className="font-medium line-clamp-2">{insights[0]}</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* QUICK ACTIONS BANNER */}
                <div className="p-4 bg-linear-to-r from-slate-100 to-indigo-50/60 dark:from-slate-800/80 dark:to-indigo-950/40 border border-slate-200 dark:border-slate-700 rounded-2xl flex flex-wrap items-center justify-between gap-3 text-xs">
                    <div className="flex items-center gap-3">
                        <span className="text-xl">💡</span>
                        <span className="text-slate-700 dark:text-slate-300 font-medium">
                            Möchtest du detaillierte Phasenströme (L1/L2/L3), Sankey-Energieflüsse, SG-Ready Wärmepumpen oder Börsenpreis-Arbitrage steuern?
                        </span>
                    </div>

                    <button
                        type="button"
                        onClick={onSwitchToExpert}
                        className="px-4 py-2 bg-slate-900 dark:bg-white hover:bg-slate-800 dark:hover:bg-slate-100 text-white dark:text-slate-900 font-bold rounded-xl shadow-xs transition cursor-pointer shrink-0"
                    >
                        Zu den Experten-Tools &rarr;
                    </button>
                </div>
            </div>
        </div>
    );
}

