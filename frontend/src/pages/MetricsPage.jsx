/*
# src/pages/MetricsPage.jsx
*/

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../api/client";
import DeviceChartModal from "../components/device/DeviceChartModal";

const CANONICAL_UNITS = {
    power: "W",
    active_power: "W",
    p_total: "W",
    p: "W",
    w: "W",
    watt: "W",
    pv_power: "W",
    pv_power_w: "W",
    load_power: "W",
    load_power_w: "W",
    grid_power: "W",
    grid_power_w: "W",
    battery_power: "W",
    battery_power_w: "W",
    battery_w: "W",
    apower: "W",
    a_act_power: "W",
    b_act_power: "W",
    c_act_power: "W",
    value: "W",
    val: "W",
    energy: "kWh",
    energy_kwh: "kWh",
    energy_wh: "Wh",
    energy_in: "kWh",
    energy_out: "kWh",
    total_energy: "kWh",
    total_energy_kwh: "kWh",
    total_charge: "kWh",
    total_discharge: "kWh",
    total_yield: "kWh",
    daily_yield: "kWh",
    a_total_energy: "Wh",
    b_total_energy: "Wh",
    c_total_energy: "Wh",
    voltage: "V",
    battery_voltage: "V",
    grid_voltage: "V",
    a_voltage: "V",
    b_voltage: "V",
    c_voltage: "V",
    current: "A",
    battery_current: "A",
    grid_current: "A",
    a_current: "A",
    b_current: "A",
    c_current: "A",
    soc: "%",
    battery_soc: "%",
    soh: "%",
    battery_level: "%",
    humidity: "%",
    frequency: "Hz",
    grid_frequency: "Hz",
    temperature: "°C",
    temp: "°C",
    device_temp: "°C",
    battery_temp: "°C",
};

function getMetricMeta(rawKey, givenUnit, config = {}, t = (k, d) => d) {
    const k = (rawKey || "").trim().toLowerCase();

    // 1. Zuerst exakte oder musterbasierte SI-Einheit für den konkreten Kanal bestimmen
    let unit = "";
    if (CANONICAL_UNITS[k]) {
        unit = (givenUnit && givenUnit.trim()) || CANONICAL_UNITS[k];
    } else if (k.includes("voltage") || k.includes("volt") || k.includes("spannung")) {
        unit = (givenUnit && givenUnit.trim()) || "V";
    } else if (k.includes("current") || k.includes("strom") || k.includes("amper")) {
        unit = (givenUnit && givenUnit.trim()) || "A";
    } else if (k.includes("frequency") || k.includes("freq") || k.includes("frequenz")) {
        unit = (givenUnit && givenUnit.trim()) || "Hz";
    } else if (k.includes("temp") || k.includes("celsius")) {
        unit = (givenUnit && givenUnit.trim()) || "°C";
    } else if (k.includes("soc") || k.includes("soh") || k.includes("humidity") || k.includes("feuchte") || k.includes("level")) {
        unit = (givenUnit && givenUnit.trim()) || "%";
    } else if (k.includes("energy") || k.includes("yield") || k.includes("ertrag") || k.includes("total")) {
        unit = (givenUnit && givenUnit.trim()) || (k.includes("wh") && !k.includes("kwh") ? "Wh" : "kWh");
    } else if (k.includes("power") || k.includes("watt") || k.includes("leistung")) {
        unit = (givenUnit && givenUnit.trim()) || (k.includes("kw") && !k.includes("kwh") ? "kW" : "W");
    } else if (givenUnit && givenUnit.trim()) {
        unit = givenUnit.trim();
    } else if (k === "value" || k === "val" || k === "main") {
        unit = config?.metric_definition?.unit || "W";
    }

    let icon = "📊";
    if (unit === "W" || unit === "kW" || k.includes("power") || k.includes("watt")) {
        icon = "🔌";
    } else if (unit === "kWh" || unit === "Wh" || k.includes("energy") || k.includes("yield")) {
        icon = "📊";
    } else if (unit === "V" || k.includes("voltage") || k.includes("spannung")) {
        icon = "⚡";
    } else if (unit === "A" || k.includes("current") || k.includes("strom")) {
        icon = "🌊";
    } else if (unit === "%" || k.includes("soc") || k.includes("level")) {
        icon = "🔋";
    } else if (unit === "Hz" || k.includes("freq")) {
        icon = "📻";
    } else if (unit === "°C" || k.includes("temp")) {
        icon = "🌡️";
    }

    let fallbackLabel = rawKey;
    if (k === "value" || k === "val") {
        if (unit === "V") fallbackLabel = t("metric_definitions.voltage", "Netzspannung");
        else if (unit === "A") fallbackLabel = t("metric_definitions.current", "Stromstärke");
        else if (unit === "kWh" || unit === "Wh") fallbackLabel = t("metric_definitions.energy", "Zählerstand / Energie");
        else if (unit === "Hz") fallbackLabel = t("metric_definitions.frequency", "Netzfrequenz");
        else if (unit === "°C") fallbackLabel = t("metric_definitions.temperature", "Temperatur");
        else if (unit === "%") fallbackLabel = t("metric_definitions.soc", "Ladezustand (SoC)");
        else fallbackLabel = config?.metric_definition?.name || t("metric_definitions.power", "Wirkleistung");
    } else if (k === "power" || k === "active_power" || k === "apower" || k === "p_total") {
        fallbackLabel = t("metric_definitions.power", "Wirkleistung");
    } else if (k === "a_act_power") {
        fallbackLabel = t("metric_definitions.a_act_power", "Wirkleistung L1");
    } else if (k === "b_act_power") {
        fallbackLabel = t("metric_definitions.b_act_power", "Wirkleistung L2");
    } else if (k === "c_act_power") {
        fallbackLabel = t("metric_definitions.c_act_power", "Wirkleistung L3");
    } else if (k === "grid_power" || k === "grid_power_w") {
        fallbackLabel = t("metric_definitions.grid_power", "Netzleistung");
    } else if (k === "pv_power" || k === "pv_power_w") {
        fallbackLabel = t("metric_definitions.pv_power", "PV-Erzeugung");
    } else if (k === "battery_power" || k === "battery_power_w" || k === "battery_w") {
        fallbackLabel = t("metric_definitions.battery_power", "Batterieleistung");
    } else if (k === "load_power" || k === "load_power_w") {
        fallbackLabel = t("metric_definitions.load_power", "Hauslast");
    } else if (k === "energy" || k === "energy_kwh" || k === "energy_wh" || k === "total_energy" || k === "total_energy_kwh") {
        fallbackLabel = t("metric_definitions.energy", "Zählerstand / Energie");
    } else if (k === "a_total_energy") {
        fallbackLabel = t("metric_definitions.a_total_energy", "Energie L1");
    } else if (k === "b_total_energy") {
        fallbackLabel = t("metric_definitions.b_total_energy", "Energie L2");
    } else if (k === "c_total_energy") {
        fallbackLabel = t("metric_definitions.c_total_energy", "Energie L3");
    } else if (k === "voltage" || k === "grid_voltage") {
        fallbackLabel = t("metric_definitions.voltage", "Netzspannung");
    } else if (k === "battery_voltage") {
        fallbackLabel = t("metric_definitions.battery_voltage", "Batteriespannung");
    } else if (k === "a_voltage") {
        fallbackLabel = t("metric_definitions.a_voltage", "Spannung L1");
    } else if (k === "b_voltage") {
        fallbackLabel = t("metric_definitions.b_voltage", "Spannung L2");
    } else if (k === "c_voltage") {
        fallbackLabel = t("metric_definitions.c_voltage", "Spannung L3");
    } else if (k === "current" || k === "grid_current") {
        fallbackLabel = t("metric_definitions.current", "Stromstärke");
    } else if (k === "battery_current") {
        fallbackLabel = t("metric_definitions.battery_current", "Batteriestrom");
    } else if (k === "a_current") {
        fallbackLabel = t("metric_definitions.a_current", "Strom L1");
    } else if (k === "b_current") {
        fallbackLabel = t("metric_definitions.b_current", "Strom L2");
    } else if (k === "c_current") {
        fallbackLabel = t("metric_definitions.c_current", "Strom L3");
    } else if (k === "soc" || k === "battery_soc" || k === "battery_level") {
        fallbackLabel = t("metric_definitions.soc", "Ladezustand (SoC)");
    } else if (k === "soh") {
        fallbackLabel = t("metric_definitions.soh", "Batteriegesundheit (SoH)");
    } else if (k === "frequency" || k === "grid_frequency") {
        fallbackLabel = t("metric_definitions.frequency", "Netzfrequenz");
    } else if (k === "temperature" || k === "temp" || k === "device_temp" || k === "battery_temp") {
        fallbackLabel = t("metric_definitions.temperature", "Temperatur");
    } else if (k === "humidity") {
        fallbackLabel = t("metric_definitions.humidity", "Luftfeuchtigkeit");
    } else if (config?.metric_definition?.name) {
        fallbackLabel = config.metric_definition.name;
    }

    const label = t(`metric_definitions.${k}`, fallbackLabel);

    return { label, unit, icon };
}

export default function MetricsPage() {
    const { t } = useTranslation();
    const [searchTerm, setSearchTerm] = useState("");
    const [categoryFilter, setCategoryFilter] = useState("all");
    const [selectedDeviceForChart, setSelectedDeviceForChart] = useState(null);

    // 📡 Live Telemetrie & Geräte-Werte
    const devicesQuery = useQuery({
        queryKey: ["devices"],
        queryFn: () => apiFetch("/api/devices/"),
        refetchInterval: 5000,
    });

    const valuesQuery = useQuery({
        queryKey: ["device-dashboard-values"],
        queryFn: () => apiFetch("/api/devices/dashboard/"),
        refetchInterval: 3000,
    });

    const statusQuery = useQuery({
        queryKey: ["devices-status"],
        queryFn: () => apiFetch("/api/devices/status/"),
        refetchInterval: 5000,
    });

    const devices = useMemo(() => devicesQuery.data || [], [devicesQuery.data]);

    const statusMap = useMemo(() => {
        return Object.fromEntries(
            (statusQuery.data || []).map((s) => [s.id, s.status === "online"])
        );
    }, [statusQuery.data]);

    // Map dashboard values by device ID
    const valueMap = useMemo(() => {
        const map = {};
        if (Array.isArray(valuesQuery.data)) {
            valuesQuery.data.forEach((v) => {
                map[v.device] = v;
            });
        }
        return map;
    }, [valuesQuery.data]);

    // Flatten all active metric channels across all devices with stable sorting
    const channels = useMemo(() => {
        const list = [];
        devices.forEach((device) => {
            const config = device.config || {};
            const metricDef = config.metric_definition || {};
            const devValueEntry = valueMap[device.id] || {};
            const metricsObj = devValueEntry.metrics || {};

            const isOnline = statusMap[device.id] ?? false;

            const metricKeys = Object.keys(metricsObj);
            if (metricKeys.length > 0) {
                metricKeys.forEach((mKey) => {
                    const mData = metricsObj[mKey] || {};
                    const meta = getMetricMeta(mKey, mData.unit, config, t);

                    list.push({
                        deviceId: device.id,
                        deviceName: device.display_name || device.identifier,
                        identifier: device.identifier,
                        metricKey: mKey,
                        metricName: meta.label,
                        icon: meta.icon,
                        unit: meta.unit,
                        liveValue: mData.value !== undefined ? mData.value : null,
                        role: config.role?.key || "unknown",
                        roleLabel: config.role?.label || "Gerät",
                        room: config.room?.name || "-",
                        floor: config.floor?.name || "-",
                        lastSeen: device.last_seen,
                        isOnline,
                        device,
                    });
                });
            } else {
                const primaryKey = metricDef.key || "power";
                const meta = getMetricMeta(primaryKey, devValueEntry.unit || metricDef.unit, config, t);
                const liveValue = devValueEntry.value !== undefined ? devValueEntry.value : null;

                list.push({
                    deviceId: device.id,
                    deviceName: device.display_name || device.identifier,
                    identifier: device.identifier,
                    metricKey: primaryKey,
                    metricName: meta.label,
                    icon: meta.icon,
                    unit: meta.unit,
                    liveValue,
                    role: config.role?.key || "unknown",
                    roleLabel: config.role?.label || "Gerät",
                    room: config.room?.name || "-",
                    floor: config.floor?.name || "-",
                    lastSeen: device.last_seen,
                    isOnline,
                    device,
                });
            }
        });

        // Stabile Sortierung: nach Gerätename, dann nach Metrik-Schlüssel
        list.sort((a, b) => {
            const nameCmp = a.deviceName.localeCompare(b.deviceName);
            if (nameCmp !== 0) return nameCmp;
            return a.metricKey.localeCompare(b.metricKey);
        });

        return list;
    }, [devices, valueMap, statusMap, t]);

    // Categories
    const categories = [
        { key: "all", label: t("common.all", "Alle Kanäle"), icon: "⚡" },
        { key: "power", label: t("metric_definitions.power", "Leistung (W)"), icon: "🔌" },
        { key: "energy", label: t("metric_definitions.energy", "Energie (kWh)"), icon: "📊" },
        { key: "voltage", label: t("metric_definitions.voltage", "Spannung (V)"), icon: "⚡" },
        { key: "current", label: t("metric_definitions.current", "Stromstärke (A)"), icon: "🌊" },
        { key: "temperature", label: t("metric_definitions.temperature", "Temperatur (°C)"), icon: "🌡️" },
    ];

    const filteredChannels = useMemo(() => {
        return channels.filter((c) => {
            const matchesSearch =
                !searchTerm ||
                c.deviceName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                c.identifier.toLowerCase().includes(searchTerm.toLowerCase()) ||
                c.metricName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                c.room.toLowerCase().includes(searchTerm.toLowerCase());

            const matchesCategory =
                categoryFilter === "all" ||
                c.metricKey.toLowerCase().includes(categoryFilter) ||
                (categoryFilter === "power" && (c.unit === "W" || c.unit === "kW")) ||
                (categoryFilter === "energy" && (c.unit === "kWh" || c.unit === "Wh"));

            return matchesSearch && matchesCategory;
        });
    }, [channels, searchTerm, categoryFilter]);

    // Stats
    const totalChannels = channels.length;
    const onlineChannels = channels.filter((c) => c.isOnline).length;
    const activeSensors = new Set(channels.map((c) => c.deviceId)).size;

    return (
        <div className="p-6 space-y-6 max-w-7xl">
            {/* HEADER */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <span>📊</span> {t("metrics.title", "Messwerte & Kanäle")}
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">
                        {t("metrics.subtitle", "Live-Kanäle, SI-Einheiten, Sensoren und historische Zeitreihen.")}
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => {
                            devicesQuery.refetch();
                            valuesQuery.refetch();
                        }}
                        className="px-3.5 py-2 rounded-xl border border-gray-200 hover:bg-gray-50 text-sm font-medium text-gray-700 flex items-center gap-1.5 transition"
                    >
                        <span>🔄</span> {t("common.refresh", "Aktualisieren")}
                    </button>
                </div>
            </div>

            {/* KPI STATS CARDS */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-xs">
                    <div className="text-xs font-semibold uppercase text-gray-500 tracking-wider">
                        {t("metrics.active_channels", "Aktive Kanäle")}
                    </div>
                    <div className="text-3xl font-bold text-gray-900 mt-2">
                        {totalChannels}
                    </div>
                    <div className="text-xs text-emerald-600 font-medium mt-1">
                        ● {onlineChannels} {t("common.online", "Online")}
                    </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-xs">
                    <div className="text-xs font-semibold uppercase text-gray-500 tracking-wider">
                        {t("nav.all_devices", "Verbundene Geräte")}
                    </div>
                    <div className="text-3xl font-bold text-gray-900 mt-2">
                        {activeSensors}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                        MQTT & OpenTelemetry
                    </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-xs">
                    <div className="text-xs font-semibold uppercase text-gray-500 tracking-wider">
                        {t("common.status", "Telemetrie-Takt")}
                    </div>
                    <div className="text-3xl font-bold text-indigo-600 mt-2">
                        ~ 3s
                    </div>
                    <div className="text-xs text-indigo-500 font-medium mt-1">
                        ⚡ Echtzeit-Live-Stream
                    </div>
                </div>
            </div>

            {/* FILTER & SEARCH BAR */}
            <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-xs space-y-3">
                <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
                    <div className="relative w-full sm:w-80">
                        <input
                            type="text"
                            placeholder={t("metrics.search", "Kanal oder Gerät suchen...")}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-9 pr-3 py-2 border rounded-xl text-sm focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                        />
                        <span className="absolute left-3 top-2.5 text-gray-400 text-sm">🔍</span>
                    </div>

                    <div className="flex flex-wrap gap-1.5 w-full sm:w-auto">
                        {categories.map((cat) => (
                            <button
                                key={cat.key}
                                onClick={() => setCategoryFilter(cat.key)}
                                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 ${categoryFilter === cat.key
                                    ? "bg-indigo-600 text-white shadow-xs"
                                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                                    }`}
                            >
                                <span>{cat.icon}</span>
                                <span>{cat.label}</span>
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* CHANNELS TABLE */}
            <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-xs">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-gray-50 border-b text-xs font-semibold text-gray-500 uppercase tracking-wider">
                            <tr>
                                <th className="py-3 px-4">{t("common.status", "Status")}</th>
                                <th className="py-3 px-4">{t("metrics.table_device_sensor", "Gerät / Sensor")}</th>
                                <th className="py-3 px-4">{t("metrics.table_metric", "Messgröße")}</th>
                                <th className="py-3 px-4">{t("metrics.table_location", "Ort / Raum")}</th>
                                <th className="py-3 px-4 text-right">{t("metrics.table_current_value", "Aktueller Wert")}</th>
                                <th className="py-3 px-4 text-center">{t("metrics.table_actions", "Aktionen")}</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {filteredChannels.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="py-12 text-center text-gray-400">
                                        {t("common.no_data", "Keine Kanäle gefunden")}
                                    </td>
                                </tr>
                            ) : (
                                filteredChannels.map((channel, i) => (
                                    <tr key={`${channel.deviceId}-${channel.metricKey}-${i}`} className="hover:bg-slate-50/80 transition">
                                        {/* Status */}
                                        <td className="py-3.5 px-4 whitespace-nowrap">
                                            <span
                                                className={`inline-block w-2.5 h-2.5 rounded-full ${channel.isOnline
                                                    ? "bg-emerald-500 ring-4 ring-emerald-50"
                                                    : "bg-slate-300"
                                                    }`}
                                                title={channel.isOnline ? "Online" : "Offline"}
                                            />
                                        </td>

                                        {/* Device Name */}
                                        <td className="py-3.5 px-4 whitespace-nowrap">
                                            <div className="font-semibold text-gray-900">
                                                {channel.deviceName}
                                            </div>
                                            <div className="text-xs text-gray-400 font-mono">
                                                {channel.identifier}
                                            </div>
                                        </td>

                                        {/* Metric Type */}
                                        <td className="py-3.5 px-4 whitespace-nowrap">
                                            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700 text-xs font-medium">
                                                <span>{channel.icon || "📊"}</span>
                                                <span>{channel.metricName}</span>
                                            </div>
                                        </td>

                                        {/* Location */}
                                        <td className="py-3.5 px-4 whitespace-nowrap text-xs text-gray-600">
                                            <span>🏢 {channel.floor}</span>
                                            <span className="text-gray-300 mx-1.5">/</span>
                                            <span>🚪 {channel.room}</span>
                                        </td>

                                        {/* Live Value */}
                                        <td className="py-3.5 px-4 whitespace-nowrap text-right font-mono font-bold text-base">
                                            {channel.liveValue !== null && channel.liveValue !== undefined ? (
                                                <span className="text-gray-900">
                                                    {Number(channel.liveValue).toLocaleString("de-DE", { maximumFractionDigits: 1 })}{" "}
                                                    <span className="text-xs text-gray-500 font-normal">{channel.unit}</span>
                                                </span>
                                            ) : (
                                                <span className="text-gray-400 text-xs font-normal">-</span>
                                            )}
                                        </td>

                                        {/* Actions */}
                                        <td className="py-3.5 px-4 whitespace-nowrap text-center">
                                            <button
                                                onClick={() => setSelectedDeviceForChart(channel.device)}
                                                className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-indigo-50 text-slate-700 hover:text-indigo-600 text-xs font-semibold transition"
                                                title="Verlauf / Chart anzeigen"
                                            >
                                                📈 Verlauf
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* CHART MODAL */}
            {selectedDeviceForChart && (
                <DeviceChartModal
                    device={selectedDeviceForChart}
                    onClose={() => setSelectedDeviceForChart(null)}
                />
            )}
        </div>
    );
}
