import { useState, lazy, Suspense } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import { useSubscription } from "../../../hooks/useSubscription";
import ProBadge from "../../../components/common/ProBadge";
import ProUpgradeModal from "../../../components/common/ProUpgradeModal";

const EditWallboxModal = lazy(() => import("../../devices/components/EditWallboxModal"));
const WallboxToolsModal = lazy(() => import("../../devices/components/WallboxToolsModal"));

export default function WallboxCard({ onOpenAddModal }) {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const queryClient = useQueryClient();

    const [proModalOpen, setProModalOpen] = useState(false);
    const [editModalOpen, setEditModalOpen] = useState(false);
    const [toolsModalOpen, setToolsModalOpen] = useState(false);
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

    // 3. Wallbox Löschen
    const deleteMutation = useMutation({
        mutationFn: async (id) => {
            return apiFetch(`/api/energy/wallboxes/${id}/`, {
                method: "DELETE",
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["wallboxes"] });
            setSelectedStationId(null);
            setFeedback({
                text: t("wallbox.deleted", "Wallbox erfolgreich gelöscht."),
                type: "success",
            });
            setTimeout(() => setFeedback({ text: null, type: null }), 4000);
        },
        onError: (err) => {
            setFeedback({ text: err.message || "Fehler beim Löschen der Wallbox.", type: "error" });
        },
    });

    const handleDelete = () => {
        if (!activeStation) return;
        const stationName = activeStation.name || activeStation.charge_point_id || "Wallbox";
        if (window.confirm(t("wallbox.confirm_delete", `Möchtest du die Wallbox "${stationName}" wirklich löschen?`))) {
            deleteMutation.mutate(activeStation.id);
        }
    };

    // 4. Remote Aktionen (Start, Stop, Unlock)
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
                return t("wallbox.mode_pv_surplus", "☀️ Nur Solarüberschuss");
            case "min_pv":
                return t("wallbox.mode_min_pv", "⛅ Min + PV-Überschuss");
            case "spot_price":
                return t("wallbox.mode_spot_price", "💶 Börsenpreisgeführt");
            case "instant":
                return t("wallbox.mode_instant", "⚡ Sofortladen (Max. Power)");
            case "off":
                return t("wallbox.mode_off", "🛑 Gesperrt / Pausiert");
            default:
                return mode;
        }
    }

    function getStatusBadge(status, isOnline, isDischargingV2g) {
        if (!isOnline) {
            return (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400 dark:bg-slate-500"></span>
                    {t("common.offline", "Offline")}
                </span>
            );
        }
        if (isDischargingV2g) {
            return (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-teal-500/15 text-teal-700 dark:text-teal-300 border border-teal-500/30 animate-pulse">
                    <span className="w-1.5 h-1.5 rounded-full bg-teal-500"></span>
                    {t("wallbox.status_v2g_discharging", "🔄 V2G / V2H Entladung")}
                </span>
            );
        }
        switch (status) {
            case "Charging":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30 animate-pulse">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                        {t("wallbox.status_charging", "Lädt aktiv")}
                    </span>
                );
            case "Preparing":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-700 dark:text-amber-400 border border-amber-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                        {t("wallbox.status_preparing", "Fahrzeug verbunden")}
                    </span>
                );
            case "SuspendedEVSE":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/15 text-cyan-700 dark:text-cyan-400 border border-cyan-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
                        {t("wallbox.status_suspended_evse", "Pausiert (Station)")}
                    </span>
                );
            case "SuspendedEV":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/15 text-cyan-700 dark:text-cyan-400 border border-cyan-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
                        {t("wallbox.status_suspended_ev", "Pausiert (Fahrzeug voll)")}
                    </span>
                );
            case "Reserved":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-500/15 text-purple-700 dark:text-purple-400 border border-purple-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span>
                        {t("wallbox.status_reserved", "🔒 Reserviert")}
                    </span>
                );
            case "Faulted":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-700 dark:text-rose-400 border border-rose-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
                        {t("wallbox.status_faulted", "⚠️ Störung")}
                    </span>
                );
            case "Unavailable":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-500/15 text-slate-700 dark:text-slate-400 border border-slate-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
                        {t("wallbox.status_unavailable", "Außer Betrieb")}
                    </span>
                );
            case "Finishing":
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/15 text-indigo-700 dark:text-indigo-400 border border-indigo-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                        {t("wallbox.status_finishing", "Beendet")}
                    </span>
                );
            case "Available":
            default:
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/15 text-blue-700 dark:text-blue-400 border border-blue-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                        {t("wallbox.status_ready", "Bereit")}
                    </span>
                );
        }
    }

    if (wallboxesQuery.isLoading) {
        return (
            <div className="bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 rounded-3xl p-6 shadow-sm animate-pulse min-h-[260px] flex items-center justify-center text-slate-400">
                <div className="flex items-center gap-3">
                    <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                    <span>{t("wallbox.loading_data", "Lade Wallbox- & Smart-Charging-Daten...")}</span>
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
                                {t("wallbox.empty_title", "E-Auto & Wallbox Smart-Charging")}
                                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                                    OCPP 1.6-J
                                </span>
                            </h3>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                {t("wallbox.empty_subtitle", "Hardwarefreies PV-Überschuss- und Börsenstrom-Laden für jede gängige Wallbox.")}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="bg-slate-50 dark:bg-slate-950/50 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-6 text-center my-4">
                    <div className="w-12 h-12 rounded-full bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 flex items-center justify-center mx-auto mb-3 text-slate-400 shadow-2xs">
                        <span className="text-xl">🔌</span>
                    </div>
                    <h4 className="text-sm font-bold text-slate-900 dark:text-slate-200 mb-1">{t("wallbox.empty_no_wallbox", "Keine Wallbox angebunden")}</h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-4">
                        {t("wallbox.empty_connect_desc", "Verbinde deine Easee, go-eCharger, Keba, Alfen, Mennekes, Zaptec oder OpenWB in unter 60 Sekunden via Cloud-WebSocket.")}
                    </p>
                    <button
                        type="button"
                        onClick={onOpenAddModal}
                        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-md shadow-emerald-600/20 cursor-pointer"
                    >
                        <span>＋</span>
                        <span>{t("wallbox.connect_btn", "Wallbox jetzt verbinden")}</span>
                    </button>
                </div>
            </div>
        );
    }

    const currentMode = activeStation.smart_charging_mode || "pv_surplus";
    const isOnline = Boolean(activeStation.is_online);
    const isCharging = Boolean(activeStation.is_charging || activeStation.status === "Charging" || activeStation.active_session);
    const isDischargingV2g = Boolean(activeStation.is_discharging_v2g || (activeStation.v2g_discharge_power_w && activeStation.v2g_discharge_power_w > 50.0));
    const isReserved = activeStation.status === "Reserved";
    const isFaulted = activeStation.status === "Faulted";
    const isUnavailable = activeStation.status === "Unavailable";
    const activePowerKw = Number(activeStation.power_kw ?? activeStation.active_power_kw ?? ((activeStation.active_power_w || 0) / 1000)).toFixed(2);
    const sessionKwh = Number(activeStation.session_energy_kwh || activeStation.active_session?.total_energy_kwh || 0).toFixed(1);
    const targetAmpere = activeStation.target_current_a || (isCharging ? activeStation.max_current_a : 0.0) || 16.0;
    const hasRealSoc = activeStation.ev_soc_pct !== null && activeStation.ev_soc_pct !== undefined;
    const evSocValue = hasRealSoc ? Math.round(Number(activeStation.ev_soc_pct)) : Math.min(100, Math.round(42 + (Number(sessionKwh) / 60) * 100));
    const liveCurrentA = activeStation.current_l1 || targetAmpere;

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
                                {getStatusBadge(activeStation.status, activeStation.is_online, isDischargingV2g)}
                            </div>
                            <p className="text-xs text-slate-400 mt-0.5">
                                {activeStation.vendor || "OCPP"} · {activeStation.phases ? `${activeStation.phases}-phasig` : "DC CCS2"} ({liveCurrentA} A) · {activeStation.ocpp_version?.toUpperCase() || "OCPP 1.6-J"} {activeStation.v2g_mode && activeStation.v2g_mode !== "off" && (activeStation.v2g_mode === "peak_shaving" ? "· ⚡ Peak Shaving" : "· 🔄 V2G")} {activeStation.departure_time && `· ⏱️ ${activeStation.departure_time}`}
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
                            onClick={() => setToolsModalOpen(true)}
                            title={t("wallbox.tools_btn_title", "OCPP Expertenwerkzeuge, Offline-RFID Sync & V2G")}
                            className="p-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 hover:bg-emerald-50 dark:hover:bg-emerald-950/40 text-slate-600 hover:text-emerald-600 dark:text-slate-300 dark:hover:text-emerald-400 border border-slate-200 dark:border-slate-700 transition cursor-pointer shadow-2xs"
                        >
                            🛠️
                        </button>

                        <button
                            type="button"
                            onClick={() => setEditModalOpen(true)}
                            title={t("wallbox.edit_btn_title", "Einstellungen & Ladeparameter bearbeiten")}
                            className="p-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 text-slate-600 hover:text-indigo-600 dark:text-slate-300 dark:hover:text-indigo-400 border border-slate-200 dark:border-slate-700 transition cursor-pointer shadow-2xs"
                        >
                            ⚙️
                        </button>

                        <button
                            type="button"
                            onClick={onOpenAddModal}
                            title={t("wallbox.add_btn_title", "Weitere Wallbox hinzufügen")}
                            className="p-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 transition cursor-pointer shadow-2xs"
                        >
                            ➕
                        </button>

                        <button
                            type="button"
                            onClick={handleDelete}
                            disabled={deleteMutation.isPending}
                            title={t("wallbox.delete_btn_title", "Diese Wallbox löschen")}
                            className="p-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 hover:bg-red-50 dark:hover:bg-red-950/40 text-slate-400 hover:text-red-600 dark:hover:text-red-400 border border-slate-200 dark:border-slate-700 hover:border-red-200 dark:hover:border-red-900 transition cursor-pointer shadow-2xs disabled:opacity-50"
                        >
                            🗑️
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
                <div className="grid grid-cols-3 gap-2.5">
                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[10px] text-slate-500 uppercase font-semibold">{t("wallbox.charging_power", "Ladeleistung")}</div>
                        <div className="text-base sm:text-lg font-bold font-mono text-slate-900 dark:text-white mt-0.5 flex items-baseline justify-between">
                            <span>{activePowerKw} kW</span>
                        </div>
                        <div className="text-[10px] text-slate-400 font-sans mt-0.5 truncate">
                            {liveCurrentA} A {activeStation.voltage_v ? `· ${Math.round(activeStation.voltage_v)} V` : ""}
                        </div>
                    </div>

                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[10px] text-slate-500 uppercase font-semibold">{t("wallbox.charged_session", "Geladen (Session)")}</div>
                        <div className="text-base sm:text-lg font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-0.5 flex items-baseline justify-between">
                            <span>{sessionKwh} kWh</span>
                        </div>
                        <div className="text-[10px] text-emerald-600 dark:text-emerald-400 font-sans mt-0.5 font-semibold truncate">
                            +{Math.round(Number(sessionKwh) / 0.17)} {t("wallbox.km_range", "km Reichweite")}
                        </div>
                    </div>

                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[10px] text-slate-500 uppercase font-semibold flex items-center justify-between">
                            <span>{t("wallbox.ev_battery", "Fahrzeug-Akku")}</span>
                            {hasRealSoc && (
                                <span className="text-[9px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-1.5 py-0.2 rounded-md">
                                    Live ISO
                                </span>
                            )}
                        </div>
                        <div className="text-base sm:text-lg font-bold font-mono text-indigo-600 dark:text-indigo-400 mt-0.5 flex items-baseline justify-between">
                            <span>{evSocValue}%</span>
                        </div>
                        <div className="text-[10px] text-slate-400 font-sans mt-0.5 truncate">
                            ~{Math.round((evSocValue / 100) * (activeStation.ev_battery_capacity_kwh ? (activeStation.ev_battery_capacity_kwh / 0.17) : 450))} {t("wallbox.km_total", "km Gesamt")}
                        </div>
                    </div>
                </div>

                {/* ⏰ SMARTES ZIELLADEN & ABFAHRTSZEIT-PLANER */}
                <div className="p-3 bg-indigo-50/80 dark:bg-indigo-950/40 rounded-2xl border border-indigo-200/80 dark:border-indigo-800/60 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs">
                    <div className="flex items-center gap-2">
                        <span className="text-base shrink-0">⏰</span>
                        <div>
                            <div className="font-bold text-indigo-950 dark:text-indigo-200">
                                {t("wallbox.departure_title", "Zielladen & Abfahrtszeit (Departure Ready)")}
                            </div>
                            <div className="text-[11px] text-indigo-700/80 dark:text-indigo-400">
                                {t("wallbox.departure_subtitle", "Lädt primär mit PV-Reststrom & günstigsten Nacht-Spotpreisen")}
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-2 self-end sm:self-center">
                        <div className="flex items-center gap-1 bg-white dark:bg-slate-900 px-2 py-1 rounded-xl border border-indigo-200 dark:border-indigo-800">
                            <span className="text-[10px] text-slate-400">{t("wallbox.departure_time", "Abfahrt:")}</span>
                            <input
                                type="time"
                                defaultValue="07:30"
                                className="font-bold font-mono text-xs text-slate-900 dark:text-white bg-transparent outline-none cursor-pointer"
                            />
                        </div>
                        <div className="flex items-center gap-1 bg-white dark:bg-slate-900 px-2 py-1 rounded-xl border border-indigo-200 dark:border-indigo-800">
                            <span className="text-[10px] text-slate-400">{t("wallbox.target_soc", "Ziel:")}</span>
                            <span className="font-bold font-mono text-xs text-indigo-600 dark:text-indigo-400">80%</span>
                        </div>
                    </div>
                </div>

                {/* Smart-Charging Modus-Umschalter Strip */}
                <div className="p-3 bg-white/70 dark:bg-slate-800/50 rounded-2xl border border-slate-200/60 dark:border-slate-700/50 flex items-center justify-between gap-3 text-xs">
                    <div className="min-w-0">
                        <div className="font-bold text-slate-800 dark:text-slate-200 truncate flex items-center gap-1.5">
                            <span>⚡ {t("wallbox.smart_charging_mode", "Smart-Charging Modus")}</span>
                            {!isPro && <ProBadge size="xs" />}
                        </div>
                        <div className="text-[11px] text-slate-400 truncate">
                            {currentMode === "pv_surplus" ? t("wallbox.mode_desc_pv", "Nur echter Solarüberschuss") : currentMode === "min_pv" ? t("wallbox.mode_desc_min_pv", "Min. Basisleistung + Solarboost") : currentMode === "spot_price" ? t("wallbox.mode_desc_spot", "Günstigste Börsenstunden") : currentMode === "instant" ? t("wallbox.mode_desc_instant", "Maximale Ladeleistung") : t("wallbox.mode_desc_paused", "Ladevorgang pausiert")}
                        </div>
                    </div>
                    <select
                        value={currentMode}
                        onChange={(e) => handleModeClick(e.target.value)}
                        className="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl px-2.5 py-1.5 text-xs font-bold cursor-pointer outline-none shrink-0"
                    >
                        <option value="pv_surplus">{t("wallbox.opt_pv_surplus", "☀️ Nur Solar")}</option>
                        <option value="min_pv">{t("wallbox.opt_min_pv", "⛅ Min + PV")}</option>
                        <option value="spot_price">{t("wallbox.opt_spot_price", "💶 Börsenpreis")}</option>
                        <option value="instant">{t("wallbox.opt_instant", "⚡ Sofortladen")}</option>
                        <option value="off">{t("wallbox.opt_off", "🛑 Gesperrt")}</option>
                    </select>
                </div>

                {/* 🛡️ § 14a EnWG Compliance Badge */}
                <div className="flex items-center justify-between px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-[11px] text-emerald-800 dark:text-emerald-300 font-semibold">
                    <span className="flex items-center gap-1.5">
                        <span>🛡️</span>
                        <span>{t("wallbox.enwg_badge", "§ 14a EnWG steuerbar (4,2 kW Netzentgelt-Schutz aktiv)")}</span>
                    </span>
                    <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">{t("wallbox.enwg_bonus", "+160 € / a Vorteil")}</span>
                </div>
            </div>

            {/* Actions Footer */}
            <div className="pt-4 mt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between gap-3 relative z-10">
                <span className="text-xs text-slate-400">
                    {t("wallbox.cable", "Kabel:")} <strong className={`${isCharging || activeStation.status === "Preparing" ? "text-emerald-600 dark:text-emerald-400" : isReserved ? "text-purple-600 dark:text-purple-400" : "text-slate-600 dark:text-slate-300"}`}>
                        {activeStation.connector_status || (activeStation.status === "Preparing" || isCharging ? t("wallbox.connected", "Gesteckt") : isReserved ? t("wallbox.status_reserved", "Reserviert") : t("wallbox.ready", "Bereit"))}
                    </strong>
                </span>
                <div className="flex items-center gap-2">
                    {isReserved && (
                        <button
                            type="button"
                            disabled={actionPending !== null}
                            onClick={() => handleRemoteAction("cancel-reserve")}
                            className="px-2.5 py-2 rounded-xl text-xs font-bold bg-purple-100 hover:bg-purple-200 dark:bg-purple-950/50 dark:hover:bg-purple-900/60 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800 transition-all cursor-pointer shadow-2xs"
                            title={t("wallbox.cancel_reserve_title", "Reservierung aufheben")}
                        >
                            {actionPending === "cancel-reserve" ? "..." : t("wallbox.cancel_reserve_btn", "🔓 Freigeben")}
                        </button>
                    )}

                    <button
                        type="button"
                        disabled={actionPending !== null || isCharging || !isOnline || isFaulted || isUnavailable}
                        onClick={() => handleRemoteAction("remote-start")}
                        className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all shadow-xs cursor-pointer ${
                            isCharging || !isOnline || isFaulted || isUnavailable
                                ? "bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed opacity-50 shadow-none"
                                : "bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/20"
                        }`}
                        title={isCharging ? t("wallbox.already_charging", "Ladevorgang läuft bereits") : t("wallbox.start_charging", "Ladevorgang manuell starten")}
                    >
                        {actionPending === "remote-start" ? "..." : t("wallbox.start_btn", "▶️ Start")}
                    </button>

                    <button
                        type="button"
                        disabled={actionPending !== null || (!isCharging && !activeStation.active_session)}
                        onClick={() => handleRemoteAction("remote-stop")}
                        className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                            isCharging || activeStation.active_session
                                ? "bg-rose-600 hover:bg-rose-500 text-white shadow-md shadow-rose-600/25 animate-pulse"
                                : "bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed opacity-50"
                        }`}
                        title={!isCharging && !activeStation.active_session ? t("wallbox.no_active_session", "Kein aktiver Ladevorgang zum Stoppen") : t("wallbox.stop_charging", "Ladevorgang jetzt stoppen")}
                    >
                        {actionPending === "remote-stop" ? "..." : t("wallbox.stop_btn", "⏹️ Stop")}
                    </button>

                    <button
                        type="button"
                        disabled={actionPending !== null || !isOnline}
                        onClick={() => handleRemoteAction("unlock")}
                        className="px-2.5 py-2 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 transition-all disabled:opacity-50 cursor-pointer shadow-2xs"
                        title={t("wallbox.unlock_cable_title", "Ladekabel entriegeln")}
                    >
                        🔓
                    </button>
                </div>
            </div>

            {proModalOpen && (
                <ProUpgradeModal
                    open={proModalOpen}
                    onClose={() => setProModalOpen(false)}
                    featureName={t("wallbox.pro_modal_title", "Intelligentes Wallbox Smart-Charging")}
                    featureDesc={t("wallbox.pro_modal_desc", "Automatische PV-Überschussregelung und dynamische Börsenstrompreis-Ladung für dein Elektroauto.")}
                />
            )}

            <Suspense fallback={null}>
                {editModalOpen && (
                    <EditWallboxModal
                        isOpen={editModalOpen}
                        onClose={() => setEditModalOpen(false)}
                        station={activeStation}
                    />
                )}

                {toolsModalOpen && (
                    <WallboxToolsModal
                        isOpen={toolsModalOpen}
                        onClose={() => setToolsModalOpen(false)}
                        station={activeStation}
                    />
                )}
            </Suspense>
        </div>
    );
}
