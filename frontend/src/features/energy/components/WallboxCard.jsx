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
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
                    Offline
                </span>
            );
        }
        switch (status) {
            case "Charging":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 animate-pulse">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                        Lädt aktiv
                    </span>
                );
            case "Preparing":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                        Fahrzeug verbunden
                    </span>
                );
            case "SuspendedEVSE":
            case "SuspendedEV":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                        Warte auf Solarstrom
                    </span>
                );
            default:
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                        Bereit
                    </span>
                );
        }
    }

    if (wallboxesQuery.isLoading) {
        return (
            <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-6 shadow-xl animate-pulse min-h-[260px] flex items-center justify-center text-slate-500">
                <div className="flex items-center gap-3">
                    <div className="w-5 h-5 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin"></div>
                    <span>Lade Wallbox- & Smart-Charging-Daten...</span>
                </div>
            </div>
        );
    }

    // Wenn noch keine Wallbox verbunden ist
    if (!activeStation) {
        return (
            <div className="bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-slate-950/80 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-6 shadow-xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>

                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                E-Auto & Wallbox Smart-Charging
                                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                                    OCPP 1.6-J
                                </span>
                            </h3>
                            <p className="text-xs text-slate-400">
                                Hardwarefreies PV-Überschuss- und Börsenstrom-Laden für jede gängige Wallbox.
                            </p>
                        </div>
                    </div>
                </div>

                <div className="bg-slate-950/50 border border-slate-800/60 rounded-xl p-6 text-center my-4">
                    <div className="w-12 h-12 rounded-full bg-slate-800/80 border border-slate-700 flex items-center justify-center mx-auto mb-3 text-slate-400">
                        <svg className="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                    </div>
                    <h4 className="text-sm font-semibold text-slate-200 mb-1">Keine Wallbox angebunden</h4>
                    <p className="text-xs text-slate-400 max-w-md mx-auto mb-4">
                        Verbinde deine Easee, go-eCharger, Keba, Alfen, Mennekes oder Zaptec in unter 60 Sekunden via Cloud-WebSocket.
                    </p>
                    <button
                        type="button"
                        onClick={onOpenAddModal}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold transition-all shadow-lg shadow-emerald-500/20 hover:scale-[1.02] active:scale-[0.98]"
                    >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Wallbox jetzt verbinden
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
        <div className="bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-slate-950/80 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-6 shadow-xl relative overflow-hidden">
            {/* Ambient Background Glow */}
            <div className="absolute top-0 right-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

            {/* Header mit Wallbox-Auswahl & Status */}
            <div className="flex flex-wrap items-center justify-between gap-3 mb-5 border-b border-slate-800/60 pb-4">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h3 className="text-lg font-bold text-white tracking-tight">
                                {activeStation.name || "Wallbox"}
                            </h3>
                            {getStatusBadge(activeStation.status, activeStation.is_online)}
                        </div>
                        <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
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
                            className="bg-slate-950/80 border border-slate-700/80 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-emerald-500"
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
                        className="px-2.5 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors flex items-center gap-1"
                    >
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        <span>Neu</span>
                    </button>
                </div>
            </div>

            {/* Feedback Alert */}
            {feedback.text && (
                <div
                    className={`mb-4 p-3 rounded-xl text-xs font-medium flex items-center gap-2 border transition-all ${
                        feedback.type === "success"
                            ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-300"
                            : "bg-red-950/40 border-red-500/40 text-red-300"
                    }`}
                >
                    <span className="text-sm">{feedback.type === "success" ? "✅" : "⚠️"}</span>
                    <span>{feedback.text}</span>
                </div>
            )}

            {/* Live-Ladeleistung & Phasen-Cockpit */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-5">
                {/* Ladeleistung */}
                <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between relative overflow-hidden">
                    <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                        Ladeleistung (Live)
                    </div>
                    <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-black text-white tracking-tight font-mono">
                            {activePowerKw}
                        </span>
                        <span className="text-sm font-semibold text-emerald-400">kW</span>
                    </div>
                    <div className="text-[11px] text-slate-400 mt-2 flex items-center gap-1">
                        <span>Sollwert:</span>
                        <span className="font-mono text-slate-200 font-bold">{targetAmpere} A</span>
                        <span className="text-slate-400">({activeStation.phases || 3}-phasig)</span>
                    </div>
                </div>

                {/* Phasenströme L1 / L2 / L3 */}
                <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between">
                    <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                        Phasenströme (L1 / L2 / L3)
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-center my-auto">
                        <div className="bg-slate-900/80 border border-slate-800 rounded-lg py-1 px-1.5">
                            <div className="text-[10px] text-slate-400">L1</div>
                            <div className="text-xs font-mono font-bold text-slate-200">
                                {Number(activeStation.current_l1 || 0).toFixed(1)} A
                            </div>
                        </div>
                        <div className="bg-slate-900/80 border border-slate-800 rounded-lg py-1 px-1.5">
                            <div className="text-[10px] text-slate-400">L2</div>
                            <div className="text-xs font-mono font-bold text-slate-200">
                                {Number(activeStation.current_l2 || 0).toFixed(1)} A
                            </div>
                        </div>
                        <div className="bg-slate-900/80 border border-slate-800 rounded-lg py-1 px-1.5">
                            <div className="text-[10px] text-slate-400">L3</div>
                            <div className="text-xs font-mono font-bold text-slate-200">
                                {Number(activeStation.current_l3 || 0).toFixed(1)} A
                            </div>
                        </div>
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1 flex justify-between">
                        <span>Spannung: ~{Math.round(activeStation.voltage_v || 230)} V</span>
                        <span>{activeStation.connector_status || "Kabel gesteckt"}</span>
                    </div>
                </div>

                {/* Session-Statistik */}
                <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between">
                    <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                        Aktuelle Session
                    </div>
                    <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-black text-white tracking-tight font-mono">
                            {sessionKwh}
                        </span>
                        <span className="text-sm font-semibold text-slate-400">kWh</span>
                    </div>
                    <div className="text-[11px] text-emerald-400 mt-2 flex items-center justify-between">
                        <span>☀️ PV-Quote: {currentMode === "pv_surplus" ? "100%" : "85%"}</span>
                        <span className="text-slate-400">ID: #{activeStation.active_transaction_id || "–"}</span>
                    </div>
                </div>
            </div>

            {/* Smart-Charging Modus-Umschalter */}
            <div className="mb-5">
                <div className="flex items-center justify-between mb-2">
                    <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                        <span>Smart-Charging Lademodus</span>
                        {!isPro && <ProBadge size="xs" />}
                    </label>
                    <span className="text-[11px] text-slate-400">
                        {currentMode === "pv_surplus" && "Lädt nur bei echtem PV-Überschuss (ab 4,1 kW 3-phasig)"}
                        {currentMode === "min_pv" && "Mindestens 6 A (1,4–4,1 kW) + Solar-Booster bei Überschuss"}
                        {currentMode === "spot_price" && `Lädt bei Börsenpreisen ≤ ${activeStation.price_threshold_ct || 15} ct/kWh`}
                        {currentMode === "instant" && "Maximale Ladeleistung (11 / 22 kW)"}
                        {currentMode === "off" && "Laden pausiert / Wallbox verriegelt"}
                    </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                    {/* 1. PV Überschuss */}
                    <button
                        type="button"
                        onClick={() => handleModeClick("pv_surplus")}
                        className={`p-3 rounded-xl border text-left transition-all relative ${
                            currentMode === "pv_surplus"
                                ? "bg-amber-500/10 border-amber-500/50 text-amber-300 shadow-lg shadow-amber-500/10 ring-1 ring-amber-500/40"
                                : "bg-slate-950/40 border-slate-800 text-slate-300 hover:bg-slate-800/60 hover:border-slate-700"
                        }`}
                    >
                        <div className="text-base mb-1">☀️</div>
                        <div className="text-xs font-bold">Nur Solar</div>
                        <div className="text-[10px] text-slate-400 truncate">100% Sonnenstrom</div>
                    </button>

                    {/* 2. Min + PV */}
                    <button
                        type="button"
                        onClick={() => handleModeClick("min_pv")}
                        className={`p-3 rounded-xl border text-left transition-all relative ${
                            currentMode === "min_pv"
                                ? "bg-emerald-500/10 border-emerald-500/50 text-emerald-300 shadow-lg shadow-emerald-500/10 ring-1 ring-emerald-500/40"
                                : "bg-slate-950/40 border-slate-800 text-slate-300 hover:bg-slate-800/60 hover:border-slate-700"
                        }`}
                    >
                        <div className="text-base mb-1">⛅</div>
                        <div className="text-xs font-bold">Min + PV</div>
                        <div className="text-[10px] text-slate-400 truncate">Basis + Solar-Boost</div>
                    </button>

                    {/* 3. Börsenpreisgeführt */}
                    <button
                        type="button"
                        onClick={() => handleModeClick("spot_price")}
                        className={`p-3 rounded-xl border text-left transition-all relative ${
                            currentMode === "spot_price"
                                ? "bg-blue-500/10 border-blue-500/50 text-blue-300 shadow-lg shadow-blue-500/10 ring-1 ring-blue-500/40"
                                : "bg-slate-950/40 border-slate-800 text-slate-300 hover:bg-slate-800/60 hover:border-slate-700"
                        }`}
                    >
                        <div className="text-base mb-1">💶</div>
                        <div className="text-xs font-bold">Börsenpreis</div>
                        <div className="text-[10px] text-slate-400 truncate">≤ {activeStation.price_threshold_ct || 15} ct/kWh</div>
                    </button>

                    {/* 4. Sofort / Boost */}
                    <button
                        type="button"
                        onClick={() => handleModeClick("instant")}
                        className={`p-3 rounded-xl border text-left transition-all relative ${
                            currentMode === "instant"
                                ? "bg-purple-500/10 border-purple-500/50 text-purple-300 shadow-lg shadow-purple-500/10 ring-1 ring-purple-500/40"
                                : "bg-slate-950/40 border-slate-800 text-slate-300 hover:bg-slate-800/60 hover:border-slate-700"
                        }`}
                    >
                        <div className="text-base mb-1">⚡</div>
                        <div className="text-xs font-bold">Sofortladen</div>
                        <div className="text-[10px] text-slate-400 truncate">Max. 11/22 kW</div>
                    </button>

                    {/* 5. Stop / Pause */}
                    <button
                        type="button"
                        onClick={() => handleModeClick("off")}
                        className={`p-3 rounded-xl border text-left transition-all col-span-2 sm:col-span-1 relative ${
                            currentMode === "off"
                                ? "bg-red-500/10 border-red-500/50 text-red-300 shadow-lg shadow-red-500/10 ring-1 ring-red-500/40"
                                : "bg-slate-950/40 border-slate-800 text-slate-300 hover:bg-slate-800/60 hover:border-slate-700"
                        }`}
                    >
                        <div className="text-base mb-1">🛑</div>
                        <div className="text-xs font-bold">Gesperrt</div>
                        <div className="text-[10px] text-slate-400 truncate">Laden pausiert</div>
                    </button>
                </div>
            </div>

            {/* Schnell-Aktionsleiste (Start / Stop / Unlock) */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-slate-800/60">
                <div className="flex items-center gap-2">
                    <button
                        type="button"
                        disabled={actionPending !== null}
                        onClick={() => handleRemoteAction("remote-start")}
                        className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 transition-all flex items-center gap-1.5 disabled:opacity-50"
                    >
                        {actionPending === "remote-start" ? "..." : "▶️ Start"}
                    </button>

                    <button
                        type="button"
                        disabled={actionPending !== null}
                        onClick={() => handleRemoteAction("remote-stop")}
                        className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 transition-all flex items-center gap-1.5 disabled:opacity-50"
                    >
                        {actionPending === "remote-stop" ? "..." : "⏹️ Stop"}
                    </button>

                    <button
                        type="button"
                        disabled={actionPending !== null}
                        onClick={() => handleRemoteAction("unlock")}
                        className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all flex items-center gap-1.5 disabled:opacity-50"
                    >
                        {actionPending === "unlock" ? "..." : "🔓 Kabel entriegeln"}
                    </button>
                </div>

                <div className="text-[11px] text-slate-500 flex items-center gap-1 font-mono">
                    <span>Protokoll: OCPP 1.6-J (JSON/WSS)</span>
                </div>
            </div>

            {proModalOpen && (
                <ProUpgradeModal
                    isOpen={proModalOpen}
                    onClose={() => setProModalOpen(false)}
                    feature={{
                        name: "Intelligentes Wallbox Smart-Charging",
                        desc: "Automatische PV-Überschussregelung und dynamische Börsenstrompreis-Ladung für dein Elektroauto.",
                    }}
                />
            )}
        </div>
    );
}
