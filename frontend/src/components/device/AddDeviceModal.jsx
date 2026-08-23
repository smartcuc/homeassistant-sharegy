/*
# src/components/device/AddDeviceModal.jsx
*/

import { useEffect, useState } from "react";
import { QRCodeSVG } from "qrcode.react";
import { useCreateDevice } from "../../hooks/useCreateDevice";
import { useDeviceStatus } from "../../hooks/useDevices";
import { useStructure } from "../../hooks/useStructure";
import { apiFetch } from "../../api/client";

/* =========================================================
   HELPERS
========================================================= */

function safeCopy(text, setCopiedKey, key) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
        setCopiedKey(key);
        setTimeout(() => setCopiedKey(null), 1500);
    } else {
        alert("Zwischenablage wird im Browser nicht unterstützt");
    }
}

/* =========================================================
   DEVICE PRESETS
========================================================= */

const PRESETS = [
    {
        id: "balkonkraftwerk",
        title: "Balkonkraftwerk & PV",
        icon: "☀️",
        desc: "Hoymiles, OpenDTU, Shelly Plus 1PM, Envertech, TSUN",
        badge: "Erzeuger",
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
        title: "Haupt- & Netzzähler",
        icon: "⚡",
        desc: "Shelly Pro 3EM / EM, Powerfox, Tibber Pulse, IR-Lesekopf",
        badge: "Netzmessung",
        defaults: {
            name: "Hauptzähler",
            role_key: "consumer",
            energy_signal_type_key: "grid_exchange",
            metric_key: "power",
        }
    },
    {
        id: "consumer",
        title: "Smarte Steckdose & Last",
        icon: "🔌",
        desc: "Shelly Plug S, Tasmota, Wärmepumpe, Wallbox",
        badge: "Verbraucher",
        defaults: {
            name: "Steckdose",
            role_key: "consumer",
            energy_signal_type_key: "household_load",
            metric_key: "power",
        }
    },
    {
        id: "battery",
        title: "Batteriespeicher & Powerstation",
        icon: "🔋",
        desc: "EcoFlow, Anker Solix, Zendure, Victron",
        badge: "Speicher",
        defaults: {
            name: "Batteriespeicher",
            role_key: "both",
            energy_signal_type_key: "battery_storage",
            metric_key: "power",
        }
    },
    {
        id: "iobroker",
        title: "ioBroker & Smart Home",
        icon: "🔧",
        desc: "ioBroker MQTT-Adapter, Home Assistant, Node-RED",
        badge: "Zentrale",
        defaults: {
            name: "ioBroker Gerät",
            role_key: "consumer",
            energy_signal_type_key: "household_load",
            metric_key: "power",
        }
    },
    {
        id: "sensor",
        title: "Umwelt- & Klimasensor",
        icon: "🌡️",
        desc: "Temperatur, Feuchte, Luftdruck, CO2, Raumklima",
        badge: "Sensor",
        defaults: {
            name: "Klimasensor",
            role_key: "consumer",
            metric_key: "temperature",
        }
    }
];


/* =========================================================
   MAIN MODAL
========================================================= */

export default function AddDeviceModal({ open, onClose }) {

    const [step, setStep] = useState(1);
    const [selectedPreset, setSelectedPreset] = useState(PRESETS[0]);
    const [name, setName] = useState("");
    const [roomId, setRoomId] = useState("");
    const [floorId, setFloorId] = useState("");
    const [device, setDevice] = useState(null);

    const createDevice = useCreateDevice();
    const { data: structure } = useStructure();

    useEffect(() => {
        if (open) {
            setStep(1);
            setSelectedPreset(PRESETS[0]);
            setName("");
            setRoomId("");
            setFloorId("");
            setDevice(null);
        }
    }, [open]);

    if (!open) return null;

    function next() {
        setStep((s) => s + 1);
    }

    function back() {
        if (!createDevice.isLoading) {
            setStep((s) => Math.max(1, s - 1));
        }
    }

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div
                className={`
                    bg-white
                    text-gray-800
                    p-6
                    rounded-2xl
                    w-full
                    relative
                    shadow-2xl
                    border border-gray-100
                    transition-all
                    ${step === 3 ? "max-w-4xl" : "max-w-xl"}
                `}
            >
                {/* PROGRESS HEADER */}
                <div className="flex items-center justify-between mb-5 pb-3 border-b border-gray-100">
                    <div>
                        <div className="text-xs font-bold uppercase tracking-wider text-indigo-600">
                            Schritt {step} von 3
                        </div>
                        <div className="text-xs text-gray-400">
                            {step === 1 && "Gerätetyp & Preset wählen"}
                            {step === 2 && "Name, Raum & Klassifizierung"}
                            {step === 3 && "Verbindung, Anleitung & Live-Test"}
                        </div>
                    </div>

                    <div className="flex items-center gap-1.5">
                        {[1, 2, 3].map((s) => (
                            <div
                                key={s}
                                className={`h-2 rounded-full transition-all ${s === step
                                        ? "w-8 bg-indigo-600"
                                        : s < step
                                            ? "w-4 bg-green-500"
                                            : "w-4 bg-gray-200"
                                    }`}
                            />
                        ))}
                    </div>
                </div>

                {step === 1 && (
                    <StepPresetSelection
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
                                alert("Fehler beim Erstellen des Geräts");
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

function StepPresetSelection({ selectedPreset, onSelect }) {
    return (
        <div>
            <h2 className="text-xl font-bold text-gray-900 mb-1">
                🔌 Was möchtest du anbinden?
            </h2>
            <p className="text-sm text-gray-500 mb-5">
                Wähle ein passendes Preset. Sharegy konfiguriert die Messgrößen und Energieflüsse automatisch vor.
            </p>

            <div className="grid sm:grid-cols-2 gap-3 max-h-[60vh] overflow-y-auto pr-1">
                {PRESETS.map((preset) => {
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
                    Gerät benennen & zuordnen
                </h2>
            </div>
            <p className="text-sm text-gray-500 mb-5">
                Vergib einen Namen und ordne das Gerät optional einem Raum zu.
            </p>

            <div className="space-y-4 mb-6">
                <div>
                    <label className="text-xs font-semibold text-gray-700 block mb-1.5">
                        Gerätename *
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
                            Etage (optional)
                        </label>
                        <select
                            value={floorId}
                            onChange={(e) => setFloorId(e.target.value)}
                            className="w-full px-3 py-2 border rounded-xl bg-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                            <option value="">🏢 Keine Etage</option>
                            {floors.map((f) => (
                                <option key={f.id} value={f.id}>{f.name}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="text-xs font-semibold text-gray-700 block mb-1.5">
                            Raum (optional)
                        </label>
                        <select
                            value={roomId}
                            onChange={(e) => setRoomId(e.target.value)}
                            className="w-full px-3 py-2 border rounded-xl bg-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                            <option value="">🚪 Kein Raum</option>
                            {rooms.map((r) => (
                                <option key={r.id} value={r.id}>{r.name}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* AUTO-CONFIG PREVIEW BADGE */}
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs">
                    <span className="text-gray-500">Automatische Vorkonfiguration:</span>
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
                    ← Zurück
                </button>

                <button
                    type="submit"
                    disabled={!name.trim() || loading}
                    className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-xl transition shadow-sm disabled:opacity-50 flex items-center gap-2"
                >
                    {loading ? "Wird erstellt..." : "Gerät anlegen & verbinden →"}
                </button>
            </div>
        </form>
    );
}


/* =========================================================
   STEP 3: CONNECTION, GUIDES & LIVE-TEST
========================================================= */

function StepConnectionAndGuides({ device, preset, onClose }) {
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
            alert("Simulation fehlgeschlagen");
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
                            {device.name || device.identifier} verbinden
                        </h2>
                        <div className="text-xs text-gray-500">
                            MQTT Topic: <span className="font-mono text-indigo-600 font-semibold">{topic}</span>
                        </div>
                    </div>
                </div>

                {isOnline ? (
                    <div className="flex items-center gap-1.5 px-3 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full border border-green-200 animate-fade-in">
                        <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        🟢 Verbunden (Live-Daten aktiv)
                    </div>
                ) : (
                    <div className="flex items-center gap-1.5 px-3 py-1 bg-amber-50 text-amber-800 text-xs font-semibold rounded-full border border-amber-200">
                        <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping" />
                        ⏳ Warte auf erste Messwerte...
                    </div>
                )}
            </div>

            {/* TOP GRID: MQTT CREDENTIALS & QR */}
            <div className="grid md:grid-cols-[1fr_2fr] gap-3 mb-4">
                {/* QR CODE CARD */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-center flex flex-col items-center justify-center">
                    <div
                        onClick={() => setShowQR(true)}
                        className="cursor-pointer p-2 bg-white rounded-lg border border-slate-200 shadow-xs hover:shadow-md transition"
                        title="Klicken zum Vergrößern"
                    >
                        <QRCodeSVG
                            value={JSON.stringify({
                                host: device.mqtt_host,
                                port: device.mqtt_port,
                                username: device.mqtt_username,
                                password: device.mqtt_password,
                                topic,
                            })}
                            size={110}
                        />
                    </div>
                    <span className="text-[11px] text-gray-400 mt-2">
                        QR-Code für Companion Apps
                    </span>
                </div>

                {/* CREDENTIALS TABLE */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 flex flex-col justify-between">
                    <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                        <div>
                            <span className="text-gray-400 block text-[10px] uppercase font-bold">Host</span>
                            <span className="font-mono font-medium text-gray-800">{device.mqtt_host || "mqtt.sharegy.de"}</span>
                        </div>
                        <div>
                            <span className="text-gray-400 block text-[10px] uppercase font-bold">Port</span>
                            <span className="font-mono font-medium text-gray-800">{device.mqtt_port || 1883}</span>
                        </div>
                        <div>
                            <span className="text-gray-400 block text-[10px] uppercase font-bold">Benutzer</span>
                            <span className="font-mono font-medium text-gray-800 break-all">{device.mqtt_username}</span>
                        </div>
                        <div>
                            <span className="text-gray-400 block text-[10px] uppercase font-bold">Passwort</span>
                            <span className="font-mono font-medium text-gray-800 break-all">{device.mqtt_password}</span>
                        </div>
                    </div>

                    <button
                        onClick={() => {
                            const text = `Host: ${device.mqtt_host || "mqtt.sharegy.de"}\nPort: ${device.mqtt_port || 1883}\nUser: ${device.mqtt_username}\nPass: ${device.mqtt_password}\nTopic: ${topic}`;
                            safeCopy(text, setCopiedKey, "all");
                        }}
                        className="w-full bg-white hover:bg-slate-100 border border-slate-300 text-gray-700 text-xs font-semibold py-2 px-3 rounded-lg transition flex items-center justify-center gap-1.5"
                    >
                        {copiedKey === "all" ? "✅ Zugangsdaten kopiert!" : "📋 Alle Zugangsdaten kopieren"}
                    </button>
                </div>
            </div>

            {/* GUIDES TAB BAR */}
            <div className="border border-slate-200 rounded-xl overflow-hidden mb-4 bg-white shadow-xs">
                <div className="flex border-b border-slate-200 bg-slate-50 text-xs font-semibold overflow-x-auto">
                    {[
                        { id: "iobroker", label: "🔧 ioBroker", icon: "🔧" },
                        { id: "shelly", label: "⚡ Shelly", icon: "⚡" },
                        { id: "homeassistant", label: "🏠 Home Assistant", icon: "🏠" },
                        { id: "otel", label: "🔭 OpenTelemetry", icon: "🔭" },
                        { id: "tasmota", label: "📡 Tasmota / OpenDTU", icon: "📡" },
                        { id: "curl", label: "🌐 cURL / REST", icon: "🌐" },
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`px-4 py-2.5 transition whitespace-nowrap ${activeTab === tab.id
                                    ? "bg-white text-indigo-600 border-b-2 border-indigo-600 font-bold"
                                    : "text-gray-500 hover:text-gray-800 hover:bg-slate-100"
                                }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* TAB CONTENTS */}
                <div className="p-4 text-xs text-gray-700 leading-relaxed max-h-48 overflow-y-auto">
                    {/* IOBROKER GUIDE */}
                    {activeTab === "iobroker" && (
                        <div className="space-y-2">
                            <div className="font-bold text-gray-900 text-sm flex items-center gap-1.5">
                                🔧 ioBroker MQTT-Adapter Einrichtung
                            </div>
                            <ol className="list-decimal list-inside space-y-1 text-gray-600 pl-1">
                                <li>Öffne ioBroker $\rightarrow$ <strong>Adapter</strong> $\rightarrow$ installiere den <strong>MQTT Client</strong> Adapter (<code className="bg-slate-100 px-1 py-0.5 rounded">mqtt-client</code>).</li>
                                <li>In den Instanz-Einstellungen:
                                    <ul className="list-disc list-inside pl-4 text-gray-500 mt-1">
                                        <li>Typ: <strong>Client / Abonnent</strong></li>
                                        <li>URL: <code className="bg-slate-100 px-1 py-0.5 rounded">{device.mqtt_host || "mqtt.sharegy.de"}</code>, Port: <code className="bg-slate-100 px-1 py-0.5 rounded">{device.mqtt_port || 1883}</code></li>
                                        <li>Benutzer & Kennwort wie oben eintragen.</li>
                                    </ul>
                                </li>
                                <li>Veröffentliche deine Messdaten per Javascript/Blockly oder per MQTT-Objekt auf:
                                    <div className="mt-1 font-mono bg-slate-900 text-green-400 p-2 rounded-lg break-all">
                                        sendTo('mqtt-client.0', 'sendMessage', &#123; topic: '{topic}', message: JSON.stringify(&#123; power: 450.0 &#125;) &#125;);
                                    </div>
                                </li>
                            </ol>
                        </div>
                    )}

                    {/* SHELLY GUIDE */}
                    {activeTab === "shelly" && (
                        <div className="space-y-2">
                            <div className="font-bold text-gray-900 text-sm">
                                ⚡ Shelly Web-Interface Konfiguration (Gen 2 / 3 & Gen 1)
                            </div>
                            <ol className="list-decimal list-inside space-y-1 text-gray-600 pl-1">
                                <li>Öffne die IP-Adresse des Shelly im Browser $\rightarrow$ <strong>Settings</strong> $\rightarrow$ <strong>MQTT</strong>.</li>
                                <li>Aktiviere <strong>Enable MQTT</strong>.</li>
                                <li>Server: <code className="bg-slate-100 px-1 py-0.5 rounded">{device.mqtt_host || "mqtt.sharegy.de"}:{device.mqtt_port || 1883}</code></li>
                                <li>User & Password wie oben angegeben eintragen.</li>
                                <li>Topic Prefix: <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">h/{device.mqtt_token}/{device.identifier}</code></li>
                                <li>Klicke auf <strong>Save settings</strong> $\rightarrow$ Der Shelly verbindet sich automatisch!</li>
                            </ol>
                        </div>
                    )}

                    {/* HOME ASSISTANT GUIDE */}
                    {activeTab === "homeassistant" && (
                        <div className="space-y-2">
                            <div className="font-bold text-gray-900 text-sm">
                                🏠 Home Assistant Automation YAML Snippet
                            </div>
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

                    {/* OPENTELEMETRY (OTEL) GUIDE */}
                    {activeTab === "otel" && (
                        <div className="space-y-2">
                            <div className="font-bold text-gray-900 text-sm flex items-center justify-between">
                                <span>🔭 OpenTelemetry (OTLP/HTTP) Integration</span>
                                <span className="text-[10px] text-gray-500 font-mono">Endpoint: /api/v1/metrics</span>
                            </div>
                            <p className="text-gray-600">
                                Sende strukturierte OTLP-Metriken per OTel Collector oder Python-Skript mit folgenden <strong>Resource Attributes</strong>:
                            </p>
                            <div className="bg-slate-100 p-2 rounded-lg font-mono text-[11px] space-y-0.5">
                                <div>home.token: <strong>{device.mqtt_token}</strong></div>
                                <div>device.id: <strong>{device.identifier}</strong></div>
                            </div>
                            <div className="text-[11px] font-semibold text-gray-800 mt-2">OTel Collector Exporter (`config.yaml`):</div>
                            <pre className="bg-slate-900 text-green-400 p-2.5 rounded-lg font-mono text-[11px] overflow-x-auto">
                                {`processors:
  resource:
    attributes:
      - key: home.token
        value: "${device.mqtt_token}"
        action: insert
      - key: device.id
        value: "${device.identifier}"
        action: insert

exporters:
  otlphttp:
    endpoint: "${window.location.origin}/api"`}
                            </pre>
                        </div>
                    )}

                    {/* TASMOTA / OPENDTU GUIDE */}
                    {activeTab === "tasmota" && (
                        <div className="space-y-2">
                            <div className="font-bold text-gray-900 text-sm">
                                📡 Tasmota / OpenDTU MQTT Setup
                            </div>
                            <p className="text-gray-600">
                                In den MQTT-Einstellungen von OpenDTU / Tasmota:
                            </p>
                            <div className="bg-slate-100 p-2.5 rounded-lg space-y-1 font-mono text-[11px]">
                                <div>Host: <strong>{device.mqtt_host || "mqtt.sharegy.de"}</strong></div>
                                <div>Port: <strong>{device.mqtt_port || 1883}</strong></div>
                                <div>Base Topic: <strong>{topic}</strong></div>
                            </div>
                        </div>
                    )}

                    {/* CURL GUIDE */}
                    {activeTab === "curl" && (
                        <div className="space-y-2">
                            <div className="font-bold text-gray-900 text-sm">
                                🌐 Direkter Test via cURL / REST API
                            </div>
                            <pre className="bg-slate-900 text-green-400 p-2.5 rounded-lg font-mono text-[11px] overflow-x-auto break-all">
                                {`curl -X POST "${window.location.origin}/api/devices/${device.id}/simulate/" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer ${localStorage.getItem("token") || "<TOKEN>"}" \\
  -d '{"value": 520.0, "metric_key": "power"}'`}
                            </pre>
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
                    {simulating ? "⏳ Sende..." : "⚡ Test-Messwert (450 W) simulieren"}
                </button>

                <button
                    onClick={onClose}
                    className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition shadow-sm"
                >
                    {isOnline ? "✅ Fertigstellen & Zum Dashboard" : "Schließen"}
                </button>
            </div>

            {/* QR FULLSCREEN OVERLAY */}
            {showQR && (
                <div
                    className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
                    onClick={() => setShowQR(false)}
                >
                    <div className="bg-white p-6 rounded-2xl text-center shadow-2xl" onClick={(e) => e.stopPropagation()}>
                        <div className="font-bold text-gray-900 mb-3">MQTT Zugangsdaten Scan</div>
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
                            Schließen
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
