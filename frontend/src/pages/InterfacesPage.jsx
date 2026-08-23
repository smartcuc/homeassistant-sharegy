/*
# src/pages/InterfacesPage.jsx
*/

import { useState } from "react";
import { useHomes } from "../hooks/useHomes";
import { QRCodeSVG } from "qrcode.react";
import { useTranslation } from "react-i18next";

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
            alert("Kopieren nicht unterstützt");
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
                alert("Fehler beim Generieren des neuen Passworts.");
            }
        }
    }

    const mqttHost = primaryHome?.mqtt_host || "mqtt.sharegy.de";
    const mqttPort = primaryHome?.mqtt_port || 1883;
    const mqttUser = primaryHome?.mqtt_username || primaryHome?.mqtt_token || "-";
    const mqttPass = primaryHome?.mqtt_password || "-";
    const baseTopic = primaryHome?.mqtt_token ? `h/${primaryHome.mqtt_token}/#` : "h/<token>/#";

    return (
        <div className="p-6 max-w-4xl space-y-6">

            {/* HEADER */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                    <span>📡</span> {t("interfaces.title", "MQTT & Schnittstellen")}
                </h1>
                <p className="text-sm text-gray-500 mt-1">
                    {t("interfaces.subtitle", "Verwalte deine globalen IoT-Telemetrie-Zugangsdaten für MQTT und OpenTelemetry.")}
                </p>
            </div>

            {/* MAIN INTERFACE CARD */}
            <div className="bg-white border border-indigo-100 rounded-2xl shadow-sm overflow-hidden ring-1 ring-indigo-50">
                <div className="p-5 bg-gradient-to-r from-indigo-50/80 via-blue-50/40 to-white border-b border-indigo-100 flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center text-xl shadow-sm">
                            📡
                        </div>
                        <div>
                            <h2 className="text-base font-bold text-gray-900">
                                {t("interfaces.title", "MQTT & Smart Home Schnittstelle")}
                            </h2>
                            <p className="text-xs text-gray-500">
                                {t("interfaces.subtitle", "Globale Zugangsdaten für ioBroker, Home Assistant, Node-RED, OTel & Shelly")}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setShowQR(true)}
                            className="px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-gray-700 text-xs font-semibold rounded-lg shadow-xs transition flex items-center gap-1.5"
                        >
                            <span>📱</span> {t("interfaces.qr_code", "QR-Code")}
                        </button>
                        <button
                            onClick={() => {
                                const text = `Host: ${mqttHost}\nPort: ${mqttPort}\nUser: ${mqttUser}\nPass: ${mqttPass}\nBase Topic: ${baseTopic}`;
                                safeCopy(text, "all_mqtt");
                            }}
                            className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-xs transition flex items-center gap-1.5"
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
                                            className="text-gray-400 hover:text-indigo-600 text-xs ml-1"
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
                                            className="text-gray-400 hover:text-indigo-600 text-xs ml-1"
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
                                                className="text-gray-400 hover:text-indigo-600 text-xs"
                                                title={showPassword ? "Verstecken" : "Anzeigen"}
                                            >
                                                {showPassword ? "🙈" : "👁️"}
                                            </button>
                                            <button
                                                onClick={() => safeCopy(mqttPass, "pass")}
                                                className="text-gray-400 hover:text-indigo-600 text-xs"
                                                title={t("common.copy", "Kopieren")}
                                            >
                                                {copiedKey === "pass" ? "✓" : "📋"}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* BASE TOPIC BANNER */}
                            <div className="p-3.5 bg-indigo-50/60 border border-indigo-100 rounded-xl flex flex-wrap items-center justify-between gap-3 text-xs">
                                <div>
                                    <span className="text-gray-500 font-medium">{t("interfaces.base_topic", "Dein persönliches Basis-Topic:")} </span>
                                    <code className="font-mono font-bold text-indigo-700 bg-white px-2 py-0.5 rounded border border-indigo-200">
                                        {baseTopic}
                                    </code>
                                </div>
                                <button
                                    onClick={handleRegeneratePassword}
                                    disabled={isRegenerating}
                                    className="text-xs text-red-600 hover:text-red-700 font-semibold hover:underline flex items-center gap-1"
                                >
                                    <span>🔄</span> {isRegenerating ? t("common.loading", "Generiere...") : t("interfaces.regenerate_btn", "Passwort neu generieren")}
                                </button>
                            </div>

                            {/* QUICK INTEGRATION GUIDES */}
                            <div className="border border-slate-200 rounded-xl overflow-hidden">
                                <div className="flex bg-slate-50 border-b border-slate-200 text-xs font-semibold overflow-x-auto">
                                    {[
                                        { id: "iobroker", label: t("interfaces.tab_iobroker", "🔧 ioBroker Anleitung") },
                                        { id: "homeassistant", label: t("interfaces.tab_ha", "🏠 Home Assistant") },
                                        { id: "otel", label: t("interfaces.tab_otel", "🔭 OpenTelemetry (OTel)") },
                                        { id: "shelly", label: t("interfaces.tab_shelly", "⚡ Shelly Web-UI") },
                                    ].map((tab) => (
                                        <button
                                            key={tab.id}
                                            onClick={() => setGuideTab(tab.id)}
                                            className={`px-4 py-2.5 transition whitespace-nowrap ${guideTab === tab.id
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

                                    {guideTab === "homeassistant" && (
                                        <div className="space-y-2">
                                            <p className="text-gray-600">
                                                Veröffentliche Sensor-Zustände automatisiert per Home Assistant MQTT-Aktion:
                                            </p>
                                            <pre className="bg-slate-900 text-slate-100 p-2.5 rounded-lg font-mono text-[11px] overflow-x-auto">
                                                {`action: mqtt.publish
data:
  topic: "h/${primaryHome?.mqtt_token || "<TOKEN>"}/meingeraet"
  payload: '{"power": {{ states("sensor.stromverbrauch") }}}'`}
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

                                    {guideTab === "shelly" && (
                                        <div className="space-y-1.5 text-gray-600">
                                            <p>1. Öffne die Weboberfläche deines Shelly im Browser $\rightarrow$ <strong>Settings</strong> $\rightarrow$ <strong>MQTT</strong>.</p>
                                            <p>2. Aktiviere <strong>Enable MQTT</strong> und trage Server <code className="bg-slate-100 px-1 rounded font-mono">{mqttHost}:{mqttPort}</code> ein.</p>
                                            <p>3. Setze das <strong>Topic Prefix</strong> auf <code className="bg-slate-100 px-1 rounded font-mono text-indigo-600">h/{primaryHome?.mqtt_token || "<TOKEN>"}/&lt;geraet_name&gt;</code>.</p>
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
                            MQTT & OTel Zugangsdaten Scan
                        </h3>
                        <p className="text-xs text-gray-500 mb-4">
                            Für automatisierte Konfiguration & Companion Apps
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
                            className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-2 rounded-xl text-xs transition"
                        >
                            {t("common.close", "Schließen")}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

