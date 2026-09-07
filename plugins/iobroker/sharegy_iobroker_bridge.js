/**
 * ###############################################################################
 * 🚀 Sharegy HEMS ioBroker Bridge (v2.1.0)
 * Bidirektionales Messen & Steuern für ioBroker
 * 
 * Bevorzugte Methode: Verschlüsseltes Outbound-WSS über Port 443 (Firewall-sicher)
 * Alternative Methode: MQTT Broker (mqtt.sharegy.de:1883)
 * ###############################################################################
 */

// ===============================================================================
// 🔧 KONFIGURATION
// ===============================================================================
const CONFIG = {
    // Trage hier dein persönliches Sharegy Home-Token ein:
    HOME_TOKEN: "DEIN_SHAREGY_HOME_TOKEN_HIER_EINTRAGEN",

    // Verbindungsmodus: 'WSS' (Empfohlen) oder 'MQTT'
    CONNECTION_MODE: "WSS",

    // WSS-Server Endpunkt (Port 443 HTTPS/WSS)
    WSS_HOST: "wss://sharegy.de",

    // MQTT Einstellungen (nur falls CONNECTION_MODE === 'MQTT')
    MQTT_INSTANCE: "mqtt-client.0",
    MQTT_TOPIC_PREFIX: "h",

    // Lokaler ioBroker Datenpunkt-Pfad
    ROOT_PATH: "0_userdata.0.sharegy",

    // Telemetrie-Sendeintervall in Millisekunden (z. B. alle 10 Sekunden)
    TELEMETRY_INTERVAL_MS: 10000,

    // Watchdog Timeout (15 Minuten Fail-Safe)
    FAILSAFE_TIMEOUT_MS: 15 * 60 * 1000,

    // Quell-Datenpunkte für Inbound-Telemetrie (optional - anpassen an deine IDs):
    SOURCE_DATAPOINTS: {
        pv_power: "",      // z. B. "fronius.0.powerflow.P_PV"
        grid_power: "",    // z. B. "shelly.0.shellypro3em#1.EMData.TotalActivePower"
        battery_soc: "",   // z. B. "sonnen.0.status.userSoc"
        room_temp: "",     // z. B. "zigbee.0.living_room.temperature"
    }
};

// ===============================================================================
// 📦 DATENPUNKT-STRUKTUR INITIALISIEREN
// ===============================================================================
const STATES = [
    // 🎛️ STEUERUNG & AKTORIK (Outbound & Schalter)
    { id: "control.bidirectional_enabled", name: "Bidirektionale Steuerung Aktiv", type: "boolean", role: "switch", def: true, write: true },
    { id: "control.floor_heating_boost", name: "Fußbodenheizung Vorheiz-Boost", type: "boolean", role: "switch", def: false, write: true },
    { id: "control.floor_heating_target_temp", name: "FBH Soll-Raumtemperatur", type: "number", role: "value.temperature", unit: "°C", def: 21.0, write: true },
    { id: "control.bwwp_boost", name: "Brauchwasser WP SG-Ready Boost", type: "boolean", role: "switch", def: false, write: true },
    { id: "control.wallbox_max_current", name: "Wallbox Max Ladestrom", type: "number", role: "value.current", unit: "A", def: 16, write: true },

    // 📈 TELEMETRIE (Inbound von lokalen Sensoren)
    { id: "telemetry.pv_power", name: "Solar PV Leistung", type: "number", role: "value.power", unit: "W", def: 0, write: true },
    { id: "telemetry.grid_power", name: "Netzleistung (Bezug +, Einspeisung -)", type: "number", role: "value.power", unit: "W", def: 0, write: true },
    { id: "telemetry.battery_soc", name: "Batterie-Ladestand (SoC)", type: "number", role: "value.battery", unit: "%", def: 50, write: true },
    { id: "telemetry.room_temp", name: "Ist-Raumtemperatur", type: "number", role: "value.temperature", unit: "°C", def: 21.0, write: true },

    // 🌡️ STATUS & BERECHNUNGEN (Von Sharegy empfangen)
    { id: "status.flow_temp_setpoint", name: "DIN EN 12831 Vorlauftemperatur-Sollwert", type: "number", role: "value.temperature", unit: "°C", def: 30.0, write: false },
    { id: "status.screed_soc", name: "Estrich-Speicher Ladestand (SoC)", type: "number", role: "value", unit: "%", def: 50.0, write: false },
    { id: "status.operating_mode", name: "Aktueller Betriebsmodus", type: "string", role: "text", def: "STANDBY", write: false },
    { id: "status.spot_price_ct", name: "Dynamischer Strompreis", type: "number", role: "value", unit: "ct/kWh", def: 15.0, write: false },
    { id: "status.failsafe_active", name: "Fail-Safe Notbetrieb Aktiv", type: "boolean", role: "indicator", def: false, write: false },
    { id: "status.connected", name: "Verbindung zu Sharegy Aktiv", type: "boolean", role: "indicator.connected", def: false, write: false },
    { id: "status.last_heartbeat", name: "Letzter Herzschlag", type: "string", role: "date", def: "", write: false }
];

async function initStates() {
    for (const s of STATES) {
        const fullId = `${CONFIG.ROOT_PATH}.${s.id}`;
        await createStateAsync(fullId, {
            name: s.name,
            type: s.type,
            role: s.role,
            unit: s.unit || undefined,
            def: s.def,
            read: true,
            write: s.write !== false
        });
    }
    log(`[Sharegy Bridge] Alle Datenpunkte unter ${CONFIG.ROOT_PATH} erfolgreich initialisiert.`, "info");
}

// ===============================================================================
// 🌐 WSS WEBSOCKET CLIENT (BEVORZUGTE METHODE)
// ===============================================================================
let ws = null;
let lastHeartbeat = Date.now();
let reconnectTimer = null;

function connectWss() {
    if (CONFIG.CONNECTION_MODE !== "WSS") return;

    try {
        const WebSocket = require("ws");
        const url = `${CONFIG.WSS_HOST}/ws/energy/${CONFIG.HOME_TOKEN}/`;

        log(`[Sharegy WSS] Verbinde mit ${url}...`, "info");
        ws = new WebSocket(url);

        ws.on("open", () => {
            log("[Sharegy WSS] Erfolgreich verbunden!", "info");
            setState(`${CONFIG.ROOT_PATH}.status.connected`, true, true);
            setState(`${CONFIG.ROOT_PATH}.status.failsafe_active`, false, true);
            lastHeartbeat = Date.now();
        });

        ws.on("message", (raw) => {
            try {
                const msg = JSON.parse(raw.toString());
                handleIncomingSharegyMessage(msg);
            } catch (err) {
                log(`[Sharegy WSS] Fehler beim Parsen der Nachricht: ${err}`, "warn");
            }
        });

        ws.on("close", () => {
            log("[Sharegy WSS] Verbindung geschlossen. Reconnect in 5s...", "warn");
            setState(`${CONFIG.ROOT_PATH}.status.connected`, false, true);
            scheduleReconnect();
        });

        ws.on("error", (err) => {
            log(`[Sharegy WSS] WebSocket Fehler: ${err.message || err}`, "error");
        });

    } catch (e) {
        log(`[Sharegy WSS] ws-Modul nicht verfügbar oder Fehler: ${e}`, "error");
        scheduleReconnect();
    }
}

function scheduleReconnect() {
    if (reconnectTimer) clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(connectWss, 5000);
}

// ===============================================================================
// 📥 NACHRICHTEN VON SHAREGY VERARBEITEN (STEUERBEFEHLE & SOLLWERTE)
// ===============================================================================
function handleIncomingSharegyMessage(msg) {
    lastHeartbeat = Date.now();
    setState(`${CONFIG.ROOT_PATH}.status.last_heartbeat`, new Date().toISOString(), true);

    const isBidiEnabled = getState(`${CONFIG.ROOT_PATH}.control.bidirectional_enabled`)?.val ?? true;

    // 1. Status & Sollwert Updates verarbeiten
    if (msg.flow_temp_setpoint_c !== undefined) {
        setState(`${CONFIG.ROOT_PATH}.status.flow_temp_setpoint`, Number(msg.flow_temp_setpoint_c), true);
    }
    if (msg.screed_soc_pct !== undefined) {
        setState(`${CONFIG.ROOT_PATH}.status.screed_soc`, Number(msg.screed_soc_pct), true);
    }
    if (msg.mode !== undefined) {
        setState(`${CONFIG.ROOT_PATH}.status.operating_mode`, String(msg.mode), true);
    }
    if (msg.spot_price_ct !== undefined) {
        setState(`${CONFIG.ROOT_PATH}.status.spot_price_ct`, Number(msg.spot_price_ct), true);
    }

    // 2. Steuerbefehle (nur ausführen wenn Bidirektionale Steuerung aktiv ist)
    if (!isBidiEnabled) {
        log("[Sharegy Bridge] Steuerbefehl ignoriert: Bidirektionale Steuerung ist pausiert.", "debug");
        return;
    }

    if (msg.action === "FLOOR_HEATING_BOOST" || msg.floor_heating_boost !== undefined) {
        const targetState = Boolean(msg.floor_heating_boost ?? (msg.action === "FLOOR_HEATING_BOOST"));
        setState(`${CONFIG.ROOT_PATH}.control.floor_heating_boost`, targetState, true);
        log(`[Sharegy Steuerung] FBH Boost geschaltet: ${targetState}`, "info");
    }

    if (msg.target_room_temp_c !== undefined) {
        setState(`${CONFIG.ROOT_PATH}.control.floor_heating_target_temp`, Number(msg.target_room_temp_c), true);
    }

    if (msg.bwwp_boost !== undefined) {
        setState(`${CONFIG.ROOT_PATH}.control.bwwp_boost`, Boolean(msg.bwwp_boost), true);
        log(`[Sharegy Steuerung] BWWP SG-Ready geschaltet: ${msg.bwwp_boost}`, "info");
    }
}

// ===============================================================================
// 📤 TELEMETRIE AN SHAREGY SENDEN
// ===============================================================================
function sendTelemetry() {
    // Werte aus Datenpunkten oder Quell-IDs lesen
    const pvPower = CONFIG.SOURCE_DATAPOINTS.pv_power ? (getState(CONFIG.SOURCE_DATAPOINTS.pv_power)?.val || 0) : (getState(`${CONFIG.ROOT_PATH}.telemetry.pv_power`)?.val || 0);
    const gridPower = CONFIG.SOURCE_DATAPOINTS.grid_power ? (getState(CONFIG.SOURCE_DATAPOINTS.grid_power)?.val || 0) : (getState(`${CONFIG.ROOT_PATH}.telemetry.grid_power`)?.val || 0);
    const batterySoc = CONFIG.SOURCE_DATAPOINTS.battery_soc ? (getState(CONFIG.SOURCE_DATAPOINTS.battery_soc)?.val || 50) : (getState(`${CONFIG.ROOT_PATH}.telemetry.battery_soc`)?.val || 50);
    const roomTemp = CONFIG.SOURCE_DATAPOINTS.room_temp ? (getState(CONFIG.SOURCE_DATAPOINTS.room_temp)?.val || 21.0) : (getState(`${CONFIG.ROOT_PATH}.telemetry.room_temp`)?.val || 21.0);

    const payload = {
        type: "telemetry",
        timestamp: new Date().toISOString(),
        pv_power_w: Number(pvPower),
        grid_power_w: Number(gridPower),
        battery_soc_pct: Number(batterySoc),
        room_temp_c: Number(roomTemp)
    };

    if (CONFIG.CONNECTION_MODE === "WSS" && ws && ws.readyState === 1) {
        ws.send(JSON.stringify(payload));
    } else if (CONFIG.CONNECTION_MODE === "MQTT") {
        sendTo(CONFIG.MQTT_INSTANCE, "sendMessage", {
            topic: `${CONFIG.MQTT_TOPIC_PREFIX}/${CONFIG.HOME_TOKEN}/telemetry`,
            message: JSON.stringify(payload)
        });
    }
}

// ===============================================================================
// 🛡️ 15-MINUTEN FAIL-SAFE WATCHDOG
// ===============================================================================
function checkWatchdog() {
    const elapsed = Date.now() - lastHeartbeat;
    if (elapsed > CONFIG.FAILSAFE_TIMEOUT_MS) {
        const wasFailSafe = getState(`${CONFIG.ROOT_PATH}.status.failsafe_active`)?.val;
        if (!wasFailSafe) {
            log("[Sharegy Watchdog] Kein Signal seit >15 Min! Aktiviere lokalen Notbetrieb/Komfort-Rückfall.", "warn");
            setState(`${CONFIG.ROOT_PATH}.status.failsafe_active`, true, true);
            // Automatisch auf Normalbetrieb zurückschalten
            setState(`${CONFIG.ROOT_PATH}.control.floor_heating_boost`, false, true);
            setState(`${CONFIG.ROOT_PATH}.control.bwwp_boost`, false, true);
        }
    }
}

// ===============================================================================
// 🚀 START
// ===============================================================================
async function main() {
    await initStates();

    if (CONFIG.CONNECTION_MODE === "WSS") {
        connectWss();
    }

    // Regelmäßiges Senden von Telemetrie
    setInterval(sendTelemetry, CONFIG.TELEMETRY_INTERVAL_MS);

    // Watchdog Überprüfung alle 60 Sekunden
    setInterval(checkWatchdog, 60000);

    log(`[Sharegy Bridge] Erfolgreich gestartet (Modus: ${CONFIG.CONNECTION_MODE}).`, "info");
}

main();
