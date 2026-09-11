/*
# src/features/energy/components/VppAggregatorCockpit.jsx
# Virtuelles Kraftwerk (VPP) Cockpit: Flexibilität, aFRR/SRL, FCR & Redispatch 2.0
*/

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function VppAggregatorCockpit() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const [selectedTso, setSelectedTso] = useState("50hertz");
    const [targetPowerKw, setTargetPowerKw] = useState(50);
    const [durationMinutes, setDurationMinutes] = useState(15);
    const [dispatchType, setDispatchType] = useState("positive_flex");
    const [dispatchResult, setDispatchResult] = useState(null);
    const [showVppGlossary, setShowVppGlossary] = useState(false);

    // 1. VPP Summary Query
    const summaryQuery = useQuery({
        queryKey: ["vpp-summary", selectedTso],
        queryFn: () => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            return apiFetch(`/api/vpp/summary/?tso=${selectedTso}`, {
                headers: { Authorization: token ? `Bearer ${token}` : "" },
            });
        },
        refetchInterval: 10000,
    });

    // 2. Redispatch Schedule Query
    const scheduleQuery = useQuery({
        queryKey: ["vpp-schedule", selectedTso],
        queryFn: () => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            return apiFetch(`/api/vpp/redispatch-schedule/?tso=${selectedTso}`, {
                headers: { Authorization: token ? `Bearer ${token}` : "" },
            });
        },
    });

    // 3. Dispatch Mutation
    const dispatchMutation = useMutation({
        mutationFn: async () => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            return apiFetch("/api/vpp/dispatch/", {
                method: "POST",
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    target_power_kw: Number(targetPowerKw),
                    duration_minutes: Number(durationMinutes),
                    dispatch_type: dispatchType,
                    requested_by: `${selectedTso.toUpperCase()} Automated Leitsystem`,
                }),
            });
        },
        onSuccess: (res) => {
            setDispatchResult(res);
            queryClient.invalidateQueries(["vpp-summary"]);
        },
    });

    const summary = summaryQuery.data?.summary || {
        total_available_positive_flex_kw: 0,
        total_available_negative_flex_kw: 0,
        total_active_assets_count: 0,
        response_time_seconds: 15,
    };
    const battery = summaryQuery.data?.battery_fleet || {
        assets_count: 0,
        total_capacity_kwh: 0,
        total_stored_energy_kwh: 0,
        average_soc_pct: 0,
        available_discharge_power_kw: 0,
        available_charge_power_kw: 0,
    };
    const steuve = summaryQuery.data?.steuve_and_loads || {
        assets_count: 0,
        curtailable_power_kw: 0,
    };
    const schedule = scheduleQuery.data?.schedule || [];

    return (
        <div className="space-y-6">

            {/* HEADER */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs">
                <div>
                    <div className="flex items-center gap-2">
                        <span className="text-2xl">⚡</span>
                        <h2 className="text-base font-black text-slate-900 dark:text-white">
                            Virtuelles Kraftwerk (VPP) & Netzstabilitäts-Pool
                        </h2>
                        <span className="bg-amber-500/10 text-amber-600 dark:text-amber-400 text-[10px] font-extrabold px-2 py-0.5 rounded-full border border-amber-500/20">
                            Netzdienlichkeit & § 14a EnWG
                        </span>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                        Bündelung unserer Hausspeicher und steuerbaren Lasten (Wallboxen, Wärmepumpen) zur Stabilisierung des Stromnetzes.
                    </p>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                    <button
                        onClick={() => setShowVppGlossary(!showVppGlossary)}
                        className={`text-xs font-bold px-3 py-1.5 rounded-xl border transition cursor-pointer flex items-center gap-1.5 ${
                            showVppGlossary
                                ? "bg-amber-500/20 border-amber-500/40 text-amber-700 dark:text-amber-300"
                                : "bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200"
                        }`}
                    >
                        <span>💡</span>
                        <span>{showVppGlossary ? "Erklärungen ausblenden" : "Einfache Erklärung"}</span>
                    </button>

                    <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
                        <span className="text-xs text-slate-500 font-medium">Netzbetreiber (ÜNB):</span>
                        <select
                            value={selectedTso}
                            onChange={(e) => setSelectedTso(e.target.value)}
                            className="bg-transparent text-xs font-bold text-slate-900 dark:text-white focus:outline-hidden cursor-pointer"
                        >
                            <option value="50hertz">50Hertz Transmission</option>
                            <option value="tennet">TenneT TSO</option>
                            <option value="amprion">Amprion</option>
                            <option value="transnetbw">TransnetBW</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* LAIEN-GLOSSAR FÜR VPP & REGELLEISTUNG */}
            {showVppGlossary && (
                <div className="bg-amber-500/10 border border-amber-500/20 p-5 rounded-2xl animate-fade-in space-y-3">
                    <div className="flex items-center justify-between">
                        <h3 className="text-xs font-black uppercase tracking-wider text-amber-900 dark:text-amber-200 flex items-center gap-1.5">
                            <span>📖</span> Was bedeuten diese Begriffe im Alltag?
                        </h3>
                        <button
                            onClick={() => setShowVppGlossary(false)}
                            className="text-amber-700 dark:text-amber-300 text-xs font-bold hover:underline"
                        >
                            Schließen ✕
                        </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                        <div className="p-3 bg-white/80 dark:bg-slate-900/80 rounded-xl border border-amber-500/10">
                            <div className="font-bold text-slate-900 dark:text-white mb-1">🔋 Virtuelles Kraftwerk (VPP)</div>
                            <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
                                Einzelne Heimbatterien sind zu klein für den großen Strommarkt. Sharegy bündelt 50 oder 500 Speicher digital zu einem großen "virtuellen Großspeicher", der bei Stromknappheit einspringen kann.
                            </p>
                        </div>
                        <div className="p-3 bg-white/80 dark:bg-slate-900/80 rounded-xl border border-amber-500/10">
                            <div className="font-bold text-slate-900 dark:text-white mb-1">🚗 § 14a EnWG Steuerbare Lasten</div>
                            <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
                                Wenn das örtliche Stromnetz droht zu überlasten, darf der Netzbetreiber Wallboxen und Wärmepumpen kurzzeitig auf 4,2 kW drosseln. Als Belohnung erhält jeder Haushalt einen pauschalen Netzentgelt-Rabatt von ca. 160 € pro Jahr.
                            </p>
                        </div>
                        <div className="p-3 bg-white/80 dark:bg-slate-900/80 rounded-xl border border-amber-500/10">
                            <div className="font-bold text-slate-900 dark:text-white mb-1">📈 96-Viertelstunden-Fahrplan (Redispatch)</div>
                            <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
                                Der Netzbetreiber bekommt für den nächsten Tag 96 Planwerte (alle 15 Minuten einen), wie viel Strom unsere Gemeinschaft einspeist oder puffern kann. So werden teure Blackouts und Stromstaus verhindert.
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* FLEXIBILITÄTS-KAPAZITÄTEN GRID */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {/* 1. Positive Regelleistung (+kW) */}
                <div className="bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-2xl">
                    <div className="flex items-center justify-between text-emerald-600 dark:text-emerald-400 text-xs font-bold mb-1">
                        <span>⚡ Positive Flexibilität (+kW)</span>
                        <span className="text-base">📈</span>
                    </div>
                    <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
                        +{summary.total_available_positive_flex_kw.toFixed(1)} <span className="text-xs font-normal text-slate-500">kW</span>
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                        Speicher-Entladung + § 14a Lastabwurf
                    </div>
                </div>

                {/* 2. Negative Regelleistung (-kW) */}
                <div className="bg-blue-500/5 dark:bg-blue-500/10 border border-blue-500/20 p-4 rounded-2xl">
                    <div className="flex items-center justify-between text-blue-600 dark:text-blue-400 text-xs font-bold mb-1">
                        <span>🔋 Negative Flexibilität (-kW)</span>
                        <span className="text-base">📉</span>
                    </div>
                    <div className="text-2xl font-black text-blue-600 dark:text-blue-400">
                        -{summary.total_available_negative_flex_kw.toFixed(1)} <span className="text-xs font-normal text-slate-500">kW</span>
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                        Netz-Laden + PV-Abregelung
                    </div>
                </div>

                {/* 3. Speicherflotte */}
                <div className="bg-indigo-500/5 dark:bg-indigo-500/10 border border-indigo-500/20 p-4 rounded-2xl">
                    <div className="flex items-center justify-between text-indigo-600 dark:text-indigo-400 text-xs font-bold mb-1">
                        <span>🔋 Heimspeicher ({battery.assets_count})</span>
                        <span className="text-base">⚡</span>
                    </div>
                    <div className="text-2xl font-black text-slate-900 dark:text-white">
                        {battery.total_stored_energy_kwh.toFixed(1)} <span className="text-xs font-normal text-slate-500">/ {battery.total_capacity_kwh.toFixed(1)} kWh</span>
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                        Mittlerer Ladestand: <strong className="text-indigo-600 dark:text-indigo-400">{battery.average_soc_pct.toFixed(0)}% SoC</strong>
                    </div>
                </div>

                {/* 4. § 14a EnWG Lasten */}
                <div className="bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 p-4 rounded-2xl">
                    <div className="flex items-center justify-between text-amber-600 dark:text-amber-400 text-xs font-bold mb-1">
                        <span>🚗 § 14a SteuVE ({steuve.assets_count})</span>
                        <span className="text-base">🛡️</span>
                    </div>
                    <div className="text-2xl font-black text-slate-900 dark:text-white">
                        {steuve.curtailable_power_kw.toFixed(1)} <span className="text-xs font-normal text-slate-500">kW dimmbar</span>
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                        Wallboxen & Wärmepumpen &gt;= 4,2 kW
                    </div>
                </div>
            </div>

            {/* DISPATCHING SIMULATOR & TEST PANEL */}
            <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <span className="text-lg">🎮</span>
                        <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                            Leitsystem-Simulator: Regelleistungs-Abruf (Dispatch)
                        </h3>
                    </div>
                    <span className="text-xs text-slate-400">
                        Reaktionszeit: &lt; 15s (Sekundärregelleistung konform)
                    </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                    <div>
                        <label className="text-[11px] font-semibold text-slate-500 block mb-1">Produkt-Typ:</label>
                        <select
                            value={dispatchType}
                            onChange={(e) => setDispatchType(e.target.value)}
                            className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-2 rounded-xl text-xs font-semibold text-slate-900 dark:text-white"
                        >
                            <option value="positive_flex">⚡ Positiv (+kW Entlastung)</option>
                            <option value="negative_flex">🔋 Negativ (-kW Speicher-Ladung)</option>
                        </select>
                    </div>

                    <div>
                        <label className="text-[11px] font-semibold text-slate-500 block mb-1">Soll-Leistung (kW):</label>
                        <input
                            type="number"
                            min="5"
                            max="500"
                            step="5"
                            value={targetPowerKw}
                            onChange={(e) => setTargetPowerKw(e.target.value)}
                            className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-2 rounded-xl text-xs font-semibold text-slate-900 dark:text-white"
                        />
                    </div>

                    <div>
                        <label className="text-[11px] font-semibold text-slate-500 block mb-1">Dauer (Minuten):</label>
                        <select
                            value={durationMinutes}
                            onChange={(e) => setDurationMinutes(e.target.value)}
                            className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-2 rounded-xl text-xs font-semibold text-slate-900 dark:text-white"
                        >
                            <option value="15">15 Minuten (Standard aFRR)</option>
                            <option value="30">30 Minuten</option>
                            <option value="60">60 Minuten (1 Stunde)</option>
                        </select>
                    </div>

                    <div className="flex items-end">
                        <button
                            type="button"
                            onClick={() => dispatchMutation.mutate()}
                            disabled={dispatchMutation.isPending}
                            className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-xs transition disabled:opacity-50 cursor-pointer"
                        >
                            {dispatchMutation.isPending ? "Sende Abruf..." : "🚀 Abruf aktivieren"}
                        </button>
                    </div>
                </div>

                {/* DISPATCH RESULT FEEDBACK */}
                {dispatchResult && (
                    <div className="mt-4 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs flex items-center justify-between">
                        <div>
                            <span className="font-bold text-emerald-600 dark:text-emerald-400">
                                ✅ Abruf erfolgreich aktiviert ({dispatchResult.connect_plus_order_id})
                            </span>
                            <span className="block text-slate-500 text-[11px] mt-0.5">
                                Angesteuert: {dispatchResult.activated_devices_count} Geräte ({dispatchResult.target_power_kw} kW für {dispatchResult.duration_minutes} Min.)
                            </span>
                        </div>
                        <span className="font-mono text-[11px] text-slate-400">
                            Status: <strong className="text-emerald-500 uppercase">{dispatchResult.status}</strong>
                        </span>
                    </div>
                )}
            </div>

            {/* 96-VIERTELSTUNDEN REDISPATCH 2.0 FAHRPLAN */}
            <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <span className="text-lg">📋</span>
                        <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                            Redispatch 2.0 / Connect+ 96-Viertelstunden-Fahrplan (PT15M)
                        </h3>
                    </div>
                    <span className="font-mono text-[11px] text-slate-400">
                        Ressource: {scheduleQuery.data?.resource_id || "DE-CONNECT-RES-001"}
                    </span>
                </div>

                <div className="overflow-x-auto max-h-72">
                    <table className="w-full text-left text-xs">
                        <thead>
                            <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 font-semibold sticky top-0 bg-white dark:bg-slate-900">
                                <th className="pb-2">Intervall</th>
                                <th className="pb-2 text-right">Planwert (Netto kW)</th>
                                <th className="pb-2 text-right">Solar-Prognose</th>
                                <th className="pb-2 text-right">Last-Prognose</th>
                                <th className="pb-2 text-right">P_max (kW)</th>
                                <th className="pb-2 text-right">P_min (kW)</th>
                                <th className="pb-2 text-right">+Flex (kW)</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-mono">
                            {schedule.slice(0, 32).map((slot, idx) => (
                                <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                                    <td className="py-2 text-slate-500 font-sans font-semibold text-[11px]">
                                        {new Date(slot.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} (#{slot.quarter_hour_index})
                                    </td>
                                    <td className="py-2 text-right font-bold text-slate-900 dark:text-white">
                                        {slot.planned_net_power_kw.toFixed(1)} kW
                                    </td>
                                    <td className="py-2 text-right text-amber-500">
                                        {slot.forecast_generation_kw.toFixed(1)} kW
                                    </td>
                                    <td className="py-2 text-right text-slate-400">
                                        {slot.forecast_consumption_kw.toFixed(1)} kW
                                    </td>
                                    <td className="py-2 text-right text-emerald-600 dark:text-emerald-400">
                                        {slot.p_max_kw.toFixed(1)} kW
                                    </td>
                                    <td className="py-2 text-right text-blue-600 dark:text-blue-400">
                                        {slot.p_min_kw.toFixed(1)} kW
                                    </td>
                                    <td className="py-2 text-right font-bold text-emerald-500">
                                        +{slot.available_positive_flex_kw.toFixed(1)} kW
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    );
}
