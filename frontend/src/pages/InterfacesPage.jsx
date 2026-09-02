/*
# src/pages/InterfacesPage.jsx
*/

import { useState } from "react";
import { useHomes } from "../hooks/useHomes";
import { QRCodeSVG } from "qrcode.react";
import { useTranslation } from "react-i18next";
import CloudInverterIntegrationCard from "../features/devices/components/CloudInverterIntegrationCard";

export default function InterfacesPage() {
    const { primaryHome, isLoading: homeLoading, regenerateMqttPassword, isRegenerating } = useHomes();
    const { t } = useTranslation();

    const [showPassword, setShowPassword] = useState(false);
    const [copiedKey, setCopiedKey] = useState(null);
    const [showQR, setShowQR] = useState(false);
    const [guideTab, setGuideTab] = useState("iobroker");

    function safeCopy(text, key) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
            setCopiedKey(key);
            setTimeout(() => setCopiedKey(null), 1500);
        } else {
            alert(t("interfaces.copy_not_supported", "Kopieren nicht unterstützt"));
        }
    }

    async function handleRegeneratePassword() {
        const msg = t(
            "interfaces.regenerate_confirm",
            "Möchtest du wirklich ein neues MQTT-Passwort generieren? Bestehende Geräte müssen anschließend mit dem neuen Passwort aktualisiert werden."
        );
        if (window.confirm(msg)) {
            try {
                await regenerateMqttPassword();
                alert(t("interfaces.regenerate_success", "Neues MQTT-Passwort erfolgreich generiert!"));
            } catch {
                alert(t("interfaces.regenerate_error", "Fehler beim Generieren des neuen Passworts."));
            }
        }
    }

    const mqttHost = primaryHome?.mqtt_host || "mqtt.sharegy.de";
    const mqttPort = primaryHome?.mqtt_port || 1883;
    const mqttUser = primaryHome?.mqtt_username || primaryHome?.mqtt_token || "-";
    const mqttPass = primaryHome?.mqtt_password || "-";
    const baseTopic = primaryHome?.mqtt_token ? `h/${primaryHome.mqtt_token}/#` : "h/<token>/#";

    const wsUrl = `wss://${window.location.host || "sharegy.de"}/ws/energy/${primaryHome?.mqtt_token || "<TOKEN>"}/`;

    return (
        <div className="p-6 max-w-4xl space-y-8">

            {/* HEADER */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                    <span>📡</span> {t("interfaces.title", "Schnittstellen")}
                </h1>
                <p className="text-sm text-gray-500 mt-1">
                    {t("interfaces.subtitle", "Verbinde deine Geräte und Zentralen direkt über Outbound-WebSocket (Shelly), Sungrow Direkt-Kopplung, Cloud-Wechselrichter, das Home Assistant Plugin oder MQTT mit Sharegy.")}
                </p>
            </div>

            {/* 1. SECTION: WEBSOCKET INTERFACE (SHELLY WSS - EMPFOHLEN) */}
            <div className="bg-white border border-amber-200/80 rounded-2xl shadow-xs overflow-hidden ring-1 ring-amber-100">
                <div className="p-5 bg-gradient-to-r from-amber-50/80 via-orange-50/30 to-white border-b border-amber-200/80 flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center text-xl shadow-xs">
                            ⚡
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-base font-bold text-gray-900">
                                    1. Outbound-WebSocket Schnittstelle (Shelly Gen2 / Gen3 / Pro)
                                </h2>
                                <span className="text-[10px] font-bold px-2 py-0.5 bg-amber-100 text-amber-800 rounded-full border border-amber-200">
                                    Empfohlen & DAU-sicher
                                </span>
                            </div>
                            <p className="text-xs text-gray-500">
                                Voll verschlüsselte Live-Verbindung über Port 443 (WSS) für Shelly 1PM Gen3, Pro 3EM, Plus 1PM uvm.
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={() => safeCopy(wsUrl, "ws_url")}
                        className="px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-white text-xs font-semibold rounded-lg shadow-2xs transition flex items-center gap-1.5 cursor-pointer"
                    >
                        {copiedKey === "ws_url" ? "✅ WSS-URL kopiert!" : "📋 WSS-URL kopieren"}
                    </button>
                </div>

                <div className="p-6 space-y-5">
                    {/* WSS URL DISPLAY */}
                    <div>
                        <div className="text-[11px] font-bold uppercase tracking-wider text-gray-500 mb-1.5">
                            Deine persönliche WebSocket Server-URL
                        </div>
                        <div className="flex items-center justify-between p-3.5 bg-amber-50/50 border border-amber-200 rounded-xl font-mono text-xs text-amber-900 font-semibold break-all gap-2">
                            <span>{wsUrl}</span>
                            <button
                                onClick={() => safeCopy(wsUrl, "ws_url")}
                                className="px-2.5 py-1 bg-white hover:bg-amber-100 border border-amber-300 text-amber-900 rounded-lg text-xs font-bold shrink-0 transition cursor-pointer"
                            >
                                {copiedKey === "ws_url" ? "✓ Kopiert" : "Kopieren"}
                            </button>
                        </div>
                    </div>

                    {/* FEATURES BADGES */}
                    <div className="grid sm:grid-cols-3 gap-3 text-xs">
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">🔒</span>
                            <div>
                                <div className="font-bold text-gray-900">TLS Verschlüsselt</div>
                                <div className="text-gray-500 text-[11px]">Sichere WSS-Verbindung über Standard HTTPS (Port 443).</div>
                            </div>
                        </div>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">🛡️</span>
                            <div>
                                <div className="font-bold text-gray-900">Keine Portweiterleitung</div>
                                <div className="text-gray-500 text-[11px]">Funktioniert hinter jeder Fritz!Box & Router ohne Freigaben.</div>
                            </div>
                        </div>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">⚡</span>
                            <div>
                                <div className="font-bold text-gray-900">Bidirektional & Aktorik</div>
                                <div className="text-gray-500 text-[11px]">Live-Leistungsmessung & Relais-Schaltung in 5 ms.</div>
                            </div>
                        </div>
                    </div>

                    {/* 3-STEP INSTRUCTIONS */}
                    <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-3">
                        <div className="font-bold text-gray-900 text-sm flex items-center gap-1.5">
                            <span>📖</span> 3-Schritte Einrichtung im Shelly Web-Interface:
                        </div>
                        <ol className="list-decimal list-inside space-y-2 text-gray-700 leading-relaxed">
                            <li>
                                Öffne die Weboberfläche deines Shelly im Browser (<code className="bg-white px-1.5 py-0.5 rounded border border-slate-300 font-mono">http://&lt;shelly-ip&gt;</code>).
                            </li>
                            <li>
                                Klicke im Menü links auf <strong>Settings</strong> $\rightarrow$ <strong>Outbound WebSocket</strong>.
                            </li>
                            <li>
                                Setze ein Häkchen bei <strong>Enable</strong>, wähle TLS/SSL und füge oben stehende <strong>Server-URL</strong> ein $\rightarrow$ Klicke auf <strong>Save Settings</strong>.
                            </li>
                        </ol>
                        <div className="p-2.5 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 text-[11px] font-medium flex items-center gap-2">
                            <span>🚀</span>
                            <span>
                                <strong>Fertig!</strong> Der Shelly verbindet sich automatisch mit Sharegy. Das Gerät wird sofort erkannt und taucht unter <strong>Geräte</strong> und im <strong>Dashboard</strong> auf.
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* 2. SECTION: SUNGROW DIREKT-KOPPLUNG (1-KLICK OAUTH & ISOLARCLOUD) */}
            <CloudInverterIntegrationCard 
                primaryHome={primaryHome} 
                filterVendor="sungrow" 
                sectionNumber={2} 
                cardTitle="2. Sungrow Wechselrichter & Batteriespeicher (SH-Serie)" 
            />

            {/* 3. SECTION: WEITERE WECHSELRICHTER & CLOUD-DIENSTE */}
            <CloudInverterIntegrationCard 
                primaryHome={primaryHome} 
                filterVendor="others" 
                sectionNumber={3} 
                cardTitle="3. Weitere Wechselrichter (SolarEdge, Fronius, Kostal, Growatt)" 
            />

            {/* 4. SECTION: NATIVE HOME ASSISTANT INTEGRATION (HACS / CUSTOM COMPONENT) */}
            <div className="bg-white border border-cyan-200/80 rounded-2xl shadow-xs overflow-hidden ring-1 ring-cyan-100">
                <div className="p-5 bg-gradient-to-r from-cyan-50/80 via-blue-50/30 to-white border-b border-cyan-200/80 flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-cyan-600 text-white flex items-center justify-center text-xl shadow-xs">
                            🏠
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-base font-bold text-gray-900">
                                    4. Natives Home Assistant Plugin (HACS / Custom Component)
                                </h2>
                                <span className="text-[10px] font-bold px-2 py-0.5 bg-cyan-100 text-cyan-800 rounded-full border border-cyan-200">
                                    Neu & Store-and-Forward
                                </span>
                            </div>
                            <p className="text-xs text-gray-500">
                                Wähle deine Home Assistant Entitäten per Klick aus — inklusive lokalem 48h-Offline-Puffer bei Netzausfall.
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={() => safeCopy(primaryHome?.mqtt_token || "", "ha_token")}
                        className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-700 text-white text-xs font-semibold rounded-lg shadow-2xs transition flex items-center gap-1.5 cursor-pointer"
                    >
                        {copiedKey === "ha_token" ? "✅ Token kopiert!" : "📋 Home Token kopieren"}
                    </button>
                </div>

                <div className="p-6 space-y-5">
                    {/* FEATURES BADGES */}
                    <div className="grid sm:grid-cols-3 gap-3 text-xs">
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">🎯</span>
                            <div>
                                <div className="font-bold text-gray-900">1-Klick Entity Picker</div>
                                <div className="text-gray-500 text-[11px]">Bequeme Auswahl aller Sensoren direkt in der Home Assistant UI.</div>
                            </div>
                        </div>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">💾</span>
                            <div>
                                <div className="font-bold text-gray-900">48h Offline-Puffer</div>
                                <div className="text-gray-500 text-[11px]">Speichert Daten bei Internetausfall lokal und sendet sie lückenlos nach.</div>
                            </div>
                        </div>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">⚡</span>
                            <div>
                                <div className="font-bold text-gray-900">Live WebSocket Stream</div>
                                <div className="text-gray-500 text-[11px]">Echtzeit-Übertragung über verschlüsseltes WSS (Port 443).</div>
                            </div>
                        </div>
                    </div>

                    {/* SETUP STEPS */}
                    <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-3">
                        <div className="font-bold text-gray-900 text-sm flex items-center gap-1.5">
                            <span>📦</span> Installation in Home Assistant:
                        </div>
                        <ol className="list-decimal list-inside space-y-2 text-gray-700 leading-relaxed">
                            <li>
                                Kopiere den Ordner <code className="bg-white px-1.5 py-0.5 rounded border border-slate-300 font-mono text-cyan-700">custom_components/sharegy</code> in deinen Home Assistant Ordner <code className="bg-white px-1.5 py-0.5 rounded border border-slate-300 font-mono">config/custom_components/</code> (oder füge das Repository in HACS hinzu).
                            </li>
                            <li>
                                Starte Home Assistant neu und öffne <strong>Einstellungen</strong> $\rightarrow$ <strong>Geräte & Dienste</strong> $\rightarrow$ <strong>Integration hinzufügen</strong>.
                            </li>
                            <li>
                                Wähle <strong>Sharegy Cloud Energy Bridge</strong>, füge dein persönliches <strong>Home Token</strong> (<code className="bg-white px-1 py-0.5 rounded font-mono text-cyan-800">{primaryHome?.mqtt_token || "<TOKEN>"}</code>) ein und wähle deine Sensoren per Dropdown aus.
                            </li>
                        </ol>
                    </div>
                </div>
            </div>

            {/* 5. SECTION: MQTT INTERFACE CARD */}
            <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
                <div className="p-5 bg-gradient-to-r from-slate-50 via-indigo-50/30 to-white border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center text-xl shadow-xs">
                            📡
                        </div>
                        <div>
                            <h2 className="text-base font-bold text-gray-900">
                                5. MQTT Broker Schnittstelle (ioBroker, Node-RED, OTel)
                            </h2>

                            <p className="text-xs text-gray-500">
                                Standard-IoT-Protokoll zur universellen Anbindung von Smart-Home-Servern und OpenTelemetry
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setShowQR(true)}
                            className="px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-gray-700 text-xs font-semibold rounded-lg shadow-2xs transition flex items-center gap-1.5 cursor-pointer"
                        >
                            <span>📱</span> {t("interfaces.qr_code", "QR-Code")}
                        </button>
                        <button
                            onClick={() => {
                                const text = `Host: ${mqttHost}\nPort: ${mqttPort}\nUser: ${mqttUser}\nPass: ${mqttPass}\nBase Topic: ${baseTopic}`;
                                safeCopy(text, "all_mqtt");
                            }}
                            className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-2xs transition flex items-center gap-1.5 cursor-pointer"
                        >
                            {copiedKey === "all_mqtt" ? `✅ ${t("common.copied", "Kopiert!")}` : t("interfaces.copy_all", "📋 Alle Daten kopieren")}
                        </button>
                    </div>
                </div>

                <div className="p-6 space-y-6">
                    {homeLoading ? (
                        <div className="text-sm text-gray-400 py-6 text-center animate-pulse">
                            {t("interfaces.loading", "Lade Schnittstellendaten...")}
                        </div>
                    ) : (
                        <>
                            {/* CREDENTIALS GRID */}
                            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                                <div className="bg-slate-50 border border-slate-200/80 p-3.5 rounded-xl">
                                    <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">
                                        {t("interfaces.broker_host", "Broker Host")}
                                    </div>
                                    <div className="font-mono text-xs font-semibold text-gray-900 flex items-center justify-between">
                                        <span>{mqttHost}</span>
                                        <button
                                            onClick={() => safeCopy(mqttHost, "host")}
                                            className="text-gray-400 hover:text-indigo-600 text-xs ml-1 cursor-pointer"
                                            title={t("common.copy", "Kopieren")}
                                        >
                                            {copiedKey === "host" ? "✓" : "📋"}
                                        </button>
                                    </div>
                                </div>

                                <div className="bg-slate-50 border border-slate-200/80 p-3.5 rounded-xl">
                                    <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">
                                        {t("interfaces.port", "Port (TCP)")}
                                    </div>
                                    <div className="font-mono text-xs font-semibold text-gray-900 flex items-center justify-between">
                                        <span>{mqttPort}</span>
                                        <span className="text-[10px] px-1.5 py-0.5 bg-emerald-100 text-emerald-700 font-semibold rounded">
                                            {t("common.active", "Aktiv")}
                                        </span>
                                    </div>
                                </div>

                                <div className="bg-slate-50 border border-slate-200/80 p-3.5 rounded-xl">
                                    <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">
                                        {t("interfaces.username", "Benutzername")}
                                    </div>
                                    <div className="font-mono text-xs font-semibold text-gray-900 flex items-center justify-between">
                                        <span className="truncate">{mqttUser}</span>
                                        <button
                                            onClick={() => safeCopy(mqttUser, "user")}
                                            className="text-gray-400 hover:text-indigo-600 text-xs ml-1 cursor-pointer"
                                            title={t("common.copy", "Kopieren")}
                                        >
                                            {copiedKey === "user" ? "✓" : "📋"}
                                        </button>
                                    </div>
                                </div>

                                <div className="bg-slate-50 border border-slate-200/80 p-3.5 rounded-xl">
                                    <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">
                                        {t("interfaces.password", "Passwort")}
                                    </div>
                                    <div className="font-mono text-xs font-semibold text-gray-900 flex items-center justify-between">
                                        <span className="truncate">
                                            {showPassword ? mqttPass : "••••••••••••••••"}
                                        </span>
                                        <div className="flex items-center gap-1.5 ml-1">
                                            <button
                                                onClick={() => setShowPassword((v) => !v)}
                                                className="text-gray-400 hover:text-indigo-600 text-xs cursor-pointer"
                                                title={showPassword ? "Verstecken" : "Anzeigen"}
                                            >
                                                {showPassword ? "🙈" : "👁️"}
                                            </button>
                                            <button
                                                onClick={() => safeCopy(mqttPass, "pass")}
                                                className="text-gray-400 hover:text-indigo-600 text-xs cursor-pointer"
                                                title={t("common.copy", "Kopieren")}
                                            >
                                                {copiedKey === "pass" ? "✓" : "📋"}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* BASE TOPIC BANNER */}
                            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl flex flex-wrap items-center justify-between gap-3 text-xs">
                                <div>
                                    <span className="text-gray-500 font-medium">{t("interfaces.base_topic", "Dein persönliches Basis-Topic:")} </span>
                                    <code className="font-mono font-bold text-indigo-700 bg-white px-2 py-0.5 rounded border border-indigo-200">
                                        {baseTopic}
                                    </code>
                                </div>
                                <button
                                    onClick={handleRegeneratePassword}
                                    disabled={isRegenerating}
                                    className="text-xs text-red-600 hover:text-red-700 font-semibold hover:underline flex items-center gap-1 cursor-pointer"
                                >
                                    <span>🔄</span> {isRegenerating ? t("common.loading", "Generiere...") : t("interfaces.regenerate_btn", "Passwort neu generieren")}
                                </button>
                            </div>

                            {/* QUICK INTEGRATION GUIDES */}
                            <div className="border border-slate-200 rounded-xl overflow-hidden">
                                <div className="flex bg-slate-50 border-b border-slate-200 text-xs font-semibold overflow-x-auto">
                                    {[
                                        { id: "iobroker", label: "🔧 ioBroker" },
                                        { id: "otel", label: "🔭 OpenTelemetry (OTel)" },
                                        { id: "nodered", label: "🟢 Node-RED / Tasmota" },
                                    ].map((tab) => (
                                        <button
                                            key={tab.id}
                                            onClick={() => setGuideTab(tab.id)}
                                            className={`px-4 py-2.5 transition whitespace-nowrap cursor-pointer ${guideTab === tab.id
                                                ? "bg-white text-indigo-600 border-b-2 border-indigo-600 font-bold"
                                                : "text-gray-500 hover:text-gray-900"
                                                }`}
                                        >
                                            {tab.label}
                                        </button>
                                    ))}
                                </div>

                                <div className="p-4 text-xs text-gray-700 leading-relaxed bg-white">
                                    {guideTab === "iobroker" && (
                                        <div className="space-y-2">
                                            <p className="text-gray-600">
                                                1. Installiere den <strong>MQTT Client Adapter</strong> (<code className="bg-slate-100 px-1 rounded">mqtt-client</code>).<br />
                                                2. Wähle Typ <strong>Client / Abonnent</strong>, trage URL <code className="bg-slate-100 px-1 rounded">{mqttHost}</code>, Port <code className="bg-slate-100 px-1 rounded">{mqttPort}</code> sowie Benutzer & Kennwort ein.<br />
                                                3. Sende Messwerte an <code className="font-mono bg-slate-100 px-1 text-indigo-600">h/{primaryHome?.mqtt_token || "<TOKEN>"}/&lt;geraet_id&gt;</code>:
                                            </p>
                                            <pre className="bg-slate-900 text-green-400 p-2.5 rounded-lg font-mono text-[11px] overflow-x-auto">
                                                {`sendTo('mqtt-client.0', 'sendMessage', {
    topic: 'h/${primaryHome?.mqtt_token || "<TOKEN>"}/balkonkraftwerk',
    message: JSON.stringify({ power: 450.0 })
});`}
                                            </pre>
                                        </div>
                                    )}

                                    {guideTab === "otel" && (
                                        <div className="space-y-2">
                                            <div className="font-bold text-gray-900 text-sm flex items-center justify-between">
                                                <span>🔭 OpenTelemetry (OTLP/HTTP) Ingestion</span>
                                                <span className="text-[10px] text-indigo-600 font-mono">Endpoint: /api/v1/metrics</span>
                                            </div>
                                            <p className="text-gray-600">
                                                Sende Telemetrie direkt via OpenTelemetry Collector oder Python SDK mit dem Resource Attribute:
                                            </p>
                                            <div className="bg-slate-100 p-2 rounded-lg font-mono text-[11px]">
                                                home.token: <strong>{primaryHome?.mqtt_token || "<TOKEN>"}</strong>
                                            </div>
                                            <pre className="bg-slate-900 text-green-400 p-2.5 rounded-lg font-mono text-[11px] overflow-x-auto">
                                                {`processors:
  resource:
    attributes:
      - key: home.token
        value: "${primaryHome?.mqtt_token || "<TOKEN>"}"
        action: insert

exporters:
  otlphttp:
    endpoint: "${window.location.origin}/api"`}
                                            </pre>
                                        </div>
                                    )}

                                    {guideTab === "nodered" && (
                                        <div className="space-y-1.5 text-gray-600">
                                            <p>1. Verwende in Node-RED oder Tasmota einen standardmäßigen <strong>MQTT Out Node</strong>.</p>
                                            <p>2. Konfiguriere den Broker auf <code className="bg-slate-100 px-1 rounded font-mono">{mqttHost}:{mqttPort}</code> mit deinen Zugangsdaten.</p>
                                            <p>3. Sende JSON-Nutzdaten wie <code className="bg-slate-100 px-1 rounded font-mono">{'{"power": 1250.5, "energy": 45.2}'}</code> an <code className="bg-slate-100 px-1 rounded font-mono text-indigo-600">h/{primaryHome?.mqtt_token || "<TOKEN>"}/&lt;geraet_name&gt;</code>.</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* QR FULLSCREEN MODAL */}
            {showQR && primaryHome && (
                <div
                    className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
                    onClick={() => setShowQR(false)}
                >
                    <div className="bg-white p-6 rounded-2xl text-center shadow-2xl max-w-sm w-full" onClick={(e) => e.stopPropagation()}>
                        <h3 className="font-bold text-gray-900 text-base mb-1">
                            MQTT & IoT Zugangsdaten Scan
                        </h3>
                        <p className="text-xs text-gray-500 mb-4">
                            Für automatisierte Konfiguration in Companion Apps & Gateways
                        </p>
                        <div className="flex justify-center mb-4">
                            <QRCodeSVG
                                value={JSON.stringify({
                                    host: mqttHost,
                                    port: mqttPort,
                                    username: mqttUser,
                                    password: mqttPass,
                                    topic_prefix: `h/${primaryHome.mqtt_token}/`,
                                })}
                                size={220}
                            />
                        </div>
                        <button
                            onClick={() => setShowQR(false)}
                            className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-2 rounded-xl text-xs transition cursor-pointer"
                        >
                            {t("common.close", "Schließen")}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
