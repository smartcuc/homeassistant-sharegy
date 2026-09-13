/*
# src/pages/InterfacesPage.jsx
*/

import { useState } from "react";
import { useHomes } from "../hooks/useHomes";
import { QRCodeSVG } from "qrcode.react";
import { useTranslation } from "react-i18next";
import CloudInverterIntegrationCard from "../features/devices/components/CloudInverterIntegrationCard";
import ShellyCloudIntegrationCard from "../features/devices/components/ShellyCloudIntegrationCard";

export default function InterfacesPage() {
    const { primaryHome, isLoading: homeLoading, regenerateMqttPassword, isRegenerating } = useHomes();
    const { t } = useTranslation();

    const [showPassword, setShowPassword] = useState(false);
    const [copiedKey, setCopiedKey] = useState(null);
    const [showQR, setShowQR] = useState(false);
    const [guideTab, setGuideTab] = useState("otel");

    function safeCopy(text, key) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
            setCopiedKey(key);
            setTimeout(() => setCopiedKey(null), 2000);
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

    function renderInterfaceStatusCard({ icon, name, key, status, guideTab: targetTab }) {
        const isOnline = status?.online || status?.connected;
        const isConfigured = status?.configured;
        const secondsAgo = status?.seconds_ago;

        let statusBadge = null;
        if (isOnline) {
            statusBadge = (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-700">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    {t("interfaces.status_online", "Live Verbunden")}
                </span>
            );
        } else if (isConfigured) {
            statusBadge = (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-700">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                    {t("interfaces.status_standby", "Bereit")}
                </span>
            );
        } else {
            statusBadge = (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-500 border border-slate-200 dark:border-slate-700">
                    {t("interfaces.status_not_connected", "Nicht aktiv")}
                </span>
            );
        }

        let timeText = t("interfaces.no_telemetry_yet", "Noch keine Telemetrie empfangen");
        if (secondsAgo !== null && secondsAgo !== undefined) {
            if (secondsAgo < 60) {
                timeText = t("interfaces.seen_seconds_ago", { count: secondsAgo, defaultValue: `vor ${secondsAgo}s synchronisiert` });
            } else if (secondsAgo < 3600) {
                const mins = Math.floor(secondsAgo / 60);
                timeText = t("interfaces.seen_minutes_ago", { count: mins, defaultValue: `vor ${mins} Min. synchronisiert` });
            } else {
                const hrs = Math.floor(secondsAgo / 3600);
                timeText = t("interfaces.seen_hours_ago", { count: hrs, defaultValue: `vor ${hrs} Std. synchronisiert` });
            }
        }

        const targetId = 
            key === "homeassistant" ? "section-ha" :
            key === "iobroker" ? "section-iobroker" :
            key === "shelly_wss" ? "section-shelly" :
            key === "cloud_inverter" ? "section-cloud-inverter" :
            key === "mqtt_direct" ? "section-mqtt" :
            key === "wmsb" ? "section-wmsb" : null;

        return (
            <div
                key={name}
                onClick={() => {
                    if (targetId) {
                        document.getElementById(targetId)?.scrollIntoView({ behavior: "smooth" });
                    }
                }}
                className={`p-3.5 rounded-2xl border transition-all cursor-pointer hover:shadow-md hover:-translate-y-0.5 ${
                    isOnline
                        ? "bg-emerald-50/40 dark:bg-emerald-950/20 border-emerald-200/80 dark:border-emerald-800/60"
                        : isConfigured
                        ? "bg-slate-50 dark:bg-slate-800/40 border-slate-200/80 dark:border-slate-700/60"
                        : "bg-white dark:bg-slate-900 border-slate-200/60 dark:border-slate-800/60"
                }`}
            >
                <div className="flex items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2 font-bold text-xs text-slate-900 dark:text-white">
                        <span className="text-base">{icon}</span>
                        <span>{name}</span>
                    </div>
                    {statusBadge}
                </div>
                <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono truncate">
                    {timeText}
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8 relative">
            {/* Centered Floating Checkmark Tooltip / Toast */}
            {copiedKey && (
                <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 bg-slate-900/95 text-white text-xs font-bold rounded-2xl shadow-2xl border border-emerald-500/50 flex items-center gap-2.5 backdrop-blur-md animate-in fade-in zoom-in-95 duration-200">
                    <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center text-xs">✓</span>
                    <span>{t("common.copied", "In Zwischenablage kopiert!")}</span>
                </div>
            )}

            {/* HEADER */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <span>📡</span> {t("interfaces.title", "Schnittstellen")}
                </h1>
                <p className="text-sm text-gray-500 mt-1">
                    {t("interfaces.subtitle", "Verbinde deine Geräte und Zentralen direkt über Outbound-WebSocket (Shelly), Sungrow Direkt-Kopplung, Cloud-Wechselrichter, das Home Assistant Plugin oder MQTT mit Sharegy.")}
                </p>
            </div>

            {/* LIVE INTERFACES STATUS & DIAGNOSTICS */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-5 sm:p-6 shadow-xs space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
                    <div className="flex items-center gap-2.5">
                        <span className="text-xl">🩺</span>
                        <div>
                            <h2 className="text-base font-bold text-gray-900 dark:text-white">
                                {t("interfaces.diagnostics_title", "Live Schnittstellen-Status & Verbindungstest")}
                            </h2>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                                {t("interfaces.diagnostics_desc", "Echtzeit-Erkennung aktiver Telemetrie über Home Assistant, ioBroker, Shelly WSS, Sungrow Cloud, Smart Meter und MQTT.")}
                            </p>
                        </div>
                    </div>
                    <span className="text-xs font-semibold px-2.5 py-1 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 rounded-full flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        {t("interfaces.live_monitoring", "Live Überwachung")}
                    </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {/* Home Assistant Card */}
                    {renderInterfaceStatusCard({
                        icon: "🏠",
                        name: "Home Assistant",
                        key: "homeassistant",
                        status: primaryHome?.interface_status?.homeassistant,
                        guideTab: "ha",
                    })}

                    {/* ioBroker Card */}
                    {renderInterfaceStatusCard({
                        icon: "🔵",
                        name: "ioBroker",
                        key: "iobroker",
                        status: primaryHome?.interface_status?.iobroker,
                        guideTab: "iobroker",
                    })}

                    {/* Shelly WSS Card */}
                    {renderInterfaceStatusCard({
                        icon: "⚡",
                        name: "Shelly Direct WSS",
                        key: "shelly_wss",
                        status: primaryHome?.interface_status?.shelly_wss,
                        guideTab: "shelly",
                    })}

                    {/* Cloud Inverters Card */}
                    {renderInterfaceStatusCard({
                        icon: "☁️",
                        name: t("interfaces.cloud_inverters", "Cloud-Wechselrichter"),
                        key: "cloud_inverter",
                        status: primaryHome?.interface_status?.cloud_inverter,
                    })}

                    {/* MQTT Direct */}
                    {renderInterfaceStatusCard({
                        icon: "📡",
                        name: "MQTT / Tasmota",
                        key: "mqtt_direct",
                        status: primaryHome?.interface_status?.mqtt_direct,
                        guideTab: "mqtt",
                    })}

                    {/* Smart Meter / wMSB */}
                    {renderInterfaceStatusCard({
                        icon: "🏢",
                        name: t("interfaces.card_wmsb", "Smart Meter / wMSB"),
                        key: "wmsb",
                        status: primaryHome?.interface_status?.wmsb,
                    })}
                </div>
            </div>

            {/* 1. SECTION: WEBSOCKET INTERFACE (SHELLY WSS - EMPFOHLEN) */}
            <div id="section-shelly" className="bg-white border border-amber-200/80 rounded-2xl shadow-xs overflow-hidden ring-1 ring-amber-100">
                <div className="p-5 bg-gradient-to-r from-amber-50/80 via-orange-50/30 to-white border-b border-amber-200/80 flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center text-xl shadow-xs">
                            ⚡
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-base font-bold text-gray-900">
                                    {t("interfaces.wss_title", "1. Outbound-WebSocket Schnittstelle (Shelly Gen2 / Gen3 / Pro)")}
                                </h2>
                                <span className="text-[10px] font-bold px-2 py-0.5 bg-amber-100 text-amber-800 rounded-full border border-amber-200">
                                    {t("interfaces.wss_badge", "Empfohlen & DAU-sicher")}
                                </span>
                            </div>
                            <p className="text-xs text-gray-500">
                                {t("interfaces.wss_desc", "Voll verschlüsselte Live-Verbindung über Port 443 (WSS) für Shelly 1PM Gen3, Pro 3EM, Plus 1PM uvm.")}
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={() => safeCopy(wsUrl, "ws_url")}
                        className="px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-white text-xs font-semibold rounded-lg shadow-2xs transition flex items-center gap-1.5 cursor-pointer"
                    >
                        {copiedKey === "ws_url" ? `✅ ${t("common.copied", "Kopiert!")}` : `📋 ${t("interfaces.copy_wss_url", "WSS-URL kopieren")}`}
                    </button>
                </div>

                <div className="p-6 space-y-5">
                    {/* WSS URL DISPLAY */}
                    <div>
                        <div className="text-[11px] font-bold uppercase tracking-wider text-gray-500 mb-1.5">
                            {t("interfaces.personal_wss_url", "Deine persönliche WebSocket Server-URL")}
                        </div>
                        <div className="flex items-center justify-between p-3.5 bg-amber-50/50 border border-amber-200 rounded-xl font-mono text-xs text-amber-900 font-semibold break-all gap-2">
                            <span>{wsUrl}</span>
                            <button
                                onClick={() => safeCopy(wsUrl, "ws_url")}
                                className="px-2.5 py-1 bg-white hover:bg-amber-100 border border-amber-300 text-amber-900 rounded-lg text-xs font-bold shrink-0 transition cursor-pointer"
                            >
                                {copiedKey === "ws_url" ? `✓ ${t("common.copied", "Kopiert")}` : t("common.copy", "Kopieren")}
                            </button>
                        </div>
                    </div>

                    {/* FEATURES BADGES */}
                    <div className="grid sm:grid-cols-3 gap-3 text-xs">
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">🔒</span>
                            <div>
                                <div className="font-bold text-gray-900">{t("interfaces.tls_encrypted", "TLS Verschlüsselt")}</div>
                                <div className="text-gray-500 text-[11px]">{t("interfaces.tls_desc", "Sichere WSS-Verbindung über Standard HTTPS (Port 443).")}</div>
                            </div>
                        </div>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">🛡️</span>
                            <div>
                                <div className="font-bold text-gray-900">{t("interfaces.no_port_forwarding", "Keine Portweiterleitung")}</div>
                                <div className="text-gray-500 text-[11px]">{t("interfaces.no_port_desc", "Funktioniert hinter jeder Fritz!Box & Router ohne Freigaben.")}</div>
                            </div>
                        </div>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">⚡</span>
                            <div>
                                <div className="font-bold text-gray-900">{t("interfaces.bidirectional", "Bidirektional & Aktorik")}</div>
                                <div className="text-gray-500 text-[11px]">{t("interfaces.bidirectional_desc", "Live-Leistungsmessung & Relais-Schaltung in 5 ms.")}</div>
                            </div>
                        </div>
                    </div>

                    {/* 3-STEP INSTRUCTIONS */}
                    <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-3">
                        <div className="font-bold text-gray-900 text-sm flex items-center gap-1.5">
                            <span>📖</span> {t("interfaces.shelly_setup_title", "3-Schritte Einrichtung im Shelly Web-Interface:")}
                        </div>
                        <ol className="list-decimal list-inside space-y-2 text-gray-700 leading-relaxed">
                            <li>
                                {t("interfaces.shelly_step_1", "Öffne die Weboberfläche deines Shelly im Browser")} (<code className="bg-white px-1.5 py-0.5 rounded border border-slate-300 font-mono">http://&lt;shelly-ip&gt;</code>).
                            </li>
                            <li>
                                {t("interfaces.shelly_step_2", "Klicke im Menü links auf Settings → Outbound WebSocket.")}
                            </li>
                            <li>
                                {t("interfaces.shelly_step_3", "Setze ein Häkchen bei Enable, wähle TLS/SSL und füge oben stehende Server-URL ein → Klicke auf Save Settings.")}
                            </li>
                        </ol>
                        <div className="p-2.5 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 text-[11px] font-medium flex items-center gap-2">
                            <span>🚀</span>
                            <span>
                                <strong>{t("interfaces.done", "Fertig!")}</strong> {t("interfaces.shelly_done_desc", "Der Shelly verbindet sich automatisch mit Sharegy. Das Gerät wird sofort erkannt und taucht unter Geräte und im Dashboard auf.")}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* 2. SECTION: SHELLY CLOUD 1-KLICK AUTO-DISCOVERY */}
            <ShellyCloudIntegrationCard primaryHome={primaryHome} />

            {/* 3. SECTION: SUNGROW DIREKT-KOPPLUNG (1-KLICK OAUTH & ISOLARCLOUD) */}
            <div id="section-cloud-inverter" className="space-y-8">
                <CloudInverterIntegrationCard 
                    primaryHome={primaryHome} 
                    filterVendor="sungrow" 
                    sectionNumber={3} 
                    cardTitle={t("interfaces.sungrow_title", "3. Sungrow Wechselrichter & Batteriespeicher (SH-Serie)")} 
                />

                {/* 4. SECTION: WEITERE WECHSELRICHTER & CLOUD-DIENSTE */}
                <CloudInverterIntegrationCard 
                    primaryHome={primaryHome} 
                    filterVendor="others" 
                    sectionNumber={4} 
                    cardTitle={t("interfaces.other_inverters_title", "4. Weitere Wechselrichter (SolarEdge, Fronius, Kostal, Growatt)")} 
                />
            </div>

            {/* 5. SECTION: NATIVE IOBROKER ADAPTER (IOBROKER.SHAREGY) */}
            <div id="section-iobroker" className="bg-white border border-blue-200/80 rounded-2xl shadow-xs overflow-hidden ring-1 ring-blue-100">
                <div className="p-5 bg-gradient-to-r from-blue-50/80 via-sky-50/30 to-white border-b border-blue-200/80 flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center text-xl shadow-xs">
                            🔵
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-base font-bold text-gray-900">
                                    {t("interfaces.iobroker_adapter_title", "5. Nativer ioBroker Adapter (iobroker.sharegy)")}
                                </h2>
                                <span className="text-[10px] font-bold px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full border border-blue-200">
                                    {t("interfaces.iobroker_adapter_badge", "Offizieller Adapter & State-Tree")}
                                </span>
                            </div>
                            <p className="text-xs text-gray-500">
                                {t("interfaces.iobroker_adapter_desc", "Direkte 2-Wege-Integration in den ioBroker Objektbaum — inklusive automatischer Geräteerkennung und Sub-Sekunden-Aktorik.")}
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={() => safeCopy(primaryHome?.mqtt_token || "", "iobroker_token")}
                        className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-2xs transition flex items-center gap-1.5 cursor-pointer"
                    >
                        {copiedKey === "iobroker_token" ? `✅ ${t("common.copied", "Kopiert!")}` : `📋 ${t("interfaces.copy_home_token", "Home Token kopieren")}`}
                    </button>
                </div>

                <div className="p-6 space-y-5">
                    {/* FEATURES BADGES */}
                    <div className="grid sm:grid-cols-3 gap-3 text-xs">
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">🌳</span>
                            <div>
                                <div className="font-bold text-gray-900">{t("interfaces.iobroker_tree", "Automatischer State-Baum")}</div>
                                <div className="text-gray-500 text-[11px]">{t("interfaces.iobroker_tree_desc", "Erstellt sharegy.0.* mit allen PV-, Speicher-, Wallbox- & Zähler-Objekten.")}</div>
                            </div>
                        </div>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">⚡</span>
                            <div>
                                <div className="font-bold text-gray-900">{t("interfaces.iobroker_stream", "Live WebSocket Stream")}</div>
                                <div className="text-gray-500 text-[11px]">{t("interfaces.iobroker_stream_desc", "Permanenter, latenzarmer Datenkanal über verschlüsseltes TLS/WSS.")}</div>
                            </div>
                        </div>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">🎛️</span>
                            <div>
                                <div className="font-bold text-gray-900">{t("interfaces.iobroker_control", "Bidirektionale Aktorik")}</div>
                                <div className="text-gray-500 text-[11px]">{t("interfaces.iobroker_control_desc", "Schaltet Relais, setzt Dimm-Stufen nach § 14a EnWG und steuert Ladevorgänge.")}</div>
                            </div>
                        </div>
                    </div>

                    {/* SETUP STEPS */}
                    <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-3">
                        <div className="font-bold text-gray-900 text-sm flex items-center gap-1.5">
                            <span>📦</span> {t("interfaces.iobroker_install_title", "Installation im ioBroker Admin:")}
                        </div>
                        <ol className="list-decimal list-inside space-y-2 text-gray-700 leading-relaxed">
                            <li>
                                {t("interfaces.iobroker_install_step_1", "Öffne die ioBroker Weboberfläche → Adapter → Aktiviere das Experten-Icon (GitHub-Katze) und installiere 'iobroker.sharegy' (oder via npm: npm i iobroker.sharegy).")}
                            </li>
                            <li>
                                {t("interfaces.iobroker_install_step_2", "Erstelle eine Instanz (sharegy.0) und trage dein persönliches Home Token ein.")}
                            </li>
                            <li>
                                {t("interfaces.iobroker_install_step_3", "Wähle deine Zähler-, PV- und Wechselrichter-Datenpunkte aus → Der Live-Sync startet sofort automatisch.")}
                            </li>
                        </ol>
                    </div>
                </div>
            </div>

            {/* 6. SECTION: NATIVE HOME ASSISTANT INTEGRATION (HACS / CUSTOM COMPONENT) */}
            <div id="section-ha" className="bg-white border border-cyan-200/80 rounded-2xl shadow-xs overflow-hidden ring-1 ring-cyan-100">
                <div className="p-5 bg-gradient-to-r from-cyan-50/80 via-blue-50/30 to-white border-b border-cyan-200/80 flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-cyan-600 text-white flex items-center justify-center text-xl shadow-xs">
                            🏠
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-base font-bold text-gray-900">
                                    {t("interfaces.ha_title", "6. Natives Home Assistant Plugin (HACS / Custom Component)")}
                                </h2>
                                <span className="text-[10px] font-bold px-2 py-0.5 bg-cyan-100 text-cyan-800 rounded-full border border-cyan-200">
                                    {t("interfaces.ha_badge", "Neu & Store-and-Forward")}
                                </span>
                            </div>
                            <p className="text-xs text-gray-500">
                                {t("interfaces.ha_desc", "Wähle deine Home Assistant Entitäten per Klick aus — inklusive lokalem 48h-Offline-Puffer bei Netzausfall.")}
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={() => safeCopy(primaryHome?.mqtt_token || "", "ha_token")}
                        className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-700 text-white text-xs font-semibold rounded-lg shadow-2xs transition flex items-center gap-1.5 cursor-pointer"
                    >
                        {copiedKey === "ha_token" ? `✅ ${t("common.copied", "Kopiert!")}` : `📋 ${t("interfaces.copy_home_token", "Home Token kopieren")}`}
                    </button>
                </div>

                <div className="p-6 space-y-5">
                    {/* FEATURES BADGES */}
                    <div className="grid sm:grid-cols-3 gap-3 text-xs">
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">🎯</span>
                            <div>
                                <div className="font-bold text-gray-900">{t("interfaces.ha_picker", "1-Klick Entity Picker")}</div>
                                <div className="text-gray-500 text-[11px]">{t("interfaces.ha_picker_desc", "Bequeme Auswahl aller Sensoren direkt in der Home Assistant UI.")}</div>
                            </div>
                        </div>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">💾</span>
                            <div>
                                <div className="font-bold text-gray-900">{t("interfaces.ha_buffer", "48h Offline-Puffer")}</div>
                                <div className="text-gray-500 text-[11px]">{t("interfaces.ha_buffer_desc", "Speichert Daten bei Internetausfall lokal und sendet sie lückenlos nach.")}</div>
                            </div>
                        </div>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">⚡</span>
                            <div>
                                <div className="font-bold text-gray-900">{t("interfaces.ha_stream", "Live WebSocket Stream")}</div>
                                <div className="text-gray-500 text-[11px]">{t("interfaces.ha_stream_desc", "Echtzeit-Übertragung über verschlüsseltes WSS (Port 443).")}</div>
                            </div>
                        </div>
                    </div>

                    {/* SETUP STEPS */}
                    <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-3">
                        <div className="font-bold text-gray-900 text-sm flex items-center gap-1.5">
                            <span>📦</span> {t("interfaces.ha_install_title", "Installation in Home Assistant:")}
                        </div>
                        <ol className="list-decimal list-inside space-y-2 text-gray-700 leading-relaxed">
                            <li>
                                {t("interfaces.ha_step_1", "Kopiere den Ordner custom_components/sharegy in deinen Home Assistant Ordner config/custom_components/ (oder füge das Repository in HACS hinzu).")}
                            </li>
                            <li>
                                {t("interfaces.ha_step_2", "Starte Home Assistant neu und öffne Einstellungen → Geräte & Dienste → Integration hinzufügen.")}
                            </li>
                            <li>
                                {t("interfaces.ha_step_3", "Wähle Sharegy Cloud Energy Bridge, füge dein persönliches Home Token ein und wähle deine Sensoren per Dropdown aus.")}
                            </li>
                        </ol>
                    </div>
                </div>
            </div>

            {/* 7. SECTION: MQTT INTERFACE CARD */}
            <div id="section-mqtt" className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
                <div className="p-5 bg-gradient-to-r from-slate-50 via-indigo-50/30 to-white border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center text-xl shadow-xs">
                            📡
                        </div>
                        <div>
                            <h2 className="text-base font-bold text-gray-900">
                                {t("interfaces.mqtt_title", "7. MQTT Broker Schnittstelle")}
                            </h2>

                            <p className="text-xs text-gray-500">
                                {t("interfaces.mqtt_desc", "Standard-IoT-Protokoll zur universellen Anbindung von OpenTelemetry, Node-RED, Tasmota, OpenDTU & Smart-Home-Zentralen")}
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
                                            className={`p-1 rounded-md text-xs transition cursor-pointer flex items-center justify-center ${
                                                copiedKey === "host"
                                                    ? "bg-emerald-100 text-emerald-700 font-bold scale-110"
                                                    : "text-gray-400 hover:text-indigo-600 hover:bg-slate-200/60"
                                            }`}
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
                                            className={`p-1 rounded-md text-xs transition cursor-pointer flex items-center justify-center ${
                                                copiedKey === "user"
                                                    ? "bg-emerald-100 text-emerald-700 font-bold scale-110"
                                                    : "text-gray-400 hover:text-indigo-600 hover:bg-slate-200/60"
                                            }`}
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
                                                className="p-1 rounded-md text-gray-400 hover:text-indigo-600 hover:bg-slate-200/60 text-xs cursor-pointer"
                                                title={showPassword ? t("common.hide", "Verstecken") : t("common.show", "Anzeigen")}
                                            >
                                                {showPassword ? "🙈" : "👁️"}
                                            </button>
                                            <button
                                                onClick={() => safeCopy(mqttPass, "pass")}
                                                className={`p-1 rounded-md text-xs transition cursor-pointer flex items-center justify-center ${
                                                    copiedKey === "pass"
                                                        ? "bg-emerald-100 text-emerald-700 font-bold scale-110"
                                                        : "text-gray-400 hover:text-indigo-600 hover:bg-slate-200/60"
                                                }`}
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
                                        { id: "otel", label: "🔭 OpenTelemetry (OTel)" },
                                        { id: "nodered", label: "🟢 Node-RED / Tasmota" },
                                        { id: "iobroker", label: "🔵 ioBroker MQTT" },
                                        { id: "ha_mqtt", label: "🏠 Home Assistant" },
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
                                    {guideTab === "otel" && (
                                        <div className="space-y-2">
                                            <div className="font-bold text-gray-900 text-sm flex items-center justify-between">
                                                <span>🔭 {t("interfaces.otel_title", "OpenTelemetry (OTLP/HTTP) Ingestion")}</span>
                                                <span className="text-[10px] text-indigo-600 font-mono">Endpoint: /api/v1/metrics</span>
                                            </div>
                                            <p className="text-gray-600">
                                                {t("interfaces.otel_desc", "Sende Telemetrie direkt via OpenTelemetry Collector oder Python SDK mit dem Resource Attribute:")}
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
                                        <div className="space-y-2 text-gray-600">
                                            <p>
                                                {t("interfaces.nodered_step_1", "1. Verwende in Node-RED einen standardmäßigen MQTT Out Node (oder in Tasmota die integrierte MQTT Telemetrie).")}<br />
                                                {t("interfaces.nodered_step_2", "2. Konfiguriere den Broker mit deinen Zugangsdaten (Host, Port, User & Kennwort).")}<br />
                                                {t("interfaces.nodered_step_3", "3. Sende JSON-Nutzdaten an dein Basis-Topic:")}
                                            </p>
                                            <pre className="bg-slate-900 text-green-400 p-2.5 rounded-lg font-mono text-[11px] overflow-x-auto">
                                                {`// Node-RED Function Node Beispiel:
msg.topic = "h/${primaryHome?.mqtt_token || "<TOKEN>"}/balkonkraftwerk";
msg.payload = {
    power: 450.0,
    voltage: 230.1,
    daily_yield_kwh: 2.35
};
return msg;`}
                                            </pre>
                                        </div>
                                    )}

                                    {guideTab === "iobroker" && (
                                        <div className="space-y-2">
                                            <p className="text-gray-600">
                                                {t("interfaces.iobroker_step_1", "1. Installiere den MQTT Client Adapter (mqtt-client).")}<br />
                                                {t("interfaces.iobroker_step_2", "2. Wähle Typ Client / Abonnent, trage URL, Port sowie Benutzer & Kennwort ein.")}<br />
                                                {t("interfaces.iobroker_step_3", "3. Sende Messwerte an dein Topic:")}
                                            </p>
                                            <pre className="bg-slate-900 text-green-400 p-2.5 rounded-lg font-mono text-[11px] overflow-x-auto">
                                                {`sendTo('mqtt-client.0', 'sendMessage', {
    topic: 'h/${primaryHome?.mqtt_token || "<TOKEN>"}/balkonkraftwerk',
    message: JSON.stringify({ power: 450.0 })
});`}
                                            </pre>
                                        </div>
                                    )}

                                    {guideTab === "ha_mqtt" && (
                                        <div className="space-y-2">
                                            <p className="text-gray-600">
                                                {t("interfaces.ha_mqtt_step_1", "Falls du statt des HACS-Plugins die native Home Assistant MQTT-Integration nutzen möchtest:")}<br />
                                                {t("interfaces.ha_mqtt_step_2", "Sende Sensorwerte automatisiert per MQTT Publish Aktion an dein Basis-Topic:")}
                                            </p>
                                            <pre className="bg-slate-900 text-green-400 p-2.5 rounded-lg font-mono text-[11px] overflow-x-auto">
                                                {`# In Home Assistant Automation (Aktion / Action):
action: mqtt.publish
data:
  topic: "h/${primaryHome?.mqtt_token || "<TOKEN>"}/hausverbrauch"
  payload: >
    {
      "power": {{ states('sensor.power_consumption') | float(0) }},
      "total_kwh": {{ states('sensor.total_energy_import') | float(0) }}
    }`}
                                            </pre>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* 8. SECTION: SMART METER GATEWAYS & WMSB INGEST (§ 42B ENWG & MSBG) */}
            <div id="section-wmsb" className="bg-white border border-emerald-200/80 rounded-2xl shadow-xs overflow-hidden ring-1 ring-emerald-100">
                <div className="p-5 bg-gradient-to-r from-emerald-50/80 via-teal-50/30 to-white border-b border-emerald-200/80 flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center text-xl shadow-xs">
                            🏢
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-base font-bold text-gray-900">
                                    {t("interfaces.wmsb_title", "8. Smart Meter Gateways, wMSB & Eichrechtliches Messwesen")}
                                </h2>
                                <span className="text-[10px] font-bold px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full border border-emerald-200">
                                    {t("interfaces.wmsb_badge", "§ 42b EnWG & MsbG Konform")}
                                </span>
                            </div>
                            <p className="text-xs text-gray-500">
                                {t("interfaces.wmsb_desc", "15-Minuten-Lastgänge von zertifizierten Smart Meter Gateways (wMSB / gMSB) für Energy Sharing & Mieterstrom.")}
                            </p>
                        </div>
                    </div>

                    <a
                        href="/app/tenants"
                        className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-2xs transition flex items-center gap-1.5"
                    >
                        <span>🏛️</span>
                        <span>{t("interfaces.to_wmsb_cockpit", "Zum Community & wMSB Cockpit")}</span>
                    </a>
                </div>

                <div className="p-6 space-y-5">
                    <div className="grid sm:grid-cols-3 gap-3 text-xs">
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">🏢</span>
                            <div>
                                <div className="font-bold text-gray-900">{t("interfaces.wmsb_cloud_push", "wMSB Cloud-Push")}</div>
                                <div className="text-gray-500 text-[11px]">{t("interfaces.wmsb_cloud_push_desc", "Direkter Push von inexogy, Solandeo, Discovergy per REST & MSCONS.")}</div>
                            </div>
                        </div>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">⚡</span>
                            <div>
                                <div className="font-bold text-gray-900">{t("interfaces.gmsb_han", "gMSB HAN / BSI iMSys")}</div>
                                <div className="text-gray-500 text-[11px]">{t("interfaces.gmsb_han_desc", "BSI TR-03109-1 konforme Erfassung lokaler Smart Meter Gateways & CLS.")}</div>
                            </div>
                        </div>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5">
                            <span className="text-base">🔌</span>
                            <div>
                                <div className="font-bold text-gray-900">{t("interfaces.mid_submetering", "MID-Submetering")}</div>
                                <div className="text-gray-500 text-[11px]">{t("interfaces.mid_submetering_desc", "Shelly Pro 3EM & Modbus für interne Liegenschaften & WEGs.")}</div>
                            </div>
                        </div>
                    </div>
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
                            {t("interfaces.qr_modal_title", "MQTT & IoT Zugangsdaten Scan")}
                        </h3>
                        <p className="text-xs text-gray-500 mb-4">
                            {t("interfaces.qr_modal_desc", "Für automatisierte Konfiguration in Companion Apps & Gateways")}
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
