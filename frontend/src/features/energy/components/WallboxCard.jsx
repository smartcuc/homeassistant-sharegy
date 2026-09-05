import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import { useSubscription } from "../../../hooks/useSubscription";
import ProBadge from "../../../components/common/ProBadge";
import ProUpgradeModal from "../../../components/common/ProUpgradeModal";

export default function WallboxCard({ onOpenAddModal }) {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const queryClient = useQueryClient();

    const [proModalOpen, setProModalOpen] = useState(false);
    const [selectedStationId, setSelectedStationId] = useState(null);
    const [actionPending, setActionPending] = useState(null);
    const [feedback, setFeedback] = useState({ text: null, type: null });

    // 1. Wallboxen aus API laden
    const wallboxesQuery = useQuery({
        queryKey: ["wallboxes"],
        queryFn: () => apiFetch("/api/energy/wallboxes/"),
        refetchInterval: 5000,
    });

    const wallboxes = Array.isArray(wallboxesQuery.data) 
        ? wallboxesQuery.data 
        : (wallboxesQuery.data?.wallboxes || []);
    const activeStation = wallboxes.find((w) => w.id === selectedStationId) || wallboxes[0] || null;

    // 2. Modus-Umschaltung
    const updateModeMutation = useMutation({
        mutationFn: async ({ id, mode, extraParams = {} }) => {
            return apiFetch(`/api/energy/wallboxes/${id}/`, {
                method: "PATCH",
                body: JSON.stringify({ smart_charging_mode: mode, ...extraParams }),
            });
        },
        onSuccess: (res, vars) => {
            queryClient.invalidateQueries({ queryKey: ["wallboxes"] });
            setFeedback({
                text: t("wallbox.mode_updated", `Lademodus auf "${getModeLabel(vars.mode)}" gesetzt.`),
                type: "success",
            });
            setTimeout(() => setFeedback({ text: null, type: null }), 4000);
        },
        onError: (err) => {
            setFeedback({ text: err.message || "Fehler beim Aktualisieren des Lademodus.", type: "error" });
        },
    });

    // 3. Remote Aktionen (Start, Stop, Unlock)
    const handleRemoteAction = async (action) => {
        if (!activeStation) return;
        setActionPending(action);
        setFeedback({ text: null, type: null });

        try {
            const res = await apiFetch(`/api/energy/wallboxes/${activeStation.id}/${action}/`, {
                method: "POST",
            });
            setFeedback({ text: res.message || `Aktion "${action}" erfolgreich ausgeführt.`, type: "success" });
            queryClient.invalidateQueries({ queryKey: ["wallboxes"] });
        } catch (err) {
            setFeedback({ text: err.message || `Fehler bei Aktion "${action}".`, type: "error" });
        } finally {
            setActionPending(null);
            setTimeout(() => setFeedback({ text: null, type: null }), 4000);
        }
    };

    const handleModeClick = (mode, extraParams = {}) => {
        if (!activeStation) return;
        if (!isPro && mode !== "instant") {
            setProModalOpen(true);
            return;
        }
        updateModeMutation.mutate({ id: activeStation.id, mode, extraParams });
    };

    function getModeLabel(mode) {
        switch (mode) {
            case "pv_surplus":
                return "☀️ Nur Solarüberschuss";
            case "min_pv":
                return "⛅ Min + PV-Überschuss";
            case "spot_price":
                return "💶 Börsenpreisgeführt";
            case "instant":
                return "⚡ Sofortladen (Max. Power)";
            case "off":
                return "🛑 Gesperrt / Pausiert";
            default:
                return mode;
        }
    }

    function getStatusBadge(status, isOnline) {
        if (!isOnline) {
            return (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400 dark:bg-slate-500"></span>
                    Offline
                </span>
            );
        }
        switch (status) {
            case "Charging":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30 animate-pulse">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                        Lädt aktiv
                    </span>
                );
            case "Preparing":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-700 dark:text-amber-400 border border-amber-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                        Fahrzeug verbunden
                    </span>
                );
            case "SuspendedEVSE":
            case "SuspendedEV":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/15 text-cyan-700 dark:text-cyan-400 border border-cyan-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
                        Warte auf Solarstrom
                    </span>
                );
            default:
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/15 text-blue-700 dark:text-blue-400 border border-blue-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                        Bereit
                    </span>
                );
        }
    }

    if (wallboxesQuery.isLoading) {
        return (
            <div className="bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 rounded-3xl p-6 shadow-sm animate-pulse min-h-[260px] flex items-center justify-center text-slate-400">
                <div className="flex items-center gap-3">
                    <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                    <span>Lade Wallbox- & Smart-Charging-Daten...</span>
                </div>
            </div>
        );
    }

    // Wenn noch keine Wallbox verbunden ist
    if (!activeStation) {
        return (
            <div className="bg-gradient-to-br from-white via-slate-50/70 to-emerald-50/30 dark:from-slate-900 dark:via-slate-900/90 dark:to-emerald-950/20 rounded-3xl p-6 border border-slate-200/90 dark:border-slate-800 shadow-sm relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>

                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-2xl shadow-2xs">
                            🚗
                        </div>
                        <div>
                            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                E-Auto & Wallbox Smart-Charging
                                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                                    OCPP 1.6-J
                                </span>
                            </h3>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                Hardwarefreies PV-Überschuss- und Börsenstrom-Laden für jede gängige Wallbox.
                            </p>
                        </div>
                    </div>
                </div>

                <div className="bg-slate-50 dark:bg-slate-950/50 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-6 text-center my-4">
                    <div className="w-12 h-12 rounded-full bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 flex items-center justify-center mx-auto mb-3 text-slate-400 shadow-2xs">
                        <span className="text-xl">🔌</span>
                    </div>
                    <h4 className="text-sm font-bold text-slate-900 dark:text-slate-200 mb-1">Keine Wallbox angebunden</h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-4">
                        Verbinde deine Easee, go-eCharger, Keba, Alfen, Mennekes, Zaptec oder OpenWB in unter 60 Sekunden via Cloud-WebSocket.
                    </p>
                    <button
                        type="button"
                        onClick={onOpenAddModal}
                        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-md shadow-emerald-600/20 cursor-pointer"
                    >
                        <span>＋</span>
                        <span>Wallbox jetzt verbinden</span>
                    </button>
                </div>
            </div>
        );
    }

    const currentMode = activeStation.smart_charging_mode || "pv_surplus";
    const activePowerKw = Number(activeStation.active_power_kw || 0).toFixed(2);
    const sessionKwh = Number(activeStation.session_energy_kwh || 0).toFixed(1);
    const targetAmpere = activeStation.target_current_a || 16.0;

    return (
        <div className="bg-gradient-to-br from-white via-slate-50/70 to-emerald-50/30 dark:from-slate-900 dark:via-slate-900/90 dark:to-emerald-950/20 rounded-3xl p-6 border border-slate-200/90 dark:border-slate-800 shadow-sm relative overflow-hidden flex flex-col justify-between">
            {/* Ambient Background Glow */}
            <div className="absolute top-0 right-0 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

            <div className="space-y-5 relative z-10">
                {/* Header mit Wallbox-Auswahl & Status */}
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-4">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-2xl shadow-2xs">
                            🚗
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
                                    {activeStation.name || "Wallbox"}
                                </h3>
                                {getStatusBadge(activeStation.status, activeStation.is_online)}
                            </div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5 mt-0.5">
                                <span>{activeStation.vendor || "OCPP"} {activeStation.model || "Wallbox"}</span>
                                <span>•</span>
                                <span className="font-mono text-slate-400">{activeStation.charge_point_id}</span>
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        {wallboxes.length > 1 && (
                            <select
                                value={activeStation.id}
                                onChange={(e) => setSelectedStationId(e.target.value)}
                                className="bg-white dark:bg-slate-950/80 border border-slate-200 dark:border-slate-700/80 text-xs font-semibold text-slate-800 dark:text-slate-200 rounded-xl px-3 py-2 cursor-pointer shadow-2xs outline-none"
                            >
                                {wallboxes.map((wb) => (
                                    <option key={wb.id} value={wb.id}>
                                        {wb.name} ({wb.charge_point_id})
                                    </option>
                                ))}
                            </select>
                        )}

                        <button
                            type="button"
                            onClick={onOpenAddModal}
                            title="Weitere Wallbox hinzufügen"
                            className="px-3 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 transition cursor-pointer flex items-center gap-1.5 shadow-2xs"
                        >
                            <span>＋</span>
                            <span>Neu</span>
                        </button>
                    </div>
                </div>

                {/* Feedback Alert */}
                {feedback.text && (
                    <div
                        className={`p-3 rounded-2xl text-xs font-bold flex items-center gap-2 border transition-all ${
                            feedback.type === "success"
                                ? "bg-emerald-50 dark:bg-emerald-950/60 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300"
                                : "bg-red-50 dark:bg-red-950/60 border-red-200 dark:border-red-800 text-red-800 dark:text-red-300"
                        }`}
                    >
                        <span className="text-sm">{feedback.type === "success" ? "✓" : "⚠️"}</span>
                        <span>{feedback.text}</span>
                    </div>
                )}

                {/* Live-Ladeleistung & Phasen-Cockpit */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    {/* Ladeleistung */}
                    <div className="p-3.5 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60 shadow-2xs flex flex-col justify-between">
                        <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
                            Ladeleistung (Live)
                        </div>
                        <div className="text-xl font-bold font-mono text-slate-900 dark:text-white mt-1 flex items-baseline gap-1">
                            <span>{activePowerKw}</span>
                            <span className="text-xs font-normal text-slate-500">kW</span>
                        </div>
                        <div className="text-[10px] text-slate-400 mt-0.5 flex items-center gap-1">
                            <span>Soll:</span>
                            <span className="font-mono text-slate-700 dark:text-slate-300 font-bold">{targetAmpere} A</span>
                            <span className="text-slate-400">({activeStation.phases || 3}-phasig)</span>
                        </div>
                    </div>

                    {/* Phasenströme L1 / L2 / L3 */}
                    <div className="p-3.5 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60 shadow-2xs flex flex-col justify-between">
                        <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400 mb-1">
                            Phasenströme (L1 / L2 / L3)
                        </div>
                        <div className="grid grid-cols-3 gap-1.5 text-center my-auto">
                            <div className="bg-slate-50 dark:bg-slate-900/80 border border-slate-200/60 dark:border-slate-700/60 rounded-xl py-1 px-1">
                                <div className="text-[9px] text-slate-400 font-bold">L1</div>
                                <div className="text-xs font-mono font-bold text-slate-800 dark:text-slate-200">
                                    {Number(activeStation.current_l1 || 0).toFixed(1)} A
                                </div>
                            </div>
                            <div className="bg-slate-50 dark:bg-slate-900/80 border border-slate-200/60 dark:border-slate-700/60 rounded-xl py-1 px-1">
                                <div className="text-[9px] text-slate-400 font-bold">L2</div>
                                <div className="text-xs font-mono font-bold text-slate-800 dark:text-slate-200">
                                    {Number(activeStation.current_l2 || 0).toFixed(1)} A
                                </div>
                            </div>
                            <div className="bg-slate-50 dark:bg-slate-900/80 border border-slate-200/60 dark:border-slate-700/60 rounded-xl py-1 px-1">
                                <div className="text-[9px] text-slate-400 font-bold">L3</div>
                                <div className="text-xs font-mono font-bold text-slate-800 dark:text-slate-200">
                                    {Number(activeStation.current_l3 || 0).toFixed(1)} A
                                </div>
                            </div>
                        </div>
                        <div className="text-[10px] text-slate-400 mt-1 flex justify-between">
                            <span>~{Math.round(activeStation.voltage_v || 230)} V</span>
                            <span>{activeStation.connector_status || "Kabel gesteckt"}</span>
                        </div>
                    </div>

                    {/* Session-Statistik */}
                    <div className="p-3.5 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60 shadow-2xs flex flex-col justify-between">
                        <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
                            Geladene Energie
                        </div>
                        <div className="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-1 flex items-baseline gap-1">
                            <span>{sessionKwh}</span>
                            <span className="text-xs font-normal text-slate-500">kWh</span>
                        </div>
                        <div className="text-[10px] text-emerald-600 dark:text-emerald-400 mt-0.5 flex items-center justify-between">
                            <span>☀️ PV-Quote: {currentMode === "pv_surplus" ? "100%" : "85%"}</span>
                            <span className="text-slate-400 font-mono">#{activeStation.active_transaction_id || "–"}</span>
                        </div>
                    </div>
                </div>

                {/* Smart-Charging Modus-Umschalter */}
                <div className="space-y-2">
                    <div className="flex items-center justify-between">
                        <label className="text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                            <span>🧭</span>
                            <span>Smart-Charging Lademodus:</span>
                            {!isPro && <ProBadge size="xs" />}
                        </label>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                        {/* 1. PV Überschuss */}
                        <button
                            type="button"
                            onClick={() => handleModeClick("pv_surplus")}
                            className={`p-2.5 rounded-2xl border text-left transition-all cursor-pointer ${
                                currentMode === "pv_surplus"
                                    ? "bg-amber-50 dark:bg-amber-950/40 border-amber-500 ring-2 ring-amber-500/20 shadow-xs"
                                    : "bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
                            }`}
                        >
                            <div className="text-base mb-0.5">☀️</div>
                            <div className="text-xs font-bold text-slate-900 dark:text-white">Nur Solar</div>
                            <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">100% Überschuss</div>
                        </button>

                        {/* 2. Min + PV */}
                        <button
                            type="button"
                            onClick={() => handleModeClick("min_pv")}
                            className={`p-2.5 rounded-2xl border text-left transition-all cursor-pointer ${
                                currentMode === "min_pv"
                                    ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-500 ring-2 ring-emerald-500/20 shadow-xs"
                                    : "bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
                            }`}
                        >
                            <div className="text-base mb-0.5">⛅</div>
                            <div className="text-xs font-bold text-slate-900 dark:text-white">Min + PV</div>
                            <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">Basis + Solar-Boost</div>
                        </button>

                        {/* 3. Börsenpreisgeführt */}
                        <button
                            type="button"
                            onClick={() => handleModeClick("spot_price")}
                            className={`p-2.5 rounded-2xl border text-left transition-all cursor-pointer ${
                                currentMode === "spot_price"
                                    ? "bg-blue-50 dark:bg-blue-950/40 border-blue-500 ring-2 ring-blue-500/20 shadow-xs"
                                    : "bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
                            }`}
                        >
                            <div className="text-base mb-0.5">💶</div>
                            <div className="text-xs font-bold text-slate-900 dark:text-white">Börsenpreis</div>
                            <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">≤ {activeStation.price_threshold_ct || 15} ct/kWh</div>
                        </button>

                        {/* 4. Sofort / Boost */}
                        <button
                            type="button"
                            onClick={() => handleModeClick("instant")}
                            className={`p-2.5 rounded-2xl border text-left transition-all cursor-pointer ${
                                currentMode === "instant"
                                    ? "bg-purple-50 dark:bg-purple-950/40 border-purple-500 ring-2 ring-purple-500/20 shadow-xs"
                                    : "bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
                            }`}
                        >
                            <div className="text-base mb-0.5">⚡</div>
                            <div className="text-xs font-bold text-slate-900 dark:text-white">Sofortladen</div>
                            <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">Max. 11/22 kW</div>
                        </button>

                        {/* 5. Stop / Pause */}
                        <button
                            type="button"
                            onClick={() => handleModeClick("off")}
                            className={`p-2.5 rounded-2xl border text-left transition-all col-span-2 sm:col-span-1 cursor-pointer ${
                                currentMode === "off"
                                    ? "bg-rose-50 dark:bg-rose-950/40 border-rose-500 ring-2 ring-rose-500/20 shadow-xs"
                                    : "bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
                            }`}
                        >
                            <div className="text-base mb-0.5">🛑</div>
                            <div className="text-xs font-bold text-slate-900 dark:text-white">Gesperrt</div>
                            <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">Laden pausiert</div>
                        </button>
                    </div>
                </div>
            </div>

            {/* Schnell-Aktionsleiste (Start / Stop / Unlock) */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-4 mt-4 border-t border-slate-100 dark:border-slate-800 relative z-10">
                <div className="flex items-center gap-2">
                    <button
                        type="button"
                        disabled={actionPending !== null}
                        onClick={() => handleRemoteAction("remote-start")}
                        className="px-3.5 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white transition-all flex items-center gap-1.5 disabled:opacity-50 cursor-pointer shadow-xs"
                    >
                        {actionPending === "remote-start" ? "..." : "▶️ Start"}
                    </button>

                    <button
                        type="button"
                        disabled={actionPending !== null}
                        onClick={() => handleRemoteAction("remote-stop")}
                        className="px-3.5 py-2 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-600 text-white transition-all flex items-center gap-1.5 disabled:opacity-50 cursor-pointer shadow-xs"
                    >
                        {actionPending === "remote-stop" ? "..." : "⏹️ Stop"}
                    </button>

                    <button
                        type="button"
                        disabled={actionPending !== null}
                        onClick={() => handleRemoteAction("unlock")}
                        className="px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 transition-all flex items-center gap-1.5 disabled:opacity-50 cursor-pointer"
                    >
                        {actionPending === "unlock" ? "..." : "🔓 Entriegeln"}
                    </button>
                </div>

                <div className="text-[11px] text-slate-400 flex items-center gap-1 font-mono">
                    <span>OCPP 1.6-J (JSON/WSS)</span>
                </div>
            </div>

            {proModalOpen && (
                <ProUpgradeModal
                    open={proModalOpen}
                    onClose={() => setProModalOpen(false)}
                    featureName="Intelligentes Wallbox Smart-Charging"
                    featureDesc="Automatische PV-Überschussregelung und dynamische Börsenstrompreis-Ladung für dein Elektroauto."
                />
            )}
        </div>
    );
}
