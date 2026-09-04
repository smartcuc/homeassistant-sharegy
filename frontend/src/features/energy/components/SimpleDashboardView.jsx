/*
# frontend/src/features/energy/components/SimpleDashboardView.jsx
*/

import { useMemo } from "react";
import { useTranslation } from "react-i18next";

export default function SimpleDashboardView({ 
    balanceData, 
    onSwitchToExpert,
    onOpenWallbox,
    onOpenBattery,
}) {
    const { t } = useTranslation();

    const kpis = balanceData?.kpis || {};
    const autarkyPct = Math.round(Number(kpis.autarky_pct ?? 78));
    const selfConsumptionPct = Math.round(Number(kpis.self_consumption_pct ?? 85));
    const savingsMonthEur = Number(kpis.savings_eur ?? 68.50).toFixed(2);

    const solarPowerW = Math.round(Number(kpis.solar_power_w ?? kpis.pv_power_w ?? 3450));
    const homePowerW = Math.round(Number(kpis.home_power_w ?? kpis.load_power_w ?? 1820));
    const gridPowerW = Math.round(Number(kpis.grid_power_w ?? -1630)); // negativ = Einspeisung, positiv = Bezug
    const batterySocPct = Math.round(Number(kpis.battery_soc_pct ?? 74));
    const batteryPowerW = Math.round(Number(kpis.battery_power_w ?? 1200)); // positiv = Laden, negativ = Entladen

    // Klartext-Status ermitteln
    const statusText = useMemo(() => {
        if (solarPowerW > 1000 && gridPowerW <= 0) {
            return {
                badge: "🟢 100% Sonnenstrom",
                badgeClass: "bg-emerald-100 text-emerald-800 border-emerald-200",
                headline: "Dein Haushalt läuft aktuell komplett autark über Solarstrom.",
                subline: `Die PV-Anlage erzeugt ${(solarPowerW / 1000).toFixed(1)} kW. Überschuss ${(Math.abs(gridPowerW) / 1000).toFixed(1)} kW fließt ins Netz bzw. in den Speicher.`,
            };
        }
        if (batteryPowerW < -200 && solarPowerW <= 300) {
            return {
                badge: "🔋 Speicher-Versorgung",
                badgeClass: "bg-amber-100 text-amber-800 border-amber-200",
                headline: "Dein Haushalt wird sauber aus dem Batteriespeicher versorgt.",
                subline: `Speicher bei ${batterySocPct}% SoC. Aktuelle Entladeleistung: ${(Math.abs(batteryPowerW) / 1000).toFixed(1)} kW.`,
            };
        }
        if (gridPowerW > 500) {
            return {
                badge: "⚡ Netzbezug aktiv",
                badgeClass: "bg-sky-100 text-sky-800 border-sky-200",
                headline: "Aktuell wird Strom aus dem öffentlichen Netz bezogen.",
                subline: `Netzbezug: ${(gridPowerW / 1000).toFixed(1)} kW · Automatische Optimierung aktiv.`,
            };
        }
        return {
            badge: "✨ Optimierter Betrieb",
            badgeClass: "bg-indigo-100 text-indigo-800 border-indigo-200",
            headline: "Energiemanagement läuft im optimalen Ausgleich.",
            subline: "Verbrauch und Erzeugung sind ausbalanciert.",
        };
    }, [solarPowerW, homePowerW, gridPowerW, batterySocPct, batteryPowerW]);

    return (
        <div className="space-y-6">
            {/* 3 HERO CARDS */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* 1. AUTARKIE HEUTE */}
                <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-xs relative overflow-hidden flex flex-col justify-between">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                            Autarkie heute
                        </span>
                        <span className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-sm font-bold">
                            ☀️
                        </span>
                    </div>

                    <div className="my-4">
                        <div className="flex items-baseline gap-2">
                            <span className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">
                                {autarkyPct}%
                            </span>
                            <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                                {autarkyPct >= 80 ? "Hervorragend" : autarkyPct >= 50 ? "Sehr gut" : "Normal"}
                            </span>
                        </div>
                        <p className="text-xs text-slate-500 mt-1">
                            Anteil deines Verbrauchs, der direkt vor Ort erzeugt wurde.
                        </p>
                    </div>

                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                        <div 
                            className="bg-emerald-500 h-full rounded-full transition-all duration-500" 
                            style={{ width: `${Math.min(100, autarkyPct)}%` }}
                        />
                    </div>
                </div>

                {/* 2. ERSPARNIS DIESEN MONAT */}
                <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-xs relative overflow-hidden flex flex-col justify-between">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                            Ersparnis diesen Monat
                        </span>
                        <span className="w-8 h-8 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center text-sm font-bold">
                            💶
                        </span>
                    </div>

                    <div className="my-4">
                        <div className="flex items-baseline gap-2">
                            <span className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">
                                {savingsMonthEur} €
                            </span>
                            <span className="text-xs font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                                Eingespart
                            </span>
                        </div>
                        <p className="text-xs text-slate-500 mt-1">
                            Vermiedene Stromkosten durch Solar, Speicher & Smart-Tarif.
                        </p>
                    </div>

                    <div className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
                        <span>🌱</span> CO₂-Einsparung: ca. {Math.round(autarkyPct * 1.8)} kg
                    </div>
                </div>

                {/* 3. AKTUELLER KLARTEXT STATUS */}
                <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-xs relative overflow-hidden flex flex-col justify-between">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                            Aktueller Status
                        </span>
                        <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${statusText.badgeClass}`}>
                            {statusText.badge}
                        </span>
                    </div>

                    <div className="my-3 space-y-1">
                        <h3 className="text-sm font-bold text-slate-900 leading-snug">
                            {statusText.headline}
                        </h3>
                        <p className="text-xs text-slate-500 leading-relaxed">
                            {statusText.subline}
                        </p>
                    </div>

                    <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600">
                        <span>Eigenverbrauch: <strong>{selfConsumptionPct}%</strong></span>
                        <span>Speicher: <strong>{batterySocPct}%</strong></span>
                    </div>
                </div>
            </div>

            {/* MINIMAL LIVE ENERGY FLOW DIAGRAM */}
            <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-xs space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-base font-bold text-slate-900">
                            ⚡ Aktueller Energiefluss auf einen Blick
                        </h2>
                        <p className="text-xs text-slate-500">
                            Live-Werte deiner Energiezentrale in Echtzeit.
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={onSwitchToExpert}
                        className="text-xs font-semibold text-sky-600 hover:text-sky-800 bg-sky-50 hover:bg-sky-100 px-3 py-1.5 rounded-xl border border-sky-200 transition cursor-pointer flex items-center gap-1.5"
                    >
                        <span>⚙️</span>
                        Experten-Ansicht öffnen
                    </button>
                </div>

                {/* VISUAL FLOW CARDS */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
                    {/* PV ERZEUGUNG */}
                    <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200/70 flex flex-col items-center text-center">
                        <div className="w-10 h-10 rounded-full bg-amber-400 text-white flex items-center justify-center text-xl shadow-xs mb-2">
                            ☀️
                        </div>
                        <span className="text-[11px] font-bold uppercase tracking-wider text-amber-900">
                            Photovoltaik
                        </span>
                        <span className="text-2xl font-extrabold text-amber-950 mt-1">
                            {(solarPowerW / 1000).toFixed(2)} <span className="text-sm font-semibold">kW</span>
                        </span>
                        <span className="text-[10px] text-amber-700 mt-0.5">
                            {solarPowerW > 0 ? "Erzeugt Strom" : "Ruhend"}
                        </span>
                    </div>

                    {/* HAUSVERBRAUCH */}
                    <div className="p-4 rounded-2xl bg-rose-50/70 border border-rose-200/70 flex flex-col items-center text-center">
                        <div className="w-10 h-10 rounded-full bg-rose-500 text-white flex items-center justify-center text-xl shadow-xs mb-2">
                            🏠
                        </div>
                        <span className="text-[11px] font-bold uppercase tracking-wider text-rose-900">
                            Hausverbrauch
                        </span>
                        <span className="text-2xl font-extrabold text-rose-950 mt-1">
                            {(homePowerW / 1000).toFixed(2)} <span className="text-sm font-semibold">kW</span>
                        </span>
                        <span className="text-[10px] text-rose-700 mt-0.5">
                            Aktuelle Gesamtsumme
                        </span>
                    </div>

                    {/* BATTERIESPEICHER */}
                    <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200/70 flex flex-col items-center text-center">
                        <div className="w-10 h-10 rounded-full bg-emerald-500 text-white flex items-center justify-center text-xl shadow-xs mb-2">
                            🔋
                        </div>
                        <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-900">
                            Batterie ({batterySocPct}%)
                        </span>
                        <span className="text-2xl font-extrabold text-emerald-950 mt-1">
                            {(Math.abs(batteryPowerW) / 1000).toFixed(2)} <span className="text-sm font-semibold">kW</span>
                        </span>
                        <span className="text-[10px] text-emerald-700 mt-0.5">
                            {batteryPowerW > 100 ? "Lädt auf ⚡" : batteryPowerW < -100 ? "Entlädt ins Haus 🏠" : "Standby"}
                        </span>
                    </div>

                    {/* NETZ / STROMNETZ */}
                    <div className={`p-4 rounded-2xl border flex flex-col items-center text-center ${gridPowerW <= 0 ? "bg-sky-50/70 border-sky-200/70" : "bg-purple-50/70 border-purple-200/70"}`}>
                        <div className={`w-10 h-10 rounded-full text-white flex items-center justify-center text-xl shadow-xs mb-2 ${gridPowerW <= 0 ? "bg-sky-500" : "bg-purple-600"}`}>
                            ⚡
                        </div>
                        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-800">
                            {gridPowerW <= 0 ? "Netzeinspeisung" : "Netzbezug"}
                        </span>
                        <span className="text-2xl font-extrabold text-slate-900 mt-1">
                            {(Math.abs(gridPowerW) / 1000).toFixed(2)} <span className="text-sm font-semibold">kW</span>
                        </span>
                        <span className={`text-[10px] mt-0.5 ${gridPowerW <= 0 ? "text-sky-700" : "text-purple-700"}`}>
                            {gridPowerW <= 0 ? "Verkauf ins Netz" : "Zukauf aus dem Netz"}
                        </span>
                    </div>
                </div>

                {/* QUICK ACTIONS BANNER */}
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl flex flex-wrap items-center justify-between gap-3 text-xs">
                    <div className="flex items-center gap-3">
                        <span className="text-lg">💡</span>
                        <span className="text-slate-700 font-medium">
                            Möchtest du detaillierte Phasenströme (L1/L2/L3), Sankey-Diagramme, SG-Ready Wärmepumpen oder Börsenpreis-Arbitrage steuern?
                        </span>
                    </div>

                    <button
                        type="button"
                        onClick={onSwitchToExpert}
                        className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl shadow-xs transition cursor-pointer"
                    >
                        Zu den Experten-Tools &rarr;
                    </button>
                </div>
            </div>
        </div>
    );
}
