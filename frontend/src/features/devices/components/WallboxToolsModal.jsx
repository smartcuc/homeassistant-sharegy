import useModalDismiss from "../../../hooks/useModalDismiss";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../../../api/client";

export default function WallboxToolsModal({ isOpen, onClose, station }) {
    const { t } = useTranslation();
    useModalDismiss(isOpen, onClose);
    const queryClient = useQueryClient();

    const [activeTab, setActiveTab] = useState("v2g"); // v2g | trigger | rfid | reservation | diagnostics | schedule | variables
    const [actionPending, setActionPending] = useState(null);
    const [feedback, setFeedback] = useState({ text: null, type: null });

    // RFID Tag Management State
    const [newTagName, setNewTagName] = useState("");
    const [newTagId, setNewTagId] = useState("");
    const [rfidFormError, setRfidFormError] = useState(null);

    // RFID Tags Query
    const { data: rfidData, isLoading: rfidLoading } = useQuery({
        queryKey: ["rfid-tags"],
        queryFn: () => apiFetch("/api/energy/rfid-tags/"),
        enabled: Boolean(isOpen),
    });

    const rfidTags = rfidData?.rfid_tags || [];

    // Add RFID Tag Mutation
    const addRfidMutation = useMutation({
        mutationFn: async ({ name, id_tag }) => {
            return apiFetch("/api/energy/rfid-tags/", {
                method: "POST",
                body: JSON.stringify({ name, id_tag }),
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["rfid-tags"] });
            setNewTagName("");
            setNewTagId("");
            setRfidFormError(null);
            setFeedback({ text: t("ocpp.rfid_add_success", "RFID-Chip erfolgreich hinzugefügt."), type: "success" });
            setTimeout(() => setFeedback({ text: null, type: null }), 4000);
        },
        onError: (err) => {
            setRfidFormError(err.message || t("ocpp.action_error", "Fehler beim Hinzufügen."));
        },
    });

    // Delete RFID Tag Mutation
    const deleteRfidMutation = useMutation({
        mutationFn: async (id) => {
            return apiFetch(`/api/energy/rfid-tags/${id}/`, {
                method: "DELETE",
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["rfid-tags"] });
            setFeedback({ text: t("ocpp.rfid_deleted", "RFID-Chip gelöscht."), type: "success" });
            setTimeout(() => setFeedback({ text: null, type: null }), 4000);
        },
        onError: (err) => {
            setFeedback({ text: err.message || t("ocpp.action_error", "Fehler beim Löschen."), type: "error" });
        },
    });

    // Toggle RFID Tag Active Mutation
    const toggleRfidMutation = useMutation({
        mutationFn: async ({ id, is_active }) => {
            return apiFetch(`/api/energy/rfid-tags/${id}/`, {
                method: "PATCH",
                body: JSON.stringify({ is_active }),
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["rfid-tags"] });
        },
        onError: (err) => {
            setFeedback({ text: err.message || t("ocpp.action_error", "Fehler beim Aktualisieren."), type: "error" });
        },
    });

    // V2G & V2H Formular (ISO 15118-20)
    const [v2gMode, setV2gMode] = useState(station?.v2g_mode || "v2h_home");
    const [v2gMinSoc, setV2gMinSoc] = useState(station?.v2g_min_soc_pct || 50);
    const [v2gMaxPower, setV2gMaxPower] = useState(station?.v2g_max_discharge_power_kw || 11.0);
    const [manualDischargePower, setManualDischargePower] = useState("3500");
    const [departureTime, setDepartureTime] = useState(station?.departure_time || "07:30");
    const [targetDepartureSoc, setTargetDepartureSoc] = useState(station?.target_departure_soc_pct || 80);
    const [peakShavingThreshold, setPeakShavingThreshold] = useState(station?.peak_shaving_threshold_w || 4200);
    const [batteryCareMode, setBatteryCareMode] = useState(station?.battery_care_mode ?? true);
    const [maxCRate, setMaxCRate] = useState(station?.max_c_rate || 0.5);

    // Reservierungsformular
    const [reserveTag, setReserveTag] = useState(station?.reserved_id_tag || "APP_USER");
    const [reserveDuration, setReserveDuration] = useState("120"); // 120 Minuten

    // Generic Action Mutation
    const remoteActionMutation = useMutation({
        mutationFn: async ({ action, payload = {} }) => {
            setActionPending(action);
            return apiFetch(`/api/energy/wallboxes/${station.id}/${action}/`, {
                method: "POST",
                body: Object.keys(payload).length > 0 ? JSON.stringify(payload) : undefined,
            });
        },
        onSuccess: (res) => {
            queryClient.invalidateQueries({ queryKey: ["wallboxes"] });
            setFeedback({ text: res.message || t("ocpp.action_success", "Aktion erfolgreich ausgeführt."), type: "success" });
            setActionPending(null);
            setTimeout(() => setFeedback({ text: null, type: null }), 5000);
        },
        onError: (err) => {
            setFeedback({ text: err.message || t("ocpp.action_error", "Fehler bei Ausführung."), type: "error" });
            setActionPending(null);
        },
    });

    if (!isOpen || !station) return null;

    const handleSaveV2g = () => {
        remoteActionMutation.mutate({
            action: "set-v2g-mode",
            payload: {
                v2g_mode: v2gMode,
                v2g_min_soc_pct: parseInt(v2gMinSoc, 10) || 50,
                v2g_max_discharge_power_kw: parseFloat(v2gMaxPower) || 11.0,
                departure_time: departureTime || null,
                target_departure_soc_pct: parseInt(targetDepartureSoc, 10) || 80,
                peak_shaving_threshold_w: parseFloat(peakShavingThreshold) || 4200.0,
                battery_care_mode: Boolean(batteryCareMode),
                max_c_rate: parseFloat(maxCRate) || 0.5,
            },
        });
    };

    const handleManualDischarge = () => {
        remoteActionMutation.mutate({
            action: "v2g-discharge",
            payload: {
                power_w: parseFloat(manualDischargePower) || 3500.0,
            },
        });
    };

    const handleGetVariables = () => {
        remoteActionMutation.mutate({
            action: "get-variables",
            payload: {
                get_variable_data: [
                    { component: { name: "ChargingStation" }, variable: { name: "Model" } },
                    { component: { name: "EVSE" }, variable: { name: "AvailabilityState" } },
                    { component: { name: "ISO15118Ctrlr" }, variable: { name: "CertificateInstalled" } },
                    { component: { name: "SmartChargingCtrlr" }, variable: { name: "LimitChangeSignificance" } },
                ]
            }
        });
    };

    const handleTrigger = (requestedMessage) => {
        remoteActionMutation.mutate({
            action: "trigger-message",
            payload: { requested_message: requestedMessage, connector_id: 1 },
        });
    };

    const handleSyncRfid = () => {
        remoteActionMutation.mutate({
            action: "sync-rfid-list",
            payload: { update_type: "Full" },
        });
    };

    const handleReserve = () => {
        remoteActionMutation.mutate({
            action: "reserve",
            payload: {
                id_tag: reserveTag.trim() || "APP_USER",
                duration_minutes: parseInt(reserveDuration, 10) || 120,
                reservation_id: 1,
            },
        });
    };

    const handleCancelReserve = () => {
        remoteActionMutation.mutate({ action: "cancel-reserve" });
    };

    const handleGetSchedule = () => {
        remoteActionMutation.mutate({
            action: "get-composite-schedule",
            payload: { duration: 86400, charging_rate_unit: "A" },
        });
    };

    const handleClearProfile = () => {
        remoteActionMutation.mutate({ action: "clear-charging-profile" });
    };

    const handleReset = (type) => {
        if (window.confirm(t("ocpp.reset_confirm", { type, name: station.name, defaultValue: `Möchtest du wirklich einen ${type}-Reset an ${station.name} senden?` }))) {
            remoteActionMutation.mutate({
                action: "reset",
                payload: { type },
            });
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in" onClick={onClose}>
            <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl max-w-3xl lg:max-w-4xl w-full overflow-hidden flex flex-col max-h-[92vh]" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/70 dark:bg-slate-900/70">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-xl shadow-inner">
                            🛠️
                        </div>
                        <div>
                            <div className="flex items-center gap-2 flex-wrap">
                                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                                    {t("wallbox.tools_title", "OCPP 1.6 / 2.0.1 / 2.1 & V2G Experte")}
                                </h3>
                                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-950/70 text-indigo-700 dark:text-indigo-300 border border-indigo-300/80 dark:border-indigo-800/80">
                                    {station.ocpp_version ? station.ocpp_version.replace("ocpp", "OCPP ") : "OCPP (1.6 / 2.0.1 / 2.1)"}
                                </span>
                                {station.supports_bidirectional && (
                                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-300 border border-emerald-300/80 dark:border-emerald-800/80">
                                        ⚡ V2G / V2H
                                    </span>
                                )}
                            </div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                {station.name} · {station.vendor || "OCPP Standard"} ({station.charge_point_id})
                            </p>
                        </div>
                    </div>
                    <button
                        type="button"
                        onClick={onClose}
                        className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500 hover:text-slate-900 dark:hover:text-white flex items-center justify-center transition cursor-pointer"
                        aria-label={t("common.close", "Schließen")}
                    >
                        ✕
                    </button>
                </div>

                {/* Tabs Segmented Control Bar */}
                <div className="px-6 pt-3.5 pb-2 bg-slate-50/50 dark:bg-slate-950/40 border-b border-slate-100 dark:border-slate-800">
                    <div className="flex items-center gap-1.5 p-1 bg-slate-200/60 dark:bg-slate-950/80 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl overflow-x-auto no-scrollbar scroll-smooth">
                        {[
                            { id: "v2g", label: t("ocpp.tab_v2g", "V2G / V2H"), icon: "🚗", tag: "ISO 15118" },
                            { id: "trigger", label: t("ocpp.tab_trigger", "Remote Trigger"), icon: "⚡" },
                            { id: "rfid", label: t("ocpp.tab_rfid", "RFID Whitelist"), icon: "💳" },
                            { id: "reservation", label: t("ocpp.tab_reservation", "Reservierung"), icon: "🔒" },
                            { id: "schedule", label: t("ocpp.tab_schedule", "Fahrplan"), icon: "📊" },
                            { id: "variables", label: t("ocpp.tab_variables", "OCPP 2.x Variablen"), icon: "⚙️", tag: "v2.0.1" },
                        ].map((tab) => {
                            const isActive = activeTab === tab.id;
                            return (
                                <button
                                    key={tab.id}
                                    type="button"
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all duration-150 cursor-pointer ${
                                        isActive
                                            ? "bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm border border-slate-200/90 dark:border-slate-700 font-bold"
                                            : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-white/40 dark:hover:bg-slate-800/40 border border-transparent"
                                    }`}
                                >
                                    <span className="text-sm">{tab.icon}</span>
                                    <span>{tab.label}</span>
                                    {tab.tag && (
                                        <span className={`text-[9px] font-mono px-1.5 py-0.2 rounded-full uppercase ${
                                            isActive
                                                ? "bg-indigo-100 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300"
                                                : "bg-slate-200 dark:bg-slate-800 text-slate-500 dark:text-slate-400"
                                        }`}>
                                            {tab.tag}
                                        </span>
                                    )}
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Feedback Notification */}
                {feedback.text && (
                    <div
                        className={`mx-6 mt-4 p-3 rounded-2xl text-xs font-bold flex items-center gap-2 border animate-fade ${
                            feedback.type === "success"
                                ? "bg-emerald-50 dark:bg-emerald-950/60 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300"
                                : "bg-red-50 dark:bg-red-950/60 border-red-200 dark:border-red-800 text-red-800 dark:text-red-300"
                        }`}
                    >
                        <span>{feedback.type === "success" ? "✓" : "⚠️"}</span>
                        <span>{feedback.text}</span>
                    </div>
                )}

                {/* Body Content */}
                <div className="p-6 overflow-y-auto space-y-4 flex-1">
                    {/* TAB 0: V2G & V2H (ISO 15118-20) */}
                    {activeTab === "v2g" && (
                        <div className="space-y-4">
                            <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-indigo-500/10 border border-emerald-500/20">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <span className="text-xl">🚗⚡</span>
                                        <h4 className="font-bold text-xs text-slate-900 dark:text-white">
                                            {t("ocpp.v2g_header_title", "Bidirektionales Laden nach ISO 15118-20 & OCPP 2.0.1 / 2.1")}
                                        </h4>
                                    </div>
                                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                                        {t("ocpp.v2g_header_badge", "V2G & V2H Aktiv")}
                                    </span>
                                </div>
                                <p className="text-[11px] text-slate-600 dark:text-slate-300 mt-1">
                                    {t("ocpp.v2g_header_desc", { capacity: station.ev_battery_capacity_kwh || 77, defaultValue: `Nutze den Fahrzeugakku (${station.ev_battery_capacity_kwh || 77} kWh) als mobilen Heimspeicher oder verdiene Geld durch Netzeinspeisung bei extremen Börsenstrom-Spitzenpreisen.` })}
                                </p>
                            </div>

                            {/* Betriebsmodus */}
                            <div className="space-y-1.5">
                                <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300">
                                    {t("ocpp.v2g_mode_label", "V2G / V2H Betriebsmodus")}
                                </label>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                    {[
                                        { id: "v2h_home", title: t("ocpp.mode_v2h_home_title", "🏠 V2H Heimspeicher-Puffer"), desc: t("ocpp.mode_v2h_home_desc", "Versorgt das Haus nachts mit Auto-Strom, sobald keine PV da ist.") },
                                        { id: "peak_shaving", title: t("ocpp.mode_peak_shaving_title", "⚡ Peak Shaving (Lastspitzen)"), desc: t("ocpp.mode_peak_shaving_desc", "Kappt Netzlastspitzen über dem Grenzwert (§ 14a EnWG).") },
                                        { id: "v2g_grid", title: t("ocpp.mode_v2g_grid_title", "💶 V2G Börsenstrom-Arbitrage"), desc: t("ocpp.mode_v2g_grid_desc", "Speist bei Spitzenpreisen (> 30 ct/kWh) mit voller Leistung ins Netz ein.") },
                                        { id: "v2x_auto", title: t("ocpp.mode_v2x_auto_title", "🤖 V2X Smart Auto (KI-Opt)"), desc: t("ocpp.mode_v2x_auto_desc", "Kombiniert Peak Shaving, Hauspuffer & Börsenspitzen automatisch.") },
                                        { id: "off", title: t("ocpp.mode_off_title", "🛑 V2G Aus / Nur Laden"), desc: t("ocpp.mode_off_desc", "Fahrzeug wird nur normal geladen, keine Rückspeisung.") },
                                    ].map((m) => (
                                        <div
                                            key={m.id}
                                            onClick={() => setV2gMode(m.id)}
                                            className={`p-3 rounded-2xl border transition cursor-pointer ${
                                                v2gMode === m.id
                                                    ? "bg-emerald-50/80 dark:bg-emerald-950/50 border-emerald-500 text-emerald-950 dark:text-emerald-200 shadow-xs"
                                                    : "bg-slate-50 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-slate-300"
                                            }`}
                                        >
                                            <div className="font-bold text-xs">{m.title}</div>
                                            <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">{m.desc}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Smart Departure Guarantee (ISO 15118-20) */}
                            <div className="p-3.5 bg-indigo-50/60 dark:bg-indigo-950/30 rounded-2xl border border-indigo-200/80 dark:border-indigo-800/60 space-y-2">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <span className="text-base">⏱️</span>
                                        <span className="text-xs font-bold text-slate-900 dark:text-white">{t("ocpp.departure_guarantee_title", "Smart Departure Guarantee (ISO 15118-20)")}</span>
                                    </div>
                                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300">
                                        {t("ocpp.departure_guarantee_badge", "Automatische Vorab-Ladung")}
                                    </span>
                                </div>
                                <p className="text-[10px] text-slate-500 dark:text-slate-400">
                                    {t("ocpp.departure_guarantee_desc", "Garantiert, dass dein Auto zur Abfahrtszeit den gewünschten Ziel-SoC erreicht hat. Rückspeisung wird rechtzeitig gestoppt und das Vorab-Laden gestartet.")}
                                </p>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                                    <div>
                                        <label className="block text-[10px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                                            {t("ocpp.departure_time_label", "Abfahrtszeit")}
                                        </label>
                                        <input
                                            type="time"
                                            value={departureTime}
                                            onChange={(e) => setDepartureTime(e.target.value)}
                                            className="w-full px-3 py-1.5 rounded-xl text-xs font-mono font-bold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 outline-none"
                                        />
                                    </div>
                                    <div>
                                        <div className="flex items-center justify-between text-[10px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                                            <span>{t("ocpp.target_soc_label", "Garantierter Ziel-SoC")}</span>
                                            <span className="font-mono text-indigo-600 dark:text-indigo-400 font-bold">{targetDepartureSoc}%</span>
                                        </div>
                                        <input
                                            type="range"
                                            min="50"
                                            max="100"
                                            step="5"
                                            value={targetDepartureSoc}
                                            onChange={(e) => setTargetDepartureSoc(e.target.value)}
                                            className="w-full accent-indigo-600 cursor-pointer mt-1"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Peak Shaving & Battery Care Settings */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                                <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200 dark:border-slate-700">
                                    <div className="flex items-center justify-between text-xs font-bold mb-1">
                                        <span className="text-slate-700 dark:text-slate-300">{t("ocpp.peak_shaving_threshold_label", "⚡ Peak Shaving Schwelle")}</span>
                                        <span className="font-mono text-amber-600 dark:text-amber-400">{peakShavingThreshold} W</span>
                                    </div>
                                    <input
                                        type="number"
                                        step="100"
                                        min="1000"
                                        max="15000"
                                        value={peakShavingThreshold}
                                        onChange={(e) => setPeakShavingThreshold(e.target.value)}
                                        className="w-full px-2.5 py-1.5 rounded-xl text-xs font-mono font-bold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 outline-none"
                                    />
                                    <div className="text-[10px] text-slate-400 mt-1">
                                        {t("ocpp.peak_shaving_threshold_desc", "Entlädt das E-Auto, wenn Hauslast diese Schwelle übersteigt (§ 14a EnWG).")}
                                    </div>
                                </div>

                                <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200 dark:border-slate-700">
                                    <div className="flex items-center justify-between text-xs font-bold mb-1">
                                        <span className="text-slate-700 dark:text-slate-300">{t("ocpp.battery_care_label", "🛡️ Battery Care (C-Rate Limit)")}</span>
                                        <span className="font-mono text-emerald-600 dark:text-emerald-400">{maxCRate}C (~{Math.round(maxCRate * (station.ev_battery_capacity_kwh || 77))} kW)</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="0.2"
                                        max="1.0"
                                        step="0.05"
                                        value={maxCRate}
                                        onChange={(e) => setMaxCRate(e.target.value)}
                                        className="w-full accent-emerald-600 cursor-pointer mt-1"
                                    />
                                    <div className="text-[10px] text-slate-400 mt-1">
                                        {t("ocpp.battery_care_desc", "Schont den Akku durch Begrenzung der Dauerentladerate.")}
                                    </div>
                                </div>
                            </div>

                            {/* SoC Schutzschieberegler & Entladeleistung */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                                <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200 dark:border-slate-700">
                                    <div className="flex items-center justify-between text-xs font-bold mb-1">
                                        <span className="text-slate-700 dark:text-slate-300">{t("ocpp.min_soc_reserve_label", "🛡️ Mindest-SoC Reserve")}</span>
                                        <span className="font-mono text-indigo-600 dark:text-indigo-400">{v2gMinSoc}% (~{Math.round((v2gMinSoc / 100) * 450)} km)</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="20"
                                        max="80"
                                        step="5"
                                        value={v2gMinSoc}
                                        onChange={(e) => setV2gMinSoc(e.target.value)}
                                        className="w-full accent-indigo-600 cursor-pointer mt-1"
                                    />
                                    <div className="text-[10px] text-slate-400 mt-1">
                                        {t("ocpp.min_soc_reserve_desc", "Fahrzeug wird niemals unter diesen Ladestand entladen.")}
                                    </div>
                                </div>

                                <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200 dark:border-slate-700">
                                    <div className="flex items-center justify-between text-xs font-bold mb-1">
                                        <span className="text-slate-700 dark:text-slate-300">{t("ocpp.max_discharge_power_label", "⚡ Max. Entladeleistung")}</span>
                                        <span className="font-mono text-emerald-600 dark:text-emerald-400">{v2gMaxPower} kW</span>
                                    </div>
                                    <input
                                        type="number"
                                        step="0.5"
                                        min="1.0"
                                        max="22.0"
                                        value={v2gMaxPower}
                                        onChange={(e) => setV2gMaxPower(e.target.value)}
                                        className="w-full px-2.5 py-1.5 rounded-xl text-xs font-mono font-bold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 outline-none"
                                    />
                                    <div className="text-[10px] text-slate-400 mt-1">
                                        {t("ocpp.max_discharge_power_desc", "Maximale Inverter-Rückspeiseleistung.")}
                                    </div>
                                </div>
                            </div>

                            {/* ISO 15118-20 Plug & Charge Status */}
                            <div className="p-3 bg-slate-900 text-slate-200 rounded-2xl border border-slate-800 text-xs">
                                <div className="font-bold flex items-center justify-between text-indigo-400 mb-2">
                                    <span className="flex items-center gap-1.5">
                                        <span>🔐</span>
                                        <span>{t("ocpp.iso15118_title", "ISO 15118-20 Plug & Charge Kommunikation")}</span>
                                    </span>
                                    <span className="text-[10px] font-mono bg-emerald-950 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-800">
                                        {t("ocpp.tls_encrypted", "TLS Verschlüsselt")}
                                    </span>
                                </div>
                                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                                    <div>
                                        <span className="text-slate-500">eMAID: </span>
                                        <span className="text-white">{station.iso15118_emaid || "DE-SHG-C1A2B3C4-1"}</span>
                                    </div>
                                    <div>
                                        <span className="text-slate-500">EV SoC: </span>
                                        <span className="text-emerald-400 font-bold">{station.ev_soc_pct !== null && station.ev_soc_pct !== undefined ? `${station.ev_soc_pct}%` : `74% (${t("ocpp.live_iso", "Live ISO")})`}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center gap-3 pt-1">
                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={handleSaveV2g}
                                    className="px-5 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition shadow-md shadow-emerald-600/20 cursor-pointer"
                                >
                                    {t("ocpp.save_v2g_btn", "💾 V2G / V2H Konfiguration speichern")}
                                </button>

                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={handleManualDischarge}
                                    className="px-4 py-2.5 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-950 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 transition cursor-pointer"
                                >
                                    {t("ocpp.manual_discharge_test_btn", "⚡ Sofort-Entladetest (3,5 kW)")}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* TAB 1: REMOTE TRIGGER */}
                    {activeTab === "trigger" && (
                        <div className="space-y-4">
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                {t("ocpp.trigger_desc", "Sende einen OCPP 1.6 / 2.0.1 / 2.1 TriggerMessage Befehl, um die Wallbox zur sofortigen Übertragung von Messwerten oder Statusnachrichten zu zwingen.")}
                            </p>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={() => handleTrigger("MeterValues")}
                                    className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/80 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 border border-slate-200 dark:border-slate-700 text-left transition cursor-pointer"
                                >
                                    <div className="font-bold text-xs text-slate-900 dark:text-white flex items-center justify-between">
                                        <span>{t("ocpp.trigger_metervalues", "📊 MeterValues anfordern")}</span>
                                        <span className="text-xs">⚡</span>
                                    </div>
                                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                                        {t("ocpp.trigger_metervalues_desc", "Aktuelle Zählerstände, Spannung & Phasenströme sofort abfragen.")}
                                    </p>
                                </button>

                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={() => handleTrigger("StatusNotification")}
                                    className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/80 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 border border-slate-200 dark:border-slate-700 text-left transition cursor-pointer"
                                >
                                    <div className="font-bold text-xs text-slate-900 dark:text-white flex items-center justify-between">
                                        <span>{t("ocpp.trigger_status", "🔄 StatusNotification anfordern")}</span>
                                        <span className="text-xs">🔌</span>
                                    </div>
                                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                                        {t("ocpp.trigger_status_desc", "Aktuellen Steck- und Betriebszustand der Wallbox synchronisieren.")}
                                    </p>
                                </button>

                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={() => handleTrigger("Heartbeat")}
                                    className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/80 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 border border-slate-200 dark:border-slate-700 text-left transition cursor-pointer"
                                >
                                    <div className="font-bold text-xs text-slate-900 dark:text-white flex items-center justify-between">
                                        <span>{t("ocpp.trigger_heartbeat", "💓 Heartbeat anfordern")}</span>
                                        <span className="text-xs">⏱️</span>
                                    </div>
                                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                                        {t("ocpp.trigger_heartbeat_desc", "Uhrzeitsynchronisation & Lebenszeichen-Ping ausführen.")}
                                    </p>
                                </button>

                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={() => handleTrigger("BootNotification")}
                                    className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/80 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 border border-slate-200 dark:border-slate-700 text-left transition cursor-pointer"
                                >
                                    <div className="font-bold text-xs text-slate-900 dark:text-white flex items-center justify-between">
                                        <span>{t("ocpp.trigger_boot", "🚀 BootNotification anfordern")}</span>
                                        <span className="text-xs">⚙️</span>
                                    </div>
                                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                                        {t("ocpp.trigger_boot_desc", "Hersteller-, Modell- und Firmware-Infos neu einlesen.")}
                                    </p>
                                </button>
                            </div>

                            <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                                <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">{t("ocpp.station_reset_label", "Station-Reset:")}</span>
                                <div className="flex items-center gap-2">
                                    <button
                                        type="button"
                                        disabled={actionPending !== null}
                                        onClick={() => handleReset("Soft")}
                                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-amber-50 dark:hover:bg-amber-950/40 text-slate-700 dark:text-slate-300 hover:text-amber-600 border border-slate-200 dark:border-slate-700 transition cursor-pointer"
                                    >
                                        {t("ocpp.soft_reset", "🔄 Soft Reset")}
                                    </button>
                                    <button
                                        type="button"
                                        disabled={actionPending !== null}
                                        onClick={() => handleReset("Hard")}
                                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-red-50 dark:hover:bg-red-950/40 text-slate-700 dark:text-slate-300 hover:text-red-600 border border-slate-200 dark:border-slate-700 transition cursor-pointer"
                                    >
                                        {t("ocpp.hard_reset", "⚡ Hard Reset")}
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* TAB 2: LOCAL AUTH LIST & RFID MANAGEMENT */}
                    {activeTab === "rfid" && (
                        <div className="space-y-5">
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                {t("ocpp.rfid_desc", "Verwalte hier deine RFID-Ladekarten und Chips. Das OCPP Local Auth List Profil synchronisiert diese direkt in den internen Flash-Speicher der Wallbox (100% Offline-Resilienz auch ohne Internet).")}
                            </p>

                            {/* NEUEN RFID TAG HINZUFÜGEN */}
                            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/80 space-y-3">
                                <div className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                    <span>➕</span>
                                    <span>{t("ocpp.rfid_add_title", "Neuen RFID-Chip / Ladekarte anlegen")}</span>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-5 gap-2.5">
                                    <div className="sm:col-span-2">
                                        <label className="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">
                                            {t("ocpp.rfid_name_label", "Bezeichnung")}
                                        </label>
                                        <input
                                            type="text"
                                            value={newTagName}
                                            onChange={(e) => setNewTagName(e.target.value)}
                                            placeholder={t("ocpp.rfid_name_placeholder", "z. B. Dienstwagen / Chip 1")}
                                            className="w-full px-3 py-2 rounded-xl text-xs font-medium bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 outline-none text-slate-900 dark:text-white"
                                        />
                                    </div>
                                    <div className="sm:col-span-2">
                                        <label className="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">
                                            {t("ocpp.rfid_id_label", "RFID-UID / Tag-ID")}
                                        </label>
                                        <input
                                            type="text"
                                            value={newTagId}
                                            onChange={(e) => setNewTagId(e.target.value)}
                                            placeholder={t("ocpp.rfid_id_placeholder", "z. B. TAG-01 oder 04A1B2C3")}
                                            className="w-full px-3 py-2 rounded-xl text-xs font-mono font-bold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 outline-none text-indigo-600 dark:text-indigo-400"
                                        />
                                    </div>
                                    <div className="sm:col-span-1 flex items-end">
                                        <button
                                            type="button"
                                            disabled={!newTagId.trim() || addRfidMutation.isPending}
                                            onClick={() => addRfidMutation.mutate({ name: newTagName.trim() || "RFID-Chip", id_tag: newTagId.trim() })}
                                            className="w-full py-2 px-3 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition disabled:opacity-40 disabled:cursor-not-allowed shadow-md shadow-emerald-600/20 cursor-pointer flex items-center justify-center gap-1.5"
                                        >
                                            <span>{addRfidMutation.isPending ? "..." : "➕ Speichern"}</span>
                                        </button>
                                    </div>
                                </div>

                                {rfidFormError && (
                                    <p className="text-[11px] text-rose-500 font-semibold">{rfidFormError}</p>
                                )}
                            </div>

                            {/* LISTE DER GESPEICHERTEN RFID-TAGS */}
                            <div className="space-y-2">
                                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 flex items-center justify-between">
                                    <span>{t("ocpp.rfid_list_title", "Hinterlegte RFID-Chips")} ({rfidTags.length})</span>
                                    {rfidLoading && <span className="text-xs text-slate-400 animate-pulse">Lade...</span>}
                                </div>

                                {rfidTags.length === 0 && !rfidLoading ? (
                                    <div className="p-4 rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 text-center text-xs text-slate-400">
                                        {t("ocpp.rfid_empty", "Noch keine RFID-Chips hinterlegt. Lege oben deinen ersten Chip an.")}
                                    </div>
                                ) : (
                                    <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                                        {rfidTags.map((tag) => (
                                            <div
                                                key={tag.id}
                                                className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 flex items-center justify-between shadow-2xs hover:border-slate-300 dark:hover:border-slate-700 transition"
                                            >
                                                <div className="flex items-center gap-3">
                                                    <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-sm shadow-2xs">
                                                        💳
                                                    </div>
                                                    <div>
                                                        <div className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                                            <span>{tag.name}</span>
                                                            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                                                                {tag.id_tag}
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="flex items-center gap-2">
                                                    <button
                                                        type="button"
                                                        onClick={() => toggleRfidMutation.mutate({ id: tag.id, is_active: !tag.is_active })}
                                                        className={`px-2.5 py-1 rounded-lg text-[10px] font-bold border transition cursor-pointer ${
                                                            tag.is_active
                                                                ? "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800"
                                                                : "bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500 border-slate-200 dark:border-slate-700"
                                                        }`}
                                                    >
                                                        {tag.is_active ? t("ocpp.rfid_active", "Aktiv") : t("ocpp.rfid_inactive", "Gesperrt")}
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => {
                                                            if (window.confirm(t("ocpp.rfid_delete_confirm", "Möchtest du diesen RFID-Tag wirklich löschen?"))) {
                                                                deleteRfidMutation.mutate(tag.id);
                                                            }
                                                        }}
                                                        className="w-7 h-7 rounded-lg bg-rose-50 dark:bg-rose-950/40 hover:bg-rose-100 dark:hover:bg-rose-900/60 text-rose-600 dark:text-rose-400 border border-rose-200/80 dark:border-rose-800/80 flex items-center justify-center text-xs transition cursor-pointer"
                                                        title="Löschen"
                                                    >
                                                        🗑️
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {/* SYNCHRONISIERUNG MIT WALLBOX */}
                            <div className="p-4 rounded-2xl bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-200/80 dark:border-indigo-800/60 flex items-center justify-between">
                                <div>
                                    <div className="text-[11px] uppercase tracking-wider text-indigo-700 dark:text-indigo-400 font-bold">
                                        {t("ocpp.rfid_version_label", "Aktuelle Listenversion auf der Box")}
                                    </div>
                                    <div className="text-2xl font-bold font-mono text-indigo-950 dark:text-indigo-200 mt-0.5">
                                        v{station.local_auth_list_version || 0}
                                    </div>
                                </div>
                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={handleSyncRfid}
                                    className="px-4 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition shadow-md shadow-indigo-600/20 cursor-pointer flex items-center gap-2"
                                >
                                    <span>📶</span>
                                    <span>{actionPending === "sync-rfid-list" ? t("ocpp.rfid_syncing", "Übertrage...") : t("ocpp.rfid_sync_btn", "Alle RFID-Chips jetzt übertragen")}</span>
                                </button>
                            </div>
                        </div>
                    )}

                    {/* TAB 3: RESERVIERUNG */}
                    {activeTab === "reservation" && (
                        <div className="space-y-4">
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                {t("ocpp.reservation_desc", "Reserviere diese Wallbox für einen bestimmten RFID-Tag (OCPP ReserveNow). Andere Nutzer oder nicht passende Tags werden währenddessen blockiert.")}
                            </p>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        {t("ocpp.reservation_tag_label", "Berechtigter RFID-Tag / Nutzer-ID")}
                                    </label>
                                    <input
                                        type="text"
                                        value={reserveTag}
                                        onChange={(e) => setReserveTag(e.target.value)}
                                        placeholder={t("ocpp.reservation_tag_placeholder", "z. B. TAG_VIP_USER")}
                                        className="w-full px-3 py-2 rounded-xl text-xs font-mono font-bold bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 outline-none"
                                    />
                                </div>

                                <div>
                                    <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        {t("ocpp.reservation_duration_label", "Dauer der Reservierung")}
                                    </label>
                                    <select
                                        value={reserveDuration}
                                        onChange={(e) => setReserveDuration(e.target.value)}
                                        className="w-full px-3 py-2 rounded-xl text-xs font-bold bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 outline-none cursor-pointer"
                                    >
                                        <option value="30">{t("ocpp.dur_30m", "30 Minuten")}</option>
                                        <option value="60">{t("ocpp.dur_1h", "1 Stunde")}</option>
                                        <option value="120">{t("ocpp.dur_2h", "2 Stunden")}</option>
                                        <option value="240">{t("ocpp.dur_4h", "4 Stunden")}</option>
                                        <option value="480">{t("ocpp.dur_8h", "8 Stunden")}</option>
                                    </select>
                                </div>
                            </div>

                            <div className="pt-2 flex items-center gap-3">
                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={handleReserve}
                                    className="px-4 py-2 rounded-xl text-xs font-bold bg-purple-600 hover:bg-purple-500 text-white transition shadow-md shadow-purple-600/20 cursor-pointer"
                                >
                                    {t("ocpp.reserve_btn", "🔒 Wallbox jetzt reservieren")}
                                </button>

                                {station.status === "Reserved" && (
                                    <button
                                        type="button"
                                        disabled={actionPending !== null}
                                        onClick={handleCancelReserve}
                                        className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 transition cursor-pointer"
                                    >
                                        {t("ocpp.cancel_reserve_btn", "🔓 Reservierung aufheben")}
                                    </button>
                                )}
                            </div>
                        </div>
                    )}

                    {/* TAB 4: COMPOSITE SCHEDULE */}
                    {activeTab === "schedule" && (
                        <div className="space-y-4">
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                {t("ocpp.schedule_desc", "GetCompositeSchedule fragt den resultierenden Ladefahrplan ab, den die Wallbox aus allen aktiven Profilen (ChargePointMax, TxDefault, TxProfile) berechnet hat.")}
                            </p>

                            <div className="flex items-center gap-3">
                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={handleGetSchedule}
                                    className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition shadow-md shadow-indigo-600/20 cursor-pointer"
                                >
                                    {t("ocpp.get_schedule_btn", "📊 Fahrplan für nächste 24h abrufen")}
                                </button>

                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={handleClearProfile}
                                    className="px-3 py-2 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-red-50 dark:hover:bg-red-950/40 text-slate-700 dark:text-slate-300 hover:text-red-600 border border-slate-200 dark:border-slate-700 transition cursor-pointer"
                                >
                                    {t("ocpp.clear_profile_btn", "🧹 Ladeprofile zurücksetzen")}
                                </button>
                            </div>

                            {station.composite_schedule_data ? (
                                <div className="p-3 bg-slate-950 text-emerald-400 rounded-2xl font-mono text-[11px] overflow-x-auto max-h-60 border border-slate-800">
                                    <pre>{JSON.stringify(station.composite_schedule_data, null, 2)}</pre>
                                </div>
                            ) : (
                                <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-200 dark:border-slate-700 text-xs text-slate-400 text-center">
                                    {t("ocpp.no_schedule_data", "Noch kein zusammengesetzter Fahrplan abgerufen. Klicke auf den Button oben.")}
                                </div>
                            )}
                        </div>
                    )}

                    {/* TAB 6: OCPP 2.x DEVICE MODEL VARIABLES */}
                    {activeTab === "variables" && (
                        <div className="space-y-4">
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                {t("ocpp.variables_desc", "OCPP 2.0.1 / 2.1 Device Model & Variable Monitoring erlaubt standardisierte Fernkonfiguration von Controller-Parametern (z.B. ISO 15118, EVSE, OCPPCommCtrlr, SmartChargingCtrlr).")}
                            </p>

                            <div className="flex items-center gap-3">
                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={handleGetVariables}
                                    className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition shadow-md shadow-indigo-600/20 cursor-pointer"
                                >
                                    {t("ocpp.get_variables_btn", "🔍 GetVariables abfragen")}
                                </button>
                            </div>

                            {station.device_variables && Object.keys(station.device_variables).length > 0 ? (
                                <div className="space-y-2">
                                    {Object.entries(station.device_variables).map(([key, val]) => (
                                        <div key={key} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 flex items-center justify-between text-xs font-mono">
                                            <span className="font-bold text-slate-800 dark:text-slate-200">{key}</span>
                                            <span className="px-2 py-0.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-bold">
                                                {typeof val === "object" ? JSON.stringify(val.value ?? val) : String(val)}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-200 dark:border-slate-700 text-xs text-slate-400 text-center">
                                    {t("ocpp.no_variables_data", "Keine gespeicherten Device-Model-Variablen vorhanden. Klicke auf \"GetVariables abfragen\".")}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
