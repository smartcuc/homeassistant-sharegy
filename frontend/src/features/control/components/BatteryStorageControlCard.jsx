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

    // Live data
    const liveSoc = storage?.live_data?.soc_pct ?? data?.battery_soc_pct ?? 74;
    const livePowerW = storage?.live_data?.power_w ?? data?.battery_power_w ?? 1200; // positive = charge, negative = discharge
    const capacityKwh = storage?.usable_capacity_kwh ?? 10.0;
    const isCharging = livePowerW > 50;
    const isDischarging = livePowerW < -50;

    // Config state
    const [minSoc, setMinSoc] = useState(storage?.min_soc_pct ?? 10);
    const [maxSoc, setMaxSoc] = useState(storage?.max_soc_pct ?? 95);
    const [controlMode, setControlMode] = useState(storage?.control_mode ?? "self_consumption");

    // 2. Mutation for updating storage config
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

    // 3. Quick Action Mutation
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
            showFeedback(res?.message || "Steuerbefehl erfolgreich gesendet.");
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
        <div className="bg-gradient-to-br from-white via-slate-50/70 to-indigo-50/30 dark:from-slate-900 dark:via-slate-900/90 dark:to-indigo-950/20 rounded-3xl p-6 border border-slate-200/90 dark:border-slate-800 shadow-sm relative overflow-hidden flex flex-col justify-between">
            {/* Ambient Glow */}
            <div className="absolute top-0 right-0 w-48 h-48 bg-indigo-500/10 rounded-full blur-2xl pointer-events-none" />

            <div className="space-y-4 relative z-10">
                {/* Header */}
                <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-2xl shadow-xs text-indigo-600 dark:text-indigo-400">
                            🔋
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h3 className="font-bold text-base text-slate-900 dark:text-white">
                                    {storage?.name || "Heimspeicher"}
                                </h3>
                                <span className={`px-2 py-0.5 text-[11px] font-bold rounded-full border ${
                                    isCharging
                                        ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 animate-pulse"
                                        : isDischarging
                                        ? "bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30"
                                        : "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400 border-slate-200"
                                }`}>
                                    {isCharging ? "⚡ Lädt (PV)" : isDischarging ? "🔋 Entlädt (Haus)" : "⚪ Standby"}
                                </span>
                            </div>
                            <p className="text-xs text-slate-400 mt-0.5">
                                {capacityKwh} kWh Kapazität · Automatische Entlade- & Ladeschutz-Regelung
                            </p>
                        </div>
                    </div>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500">Ladestand (SoC)</div>
                        <div className="text-lg font-bold font-mono text-slate-900 dark:text-white mt-0.5 flex items-baseline justify-between">
                            <span>{liveSoc}%</span>
                            <span className="text-xs font-normal text-slate-400 font-sans">{((liveSoc / 100) * capacityKwh).toFixed(1)} kWh</span>
                        </div>
                    </div>

                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500">Ladeleistung (Live)</div>
                        <div className="text-lg font-bold font-mono text-indigo-600 dark:text-indigo-400 mt-0.5">
                            {Math.abs(livePowerW) > 20 ? `${Math.abs(livePowerW).toLocaleString("de-DE")} W` : "0 W"}
                        </div>
                    </div>
                </div>

                {/* Strategy & Reserve Settings Strip */}
                <div className="p-3 bg-white/70 dark:bg-slate-800/50 rounded-2xl border border-slate-200/60 dark:border-slate-700/50 flex items-center justify-between gap-3 text-xs">
                    <div className="min-w-0">
                        <div className="font-bold text-slate-800 dark:text-slate-200 truncate">🧭 Betriebsstrategie</div>
                        <div className="text-[11px] text-slate-400 truncate">
                            {controlMode === "price_optimized" ? "Spotmarkt-Arbitrage (Tiefstpreise)" : controlMode === "backup_only" ? "Notstrom-Reserve (100% Prio)" : "PV-Vorrang (Eigenverbrauch)"}
                        </div>
                    </div>
                    <select
                        value={controlMode}
                        onChange={(e) => handleSaveConfig(minSoc, maxSoc, e.target.value)}
                        className="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl px-2.5 py-1.5 text-xs font-bold cursor-pointer outline-none shrink-0"
                    >
                        <option value="self_consumption">☀️ PV-Vorrang</option>
                        <option value="price_optimized">⚡ Spot-Arbitrage</option>
                        <option value="backup_only">🛡️ Notstrom</option>
                    </select>
                </div>
            </div>

            {/* Actions */}
            <div className="pt-4 mt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between gap-3 relative z-10">
                <span className="text-xs text-slate-400">
                    Schutz: <strong className="text-indigo-600 dark:text-indigo-400">{minSoc}% Min · {maxSoc}% Max</strong>
                </span>
                <button
                    type="button"
                    onClick={() => handleTriggerQuickAction("charge_now")}
                    disabled={actionMutation.isPending}
                    className="px-4 py-2 rounded-xl text-xs font-bold transition shadow-xs cursor-pointer bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-600/20"
                >
                    🚀 Schnellladung (1h)
                </button>
            </div>
        </div>
    );
}
