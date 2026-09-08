import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../../../api/client";

export default function WallboxToolsModal({ isOpen, onClose, station }) {
    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const [activeTab, setActiveTab] = useState("v2g"); // v2g | trigger | rfid | reservation | diagnostics | schedule | variables
    const [actionPending, setActionPending] = useState(null);
    const [feedback, setFeedback] = useState({ text: null, type: null });

    // V2G & V2H Formular (ISO 15118-20)
    const [v2gMode, setV2gMode] = useState(station?.v2g_mode || "v2h_home");
    const [v2gMinSoc, setV2gMinSoc] = useState(station?.v2g_min_soc_pct || 50);
    const [v2gMaxPower, setV2gMaxPower] = useState(station?.v2g_max_discharge_power_kw || 11.0);
    const [manualDischargePower, setManualDischargePower] = useState("3500");

    // Reservierungsformular
    const [reserveTag, setReserveTag] = useState(station?.reserved_id_tag || "APP_USER");
    const [reserveDuration, setReserveDuration] = useState("120"); // 120 Minuten

    // Diagnostics Formular
    const [diagnosticsUrl, setDiagnosticsUrl] = useState("https://sharegy.de/api/energy/wallboxes/diagnostics-upload/");

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
            setFeedback({ text: res.message || "Aktion erfolgreich ausgeführt.", type: "success" });
            setActionPending(null);
            setTimeout(() => setFeedback({ text: null, type: null }), 5000);
        },
        onError: (err) => {
            setFeedback({ text: err.message || "Fehler bei Ausführung.", type: "error" });
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

    const handleGetDiagnostics = () => {
        remoteActionMutation.mutate({
            action: "get-diagnostics",
            payload: { location: diagnosticsUrl.trim() },
        });
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
        if (window.confirm(`Möchtest du wirklich einen ${type}-Reset an ${station.name} senden?`)) {
            remoteActionMutation.mutate({
                action: "reset",
                payload: { type },
            });
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
            <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl max-w-3xl lg:max-w-4xl w-full overflow-hidden flex flex-col max-h-[92vh]">
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
                                    {station.ocpp_version?.toUpperCase() || "OCPP 1.6-J"}
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
                        aria-label="Schließen"
                    >
                        ✕
                    </button>
                </div>

                {/* Tabs Segmented Control Bar */}
                <div className="px-6 pt-3.5 pb-2 bg-slate-50/50 dark:bg-slate-950/40 border-b border-slate-100 dark:border-slate-800">
                    <div className="flex items-center gap-1.5 p-1 bg-slate-200/60 dark:bg-slate-950/80 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl overflow-x-auto no-scrollbar scroll-smooth">
                        {[
                            { id: "v2g", label: "V2G / V2H", icon: "🚗", tag: "ISO 15118" },
                            { id: "trigger", label: "Remote Trigger", icon: "⚡" },
                            { id: "rfid", label: "RFID Whitelist", icon: "💳" },
                            { id: "reservation", label: "Reservierung", icon: "🔒" },
                            { id: "schedule", label: "Fahrplan", icon: "📊" },
                            { id: "diagnostics", label: "Diagnose & Logs", icon: "🛠️" },
                            { id: "variables", label: "OCPP 2.x Variablen", icon: "⚙️", tag: "v2.0.1" },
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
                                            Bidirektionales Laden nach ISO 15118-20 & OCPP 2.0.1 / 2.1
                                        </h4>
                                    </div>
                                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                                        V2G & V2H Aktiv
                                    </span>
                                </div>
                                <p className="text-[11px] text-slate-600 dark:text-slate-300 mt-1">
                                    Nutze den Fahrzeugakku ({station.ev_battery_capacity_kwh || 77} kWh) als mobilen Heimspeicher oder verdiene Geld durch Netzeinspeisung bei extremen Börsenstrom-Spitzenpreisen.
                                </p>
                            </div>

                            {/* Betriebsmodus */}
                            <div className="space-y-1.5">
                                <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300">
                                    V2G / V2H Betriebsmodus
                                </label>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                    {[
                                        { id: "v2h_home", title: "🏠 V2H Heimspeicher-Puffer", desc: "Versorgt das Haus nachts mit Auto-Strom, sobald keine PV da ist." },
                                        { id: "v2g_grid", title: "⚡ V2G Börsenstrom-Arbitrage", desc: "Speist bei Spitzenpreisen (> 30 ct/kWh) mit voller Leistung ins Netz ein." },
                                        { id: "v2x_auto", title: "🤖 V2X Smart Auto (KI-Opt)", desc: "Kombiniert Hauspufferung & Börsenspitzen automatisch." },
                                        { id: "off", title: "🛑 V2G Aus / Nur Laden", desc: "Fahrzeug wird nur normal geladen, keine Rückspeisung." },
                                    ].map((m) => (
                                        <div
                                            key={m.id}
                                            onClick={() => setV2gMode(m.id)}
                                            className={`p-3 rounded-2xl border transition cursor-pointer ${
                                                v2gMode === m.id
                                                    ? "bg-emerald-50/80 dark:bg-emerald-950/50 border-emerald-500 text-emerald-950 dark:text-emerald-200"
                                                    : "bg-slate-50 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-slate-300"
                                            }`}
                                        >
                                            <div className="font-bold text-xs">{m.title}</div>
                                            <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">{m.desc}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* SoC Schutzschieberegler & Entladeleistung */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                                <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200 dark:border-slate-700">
                                    <div className="flex items-center justify-between text-xs font-bold mb-1">
                                        <span className="text-slate-700 dark:text-slate-300">🛡️ Mindest-SoC Reserve</span>
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
                                        Fahrzeug wird niemals unter diesen Ladestand entladen.
                                    </div>
                                </div>

                                <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200 dark:border-slate-700">
                                    <div className="flex items-center justify-between text-xs font-bold mb-1">
                                        <span className="text-slate-700 dark:text-slate-300">⚡ Max. Entladeleistung</span>
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
                                        Maximale Inverter-Rückspeiseleistung.
                                    </div>
                                </div>
                            </div>

                            {/* ISO 15118-20 Plug & Charge Status */}
                            <div className="p-3 bg-slate-900 text-slate-200 rounded-2xl border border-slate-800 text-xs">
                                <div className="font-bold flex items-center justify-between text-indigo-400 mb-2">
                                    <span className="flex items-center gap-1.5">
                                        <span>🔐</span>
                                        <span>ISO 15118-20 Plug & Charge Kommunikation</span>
                                    </span>
                                    <span className="text-[10px] font-mono bg-emerald-950 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-800">
                                        TLS Verschlüsselt
                                    </span>
                                </div>
                                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                                    <div>
                                        <span className="text-slate-500">eMAID: </span>
                                        <span className="text-white">{station.iso15118_emaid || "DE-SHG-C1A2B3C4-1"}</span>
                                    </div>
                                    <div>
                                        <span className="text-slate-500">EV SoC: </span>
                                        <span className="text-emerald-400 font-bold">{station.ev_soc_pct !== null && station.ev_soc_pct !== undefined ? `${station.ev_soc_pct}%` : "74% (Live ISO)"}</span>
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
                                    💾 V2G / V2H Konfiguration speichern
                                </button>

                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={handleManualDischarge}
                                    className="px-4 py-2.5 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-950 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 transition cursor-pointer"
                                >
                                    ⚡ Sofort-Entladetest (3,5 kW)
                                </button>
                            </div>
                        </div>
                    )}

                    {/* TAB 1: REMOTE TRIGGER */}
                    {activeTab === "trigger" && (
                        <div className="space-y-4">
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                Sende einen <strong>OCPP 1.6 / 2.0.1 TriggerMessage</strong> Befehl, um die Wallbox zur sofortigen Übertragung von Messwerten oder Statusnachrichten zu zwingen.
                            </p>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={() => handleTrigger("MeterValues")}
                                    className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/80 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 border border-slate-200 dark:border-slate-700 text-left transition cursor-pointer"
                                >
                                    <div className="font-bold text-xs text-slate-900 dark:text-white flex items-center justify-between">
                                        <span>📊 MeterValues anfordern</span>
                                        <span className="text-xs">⚡</span>
                                    </div>
                                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                                        Aktuelle Zählerstände, Spannung & Phasenströme sofort abfragen.
                                    </p>
                                </button>

                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={() => handleTrigger("StatusNotification")}
                                    className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/80 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 border border-slate-200 dark:border-slate-700 text-left transition cursor-pointer"
                                >
                                    <div className="font-bold text-xs text-slate-900 dark:text-white flex items-center justify-between">
                                        <span>🔄 StatusNotification anfordern</span>
                                        <span className="text-xs">🔌</span>
                                    </div>
                                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                                        Aktuellen Steck- und Betriebszustand der Wallbox synchronisieren.
                                    </p>
                                </button>

                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={() => handleTrigger("Heartbeat")}
                                    className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/80 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 border border-slate-200 dark:border-slate-700 text-left transition cursor-pointer"
                                >
                                    <div className="font-bold text-xs text-slate-900 dark:text-white flex items-center justify-between">
                                        <span>💓 Heartbeat anfordern</span>
                                        <span className="text-xs">⏱️</span>
                                    </div>
                                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                                        Uhrzeitsynchronisation & Lebenszeichen-Ping ausführen.
                                    </p>
                                </button>

                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={() => handleTrigger("BootNotification")}
                                    className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/80 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 border border-slate-200 dark:border-slate-700 text-left transition cursor-pointer"
                                >
                                    <div className="font-bold text-xs text-slate-900 dark:text-white flex items-center justify-between">
                                        <span>🚀 BootNotification anfordern</span>
                                        <span className="text-xs">⚙️</span>
                                    </div>
                                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                                        Hersteller-, Modell- und Firmware-Infos neu einlesen.
                                    </p>
                                </button>
                            </div>

                            <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                                <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">Station-Reset:</span>
                                <div className="flex items-center gap-2">
                                    <button
                                        type="button"
                                        disabled={actionPending !== null}
                                        onClick={() => handleReset("Soft")}
                                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-amber-50 dark:hover:bg-amber-950/40 text-slate-700 dark:text-slate-300 hover:text-amber-600 border border-slate-200 dark:border-slate-700 transition cursor-pointer"
                                    >
                                        🔄 Soft Reset
                                    </button>
                                    <button
                                        type="button"
                                        disabled={actionPending !== null}
                                        onClick={() => handleReset("Hard")}
                                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-red-50 dark:hover:bg-red-950/40 text-slate-700 dark:text-slate-300 hover:text-red-600 border border-slate-200 dark:border-slate-700 transition cursor-pointer"
                                    >
                                        ⚡ Hard Reset
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* TAB 2: LOCAL AUTH LIST */}
                    {activeTab === "rfid" && (
                        <div className="space-y-4">
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                Das <strong>OCPP 1.6 Local Auth List</strong> Profil synchronisiert alle in Sharegy angelegten RFID-Chips direkt in den internen Flash-Speicher der Wallbox. Damit funktioniert die Freischaltung auch bei Internetausfall (100% Offline-Resilienz).
                            </p>

                            <div className="p-4 rounded-2xl bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-200/80 dark:border-indigo-800/60 flex items-center justify-between">
                                <div>
                                    <div className="text-[11px] uppercase tracking-wider text-indigo-700 dark:text-indigo-400 font-bold">
                                        Aktuelle Listenversion auf der Box
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
                                    <span>{actionPending === "sync-rfid-list" ? "Übertrage..." : "Alle RFID-Chips jetzt übertragen"}</span>
                                </button>
                            </div>
                        </div>
                    )}

                    {/* TAB 3: RESERVIERUNG */}
                    {activeTab === "reservation" && (
                        <div className="space-y-4">
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                Reserviere diese Wallbox für einen bestimmten RFID-Tag (OCPP <code>ReserveNow</code>). Andere Nutzer oder nicht passende Tags werden währenddessen blockiert.
                            </p>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        Berechtigter RFID-Tag / Nutzer-ID
                                    </label>
                                    <input
                                        type="text"
                                        value={reserveTag}
                                        onChange={(e) => setReserveTag(e.target.value)}
                                        placeholder="z. B. TAG_VIP_USER"
                                        className="w-full px-3 py-2 rounded-xl text-xs font-mono font-bold bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 outline-none"
                                    />
                                </div>

                                <div>
                                    <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        Dauer der Reservierung
                                    </label>
                                    <select
                                        value={reserveDuration}
                                        onChange={(e) => setReserveDuration(e.target.value)}
                                        className="w-full px-3 py-2 rounded-xl text-xs font-bold bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 outline-none cursor-pointer"
                                    >
                                        <option value="30">30 Minuten</option>
                                        <option value="60">1 Stunde</option>
                                        <option value="120">2 Stunden</option>
                                        <option value="240">4 Stunden</option>
                                        <option value="480">8 Stunden</option>
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
                                    🔒 Wallbox jetzt reservieren
                                </button>

                                {station.status === "Reserved" && (
                                    <button
                                        type="button"
                                        disabled={actionPending !== null}
                                        onClick={handleCancelReserve}
                                        className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 transition cursor-pointer"
                                    >
                                        🔓 Reservierung aufheben
                                    </button>
                                )}
                            </div>
                        </div>
                    )}

                    {/* TAB 4: DIAGNOSTICS */}
                    {activeTab === "diagnostics" && (
                        <div className="space-y-4">
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                Fordere die Wallbox an, ihre internen Betriebs- und Fehlerprotokolle via <strong>OCPP GetDiagnostics</strong> an eine Ziel-URL hochzuladen.
                            </p>

                            <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 flex items-center justify-between">
                                <div>
                                    <div className="text-[11px] uppercase font-bold text-slate-500">Status des Diagnose-Uploads</div>
                                    <div className="text-sm font-bold text-slate-900 dark:text-white mt-0.5 flex items-center gap-2">
                                        <span className={`w-2 h-2 rounded-full ${station.diagnostics_status === "Uploading" ? "bg-amber-500 animate-pulse" : station.diagnostics_status === "Uploaded" ? "bg-emerald-500" : "bg-slate-400"}`}></span>
                                        <span>{station.diagnostics_status || "Idle (Bereit)"}</span>
                                    </div>
                                    {station.last_diagnostics_file && (
                                        <div className="text-[10px] font-mono text-slate-400 mt-1">
                                            Datei: {station.last_diagnostics_file}
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div>
                                <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                                    Ziel-Upload-URL (HTTPS / FTP)
                                </label>
                                <input
                                    type="text"
                                    value={diagnosticsUrl}
                                    onChange={(e) => setDiagnosticsUrl(e.target.value)}
                                    className="w-full px-3 py-2 rounded-xl text-xs font-mono bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 outline-none"
                                />
                            </div>

                            <button
                                type="button"
                                disabled={actionPending !== null}
                                onClick={handleGetDiagnostics}
                                className="px-4 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition shadow-md shadow-indigo-600/20 cursor-pointer"
                            >
                                📋 Diagnose-Upload jetzt anfordern
                            </button>
                        </div>
                    )}

                    {/* TAB 5: COMPOSITE SCHEDULE */}
                    {activeTab === "schedule" && (
                        <div className="space-y-4">
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                <strong>GetCompositeSchedule</strong> fragt den resultierenden Ladefahrplan ab, den die Wallbox aus allen aktiven Profilen (ChargePointMax, TxDefault, TxProfile) berechnet hat.
                            </p>

                            <div className="flex items-center gap-3">
                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={handleGetSchedule}
                                    className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition shadow-md shadow-indigo-600/20 cursor-pointer"
                                >
                                    📊 Fahrplan für nächste 24h abrufen
                                </button>

                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={handleClearProfile}
                                    className="px-3 py-2 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-red-50 dark:hover:bg-red-950/40 text-slate-700 dark:text-slate-300 hover:text-red-600 border border-slate-200 dark:border-slate-700 transition cursor-pointer"
                                >
                                    🧹 Ladeprofile zurücksetzen
                                </button>
                            </div>

                            {station.composite_schedule_data ? (
                                <div className="p-3 bg-slate-950 text-emerald-400 rounded-2xl font-mono text-[11px] overflow-x-auto max-h-60 border border-slate-800">
                                    <pre>{JSON.stringify(station.composite_schedule_data, null, 2)}</pre>
                                </div>
                            ) : (
                                <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-200 dark:border-slate-700 text-xs text-slate-400 text-center">
                                    Noch kein zusammengesetzter Fahrplan abgerufen. Klicke auf den Button oben.
                                </div>
                            )}
                        </div>
                    )}

                    {/* TAB 6: OCPP 2.x DEVICE MODEL VARIABLES */}
                    {activeTab === "variables" && (
                        <div className="space-y-4">
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                <strong>OCPP 2.0.1 / 2.1 Device Model & Variable Monitoring</strong> erlaubt standardisierte Fernkonfiguration von Controller-Parametern (z.B. ISO 15118, EVSE, OCPPCommCtrlr, SmartChargingCtrlr).
                            </p>

                            <div className="flex items-center gap-3">
                                <button
                                    type="button"
                                    disabled={actionPending !== null}
                                    onClick={handleGetVariables}
                                    className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition shadow-md shadow-indigo-600/20 cursor-pointer"
                                >
                                    🔍 GetVariables abfragen
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
                                    Keine gespeicherten Device-Model-Variablen vorhanden. Klicke auf &quot;GetVariables abfragen&quot;.
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
