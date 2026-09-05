import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function BatteryStorageControlCard() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const [actionFeedback, setActionFeedback] = useState(null);

    // 1. Load Producers / Storage Systems data
    const storageQuery = useQuery({
        queryKey: ["producer-systems"],
        queryFn: () => apiFetch("/api/producers/me/"),
        refetchInterval: 5000,
    });

    const data = storageQuery.data || {};
    const storages = data.storages || [];
    const storage = storages[0] || null; // Primary storage system

    // Fallback/Demo live data if not connected yet
    const liveSoc = storage?.live_data?.soc_pct ?? data?.battery_soc_pct ?? 74;
    const livePowerW = storage?.live_data?.power_w ?? data?.battery_power_w ?? 1200; // positive = charge, negative = discharge
    const capacityKwh = storage?.usable_capacity_kwh ?? 10.0;
    const isCharging = livePowerW > 50;
    const isDischarging = livePowerW < -50;

    // Config state
    const [minSoc, setMinSoc] = useState(storage?.min_soc_pct ?? 10);
    const [maxSoc, setMaxSoc] = useState(storage?.max_soc_pct ?? 95);
    const [controlMode, setControlMode] = useState(storage?.control_mode ?? "self_consumption");

    // 2. Mutation for updating storage config (min_soc, max_soc, control_mode)
    const updateMutation = useMutation({
        mutationFn: (payload) => {
            if (storage?.id) {
                return apiFetch(`/api/producers/storages/${storage.id}/`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });
            }
            return Promise.resolve(payload);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["producer-systems"] });
            queryClient.invalidateQueries({ queryKey: ["load-management-hub"] });
            showFeedback("Speicher-Einstellungen erfolgreich gespeichert.");
        },
    });

    // 3. Quick Action Mutation (e.g. forced grid charge, backup hold)
    const actionMutation = useMutation({
        mutationFn: (actionPayload) =>
            apiFetch("/api/energy/load-management/hub/action/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(actionPayload),
            }),
        onSuccess: (res) => {
            queryClient.invalidateQueries({ queryKey: ["producer-systems"] });
            queryClient.invalidateQueries({ queryKey: ["load-management-hub"] });
            showFeedback(res?.message || "Steuerbefehl erfolgreich an Wechselrichter gesendet.");
        },
    });

    const showFeedback = (msg) => {
        setActionFeedback(msg);
        setTimeout(() => setActionFeedback(null), 3500);
    };

    const handleSaveConfig = (newMin, newMax, newMode) => {
        setMinSoc(newMin);
        setMaxSoc(newMax);
        setControlMode(newMode);
        updateMutation.mutate({
            min_soc_pct: newMin,
            max_soc_pct: newMax,
            control_mode: newMode,
        });
    };

    const handleTriggerQuickAction = (actionName) => {
        actionMutation.mutate({
            category: "battery",
            action: actionName,
            device_id: storage ? `storage_${storage.id}` : "battery_main",
        });
    };

    return (
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200/90 dark:border-slate-800 shadow-xs space-y-5">
            {/* Feedback Banner */}
            {actionFeedback && (
                <div className="p-3 bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 rounded-2xl text-xs font-bold flex items-center gap-2 animate-in fade-in">
                    <span>✓</span>
                    <span>{actionFeedback}</span>
                </div>
            )}

            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-2xl shadow-2xs">
                        🔋
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h3 className="text-base font-bold text-slate-900 dark:text-white">
                                {storage?.name || "Heimspeicher & Betriebsstrategie"}
                            </h3>
                            <span className={`px-2.5 py-0.5 text-[10px] font-bold rounded-full border ${
                                isCharging
                                    ? "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800"
                                    : isDischarging
                                    ? "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800"
                                    : "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700"
                            }`}>
                                {isCharging ? "⚡ Lädt (PV/Netz)" : isDischarging ? "🔋 Entlädt (Haus)" : "⏸️ Standby"}
                            </span>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            {storage?.manufacturer ? `${storage.manufacturer} · ` : ""}
                            Kapazität: {capacityKwh} kWh · Automatische Entlade- und Ladeschutz-Regelung.
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2 self-start sm:self-auto">
                    <button
                        type="button"
                        onClick={() => handleTriggerQuickAction("charge_now")}
                        disabled={actionMutation.isPending}
                        className="px-3.5 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 dark:bg-indigo-950/60 dark:hover:bg-indigo-900/80 dark:text-indigo-300 text-xs font-bold rounded-xl border border-indigo-200 dark:border-indigo-800 transition cursor-pointer flex items-center gap-1.5"
                        title="Speicher forciert für 60 Minuten aus PV/Netz laden"
                    >
                        <span>🚀</span>
                        <span>Schnellladung (1h)</span>
                    </button>
                </div>
            </div>

            {/* Live SoC & Power Flow Gauges */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 bg-slate-50 dark:bg-slate-950/60 p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800/80">
                {/* 1. SoC % Gauge */}
                <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs font-semibold text-slate-500 dark:text-slate-400">
                        <span>Aktueller Ladestand</span>
                        <span className="font-mono font-bold text-slate-900 dark:text-white">{liveSoc}%</span>
                    </div>
                    <div className="w-full bg-slate-200 dark:bg-slate-800 h-3.5 rounded-full overflow-hidden p-0.5 flex">
                        <div
                            style={{ width: `${Math.min(100, Math.max(0, liveSoc))}%` }}
                            className={`h-full rounded-full transition-all duration-500 ${
                                liveSoc >= 40
                                    ? "bg-gradient-to-r from-emerald-500 to-emerald-400"
                                    : liveSoc >= 20
                                    ? "bg-gradient-to-r from-amber-500 to-amber-400"
                                    : "bg-gradient-to-r from-rose-500 to-rose-400"
                            }`}
                        />
                    </div>
                    <div className="text-[10px] text-slate-400 flex justify-between">
                        <span>Min: {minSoc}%</span>
                        <span>Max: {maxSoc}%</span>
                    </div>
                </div>

                {/* 2. Live Power (W) */}
                <div className="space-y-1">
                    <div className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                        Lade- / Entladeleistung
                    </div>
                    <div className="text-xl font-black font-mono text-slate-900 dark:text-white flex items-baseline gap-1">
                        <span>{Math.abs(livePowerW).toLocaleString("de-DE")}</span>
                        <span className="text-xs font-normal text-slate-500">W</span>
                    </div>
                    <div className="text-[10px] text-slate-400">
                        {isCharging ? "Überschuss wird gespeichert" : isDischarging ? "Versorgt Haushalt" : "Ausgeglichen"}
                    </div>
                </div>

                {/* 3. Stored Energy (kWh) */}
                <div className="space-y-1">
                    <div className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                        Gespeicherte Energie
                    </div>
                    <div className="text-xl font-black font-mono text-indigo-600 dark:text-indigo-400 flex items-baseline gap-1">
                        <span>{((liveSoc / 100) * capacityKwh).toFixed(1)}</span>
                        <span className="text-xs font-normal text-slate-500">/ {capacityKwh} kWh</span>
                    </div>
                    <div className="text-[10px] text-slate-400">
                        ca. {Math.round((liveSoc / 100) * 12)} h Haushalts-Autarkie
                    </div>
                </div>
            </div>

            {/* Betriebsstrategie Selector */}
            <div className="space-y-2">
                <label className="text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                    <span>🧭</span>
                    <span>Betriebsstrategie & Optimierungsmodus:</span>
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                    {[
                        {
                            key: "self_consumption",
                            icon: "☀️",
                            title: "PV-Vorrang (Autarkie)",
                            desc: "Überschuss speichern, abends entladen",
                        },
                        {
                            key: "price_optimized",
                            icon: "⚡",
                            title: "Spotmarkt-Arbitrage",
                            desc: "Netzladung bei Börsen-Tiefstpreisen",
                        },
                        {
                            key: "backup_only",
                            icon: "🛡️",
                            title: "Notstrom-Priorität",
                            desc: "Speicher immer auf 100% halten",
                        },
                    ].map((mode) => (
                        <button
                            key={mode.key}
                            type="button"
                            onClick={() => handleSaveConfig(minSoc, maxSoc, mode.key)}
                            className={`p-3 rounded-2xl border text-left transition-all cursor-pointer ${
                                controlMode === mode.key
                                    ? "bg-indigo-50/70 dark:bg-indigo-950/40 border-indigo-500 ring-2 ring-indigo-500/20 shadow-xs"
                                    : "bg-slate-50/50 dark:bg-slate-800/30 border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800"
                            }`}
                        >
                            <div className="flex items-center gap-2 font-bold text-xs text-slate-900 dark:text-white">
                                <span>{mode.icon}</span>
                                <span>{mode.title}</span>
                            </div>
                            <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-1">
                                {mode.desc}
                            </div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Sicherheits- & Schutzparameter (Min / Max SoC) */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                {/* Min-SoC / Notstrom-Reserve */}
                <div className="bg-slate-50 dark:bg-slate-950/40 p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 space-y-2.5">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 font-bold text-xs text-slate-900 dark:text-white">
                            <span>🛡️</span>
                            <span>Notstrom-Reserve (Min-SoC):</span>
                        </div>
                        <span className="font-mono font-bold text-xs px-2 py-0.5 bg-white dark:bg-slate-800 rounded-md border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white">
                            {minSoc}%
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        {[5, 10, 15, 20, 30].map((val) => (
                            <button
                                key={val}
                                type="button"
                                onClick={() => handleSaveConfig(val, maxSoc, controlMode)}
                                className={`flex-1 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
                                    minSoc === val
                                        ? "bg-indigo-600 text-white shadow-2xs"
                                        : "bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-100"
                                }`}
                            >
                                {val}%
                            </button>
                        ))}
                    </div>
                    <p className="text-[10px] text-slate-400">
                        Speicher entlädt maximal bis {minSoc}%, um Notstrom für Netzausfälle zu sichern und Tiefentladung zu verhindern.
                    </p>
                </div>

                {/* Max-SoC / Zellschonung */}
                <div className="bg-slate-50 dark:bg-slate-950/40 p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 space-y-2.5">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 font-bold text-xs text-slate-900 dark:text-white">
                            <span>🔋</span>
                            <span>Zellschonung (Max-SoC):</span>
                        </div>
                        <span className="font-mono font-bold text-xs px-2 py-0.5 bg-white dark:bg-slate-800 rounded-md border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white">
                            {maxSoc}%
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        {[80, 85, 90, 95, 100].map((val) => (
                            <button
                                key={val}
                                type="button"
                                onClick={() => handleSaveConfig(minSoc, val, controlMode)}
                                className={`flex-1 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
                                    maxSoc === val
                                        ? "bg-indigo-600 text-white shadow-2xs"
                                        : "bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-100"
                                }`}
                            >
                                {val}%
                            </button>
                        ))}
                    </div>
                    <p className="text-[10px] text-slate-400">
                        Begrenzung auf {maxSoc}% schützt die Batteriezellen vor kalendarischer Alterung bei sommerlichen Dauer-Vollzuständen.
                    </p>
                </div>
            </div>
        </div>
    );
}
