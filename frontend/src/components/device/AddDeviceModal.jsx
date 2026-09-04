/*
# src/components/device/AddDeviceModal.jsx
*/

import { useEffect, useState, useMemo } from "react";
import { QRCodeSVG } from "qrcode.react";
import { useCreateDevice } from "../../hooks/useCreateDevice";
import { useDeviceStatus } from "../../hooks/useDevices";
import { useStructure } from "../../hooks/useStructure";
import { apiFetch } from "../../api/client";
import { useTranslation } from "react-i18next";

/* =========================================================
   HELPERS
========================================================= */

function safeCopy(text, setCopiedKey, key) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
        setCopiedKey(key);
        setTimeout(() => setCopiedKey(null), 1500);
    }
}

/* =========================================================
   MAIN MODAL
========================================================= */

export default function AddDeviceModal({ open, onClose }) {
    const { t, i18n } = useTranslation();

    const presets = useMemo(() => [
        {
            id: "balkonkraftwerk",
            title: t("device_add.preset_bkw_title", "Balkonkraftwerk & PV"),
            icon: "☀️",
            desc: t("device_add.preset_bkw_desc", "Hoymiles, OpenDTU, Shelly Plus 1PM, Envertech, TSUN"),
            badge: t("devices.role_producer", "Erzeuger"),
            defaults: {
                name: "Balkonkraftwerk",
                role_key: "producer",
                generator_type_key: "solar",
                energy_signal_type_key: "solar_production",
                metric_key: "power",
            }
        },
        {
            id: "grid_meter",
            title: t("device_add.preset_meter_title", "Haupt- & Netzzähler"),
            icon: "⚡",
            desc: t("device_add.preset_meter_desc", "Shelly Pro 3EM / EM, Powerfox, Tibber Pulse, IR-Lesekopf"),
            badge: t("devices.role_grid", "Netzmessung"),
            defaults: {
                name: "Hauptzähler",
                role_key: "consumer",
                energy_signal_type_key: "grid_exchange",
                metric_key: "power",
            }
        },
        {
            id: "consumer",
            title: t("device_add.preset_plug_title", "Smarte Steckdose & Last"),
            icon: "🔌",
            desc: t("device_add.preset_plug_desc", "Shelly Plug S, Tasmota, Wärmepumpe, Wallbox"),
            badge: t("devices.role_consumer", "Verbraucher"),
            defaults: {
                name: "Steckdose",
                role_key: "consumer",
                energy_signal_type_key: "household_load",
                metric_key: "power",
            }
        },
        {
            id: "battery",
            title: t("device_add.preset_battery_title", "Batteriespeicher & Powerstation"),
            icon: "🔋",
            desc: t("device_add.preset_battery_desc", "EcoFlow, Anker Solix, Zendure, Victron"),
            badge: t("devices.role_battery", "Speicher"),
            defaults: {
                name: "Batteriespeicher",
                role_key: "both",
                energy_signal_type_key: "battery_storage",
                metric_key: "power",
            }
        },
        {
            id: "iobroker",
            title: t("device_add.preset_hub_title", "ioBroker & Smart Home"),
            icon: "🔧",
            desc: t("device_add.preset_hub_desc", "ioBroker MQTT-Adapter, Home Assistant, Node-RED"),
            badge: "Hub",
            defaults: {
                name: "ioBroker Gerät",
                role_key: "consumer",
                energy_signal_type_key: "household_load",
                metric_key: "power",
            }
        },
        {
            id: "sensor",
            title: t("device_add.preset_sensor_title", "Umwelt- & Klimasensor"),
            icon: "🌡️",
            desc: t("device_add.preset_sensor_desc", "Temperatur, Feuchte, Luftdruck, CO2, Raumklima"),
            badge: "Sensor",
            defaults: {
                name: "Klimasensor",
                role_key: "consumer",
                metric_key: "temperature",
            }
        }
    ], [t, i18n.language]);

    const [step, setStep] = useState(1);
    const [selectedPreset, setSelectedPreset] = useState(presets[0]);
    const [name, setName] = useState("");
    const [roomId, setRoomId] = useState("");
    const [floorId, setFloorId] = useState("");
    const [device, setDevice] = useState(null);
    const [showMqttPassword, setShowMqttPassword] = useState(false);

    const { data: structure } = useStructure();
    const createDevice = useCreateDevice();

    useEffect(() => {
        if (open) {
            setStep(1);
            setSelectedPreset(presets[0]);
            setName("");
            setRoomId("");
            setFloorId("");
            setDevice(null);
        }
    }, [open, presets]);

    if (!open) return null;

    function next() {
        setStep((s) => Math.min(s + 1, 3));
    }

    function back() {
        setStep((s) => Math.max(s - 1, 1));
    }

    return (
        <div
            className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 relative"
                onClick={(e) => e.stopPropagation()}
            >
                {/* STEP INDICATOR */}
                <div className="flex items-center gap-2 mb-6 text-xs text-gray-500 font-medium">
                    <span className={`px-2.5 py-1 rounded-full ${step === 1 ? "bg-indigo-600 text-white font-bold" : "bg-gray-100 text-gray-700"}`}>
                        1. {t("device_add.step1_title", "Preset")}
                    </span>
                    <span>→</span>
                    <span className={`px-2.5 py-1 rounded-full ${step === 2 ? "bg-indigo-600 text-white font-bold" : "bg-gray-100 text-gray-700"}`}>
                        2. {t("device_add.step2_title", "Name & Raum")}
                    </span>
                    <span>→</span>
                    <span className={`px-2.5 py-1 rounded-full ${step === 3 ? "bg-indigo-600 text-white font-bold" : "bg-gray-100 text-gray-700"}`}>
                        3. {t("device_add.step3_title", "Verbindung & Test")}
                    </span>
                </div>

                {step === 1 && (
                    <StepPresetSelection
                        presets={presets}
                        selectedPreset={selectedPreset}
                        onSelect={(preset) => {
                            setSelectedPreset(preset);
                            setName(preset.defaults.name || "");
                            next();
                        }}
                    />
                )}

                {step === 2 && (
                    <StepNameAndLocation
                        name={name}
                        setName={setName}
                        roomId={roomId}
                        setRoomId={setRoomId}
                        floorId={floorId}
                        setFloorId={setFloorId}
                        preset={selectedPreset}
                        structure={structure}
                        loading={createDevice.isLoading}
                        onNext={async () => {
                            const identifier = name
                                .toLowerCase()
                                .replace(/ä/g, "ae")
                                .replace(/ö/g, "oe")
                                .replace(/ü/g, "ue")
                                .replace(/ß/g, "ss")
                                .replace(/\s+/g, "_")
                                .replace(/[^\w]/g, "")
                                .replace(/_+/g, "_")
                                .replace(/^_|_$/g, "") || `device_${Date.now()}`;

                            try {
                                const payload = {
                                    identifier,
                                    name,
                                    role_key: selectedPreset.defaults.role_key,
                                    generator_type_key: selectedPreset.defaults.generator_type_key,
                                    energy_signal_type_key: selectedPreset.defaults.energy_signal_type_key,
                                    metric_key: selectedPreset.defaults.metric_key,
                                    room_id: roomId ? Number(roomId) : null,
                                    floor_id: floorId ? Number(floorId) : null,
                                };

                                const result = await createDevice.mutateAsync(payload);
                                setDevice(result);
                                next();
                            } catch {
                                alert(t("common.error", "Fehler beim Erstellen des Geräts"));
                            }
                        }}
                        onBack={back}
                    />
                )}

                {step === 3 && device && (
                    <StepConnectionAndGuides
                        device={device}
                        preset={selectedPreset}
                        onClose={onClose}
                    />
                )}

                <button
                    onClick={onClose}
                    className="absolute top-5 right-5 text-gray-400 hover:text-gray-600 transition p-1"
                >
                    ✕
                </button>
            </div>
        </div>
    );
}

/* =========================================================
   STEP 1: PRESET SELECTION
========================================================= */

function StepPresetSelection({ presets, selectedPreset, onSelect }) {
    const { t } = useTranslation();

    return (
        <div>
            <h2 className="text-xl font-bold text-gray-900 mb-1">
                🔌 {t("device_add.step1_title", "Was möchtest du anbinden?")}
            </h2>
            <p className="text-sm text-gray-500 mb-5">
                {t("device_add.step1_desc", "Wähle ein passendes Preset. Sharegy konfiguriert die Messgrößen und Energieflüsse automatisch vor.")}
            </p>

            <div className="grid sm:grid-cols-2 gap-3 max-h-[60vh] overflow-y-auto pr-1">
                {presets.map((preset) => {
                    const isSelected = selectedPreset?.id === preset.id;
                    return (
                        <button
                            key={preset.id}
                            onClick={() => onSelect(preset)}
                            className={`
                                text-left p-4 rounded-xl border transition-all flex flex-col justify-between
                                ${isSelected
                                    ? "border-indigo-500 bg-indigo-50/60 ring-2 ring-indigo-500/20 shadow-sm"
                                    : "border-gray-200 bg-white hover:border-indigo-300 hover:bg-gray-50"
                                }
                            `}
                        >
                            <div className="flex items-start justify-between gap-2 mb-2">
                                <div className="text-2xl">{preset.icon}</div>
                                <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
                                    {preset.badge}
                                </span>
                            </div>
                            <div>
                                <div className="font-semibold text-gray-900 text-sm mb-1">
                                    {preset.title}
                                </div>
                                <div className="text-xs text-gray-500 line-clamp-2">
                                    {preset.desc}
                                </div>
                            </div>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}

/* =========================================================
   STEP 2: NAME & LOCATION
========================================================= */

function StepNameAndLocation({
    name,
    setName,
    roomId,
    setRoomId,
    floorId,
    setFloorId,
    preset,
    structure,
    loading,
    onNext,
    onBack,
}) {
    const { t } = useTranslation();
    const rooms = structure?.rooms || [];
    const floors = structure?.floors || [];

    function submit(e) {
        e.preventDefault();
        if (name.trim() && !loading) {
            onNext();
        }
    }

    return (
        <form onSubmit={submit}>
            <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">{preset.icon}</span>
                <h2 className="text-xl font-bold text-gray-900">
                    {t("device_add.step3_title", "Gerät benennen & zuordnen")}
                </h2>
            </div>
            <p className="text-sm text-gray-500 mb-5">
                {t("device_add.step3_desc", "Passe Gerätename, Raum und Etage an. Die Konfiguration kann jederzeit nachträglich geändert werden.")}
            </p>

            <div className="space-y-4 mb-6">
                <div>
                    <label className="text-xs font-semibold text-gray-700 block mb-1.5">
                        {t("device_add.device_name", "Gerätename")} *
                    </label>
                    <input
                        autoFocus
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="z. B. Balkonkraftwerk Süd"
                        className="w-full px-3.5 py-2.5 border rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm font-medium"
                        required
                    />
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <label className="text-xs font-semibold text-gray-700 block mb-1.5">
                            {t("device_add.floor_optional", "Etage (optional)")}
                        </label>
                        <select
                            value={floorId}
                            onChange={(e) => setFloorId(e.target.value)}
                            className="w-full px-3 py-2 border rounded-xl bg-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                            <option value="">🏢 {t("devices.no_floor", "Keine Etage")}</option>
                            {floors.map((f) => (
                                <option key={f.id} value={f.id}>{f.name}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="text-xs font-semibold text-gray-700 block mb-1.5">
                            {t("device_add.room_optional", "Raum (optional)")}
                        </label>
                        <select
                            value={roomId}
                            onChange={(e) => setRoomId(e.target.value)}
                            className="w-full px-3 py-2 border rounded-xl bg-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                            <option value="">🚪 {t("devices.no_room", "Kein Raum")}</option>
                            {rooms.map((r) => (
                                <option key={r.id} value={r.id}>{r.name}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* AUTO-CONFIG PREVIEW BADGE */}
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs">
                    <span className="text-gray-500">{t("device_setup.signal_prompt", "Automatische Vorkonfiguration:")}</span>
                    <span className="font-semibold text-indigo-700">
                        {preset.defaults.role_key} • {preset.defaults.metric_key || "power"}
                    </span>
                </div>
            </div>

            <div className="flex justify-between pt-2">
                <button
                    type="button"
                    onClick={onBack}
                    disabled={loading}
                    className="px-4 py-2.5 border rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 transition"
                >
                    ← {t("common.back", "Zurück")}
                </button>

                <button
                    type="submit"
                    disabled={!name.trim() || loading}
                    className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-xl transition shadow-sm disabled:opacity-50 flex items-center gap-2"
                >
                    {loading ? t("common.saving", "Wird erstellt...") : `${t("common.next", "Weiter")} →`}
                </button>
            </div>
        </form>
    );
}

/* =========================================================
   STEP 3: CONNECTION, GUIDES & LIVE-TEST
========================================================= */

function StepConnectionAndGuides({ device, preset, onClose }) {
    const { t } = useTranslation();
    const [copiedKey, setCopiedKey] = useState(null);
    const [activeTab, setActiveTab] = useState(
        preset.id === "iobroker" ? "iobroker" : "shelly"
    );
    const [showQR, setShowQR] = useState(false);
    const [simulating, setSimulating] = useState(false);
    const [simulatedValue, setSimulatedValue] = useState(null);

    const { data: devices } = useDeviceStatus();
    const status = devices?.find((d) => d.identifier === device.identifier);
    const isOnline = status?.status === "online" || status?.status === "stale" || simulatedValue !== null;

    const topic = `h/${device.mqtt_token}/${device.identifier}`;
    const wsUrl = `wss://${window.location.host.includes("localhost") ? "sharegy.de" : window.location.host}/ws/energy/${device.mqtt_token}/`;

    // Test-Messwert Simulator
    async function handleSimulate(val = 450.0) {
        try {
            setSimulating(true);
            await apiFetch(`/api/devices/${device.id}/simulate/`, {
                method: "POST",
                body: JSON.stringify({ value: val, metric_key: preset.defaults.metric_key || "power" }),
            });
            setSimulatedValue(val);
        } catch {
            alert(t("common.error", "Simulation fehlgeschlagen"));
        } finally {
            setSimulating(false);
        }
    }

    return (
        <div>
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                    <span className="text-2xl">{preset.icon}</span>
                    <div>
                        <h2 className="text-xl font-bold text-gray-900">
                            {device.name || device.identifier} {t("common.edit", "verbinden")}
                        </h2>
                        <div className="text-xs text-gray-500">
                            WSS & MQTT Interface bereit
                        </div>
                    </div>
                </div>

                {isOnline ? (
                    <div className="flex items-center gap-1.5 px-3 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full border border-green-200">
                        <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        🟢 {t("device_add.connected_live", "Verbunden (Live-Daten aktiv)")}
                    </div>
                ) : (
                    <div className="flex items-center gap-1.5 px-3 py-1 bg-amber-50 text-amber-800 text-xs font-semibold rounded-full border border-amber-200">
                        <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping" />
                        ⏳ {t("device_add.waiting_data", "Warte auf erste Messwerte...")}
                    </div>
                )}
            </div>

            {/* ⚡ PROMINENT WEBSOCKET (WSS) BANNER (SHELLY & MODERN DEVICES) */}
            <div className="bg-gradient-to-r from-amber-50/90 via-orange-50/40 to-white border border-amber-200 rounded-2xl p-4 mb-4 shadow-2xs">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                        <span className="text-base">⚡</span>
                        <span className="text-xs font-bold text-amber-950 uppercase tracking-wider">
                            Empfohlen für Shelly & Smart Plugs: Outbound-WebSocket (WSS)
                        </span>
                        <span className="text-[10px] font-extrabold bg-amber-200 text-amber-900 px-2 py-0.5 rounded-full">
                            Port 443 · Zero-Config
                        </span>
                    </div>
                    <button
                        type="button"
                        onClick={() => safeCopy(wsUrl, setCopiedKey, "ws_url")}
                        className="px-2.5 py-1 bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold rounded-lg transition cursor-pointer shadow-2xs flex items-center gap-1"
                    >
                        {copiedKey === "ws_url" ? "✅ WSS-URL kopiert!" : "📋 WSS-URL kopieren"}
                    </button>
                </div>
                <div className="flex items-center justify-between p-2.5 bg-white border border-amber-200/90 rounded-xl font-mono text-xs text-amber-950 font-semibold break-all">
                    <span>{wsUrl}</span>
                </div>
                <div className="text-[11px] text-amber-900/80 mt-2 flex items-center gap-3">
                    <span>🔒 TLS Verschlüsselt</span>
                    <span>•</span>
                    <span>🛡️ Funktioniert ohne Router-Portfreigaben</span>
                    <span>•</span>
                    <span>💡 Sofortige Relais-Schaltung</span>
                </div>
            </div>

            {/* TOP GRID: MQTT CREDENTIALS & QR */}
            <div className="grid md:grid-cols-[1fr_2fr] gap-3 mb-4">
                {/* QR CODE CARD */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-center flex flex-col items-center justify-center">
                    <div
                        onClick={() => setShowQR(true)}
                        className="cursor-pointer p-2 bg-white rounded-lg border border-slate-200 shadow-xs hover:shadow-md transition"
                    >
                        <QRCodeSVG
                            value={JSON.stringify({
                                wss_url: wsUrl,
                                host: device.mqtt_host,
                                port: device.mqtt_port,
                                username: device.mqtt_username,
                                password: device.mqtt_password,
                                topic,
                            })}
                            size={105}
                        />
                    </div>
                    <span className="text-[10px] text-gray-400 mt-2">
                        {t("interfaces.qr_modal_desc", "QR-Code für Companion Apps")}
                    </span>
                </div>

                {/* CREDENTIALS TABLE (MQTT) */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 flex flex-col justify-between">
                    <div className="text-[10px] uppercase font-bold text-gray-500 mb-1.5 flex items-center justify-between">
                        <span>📡 Klassische MQTT Zugangsdaten (ioBroker, OpenDTU, Tasmota)</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                        <div>
                            <span className="text-gray-400 block text-[10px] uppercase font-bold">{t("interfaces.broker_host", "Host")}</span>
                            <span className="font-mono font-medium text-gray-800">{device.mqtt_host || "mqtt.sharegy.de"}</span>
                        </div>
                        <div>
                            <span className="text-gray-400 block text-[10px] uppercase font-bold">{t("interfaces.port", "Port")}</span>
                            <span className="font-mono font-medium text-gray-800">{device.mqtt_port || 1883}</span>
                        </div>
                        <div>
                            <span className="text-gray-400 block text-[10px] uppercase font-bold">{t("interfaces.username", "Benutzer")}</span>
                            <span className="font-mono font-medium text-gray-800 break-all">{device.mqtt_username}</span>
                        </div>
                        <div>
                            <div className="flex items-center justify-between">
                                <span className="text-gray-400 block text-[10px] uppercase font-bold">{t("interfaces.password", "Passwort")}</span>
                                <button
                                    type="button"
                                    onClick={() => setShowMqttPassword((v) => !v)}
                                    className="text-[10px] text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer"
                                    title={showMqttPassword ? "Passwort verbergen" : "Passwort anzeigen"}
                                >
                                    {showMqttPassword ? "🙈" : "👁️"}
                                </button>
                            </div>
                            <span className="font-mono font-medium text-gray-800 break-all">
                                {showMqttPassword ? device.mqtt_password : "••••••••••••••••"}
                            </span>
                        </div>
                    </div>

                    <button
                        onClick={() => {
                            const text = `WSS-URL: ${wsUrl}\nMQTT-Host: ${device.mqtt_host || "mqtt.sharegy.de"}\nMQTT-Port: ${device.mqtt_port || 1883}\nUser: ${device.mqtt_username}\nPass: ${device.mqtt_password}\nTopic: ${topic}`;
                            safeCopy(text, setCopiedKey, "all");
                        }}
                        className="w-full bg-white hover:bg-slate-100 border border-slate-300 text-gray-700 text-xs font-semibold py-2 px-3 rounded-lg transition flex items-center justify-center gap-1.5 cursor-pointer"
                    >
                        {copiedKey === "all" ? `✅ ${t("common.copied", "Kopiert!")}` : t("interfaces.copy_all", "📋 Alle Zugangsdaten kopieren")}
                    </button>
                </div>
            </div>

            {/* GUIDES TAB BAR */}
            <div className="border border-slate-200 rounded-xl overflow-hidden mb-4 bg-white shadow-xs">
                <div className="flex border-b border-slate-200 bg-slate-50 text-xs font-semibold overflow-x-auto">
                    {[
                        { id: "shelly", label: "⚡ Shelly (WSS - Empfohlen)", icon: "⚡" },
                        { id: "homeassistant", label: t("interfaces.tab_ha", "🏠 Home Assistant"), icon: "🏠" },
                        { id: "iobroker", label: t("interfaces.tab_iobroker", "🔧 ioBroker"), icon: "🔧" },
                        { id: "mqtt", label: "📡 Tasmota / OpenDTU", icon: "📡" },
                        { id: "otel", label: t("interfaces.tab_otel", "🔭 OpenTelemetry"), icon: "🔭" },
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`px-4 py-2.5 transition whitespace-nowrap cursor-pointer ${activeTab === tab.id
                                    ? "bg-white text-indigo-600 border-b-2 border-indigo-600 font-bold"
                                    : "text-gray-500 hover:text-gray-800 hover:bg-slate-100"
                                }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* TAB CONTENTS */}
                <div className="p-4 text-xs text-gray-700 leading-relaxed max-h-52 overflow-y-auto">
                    {/* SHELLY WSS GUIDE */}
                    {activeTab === "shelly" && (
                        <div className="space-y-2">
                            <div className="font-bold text-gray-900 text-sm flex items-center gap-1.5">
                                ⚡ Shelly Web-Interface (Settings $\rightarrow$ Outbound WebSocket)
                            </div>
                            <ol className="list-decimal list-inside space-y-1.5 text-gray-600 pl-1">
                                <li>Öffne die IP deines Shelly im Browser (<code className="bg-slate-100 px-1 py-0.5 rounded font-mono">http://&lt;shelly-ip&gt;</code>).</li>
                                <li>Navigiere zu <strong>Settings $\rightarrow$ Outbound WebSocket</strong> (bzw. <em>Advanced</em>).</li>
                                <li>Setze das Häkchen bei <strong>Enable</strong> und trage die Server-URL ein:
                                    <div className="mt-1 font-mono bg-slate-900 text-amber-300 p-2 rounded-lg break-all text-[11px]">
                                        {wsUrl}
                                    </div>
                                </li>
                                <li>Klicke auf <strong>Save Settings</strong>. Das Gerät verbindet sich sekundenschnell per WSS!</li>
                            </ol>
                        </div>
                    )}

                    {/* HOME ASSISTANT GUIDE */}
                    {activeTab === "homeassistant" && (
                        <div className="space-y-2">
                            <div className="font-bold text-gray-900 text-sm">
                                🏠 Home Assistant Integration
                            </div>
                            <p className="text-gray-600 text-[11px]">
                                Nutze die offizielle <strong>Sharegy Cloud Bridge</strong> über HACS oder verbinde Entitäten per MQTT Automation:
                            </p>
                            <pre className="bg-slate-900 text-slate-100 p-2.5 rounded-lg font-mono text-[11px] overflow-x-auto">
                                {`alias: "Sharegy Sync - ${device.name || device.identifier}"
trigger:
  - platform: state
    entity_id: sensor.pv_leistung
action:
  - service: mqtt.publish
    data:
      topic: "${topic}"
      payload: >
        {"power": {{ states('sensor.pv_leistung') | float(0) }}}`}
                            </pre>
                        </div>
                    )}

                    {/* IOBROKER GUIDE */}
                    {activeTab === "iobroker" && (
                        <div className="space-y-2">
                            <div className="font-bold text-gray-900 text-sm flex items-center gap-1.5">
                                🔧 {t("interfaces.tab_iobroker", "ioBroker")}
                            </div>
                            <ol className="list-decimal list-inside space-y-1 text-gray-600 pl-1">
                                <li>ioBroker $\rightarrow$ <strong>Adapter</strong> $\rightarrow$ <strong>MQTT Client</strong> (<code className="bg-slate-100 px-1 py-0.5 rounded">mqtt-client</code>).</li>
                                <li>URL: <code className="bg-slate-100 px-1 py-0.5 rounded">{device.mqtt_host || "mqtt.sharegy.de"}</code>, Port: <code className="bg-slate-100 px-1 py-0.5 rounded">{device.mqtt_port || 1883}</code></li>
                                <li>Topic:
                                    <div className="mt-1 font-mono bg-slate-900 text-green-400 p-2 rounded-lg break-all">
                                        sendTo('mqtt-client.0', 'sendMessage', &#123; topic: '{topic}', message: JSON.stringify(&#123; power: 450.0 &#125;) &#125;);
                                    </div>
                                </li>
                            </ol>
                        </div>
                    )}

                    {/* TASMOTA / OPENDTU GUIDE */}
                    {activeTab === "mqtt" && (
                        <div className="space-y-2">
                            <div className="font-bold text-gray-900 text-sm">
                                📡 Tasmota, OpenDTU & AhoyDTU (MQTT)
                            </div>
                            <ol className="list-decimal list-inside space-y-1 text-gray-600 pl-1">
                                <li>Host: <code className="bg-slate-100 px-1 py-0.5 rounded">{device.mqtt_host || "mqtt.sharegy.de"}</code>, Port: <code className="bg-slate-100 px-1 py-0.5 rounded">{device.mqtt_port || 1883}</code></li>
                                <li>Publish Topic: <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">{topic}</code></li>
                                <li>Benutzer & Passwort aus der Tabelle oben eintragen.</li>
                            </ol>
                        </div>
                    )}

                    {/* OPENTELEMETRY (OTEL) GUIDE */}
                    {activeTab === "otel" && (
                        <div className="space-y-2">
                            <div className="font-bold text-gray-900 text-sm flex items-center justify-between">
                                <span>🔭 OpenTelemetry (OTLP/HTTP) Integration</span>
                            </div>
                            <div className="bg-slate-100 p-2 rounded-lg font-mono text-[11px] space-y-0.5">
                                <div>home.token: <strong>{device.mqtt_token}</strong></div>
                                <div>device.id: <strong>{device.identifier}</strong></div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* FOOTER ACTIONS */}
            <div className="flex items-center justify-between pt-2 border-t border-slate-100">
                <button
                    onClick={() => handleSimulate(450.0)}
                    disabled={simulating}
                    className="px-3.5 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 text-xs font-semibold rounded-xl transition flex items-center gap-1.5"
                >
                    {simulating ? `⏳ ${t("common.loading", "Sende...")}` : `⚡ ${t("device_add.simulate_btn", "Test-Messwert (450 W) simulieren")}`}
                </button>

                <button
                    onClick={onClose}
                    className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition shadow-sm"
                >
                    {isOnline ? `✅ ${t("device_add.finish_to_dashboard", "Fertigstellen & Zum Dashboard")}` : t("common.close", "Schließen")}
                </button>
            </div>

            {/* QR FULLSCREEN OVERLAY */}
            {showQR && (
                <div
                    className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
                    onClick={() => setShowQR(false)}
                >
                    <div className="bg-white p-6 rounded-2xl text-center shadow-2xl" onClick={(e) => e.stopPropagation()}>
                        <div className="font-bold text-gray-900 mb-3">{t("interfaces.qr_modal_title", "MQTT Zugangsdaten Scan")}</div>
                        <QRCodeSVG
                            value={JSON.stringify({
                                host: device.mqtt_host,
                                port: device.mqtt_port,
                                username: device.mqtt_username,
                                password: device.mqtt_password,
                                topic,
                            })}
                            size={240}
                        />
                        <button
                            onClick={() => setShowQR(false)}
                            className="mt-4 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-xs font-semibold transition"
                        >
                            {t("common.close", "Schließen")}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
