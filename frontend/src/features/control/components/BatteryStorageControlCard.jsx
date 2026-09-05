import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import StorageSystemModal from "../../producer/components/StorageSystemModal";

export default function BatteryStorageControlCard() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const [actionFeedback, setActionFeedback] = useState(null);
    const [editModalOpen, setEditModalOpen] = useState(false);

    // 1. Live Storage Systems from Backend
    const storageQuery = useQuery({
        queryKey: ["storages"],
        queryFn: () => apiFetch("/api/producer/storage/"),
        refetchInterval: 5000,
    });

    const storages = Array.isArray(storageQuery.data) ? storageQuery.data : (storageQuery.data?.storages || []);
    const storage = storages[0] || null; // Primary active storage system

    // Real Live Telemetry & Specs
    const liveSoc = storage?.live_soc_pct ?? 74;
    const livePowerW = storage?.live_power_w ?? 1200; // positive = discharge / negative = charge or vice versa
    const capacityKwh = Number(storage?.capacity_kwh || 10.0);
    const minSoc = storage?.min_soc_reserve_pct ?? 10;
    const maxSoc = storage?.max_soc_pct ?? 95;
    const controlMode = storage?.control_mode || "self_consumption";
    const storedKwh = storage?.current_stored_kwh ?? ((liveSoc / 100) * capacityKwh).toFixed(1);

    const isCharging = storage?.status === "charging" || livePowerW < -50 || (livePowerW > 50 && storage?.is_charging);
    const isDischarging = storage?.status === "discharging" || livePowerW > 50;

    // 2. Mutation for changing storage mode
    const modeMutation = useMutation({
        mutationFn: (newMode) => {
            if (!storage?.id) return Promise.resolve();
            return apiFetch(`/api/producer/storage/${storage.id}/`, {
                method: "PATCH",
                body: JSON.stringify({
                    control_mode: newMode,
                    ems_control_enabled: true,
                }),
            });
        },
        onSuccess: (res, newMode) => {
            queryClient.invalidateQueries({ queryKey: ["storages"] });
            queryClient.invalidateQueries({ queryKey: ["load-management-hub"] });
            const modeLabels = {
                self_consumption: "☀️ PV-Vorrang (Autarkie)",
                price_optimized: "⚡ Spotmarkt-Arbitrage",
                backup_only: "🛡️ Notstrom-Priorität",
                forced_charge: "🚀 Zwangsladung",
                idle: "💤 Standby",
            };
            showFeedback(`Modus auf "${modeLabels[newMode] || newMode}" gesetzt.`);
        },
        onError: (err) => {
            showFeedback(`Fehler: ${err.message || "Modus konnte nicht geändert werden."}`);
        },
    });

    // 3. Quick Action Mutation (Forced Charge 1h / Control)
    const actionMutation = useMutation({
        mutationFn: async (actionPayload) => {
            if (!storage?.id) {
                return apiFetch("/api/energy/load-management/hub/action/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(actionPayload),
                });
            }
            return apiFetch(`/api/producer/storage/${storage.id}/control/`, {
                method: "POST",
                body: JSON.stringify(actionPayload),
            });
        },
        onSuccess: (res) => {
            queryClient.invalidateQueries({ queryKey: ["storages"] });
            queryClient.invalidateQueries({ queryKey: ["load-management-hub"] });
            showFeedback(res?.message || "Steuerbefehl erfolgreich an Speicher gesendet.");
        },
        onError: (err) => {
            showFeedback(`Fehler: ${err.message || "Steuerbefehl fehlgeschlagen."}`);
        },
    });

    const showFeedback = (msg) => {
        setActionFeedback(msg);
        setTimeout(() => setActionFeedback(null), 3500);
    };

    const handleModeChange = (newMode) => {
        modeMutation.mutate(newMode);
    };

    const handleTriggerQuickAction = () => {
        actionMutation.mutate({
            action: isCharging ? "idle" : "forced_charge",
            target_power_kw: storage?.max_charge_power_kw || 3.0,
            duration_minutes: 60,
        });
    };

    // If no storage configured yet
    if (!storage && !storageQuery.isLoading) {
        return (
            <div className="bg-gradient-to-br from-white via-slate-50/70 to-indigo-50/30 dark:from-slate-900 dark:via-slate-900/90 dark:to-indigo-950/20 rounded-3xl p-6 border border-slate-200/90 dark:border-slate-800 shadow-sm relative overflow-hidden flex flex-col justify-between">
                <div className="space-y-4 relative z-10">
                    <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-2xl shadow-xs text-indigo-600 dark:text-indigo-400">
                                🔋
                            </div>
                            <div>
                                <h3 className="font-bold text-base text-slate-900 dark:text-white">
                                    Heimspeicher
                                </h3>
                                <p className="text-xs text-slate-400 mt-0.5">
                                    Kein Batteriespeicher angebunden
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="p-4 bg-white/70 dark:bg-slate-800/50 rounded-2xl border border-slate-200/60 dark:border-slate-700/50 text-xs text-slate-500 dark:text-slate-400 text-center">
                        Binde deinen Hybrid-Wechselrichter oder Hausspeicher ein, um Notstrom-Reserve, Zellschonung und Spotmarkt-Laden zu steuern.
                    </div>
                </div>

                <div className="pt-4 mt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-end relative z-10">
                    <button
                        type="button"
                        onClick={() => setEditModalOpen(true)}
                        className="px-4 py-2 rounded-xl text-xs font-bold transition shadow-xs cursor-pointer bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-600/20 flex items-center gap-1.5"
                    >
                        <span>➕</span>
                        <span>Speicher anlegen</span>
                    </button>
                </div>

                <StorageSystemModal
                    isOpen={editModalOpen}
                    onClose={() => setEditModalOpen(false)}
                    storage={null}
                    onSaved={() => queryClient.invalidateQueries({ queryKey: ["storages"] })}
                />
            </div>
        );
    }

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
                                    {isCharging ? "⚡ Lädt" : isDischarging ? "🔋 Entlädt" : "⚪ Standby"}
                                </span>
                            </div>
                            <p className="text-xs text-slate-400 mt-0.5">
                                {capacityKwh.toFixed(1)} kWh Kapazität · max. {storage?.max_charge_power_kw || 5.0} kW Laden
                            </p>
                        </div>
                    </div>

                    <button
                        type="button"
                        onClick={() => setEditModalOpen(true)}
                        className="p-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition cursor-pointer border border-slate-200/80 dark:border-slate-700 shadow-2xs"
                        title="Speicher-Parameter bearbeiten"
                    >
                        ⚙️
                    </button>
                </div>

                {/* Feedback */}
                {actionFeedback && (
                    <div className="p-2.5 rounded-2xl text-xs font-bold flex items-center gap-2 border bg-emerald-50 dark:bg-emerald-950/60 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 animate-fade-in">
                        <span>✓</span>
                        <span>{actionFeedback}</span>
                    </div>
                )}

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500">Ladestand (SoC)</div>
                        <div className="text-lg font-bold font-mono text-slate-900 dark:text-white mt-0.5 flex items-baseline justify-between">
                            <span>{liveSoc}%</span>
                            <span className="text-xs font-normal text-slate-400 font-sans">{storedKwh} kWh</span>
                        </div>
                    </div>

                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500">Ladeleistung (Live)</div>
                        <div className="text-lg font-bold font-mono text-indigo-600 dark:text-indigo-400 mt-0.5">
                            {Math.abs(livePowerW) > 10 ? `${Math.abs(livePowerW).toLocaleString("de-DE")} W` : "0 W"}
                        </div>
                    </div>
                </div>

                {/* Strategy & Reserve Settings Strip */}
                <div className="p-3 bg-white/70 dark:bg-slate-800/50 rounded-2xl border border-slate-200/60 dark:border-slate-700/50 flex items-center justify-between gap-3 text-xs">
                    <div className="min-w-0">
                        <div className="font-bold text-slate-800 dark:text-slate-200 truncate">🧭 Betriebsstrategie</div>
                        <div className="text-[11px] text-slate-400 truncate">
                            {controlMode === "price_optimized" ? `Spot-Arbitrage (≤ ${storage?.price_threshold_ct || 15} ct/kWh)` : controlMode === "backup_only" ? "Notstrom-Reserve (100% Prio)" : controlMode === "forced_charge" ? "Zwangsladung aktiv" : "PV-Vorrang (Eigenverbrauch)"}
                        </div>
                    </div>
                    <select
                        value={controlMode}
                        onChange={(e) => handleModeChange(e.target.value)}
                        disabled={modeMutation.isPending}
                        className="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl px-2.5 py-1.5 text-xs font-bold cursor-pointer outline-none shrink-0"
                    >
                        <option value="self_consumption">☀️ PV-Vorrang</option>
                        <option value="price_optimized">⚡ Spot-Arbitrage</option>
                        <option value="backup_only">🛡️ Notstrom</option>
                        <option value="forced_charge">🚀 Zwangsladung</option>
                        <option value="idle">💤 Standby</option>
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
                    onClick={handleTriggerQuickAction}
                    disabled={actionMutation.isPending}
                    className="px-4 py-2 rounded-xl text-xs font-bold transition shadow-xs cursor-pointer bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-600/20"
                >
                    {isCharging ? "⏹️ Ladung stoppen" : "🚀 Schnellladung (1h)"}
                </button>
            </div>

            {/* Storage System Modal for complete configuration (capacity, sensors, limits) */}
            <StorageSystemModal
                isOpen={editModalOpen}
                onClose={() => setEditModalOpen(false)}
                storage={storage}
                onSaved={() => queryClient.invalidateQueries({ queryKey: ["storages"] })}
            />
        </div>
    );
}
