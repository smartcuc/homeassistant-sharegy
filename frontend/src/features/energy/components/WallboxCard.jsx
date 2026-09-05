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
            <div className="absolute top-0 right-0 w-48 h-48 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none"></div>

            <div className="space-y-4 relative z-10">
                {/* Header mit Wallbox-Auswahl & Status */}
                <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-2xl shadow-xs">
                            🚗
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
                                    {activeStation.name || "Wallbox"}
                                </h3>
                                {getStatusBadge(activeStation.status, activeStation.is_online)}
                            </div>
                            <p className="text-xs text-slate-400 mt-0.5">
                                {activeStation.vendor || "OCPP"} · {activeStation.phases || 3}-phasig ({targetAmpere} A)
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        {wallboxes.length > 1 && (
                            <select
                                value={activeStation.id}
                                onChange={(e) => setSelectedStationId(e.target.value)}
                                className="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl px-2.5 py-1.5 text-xs font-bold cursor-pointer outline-none shadow-2xs"
                            >
                                {wallboxes.map((wb) => (
                                    <option key={wb.id} value={wb.id}>
                                        {wb.name}
                                    </option>
                                ))}
                            </select>
                        )}

                        <button
                            type="button"
                            onClick={onOpenAddModal}
                            title="Weitere Wallbox hinzufügen"
                            className="p-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 transition cursor-pointer shadow-2xs"
                        >
                            ➕
                        </button>
                    </div>
                </div>

                {/* Feedback Alert */}
                {feedback.text && (
                    <div
                        className={`p-2.5 rounded-2xl text-xs font-bold flex items-center gap-2 border transition-all ${
                            feedback.type === "success"
                                ? "bg-emerald-50 dark:bg-emerald-950/60 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300"
                                : "bg-red-50 dark:bg-red-950/60 border-red-200 dark:border-red-800 text-red-800 dark:text-red-300"
                        }`}
                    >
                        <span className="text-sm">{feedback.type === "success" ? "✓" : "⚠️"}</span>
                        <span>{feedback.text}</span>
                    </div>
                )}

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500">Ladeleistung (Live)</div>
                        <div className="text-lg font-bold font-mono text-slate-900 dark:text-white mt-0.5 flex items-baseline justify-between">
                            <span>{activePowerKw} kW</span>
                            <span className="text-xs font-normal text-slate-400 font-sans">{activeStation.phases || 3}P · {targetAmpere}A</span>
                        </div>
                    </div>

                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500">Geladene Energie</div>
                        <div className="text-lg font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-0.5 flex items-baseline justify-between">
                            <span>{sessionKwh} kWh</span>
                            <span className="text-xs font-normal text-emerald-600 dark:text-emerald-400 font-sans">☀️ {currentMode === "pv_surplus" ? "100%" : "85%"} PV</span>
                        </div>
                    </div>
                </div>

                {/* Smart-Charging Modus-Umschalter Strip */}
                <div className="p-3 bg-white/70 dark:bg-slate-800/50 rounded-2xl border border-slate-200/60 dark:border-slate-700/50 flex items-center justify-between gap-3 text-xs">
                    <div className="min-w-0">
                        <div className="font-bold text-slate-800 dark:text-slate-200 truncate flex items-center gap-1.5">
                            <span>⚡ Smart-Charging Modus</span>
                            {!isPro && <ProBadge size="xs" />}
                        </div>
                        <div className="text-[11px] text-slate-400 truncate">
                            {currentMode === "pv_surplus" ? "Nur echter Solarüberschuss" : currentMode === "min_pv" ? "Min. Basisleistung + Solarboost" : currentMode === "spot_price" ? "Günstigste Börsenstunden" : currentMode === "instant" ? "Maximale Ladeleistung" : "Ladevorgang pausiert"}
                        </div>
                    </div>
                    <select
                        value={currentMode}
                        onChange={(e) => handleModeClick(e.target.value)}
                        className="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl px-2.5 py-1.5 text-xs font-bold cursor-pointer outline-none shrink-0"
                    >
                        <option value="pv_surplus">☀️ Nur Solar</option>
                        <option value="min_pv">⛅ Min + PV</option>
                        <option value="spot_price">💶 Börsenpreis</option>
                        <option value="instant">⚡ Sofortladen</option>
                        <option value="off">🛑 Gesperrt</option>
                    </select>
                </div>
            </div>

            {/* Actions Footer */}
            <div className="pt-4 mt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between gap-3 relative z-10">
                <span className="text-xs text-slate-400">
                    Kabel: <strong className="text-emerald-600 dark:text-emerald-400">{activeStation.connector_status || "Gesteckt"}</strong>
                </span>
                <div className="flex items-center gap-2">
                    <button
                        type="button"
                        disabled={actionPending !== null}
                        onClick={() => handleRemoteAction("remote-start")}
                        className="px-3.5 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white transition-all disabled:opacity-50 cursor-pointer shadow-xs"
                    >
                        {actionPending === "remote-start" ? "..." : "▶️ Start"}
                    </button>

                    <button
                        type="button"
                        disabled={actionPending !== null}
                        onClick={() => handleRemoteAction("remote-stop")}
                        className="px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-200 hover:bg-slate-300 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 transition-all disabled:opacity-50 cursor-pointer"
                    >
                        {actionPending === "remote-stop" ? "..." : "⏹️ Stop"}
                    </button>

                    <button
                        type="button"
                        disabled={actionPending !== null}
                        onClick={() => handleRemoteAction("unlock")}
                        className="px-2.5 py-2 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 transition-all disabled:opacity-50 cursor-pointer"
                        title="Ladekabel entriegeln"
                    >
                        🔓
                    </button>
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
