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

function fallbackByUnit(unit, t) {
    if (unit === "%") return t("metric_definitions.soc", "Ladezustand (SoC)");
    if (unit === "V") return t("metric_definitions.voltage", "Netzspannung");
    if (unit === "A") return t("metric_definitions.current", "Stromstärke");
    if (unit === "kWh" || unit === "Wh") return t("metric_definitions.energy", "Zählerstand / Energie");
    if (unit === "Hz") return t("metric_definitions.frequency", "Netzfrequenz");
    if (unit === "°C") return t("metric_definitions.temperature", "Temperatur");
    return t("metric_definitions.power", "Wirkleistung");
}

const VALID_UNITS = {
    voltage: ["V", "kV", "mV", "v"],
    current: ["A", "mA", "kA", "a"],
    frequency: ["Hz", "kHz", "hz"],
    temperature: ["°C", "C", "c", "K", "°F"],
    soc: ["%", "pct"],
    energy: ["kWh", "Wh", "MWh", "kwh", "wh"],
    power: ["W", "kW", "MW", "w", "kw"],
};

function getMetricMeta(rawKey, givenUnit, config = {}, t = (k, d) => d) {
    const k = (rawKey || "").trim().toLowerCase();
    const cfgDef = config?.metric_definition;
    const cfgUnit = cfgDef?.unit?.trim() || "";
    const cfgKey = cfgDef?.key?.toLowerCase()?.trim() || "";
    const cfgName = cfgDef?.name?.trim() || "";
    const u = (givenUnit || "").trim();

    // 1. Zuerst exakte oder musterbasierte SI-Einheit für den konkreten Kanal bestimmen
    let unit = "";
    if (k === "value" || k === "val" || k === "main" || k === "") {
        if (cfgUnit) {
            unit = cfgUnit;
        } else if (cfgKey && CANONICAL_UNITS[cfgKey]) {
            unit = CANONICAL_UNITS[cfgKey];
        } else if (u && u !== "W" && u !== "w") {
            unit = u;
        } else {
            unit = "W";
        }
    } else if (k.includes("voltage") || k.includes("volt") || k.includes("spannung")) {
        unit = VALID_UNITS.voltage.includes(u) ? u : "V";
    } else if (k.includes("current") || k.includes("strom") || k.includes("amper")) {
        unit = VALID_UNITS.current.includes(u) ? u : "A";
    } else if (k.includes("frequency") || k.includes("freq") || k.includes("frequenz")) {
        unit = VALID_UNITS.frequency.includes(u) ? u : "Hz";
    } else if (k.includes("temp") || k.includes("celsius")) {
        unit = VALID_UNITS.temperature.includes(u) ? u : "°C";
    } else if (k.includes("soc") || k.includes("soh") || k.includes("humidity") || k.includes("feuchte") || k.includes("level")) {
        unit = VALID_UNITS.soc.includes(u) ? u : "%";
    } else if (k.includes("energy") || k.includes("yield") || k.includes("ertrag") || k.includes("total")) {
        unit = VALID_UNITS.energy.includes(u) ? u : (k.includes("wh") && !k.includes("kwh") ? "Wh" : "kWh");
    } else if (k.includes("power") || k.includes("watt") || k.includes("leistung")) {
        unit = VALID_UNITS.power.includes(u) ? u : (k.includes("kw") && !k.includes("kwh") ? "kW" : "W");
    } else if (CANONICAL_UNITS[k]) {
        unit = CANONICAL_UNITS[k];
    } else if (cfgUnit) {
        unit = cfgUnit;
    } else if (u) {
        unit = u;
    } else {
        unit = "W";
    }

    // 2. Passendes Icon
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

    // 3. Eindeutiges, sauberes Label bestimmen
    let label = "";

    if (k === "value" || k === "val" || k === "main" || k === "") {
        // Generischer Key -> Schau zuerst auf die konfigurierte MetricDefinition
        if (cfgKey && cfgKey !== "value" && cfgKey !== "val") {
            label = t(`metric_definitions.${cfgKey}`, cfgName || fallbackByUnit(unit, t));
        } else if (cfgName && cfgName.toLowerCase() !== "value" && cfgName.toLowerCase() !== "val") {
            label = cfgName;
        } else {
            label = fallbackByUnit(unit, t);
        }
    } else {
        // Spezifischer Metrik-Key vorhanden
        if (k === "power" || k === "active_power" || k === "apower" || k === "p_total") label = t("metric_definitions.power", "Wirkleistung");
        else if (k === "a_act_power") label = t("metric_definitions.a_act_power", "Wirkleistung L1");
        else if (k === "b_act_power") label = t("metric_definitions.b_act_power", "Wirkleistung L2");
        else if (k === "c_act_power") label = t("metric_definitions.c_act_power", "Wirkleistung L3");
        else if (k === "grid_power" || k === "grid_power_w") label = t("metric_definitions.grid_power", "Netzleistung");
        else if (k === "pv_power" || k === "pv_power_w") label = t("metric_definitions.pv_power", "PV-Erzeugung");
        else if (k === "battery_power" || k === "battery_power_w" || k === "battery_w") label = t("metric_definitions.battery_power", "Batterieleistung");
        else if (k === "load_power" || k === "load_power_w") label = t("metric_definitions.load_power", "Hauslast");
        else if (k === "energy" || k === "energy_kwh" || k === "energy_wh" || k === "total_energy" || k === "total_energy_kwh") label = t("metric_definitions.energy", "Zählerstand / Energie");
        else if (k === "a_total_energy") label = t("metric_definitions.a_total_energy", "Energie L1");
        else if (k === "b_total_energy") label = t("metric_definitions.b_total_energy", "Energie L2");
        else if (k === "c_total_energy") label = t("metric_definitions.c_total_energy", "Energie L3");
        else if (k === "voltage" || k === "grid_voltage") label = t("metric_definitions.voltage", "Netzspannung");
        else if (k === "battery_voltage") label = t("metric_definitions.battery_voltage", "Batteriespannung");
        else if (k === "a_voltage") label = t("metric_definitions.a_voltage", "Spannung L1");
        else if (k === "b_voltage") label = t("metric_definitions.b_voltage", "Spannung L2");
        else if (k === "c_voltage") label = t("metric_definitions.c_voltage", "Spannung L3");
        else if (k === "current" || k === "grid_current") label = t("metric_definitions.current", "Stromstärke");
        else if (k === "battery_current") label = t("metric_definitions.battery_current", "Batteriestrom");
        else if (k === "a_current") label = t("metric_definitions.a_current", "Strom L1");
        else if (k === "b_current") label = t("metric_definitions.b_current", "Strom L2");
        else if (k === "c_current") label = t("metric_definitions.c_current", "Strom L3");
        else if (k === "soc" || k === "battery_soc" || k === "battery_level") label = t("metric_definitions.soc", "Ladezustand (SoC)");
        else if (k === "soh") label = t("metric_definitions.soh", "Batteriegesundheit (SoH)");
        else if (k === "frequency" || k === "grid_frequency") label = t("metric_definitions.frequency", "Netzfrequenz");
        else if (k === "temperature" || k === "temp" || k === "device_temp" || k === "battery_temp") label = t("metric_definitions.temperature", "Temperatur");
        else if (k === "humidity") label = t("metric_definitions.humidity", "Luftfeuchtigkeit");
        else label = t(`metric_definitions.${k}`, cfgName || rawKey);
    }

    return { label, unit, icon };
}

export default function MetricsPage() {
    const { t } = useTranslation();
    const [searchTerm, setSearchTerm] = useState("");
    const [categoryFilter, setCategoryFilter] = useState("all");
    const [selectedDeviceId, setSelectedDeviceId] = useState("all");
    const [selectedDeviceForChart, setSelectedDeviceForChart] = useState(null);

    // Sortierung
    const [sortField, setSortField] = useState("deviceName");
    const [sortDir, setSortDir] = useState("asc");

    // Paginierung (Default 25)
    const [pageSize, setPageSize] = useState(25);
    const [currentPage, setCurrentPage] = useState(1);

    // 📡 Live Telemetrie & Geräte-Werte (mit Fast-Cache)
    const devicesQuery = useQuery({
        queryKey: ["devices"],
        queryFn: () => apiFetch("/api/devices/"),
        staleTime: 30000,
        placeholderData: (prev) => prev,
    });

    const valuesQuery = useQuery({
        queryKey: ["device-dashboard-values"],
        queryFn: () => apiFetch("/api/devices/dashboard/"),
        refetchInterval: 10000,
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

    // Flatten all active metric channels across all devices
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

        return list;
    }, [devices, valueMap, statusMap, t]);

    // Distinct devices for filter dropdown
    const deviceOptions = useMemo(() => {
        const map = new Map();
        channels.forEach((c) => {
            if (!map.has(c.deviceId)) {
                map.set(c.deviceId, { id: c.deviceId, name: c.deviceName, count: 1 });
            } else {
                map.get(c.deviceId).count += 1;
            }
        });
        return Array.from(map.values()).sort((a, b) => a.name.localeCompare(b.name, "de"));
    }, [channels]);

    // Categories
    const categories = [
        { key: "all", label: t("common.all", "Alle Kanäle"), icon: "⚡" },
        { key: "power", label: t("metric_definitions.power", "Leistung (W)"), icon: "🔌" },
        { key: "energy", label: t("metric_definitions.energy", "Energie (kWh)"), icon: "📊" },
        { key: "voltage", label: t("metric_definitions.voltage", "Spannung (V)"), icon: "⚡" },
        { key: "current", label: t("metric_definitions.current", "Stromstärke (A)"), icon: "🌊" },
        { key: "temperature", label: t("metric_definitions.temperature", "Temperatur (°C)"), icon: "🌡️" },
    ];

    // Filter
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

            const matchesDevice = selectedDeviceId === "all" || String(c.deviceId) === String(selectedDeviceId);

            return matchesSearch && matchesCategory && matchesDevice;
        });
    }, [channels, searchTerm, categoryFilter, selectedDeviceId]);

    // Sortierung anwenden
    const sortedChannels = useMemo(() => {
        const list = [...filteredChannels];
        list.sort((a, b) => {
            let res = 0;
            if (sortField === "status") {
                res = (a.isOnline === b.isOnline ? 0 : a.isOnline ? -1 : 1);
            } else if (sortField === "deviceName") {
                res = a.deviceName.localeCompare(b.deviceName, "de");
            } else if (sortField === "metricName") {
                res = a.metricName.localeCompare(b.metricName, "de");
            } else if (sortField === "room") {
                res = `${a.floor}/${a.room}`.localeCompare(`${b.floor}/${b.room}`, "de");
            } else if (sortField === "liveValue") {
                const valA = a.liveValue !== null && a.liveValue !== undefined ? Number(a.liveValue) : -Infinity;
                const valB = b.liveValue !== null && b.liveValue !== undefined ? Number(b.liveValue) : -Infinity;
                res = valA - valB;
            }
            return sortDir === "asc" ? res : -res;
        });
        return list;
    }, [filteredChannels, sortField, sortDir]);

    // Paginierung berechnen
    const totalItems = sortedChannels.length;
    const isAll = pageSize >= 9999;
    const totalPages = isAll ? 1 : Math.max(1, Math.ceil(totalItems / pageSize));
    const safePage = Math.min(currentPage, totalPages);

    const paginatedChannels = useMemo(() => {
        if (isAll) return sortedChannels;
        const start = (safePage - 1) * pageSize;
        return sortedChannels.slice(start, start + pageSize);
    }, [sortedChannels, isAll, safePage, pageSize]);

    const handleSort = (field) => {
        if (sortField === field) {
            setSortDir(sortDir === "asc" ? "desc" : "asc");
        } else {
            setSortField(field);
            setSortDir("asc");
        }
    };

    const handleFilterChange = (setter, val) => {
        setter(val);
        setCurrentPage(1);
    };

    // Stats
    const totalChannels = channels.length;
    const onlineChannels = channels.filter((c) => c.isOnline).length;
    const activeSensors = new Set(channels.map((c) => c.deviceId)).size;

    const startIdx = isAll ? 1 : (safePage - 1) * pageSize + 1;
    const endIdx = isAll ? totalItems : Math.min(safePage * pageSize, totalItems);

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
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
                        type="button"
                        onClick={() => {
                            devicesQuery.refetch();
                            valuesQuery.refetch();
                            statusQuery.refetch();
                        }}
                        className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 border border-emerald-200/80 text-emerald-700 text-xs font-semibold hover:bg-emerald-100/70 transition shadow-2xs cursor-pointer"
                        title="Live-Telemetrie aktiv (Klicken für sofortigen Refetch)"
                    >
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                        </span>
                        <span>Live-Sync (~10s)</span>
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
                        Echtzeit
                    </div>
                    <div className="text-xs text-indigo-500 font-medium mt-1">
                        ⚡ WSS / HTTP Stream
                    </div>
                </div>
            </div>

            {/* FILTER & SEARCH BAR */}
            <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-xs space-y-3">
                <div className="flex flex-col lg:flex-row gap-3 items-stretch lg:items-center justify-between">
                    {/* Left: Search + Device Selector */}
                    <div className="flex flex-wrap sm:flex-nowrap items-center gap-2.5 flex-1 max-w-xl">
                        <div className="relative flex-1 min-w-[200px]">
                            <input
                                type="text"
                                placeholder={t("metrics.search", "Kanal, Gerät oder Raum suchen...")}
                                value={searchTerm}
                                onChange={(e) => handleFilterChange(setSearchTerm, e.target.value)}
                                className="w-full pl-9 pr-8 py-2 border border-gray-200 rounded-xl text-xs font-medium focus:outline-hidden focus:ring-2 focus:ring-indigo-500 bg-white shadow-2xs"
                            />
                            <span className="absolute left-3 top-2.5 text-gray-400 text-xs">🔍</span>
                            {searchTerm && (
                                <button
                                    type="button"
                                    onClick={() => handleFilterChange(setSearchTerm, "")}
                                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-xs"
                                >
                                    ✕
                                </button>
                            )}
                        </div>

                        {/* Device Selector */}
                        <div className="flex items-center gap-1.5 bg-white border border-gray-200 px-3 py-1.5 rounded-xl shadow-2xs shrink-0">
                            <span className="text-xs font-semibold text-gray-500">📟 Gerät:</span>
                            <select
                                value={selectedDeviceId}
                                onChange={(e) => handleFilterChange(setSelectedDeviceId, e.target.value)}
                                className="text-xs font-bold text-gray-800 bg-transparent border-none focus:outline-hidden cursor-pointer max-w-[160px] truncate"
                            >
                                <option value="all">Alle Geräte ({deviceOptions.length})</option>
                                {deviceOptions.map((d) => (
                                    <option key={d.id} value={d.id}>
                                        {d.name} ({d.count})
                                    </option>
                                ))}
                            </select>
                        </div>

                        {(searchTerm || selectedDeviceId !== "all" || categoryFilter !== "all") && (
                            <button
                                type="button"
                                onClick={() => {
                                    setSearchTerm("");
                                    setSelectedDeviceId("all");
                                    setCategoryFilter("all");
                                    setCurrentPage(1);
                                }}
                                className="text-xs font-bold text-indigo-600 hover:text-indigo-800 transition cursor-pointer px-2 py-1.5 bg-indigo-50/70 rounded-xl shrink-0"
                            >
                                ✕ Reset
                            </button>
                        )}
                    </div>

                    {/* Right: Horizontal Scrollable Category Pills */}
                    <div className="flex items-center gap-1.5 overflow-x-auto whitespace-nowrap pb-1 pt-0.5 lg:pb-0">
                        {categories.map((cat) => (
                            <button
                                key={cat.key}
                                type="button"
                                onClick={() => handleFilterChange(setCategoryFilter, cat.key)}
                                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 shrink-0 cursor-pointer ${
                                    categoryFilter === cat.key
                                        ? "bg-indigo-600 text-white shadow-2xs"
                                        : "bg-gray-100 hover:bg-gray-200/80 text-gray-700"
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
                        <thead className="bg-gray-50/80 border-b border-gray-200 text-xs font-semibold text-gray-500 uppercase tracking-wider select-none">
                            <tr>
                                {/* Status Header */}
                                <th
                                    onClick={() => handleSort("status")}
                                    className="py-3 px-4 cursor-pointer hover:bg-gray-100 transition"
                                    title="Nach Online-Status sortieren"
                                >
                                    <div className="flex items-center gap-1">
                                        <span>{t("common.status", "Status")}</span>
                                        <span className="text-[10px] text-gray-400">
                                            {sortField === "status" ? (sortDir === "asc" ? "▲" : "▼") : "⇅"}
                                        </span>
                                    </div>
                                </th>

                                {/* Device Header */}
                                <th
                                    onClick={() => handleSort("deviceName")}
                                    className="py-3 px-4 cursor-pointer hover:bg-gray-100 transition"
                                    title="Nach Gerätename sortieren"
                                >
                                    <div className="flex items-center gap-1">
                                        <span>{t("metrics.table_device_sensor", "Gerät / Sensor")}</span>
                                        <span className="text-[10px] text-gray-400">
                                            {sortField === "deviceName" ? (sortDir === "asc" ? "▲" : "▼") : "⇅"}
                                        </span>
                                    </div>
                                </th>

                                {/* Metric Header */}
                                <th
                                    onClick={() => handleSort("metricName")}
                                    className="py-3 px-4 cursor-pointer hover:bg-gray-100 transition"
                                    title="Nach Messgröße sortieren"
                                >
                                    <div className="flex items-center gap-1">
                                        <span>{t("metrics.table_metric", "Messgröße")}</span>
                                        <span className="text-[10px] text-gray-400">
                                            {sortField === "metricName" ? (sortDir === "asc" ? "▲" : "▼") : "⇅"}
                                        </span>
                                    </div>
                                </th>

                                {/* Location Header */}
                                <th
                                    onClick={() => handleSort("room")}
                                    className="py-3 px-4 cursor-pointer hover:bg-gray-100 transition"
                                    title="Nach Ort/Raum sortieren"
                                >
                                    <div className="flex items-center gap-1">
                                        <span>{t("metrics.table_location", "Ort / Raum")}</span>
                                        <span className="text-[10px] text-gray-400">
                                            {sortField === "room" ? (sortDir === "asc" ? "▲" : "▼") : "⇅"}
                                        </span>
                                    </div>
                                </th>

                                {/* Live Value Header */}
                                <th
                                    onClick={() => handleSort("liveValue")}
                                    className="py-3 px-4 text-right cursor-pointer hover:bg-gray-100 transition"
                                    title="Nach Messwert sortieren"
                                >
                                    <div className="flex items-center justify-end gap-1">
                                        <span>{t("metrics.table_current_value", "Aktueller Wert")}</span>
                                        <span className="text-[10px] text-gray-400">
                                            {sortField === "liveValue" ? (sortDir === "asc" ? "▲" : "▼") : "⇅"}
                                        </span>
                                    </div>
                                </th>

                                {/* Action Header */}
                                <th className="py-3 px-4 text-center">{t("metrics.table_actions", "Aktionen")}</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {paginatedChannels.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="py-12 text-center text-gray-400">
                                        <div className="space-y-2">
                                            <span className="text-3xl">🔍</span>
                                            <div className="font-semibold text-gray-700">{t("common.no_data", "Keine Kanäle gefunden")}</div>
                                            <p className="text-xs text-gray-400">Passe deine Filterkriterien oder den Suchbegriff an.</p>
                                        </div>
                                    </td>
                                </tr>
                            ) : (
                                paginatedChannels.map((channel, i) => (
                                    <tr key={`${channel.deviceId}-${channel.metricKey}-${i}`} className="hover:bg-slate-50/80 transition">
                                        {/* Status */}
                                        <td className="py-3.5 px-4 whitespace-nowrap">
                                            <span
                                                className={`inline-block w-2.5 h-2.5 rounded-full ${
                                                    channel.isOnline
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
                                            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-50 border border-indigo-100/60 text-indigo-700 text-xs font-semibold">
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
                                        <td className="py-3.5 px-4 whitespace-nowrap text-right font-mono font-black text-base text-gray-900">
                                            {channel.liveValue !== null && channel.liveValue !== undefined ? (
                                                <span>
                                                    {Number(channel.liveValue).toLocaleString("de-DE", { maximumFractionDigits: 1 })}{" "}
                                                    <span className="text-xs text-gray-500 font-normal uppercase">{channel.unit}</span>
                                                </span>
                                            ) : (
                                                <span className="text-gray-400 text-xs font-normal">-</span>
                                            )}
                                        </td>

                                        {/* Actions */}
                                        <td className="py-3.5 px-4 whitespace-nowrap text-center">
                                            <button
                                                type="button"
                                                onClick={() => setSelectedDeviceForChart(channel.device)}
                                                className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-indigo-50 text-slate-700 hover:text-indigo-600 text-xs font-semibold transition cursor-pointer"
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

                {/* PAGINATION & FOOTER TOOLBAR */}
                {totalItems > 0 && (
                    <div className="p-4 border-t border-gray-100 bg-gray-50/50 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-gray-600">
                        {/* Summary Count */}
                        <div>
                            {isAll ? (
                                <span>Zeige alle <b>{totalItems}</b> Messkanäle</span>
                            ) : (
                                <span>
                                    Zeige <b>{startIdx}–{endIdx}</b> von <b>{totalItems}</b> Messkanälen
                                </span>
                            )}
                        </div>

                        {/* Page Size Selector */}
                        <div className="flex items-center gap-1 bg-white border border-gray-200 p-0.5 rounded-xl shadow-2xs">
                            <span className="text-[11px] font-semibold text-gray-400 px-2">Zeilen:</span>
                            {[15, 25, 50, 99999].map((size) => (
                                <button
                                    key={size}
                                    type="button"
                                    onClick={() => {
                                        setPageSize(size);
                                        setCurrentPage(1);
                                    }}
                                    className={`px-2.5 py-1 rounded-lg text-xs font-bold transition cursor-pointer ${
                                        pageSize === size
                                            ? "bg-indigo-600 text-white shadow-2xs"
                                            : "text-gray-600 hover:bg-gray-100"
                                    }`}
                                >
                                    {size >= 9999 ? "Alle" : size}
                                </button>
                            ))}
                        </div>

                        {/* Page Navigation Buttons */}
                        {!isAll && totalPages > 1 && (
                            <div className="flex items-center gap-1">
                                <button
                                    type="button"
                                    disabled={safePage <= 1}
                                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                                    className="px-2.5 py-1 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed font-semibold transition cursor-pointer"
                                >
                                    ‹ Zurück
                                </button>

                                {Array.from({ length: totalPages }, (_, idx) => idx + 1).map((p) => (
                                    <button
                                        key={p}
                                        type="button"
                                        onClick={() => setCurrentPage(p)}
                                        className={`w-7 h-7 rounded-lg text-xs font-bold transition cursor-pointer ${
                                            p === safePage
                                                ? "bg-indigo-600 text-white shadow-2xs"
                                                : "bg-white border border-gray-200 text-gray-700 hover:bg-gray-50"
                                        }`}
                                    >
                                        {p}
                                    </button>
                                ))}

                                <button
                                    type="button"
                                    disabled={safePage >= totalPages}
                                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                                    className="px-2.5 py-1 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed font-semibold transition cursor-pointer"
                                >
                                    Vor ›
                                </button>
                            </div>
                        )}
                    </div>
                )}
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
