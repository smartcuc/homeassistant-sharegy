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
    const [guideTab, setGuideTab] = useState("iobroker_wss");
    const [haTab, setHaTab] = useState("entities");
    const [bidiEnabled, setBidiEnabled] = useState(true);

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
                    <span>📡</span> {t("interfaces.title", "Schnittstellen & Smart Home")}
                </h1>
                <p className="text-sm text-gray-500 mt-1">
                    {t("interfaces.subtitle", "Verbinde deine Geräte und Zentralen direkt über Outbound-WebSocket (WSS bevorzugt), Home Assistant, ioBroker oder MQTT bidirektional mit Sharegy.")}
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
            <CloudInverterIntegrationCard 
                primaryHome={primaryHome} 
                filterVendor="sungrow" 
                sectionNumber={3} 
                cardTitle="3. Sungrow Wechselrichter & Batteriespeicher (SH-Serie)" 
            />

            {/* 4. SECTION: WEITERE WECHSELRICHTER & CLOUD-DIENSTE */}
            <CloudInverterIntegrationCard 
                primaryHome={primaryHome} 
                filterVendor="others" 
                sectionNumber={4} 
                cardTitle="4. Weitere Wechselrichter (SolarEdge, Fronius, Kostal, Growatt)" 
            />

            {/* 5. SECTION: NATIVE HOME ASSISTANT INTEGRATION (HACS / CUSTOM COMPONENT) */}
            <div className="bg-white border border-cyan-200/80 rounded-2xl shadow-xs overflow-hidden ring-1 ring-cyan-100">
                <div className="p-5 bg-gradient-to-r from-cyan-50/80 via-blue-50/30 to-white border-b border-cyan-200/80 flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-cyan-600 text-white flex items-center justify-center text-xl shadow-xs">
                            🏠
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-base font-bold text-gray-900">
                                    5. Home Assistant Integration (v2.1.0 – Bidirektionales Messen & Steuern)
                                </h2>
                                <span className="text-[10px] font-bold px-2 py-0.5 bg-cyan-100 text-cyan-800 rounded-full border border-cyan-200">
                                    WSS & MQTT Kompatibel
                                </span>
                            </div>
                            <p className="text-xs text-gray-500">
                                Vollständige HACS-Integration für Live-Monitoring, DIN EN 12831 Heizkurven, Estrich-Puffer-Boost und SG-Ready Steuerung.
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        {/* Interactive Toggle for Bidirectional Mode */}
                        <div className="flex items-center gap-2 bg-white/80 backdrop-blur px-3 py-1.5 rounded-xl border border-cyan-200 shadow-2xs">
                            <span className="text-xs font-bold text-gray-700">Bidirektionale Aktorik:</span>
                            <button
                                type="button"
                                onClick={() => setBidiEnabled(!bidiEnabled)}
                                className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-hidden ${bidiEnabled ? 'bg-emerald-500' : 'bg-slate-300'}`}
                            >
                                <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition duration-200 ease-in-out ${bidiEnabled ? 'translate-x-4' : 'translate-x-0'}`} />
                            </button>
                            <span className={`text-[11px] font-bold ${bidiEnabled ? 'text-emerald-700' : 'text-slate-500'}`}>
                                {bidiEnabled ? "Aktiv" : "Pausiert"}
                            </span>
                        </div>

                        <button
                            onClick={() => safeCopy(primaryHome?.mqtt_token || "", "ha_token")}
                            className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-700 text-white text-xs font-semibold rounded-lg shadow-2xs transition flex items-center gap-1.5 cursor-pointer"
                        >
                            {copiedKey === "ha_token" ? `✅ ${t("common.copied", "Kopiert!")}` : `📋 ${t("interfaces.copy_home_token", "Home Token kopieren")}`}
                        </button>
                    </div>
                </div>

                <div className="p-6 space-y-5">
                    {/* PROTOCOL BANNER */}
                    <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl flex flex-wrap items-center justify-between gap-3 text-xs">
                        <div className="flex items-center gap-2">
                            <span className="text-base">🔒</span>
                            <span className="text-gray-700 font-medium">
                                <strong>Verbindungsmethode:</strong> Outbound WSS über Port 443 (HTTPS) ist die <strong>bevorzugte Methode</strong>. Keine Portfreigaben nötig.
                            </span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-[11px] px-2 py-0.5 bg-emerald-100 text-emerald-800 font-bold rounded-md">
                                WSS (Port 443) Bevorzugt
                            </span>
                            <span className="text-[11px] px-2 py-0.5 bg-indigo-100 text-indigo-800 font-medium rounded-md">
                                MQTT Fallback Aktiv
                            </span>
                        </div>
                    </div>

                    {/* HA NAVIGATION TABS */}
                    <div className="border border-slate-200 rounded-xl overflow-hidden">
                        <div className="flex bg-slate-50 border-b border-slate-200 text-xs font-semibold overflow-x-auto">
                            {[
                                { id: "entities", label: "📊 Verfügbare Entitäten (Messen & Steuern)" },
                                { id: "automations", label: "🤖 Automationen (FBH, BWWP & Dynamischer Strompreis)" },
                                { id: "install", label: "📦 Installation & Einrichtung" },
                            ].map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => setHaTab(tab.id)}
                                    className={`px-4 py-2.5 transition whitespace-nowrap cursor-pointer ${haTab === tab.id
                                        ? "bg-white text-cyan-700 border-b-2 border-cyan-600 font-bold"
                                        : "text-gray-500 hover:text-gray-900"
                                    }`}
                                >
                                    {tab.label}
                                </button>
                            ))}
                        </div>

                        <div className="p-4 text-xs text-gray-700 leading-relaxed bg-white">
                            {haTab === "entities" && (
                                <div className="space-y-4">
                                    <div>
                                        <h4 className="font-bold text-gray-900 text-xs uppercase tracking-wider mb-2 flex items-center gap-1.5">
                                            <span>📈</span> 1. Inbound Messwerte & Live-Sensoren (Sharegy &rarr; HA)
                                        </h4>
                                        <div className="overflow-x-auto border border-slate-200 rounded-lg">
                                            <table className="min-w-full divide-y divide-slate-200 text-[11px]">
                                                <thead className="bg-slate-50 text-gray-600 font-semibold">
                                                    <tr>
                                                        <th className="px-3 py-2 text-left">Entität</th>
                                                        <th className="px-3 py-2 text-center">Einheit</th>
                                                        <th className="px-3 py-2 text-left">Funktion</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="divide-y divide-slate-100 font-mono">
                                                    <tr>
                                                        <td className="px-3 py-1.5 font-bold text-cyan-800">sensor.sharegy_solar_erzeugung</td>
                                                        <td className="px-3 py-1.5 text-center font-sans text-gray-500">W</td>
                                                        <td className="px-3 py-1.5 font-sans text-gray-700">Aktuelle PV-Leistung aller Wechselrichter</td>
                                                    </tr>
                                                    <tr>
                                                        <td className="px-3 py-1.5 font-bold text-cyan-800">sensor.sharegy_fbh_vorlauf_solltemperatur</td>
                                                        <td className="px-3 py-1.5 text-center font-sans text-gray-500">°C</td>
                                                        <td className="px-3 py-1.5 font-sans text-gray-700">Berechnete DIN EN 12831 Vorlauftemperatur nach Heizkurve</td>
                                                    </tr>
                                                    <tr>
                                                        <td className="px-3 py-1.5 font-bold text-cyan-800">sensor.sharegy_fbh_estrich_speicher_ladestand_soc</td>
                                                        <td className="px-3 py-1.5 text-center font-sans text-gray-500">%</td>
                                                        <td className="px-3 py-1.5 font-sans text-gray-700">Ladezustand des thermischen Estrich-Speichers</td>
                                                    </tr>
                                                    <tr>
                                                        <td className="px-3 py-1.5 font-bold text-cyan-800">sensor.sharegy_fbh_betriebsmodus</td>
                                                        <td className="px-3 py-1.5 text-center font-sans text-gray-500">Text</td>
                                                        <td className="px-3 py-1.5 font-sans text-gray-700">PV_BOOST, GRID_ARBITRAGE, COMFORT, ECO</td>
                                                    </tr>
                                                    <tr>
                                                        <td className="px-3 py-1.5 font-bold text-cyan-800">sensor.sharegy_borsenstrompreis</td>
                                                        <td className="px-3 py-1.5 text-center font-sans text-gray-500">ct/kWh</td>
                                                        <td className="px-3 py-1.5 font-sans text-gray-700">Aktueller dynamischer Börsenstrompreis (EPEX Spot)</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>

                                    <div>
                                        <h4 className="font-bold text-gray-900 text-xs uppercase tracking-wider mb-2 flex items-center gap-1.5">
                                            <span>🎛️</span> 2. Outbound Schalter & Sollwert-Regler (HA &rarr; Aktoren)
                                        </h4>
                                        <div className="overflow-x-auto border border-slate-200 rounded-lg">
                                            <table className="min-w-full divide-y divide-slate-200 text-[11px]">
                                                <thead className="bg-slate-50 text-gray-600 font-semibold">
                                                    <tr>
                                                        <th className="px-3 py-2 text-left">Entität</th>
                                                        <th className="px-3 py-2 text-center">Typ</th>
                                                        <th className="px-3 py-2 text-left">Funktion</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="divide-y divide-slate-100 font-mono">
                                                    <tr>
                                                        <td className="px-3 py-1.5 font-bold text-emerald-800">switch.sharegy_bidirektionale_steuerung</td>
                                                        <td className="px-3 py-1.5 text-center font-sans text-emerald-600 font-bold">Schalter</td>
                                                        <td className="px-3 py-1.5 font-sans text-gray-700">Master-Schalter: Freigabe / Not-Aus für automatische Eingriffe</td>
                                                    </tr>
                                                    <tr>
                                                        <td className="px-3 py-1.5 font-bold text-emerald-800">switch.sharegy_fussbodenheizung_boost</td>
                                                        <td className="px-3 py-1.5 text-center font-sans text-emerald-600 font-bold">Schalter</td>
                                                        <td className="px-3 py-1.5 font-sans text-gray-700">Manueller Vorheiz-Boost für den thermischen Estrich-Speicher</td>
                                                    </tr>
                                                    <tr>
                                                        <td className="px-3 py-1.5 font-bold text-emerald-800">switch.sharegy_brauchwasser_wp_boost</td>
                                                        <td className="px-3 py-1.5 text-center font-sans text-emerald-600 font-bold">Schalter</td>
                                                        <td className="px-3 py-1.5 font-sans text-gray-700">SG-Ready Warmwasser-Boost (PV / Günstigstrom)</td>
                                                    </tr>
                                                    <tr>
                                                        <td className="px-3 py-1.5 font-bold text-blue-800">number.sharegy_fbh_soll_raumtemperatur</td>
                                                        <td className="px-3 py-1.5 text-center font-sans text-blue-600 font-bold">Regler (18–24°C)</td>
                                                        <td className="px-3 py-1.5 font-sans text-gray-700">Ziel-Komfort-Raumtemperatur</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {haTab === "automations" && (
                                <div className="space-y-3">
                                    <p className="text-gray-600">
                                        Beispiel-Automation: Fußbodenheizung bei dynamischem Tiefpreis automatisch vorheizen und Wärme im Estrich puffern:
                                    </p>
                                    <pre className="bg-slate-900 text-green-400 p-3 rounded-lg font-mono text-[11px] overflow-x-auto">
{`alias: "Sharegy: Fußbodenheizung bei Tiefpreis boosten"
trigger:
  - platform: numeric_state
    entity_id: sensor.sharegy_borsenstrompreis
    below: 15.0 # unter 15 ct/kWh
condition:
  - condition: state
    entity_id: switch.sharegy_bidirektionale_steuerung
    state: "on"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.sharegy_fussbodenheizung_boost`}
                                    </pre>
                                </div>
                            )}

                            {haTab === "install" && (
                                <div className="space-y-3">
                                    <ol className="list-decimal list-inside space-y-2 text-gray-700 leading-relaxed">
                                        <li>Kopiere den Ordner <code className="bg-slate-100 px-1.5 py-0.5 rounded border border-slate-300 font-mono">plugins/homeassistant/custom_components/sharegy</code> in deinen Home Assistant Ordner <code className="bg-slate-100 px-1.5 py-0.5 rounded border border-slate-300 font-mono">config/custom_components/sharegy</code>.</li>
                                        <li>Starte Home Assistant neu.</li>
                                        <li>Öffne <strong>Einstellungen &rarr; Geräte & Dienste &rarr; Integration hinzufügen</strong> und wähle <strong>Sharegy HEMS</strong>.</li>
                                        <li>Füge dein persönliches Token ein (<code className="bg-slate-100 px-1 rounded font-mono">{primaryHome?.mqtt_token || "&lt;TOKEN&gt;"}</code>).</li>
                                    </ol>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* 6. SECTION: IOBROKER JAVASCRIPT & MQTT BROKER INTERFACE CARD */}
            <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
                <div className="p-5 bg-gradient-to-r from-slate-50 via-indigo-50/30 to-white border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center text-xl shadow-xs">
                            🔧
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-base font-bold text-gray-900">
                                    6. ioBroker Adapter & MQTT Schnittstelle (Messen & Steuern)
                                </h2>
                                <span className="text-[10px] font-bold px-2 py-0.5 bg-indigo-100 text-indigo-800 rounded-full border border-indigo-200">
                                    WSS & MQTT Dual-Mode
                                </span>
                            </div>

                            <p className="text-xs text-gray-500">
                                Bidirektionale Anbindung für ioBroker JavaScript, MQTT-Client Adapter, Node-RED und OpenTelemetry.
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
                                const text = `Host: ${mqttHost}\nPort: ${mqttPort}\nUser: ${mqttUser}\nPass: ${mqttPass}\nBase Topic: ${baseTopic}\nWSS URL: ${wsUrl}`;
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
                                        {t("interfaces.port", "Port (TCP / WSS)")}
                                    </div>
                                    <div className="font-mono text-xs font-semibold text-gray-900 flex items-center justify-between">
                                        <span>{mqttPort} (MQTT) / 443 (WSS)</span>
                                        <span className="text-[10px] px-1.5 py-0.5 bg-emerald-100 text-emerald-700 font-semibold rounded">
                                            {t("common.active", "Aktiv")}
                                        </span>
                                    </div>
                                </div>

                                <div className="bg-slate-50 border border-slate-200/80 p-3.5 rounded-xl">
                                    <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">
                                        {t("interfaces.username", "Benutzername / Token")}
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
                                        { id: "iobroker_wss", label: "🔧 ioBroker JavaScript Bridge (WSS Bevorzugt)" },
                                        { id: "iobroker_mqtt", label: "📡 ioBroker MQTT Client Adapter" },
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
                                    {guideTab === "iobroker_wss" && (
                                        <div className="space-y-3">
                                            <div className="p-3 bg-indigo-50/70 border border-indigo-200 rounded-xl text-indigo-900 flex items-start gap-2.5">
                                                <span className="text-base">🚀</span>
                                                <div>
                                                    <div className="font-bold">WSS Outbound Bridge (Empfohlen)</div>
                                                    <div className="text-[11px] text-indigo-800">
                                                        Verbindet sich über den ioBroker JavaScript Adapter direkt mit Sharegy WSS (Port 443). Erstellt automatisch Datenpunkte unter <code className="bg-white px-1 rounded font-mono">0_userdata.0.sharegy.*</code> für bidirektionales Messen & Steuern mit 15-Minuten Fail-Safe Schutz.
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="flex justify-between items-center">
                                                <span className="font-bold text-gray-800">Skript-Vorlage (sharegy_iobroker_bridge.js):</span>
                                                <button
                                                    onClick={() => safeCopy(`// Sharegy ioBroker Bridge\nconst HOME_TOKEN = "${primaryHome?.mqtt_token || "DEIN_TOKEN"}";\n// Siehe vollständiges Skript im Repository plugins/iobroker/sharegy_iobroker_bridge.js`, "iobroker_snippet")}
                                                    className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-[11px] font-bold cursor-pointer"
                                                >
                                                    {copiedKey === "iobroker_snippet" ? "✓ Kopiert" : "📋 Skript kopieren"}
                                                </button>
                                            </div>

                                            <pre className="bg-slate-900 text-green-400 p-2.5 rounded-lg font-mono text-[11px] overflow-x-auto">
{`const CONFIG = {
    HOME_TOKEN: "${primaryHome?.mqtt_token || "<TOKEN>"}",
    CONNECTION_MODE: "WSS", // 'WSS' (Bevorzugt) oder 'MQTT'
    WSS_HOST: "wss://${window.location.host || "sharegy.de"}",
    ROOT_PATH: "0_userdata.0.sharegy",
    TELEMETRY_INTERVAL_MS: 10000
};`}
                                            </pre>
                                        </div>
                                    )}

                                    {guideTab === "iobroker_mqtt" && (
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
                                        <div className="space-y-1.5 text-gray-600">
                                            <p>{t("interfaces.nodered_step_1", "1. Verwende in Node-RED oder Tasmota einen standardmäßigen MQTT Out Node.")}</p>
                                            <p>{t("interfaces.nodered_step_2", "2. Konfiguriere den Broker mit deinen Zugangsdaten.")}</p>
                                            <p>{t("interfaces.nodered_step_3", "3. Sende JSON-Nutzdaten an dein Basis-Topic.")}</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* 7. SECTION: SMART METER GATEWAYS & WMSB INGEST (§ 42B ENWG) */}
            <div className="bg-white border border-emerald-200/80 rounded-2xl shadow-xs overflow-hidden ring-1 ring-emerald-100">
                <div className="p-5 bg-gradient-to-r from-emerald-50/80 via-teal-50/30 to-white border-b border-emerald-200/80 flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center text-xl shadow-xs">
                            🏢
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-base font-bold text-gray-900">
                                    {t("interfaces.wmsb_title", "7. Smart Meter Gateways, wMSB & Eichrechtliches Messwesen")}
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
                                <div className="text-gray-500 text-[11px]">{t("interfaces.gmsb_han_desc", "BSI TR-03109-1 konforme Erfassung lokaler Smart Meter Gateways.")}</div>
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
