/*
# src/pages/DevicesPage.jsx
*/

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useMemo, useEffect, memo } from "react";
import { apiFetch } from "../api/client";
import KPISparklineECharts from "../components/ui/KPISparklineECharts";
import DeviceChartModal from "../components/device/DeviceChartModal";
import DeviceSetupModal from "../components/device/DeviceSetupModal";
import DeviceBaselineModal from "../components/device/DeviceBaselineModal";
import AddDeviceModal from "../components/device/AddDeviceModal";
import RemoveDevicesModal from "../components/device/RemoveDevicesModal";
import TrashBinModal from "../components/device/TrashBinModal";

import { useTrashCount } from "../hooks/useTrashDevices";
import { useStructure } from "../hooks/useStructure";
import useUserPreference from "../hooks/useUserPreference";
import { useTranslation } from "react-i18next";


function ensureOrder(items, storedOrder) {

    const itemIds = items.map(item => item.id);

    const existing = storedOrder.filter(id =>
        itemIds.includes(id)
    );

    const missing = itemIds.filter(id =>
        !existing.includes(id)
    );

    return [...existing, ...missing];
}


function isIncomplete(config) {

    if (!config?.role) {
        return true;
    }

    if (!config?.metric_definition) {
        return true;
    }

    if (
        config?.role?.key === "producer" &&
        !config?.generator_type
    ) {
        return true;
    }

    return false;
}


function getRoleColor(config) {
    if (config?.is_grid_source) {
        return {
            text: "text-emerald-700",
            bg: "bg-white",
            badgeBg: "bg-emerald-50 border-emerald-200/80 text-emerald-700",
            ring: "hover:border-emerald-300",
            chart: "#10b981",
        };
    }

    switch (config?.role?.key) {
        case "producer":
            return {
                text: "text-amber-700",
                bg: "bg-white",
                badgeBg: "bg-amber-50 border-amber-200/80 text-amber-800",
                ring: "hover:border-amber-300",
                chart: "#f59e0b",
            };

        case "consumer":
            return {
                text: "text-blue-700",
                bg: "bg-white",
                badgeBg: "bg-blue-50 border-blue-200/80 text-blue-700",
                ring: "hover:border-blue-300",
                chart: "#2563eb",
            };

        case "battery":
            return {
                text: "text-purple-700",
                bg: "bg-white",
                badgeBg: "bg-purple-50 border-purple-200/80 text-purple-700",
                ring: "hover:border-purple-300",
                chart: "#8b5cf6",
            };

        case "sensor":
            return {
                text: "text-teal-700",
                bg: "bg-white",
                badgeBg: "bg-teal-50 border-teal-200/80 text-teal-700",
                ring: "hover:border-teal-300",
                chart: "#0d9488",
            };

        case "both":
            return {
                text: "text-cyan-700",
                bg: "bg-white",
                badgeBg: "bg-cyan-50 border-cyan-200/80 text-cyan-700",
                ring: "hover:border-cyan-300",
                chart: "#0891b2",
            };

        default:
            return {
                text: "text-indigo-700",
                bg: "bg-white",
                badgeBg: "bg-slate-100 border-slate-200 text-slate-700",
                ring: "hover:border-slate-300",
                chart: "#6366f1",
            };
    }
}

/* =========================================================
   DEVICE CARD
========================================================= */
const DeviceCard = memo(function DeviceCard({ device, onSelect, onEdit, onDelete, onBaseline }) {
    const { t } = useTranslation();
    const config = device.config || {};
    const isOnline = device.status === "online";
    const missing = isIncomplete(config);

    const [isSwitching, setIsSwitching] = useState(false);
    const [relayState, setRelayState] = useState(device.relay_state ?? false);

    useEffect(() => {
        if (device.relay_state !== undefined) {
            setRelayState(device.relay_state);
        }
    }, [device.relay_state]);

    const handleToggleRelay = async (e) => {
        e.stopPropagation();
        if (isSwitching) return;
        setIsSwitching(true);
        const target = !relayState;
        setRelayState(target); // Optimistisches Feedback
        try {
            const res = await apiFetch(`/api/devices/${device.id}/switch/`, {
                method: "POST",
                body: JSON.stringify({ state: "toggle" }),
            });
            if (res && res.relay_state !== undefined) {
                setRelayState(res.relay_state);
            }
        } catch (err) {
            console.error("Relay switch error:", err);
            setRelayState(!target); // Revert bei Fehler
        } finally {
            setIsSwitching(false);
        }
    };

    const roleStyle = getRoleColor(config);

    function getIcon(config) {
        if (config?.is_grid_source) return "🔌";
        switch (config?.role?.key) {
            case "producer": return "☀️";
            case "consumer": return "⚡";
            case "battery": return "🔋";
            case "sensor": return "🌡️";
            default: return "📟";
        }
    }

    return (
        <div
            onClick={() => onSelect(device)}
            className={`
                cursor-pointer
                border rounded-2xl
                p-4 sm:p-5
                shadow-2xs hover:shadow-md
                transition-all duration-200
                flex flex-col justify-between
                relative
                ${roleStyle.ring}
                ${missing
                    ? "border-amber-300/80 bg-amber-50/40"
                    : `border-gray-200/80 bg-white hover:border-gray-300`
                }
            `}
        >
            <div>
                {/* Top Row: Info & Action Toolbar */}
                <div className="flex justify-between items-start gap-2 mb-2">
                    <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                            <span className="text-lg shrink-0">{getIcon(config)}</span>
                            <span className="font-bold text-gray-900 truncate text-sm sm:text-base" title={device.display_name}>
                                {device.display_name}
                            </span>
                            {missing && (
                                <span className="text-amber-600 text-xs shrink-0" title={t("devices.incomplete_badge", "Unvollständig konfiguriert")}>
                                    ⚠
                                </span>
                            )}
                        </div>
                        <div className="text-[11px] font-mono text-gray-400 truncate mt-0.5">
                            {device.identifier}
                        </div>
                    </div>

                    {/* Action Buttons & Status Dot */}
                    <div className="flex items-center gap-0.5 shrink-0 bg-slate-50 border border-slate-100 rounded-xl p-0.5">
                        <button
                            type="button"
                            onClick={(e) => {
                                e.stopPropagation();
                                onBaseline?.(device);
                            }}
                            className="text-gray-400 hover:text-indigo-600 p-1.5 rounded-lg hover:bg-white transition cursor-pointer"
                            title={t("devices.baseline_title", "Geräteprofil & Baseline-Überwachung")}
                        >
                            🧠
                        </button>

                        <button
                            type="button"
                            onClick={(e) => {
                                e.stopPropagation();
                                onEdit(device);
                            }}
                            className="text-gray-400 hover:text-gray-700 p-1.5 rounded-lg hover:bg-white transition cursor-pointer"
                            title={t("devices.setup_title", "Konfigurieren")}
                        >
                            ⚙️
                        </button>

                        <button
                            type="button"
                            onClick={(e) => {
                                e.stopPropagation();
                                onDelete(device);
                            }}
                            className="text-gray-400 hover:text-rose-600 p-1.5 rounded-lg hover:bg-white transition cursor-pointer"
                            title={t("nav.remove_device", "In den Papierkorb verschieben")}
                        >
                            🗑️
                        </button>

                        <span
                            className={`w-2 h-2 rounded-full mx-1 ${isOnline ? "bg-emerald-500 shadow-xs shadow-emerald-500/80" : "bg-gray-300"}`}
                            title={isOnline ? "Online" : "Offline"}
                        />
                    </div>
                </div>

                {/* Role Badge & Location */}
                <div className="flex items-center gap-2 mb-3">
                    <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${roleStyle.badgeBg}`}>
                        {config.is_grid_source ? t("devices.role_grid", "Netz") : (config.role?.label || "–")}
                    </span>
                    {(config.floor?.name || config.room?.name) && (
                        <span className="text-[11px] text-gray-500 truncate">
                            {[config.floor?.name, config.room?.name].filter(Boolean).join(" · ")}
                        </span>
                    )}
                </div>

                {/* Primary Metric Value */}
                <div className="text-xl sm:text-2xl font-black text-gray-900 tracking-tight font-mono">
                    {device.value != null ? (
                        <>
                            {device.value} <span className="text-xs font-semibold text-gray-500 uppercase">{device.unit || ""}</span>
                        </>
                    ) : device.status === "stale" ? (
                        <span className="text-xs font-medium text-gray-400">
                            {t("common.no_recent_data", "Keine aktuellen Daten")}
                        </span>
                    ) : device.status === "offline" ? (
                        <span className="text-xs font-medium text-gray-400">
                            {t("common.offline", "Offline")}
                        </span>
                    ) : (
                        <span className="text-xs font-medium text-gray-400">
                            {t("common.no_data", "Keine Daten")}
                        </span>
                    )}
                </div>
            </div>

            {/* Sparkline Chart & Relay Switch */}
            <div className="mt-3">
                {device.sparkline?.length > 0 && (
                    <div className="mb-2">
                        <KPISparklineECharts
                            values={device.sparkline}
                            color={roleStyle.chart}
                            unit={device.unit}
                        />
                    </div>
                )}

                {/* ⚡ INTERAKTIVER RELAIS-SCHALTER (AKTORIK) */}
                {device.is_switchable && (
                    <div className="pt-2.5 border-t border-gray-100 flex items-center justify-between">
                        <span className="text-xs font-semibold text-gray-700 flex items-center gap-1.5">
                            <span className="text-amber-500 font-bold">⚡</span>
                            <span>{relayState ? t("devices.relay_on", "Relais AN") : t("devices.relay_off", "Relais AUS")}</span>
                        </span>
                        <button
                            type="button"
                            onClick={handleToggleRelay}
                            disabled={isSwitching}
                            className={`relative inline-flex h-5 w-10 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-hidden ${
                                relayState ? "bg-emerald-500" : "bg-gray-300"
                            } ${isSwitching ? "opacity-60 cursor-wait" : ""}`}
                            title={relayState ? t("devices.relay_turn_off", "Relais ausschalten") : t("devices.relay_turn_on", "Relais einschalten")}
                        >
                            <span
                                className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out ${
                                    relayState ? "translate-x-5" : "translate-x-0"
                                }`}
                            />
                        </button>
                    </div>
                )}

                {missing && (
                    <div className="text-[11px] font-semibold text-amber-700 mt-2 bg-amber-100/60 rounded-lg px-2.5 py-1 flex items-center gap-1.5">
                        <span>⚠</span>
                        <span>{t("devices.incomplete_badge", "Unvollständig konfiguriert")}</span>
                    </div>
                )}
            </div>
        </div>
    );
});


/* =========================================================
   PAGE
========================================================= */

export default function DevicesPage() {

    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const statusOptions = useMemo(() => [
        {
            key: "online",
            icon: "🟢",
            label: t("devices.filter_online", "Online"),
            title: t("devices.online_desc", "Nur Geräte mit aktuellen Daten"),
        },
        {
            key: "offline",
            icon: "⚫",
            label: t("devices.filter_offline", "Offline"),
            title: t("devices.offline_desc", "Geräte ohne aktuelle Daten"),
        },
        {
            key: "missing",
            icon: "⚠️",
            label: t("devices.filter_missing", "Offen"),
            title: t("devices.missing_desc", "Unvollständig konfigurierte Geräte"),
        },
    ], [t]);

    const roleOptions = useMemo(() => ({
        producer: {
            icon: "☀️",
            label: t("devices.role_producer", "Erzeuger"),
            title: "Energieerzeuger anzeigen",
        },
        consumer: {
            icon: "⚡",
            label: t("devices.role_consumer", "Verbraucher"),
            title: "Energieverbraucher anzeigen",
        },
        battery: {
            icon: "🔋",
            label: t("devices.role_battery", "Speicher"),
            title: "Batteriespeicher anzeigen",
        },
        grid: {
            icon: "🔌",
            label: t("devices.role_grid", "Netz"),
            title: "Netzanschlüsse anzeigen",
        },
        sensor: {
            icon: "🌡️",
            label: t("devices.role_sensor", "Sensor"),
            title: "Sensoren & Messfühler anzeigen",
        },
        both: {
            icon: "🔄",
            label: t("devices.role_both", "Beides"),
            title: "Erzeuger & Verbraucher anzeigen",
        },
    }), [t]);

    const [chartDevice, setChartDevice] = useState(null);
    const [baselineDevice, setBaselineDevice] = useState(null);
    const [modalMode, setModalMode] = useState(null);
    const [editingDevice, setEditingDevice] = useState(null);

    const [openAddDevice, setOpenAddDevice] = useState(false);
    const [openRemoveDevice, setOpenRemoveDevice] = useState(false);
    const [openTrashBin, setOpenTrashBin] = useState(false);
    const trashQuery = useTrashCount();
    const trashCount = trashQuery?.data?.count ?? 0;

    function handleDeviceUpdated(device) {
        const updatedDev = device?.device || device;
        if (!updatedDev?.id) return;

        queryClient.setQueryData(
            ["devices"],
            old => old?.map(d =>
                d.id === updatedDev.id ? { ...d, ...updatedDev } : d
            ) || []
        );

        queryClient.invalidateQueries({ queryKey: ["devices"] });
        queryClient.invalidateQueries({ queryKey: ["devices-status"] });
        queryClient.invalidateQueries({ queryKey: ["dashboard-devices"] });
    }

    async function handleQuickDelete(device) {
        const confirmed = window.confirm(
            t("devices.confirm_trash_single", {
                name: device.display_name || device.identifier,
                defaultValue: `Gerät "${device.display_name || device.identifier}" in den Papierkorb verschieben?`
            })
        );
        if (!confirmed) return;

        try {
            await apiFetch("/api/devices/remove/", {
                method: "POST",
                body: JSON.stringify({
                    device_ids: [device.id],
                }),
            });
            await Promise.all([
                queryClient.invalidateQueries({ queryKey: ["devices"] }),
                queryClient.invalidateQueries({ queryKey: ["device-trash"] }),
                queryClient.invalidateQueries({ queryKey: ["trash-count"] }),
                queryClient.invalidateQueries({ queryKey: ["unconfigured-devices"] }),
            ]);
        } catch (err) {
            console.error("Failed to trash device", err);
        }
    }

    const [filterText, setFilterText] = useState("");
    const [selectedFloor, setSelectedFloor] = useState("all");
    const [selectedRoom, setSelectedRoom] = useState("all");

    const devicesQuery = useQuery({
        queryKey: ["devices"],
        queryFn: () => apiFetch("/api/devices/"),
    });

    const statusQuery = useQuery({
        queryKey: ["devices-status"],
        queryFn: () => apiFetch("/api/devices/status/"),
        refetchInterval: 5000,
    });

    const valuesQuery = useQuery({
        queryKey: ["devices-values"],
        queryFn: () => apiFetch("/api/devices/dashboard/"),
        refetchInterval: 3000,
        retry: false,
    });

    const {
        value: settings,
        setValue: saveSettings,
        isLoading: settingsLoading,
    } = useUserPreference("devicepage");

    const showFloors = useMemo(
        () => settings.showFloors ?? true,
        [settings.showFloors]
    );

    const showRooms = useMemo(
        () => settings.showRooms ?? true,
        [settings.showRooms]
    );

    const statusFilter = useMemo(
        () => settings.statusFilter ?? null,
        [settings.statusFilter]
    );

    const floorOrder = useMemo(
        () => settings.floorOrder ?? [],
        [settings.floorOrder]
    );

    const roomOrder = useMemo(
        () => settings.roomOrder ?? [],
        [settings.roomOrder]
    );

    const deviceOrder = useMemo(
        () => settings.deviceOrder ?? [],
        [settings.deviceOrder]
    );

    const structureQuery = useStructure();
    const structure = structureQuery?.data;

    const devices = useMemo(
        () => devicesQuery.data ?? [],
        [devicesQuery.data]
    );

    const statusMap = Object.fromEntries(
        (statusQuery.data || []).map(s => [s.id, s])
    );

    const valueMap = Object.fromEntries(
        (valuesQuery.data || []).map(v => [v.device, v])
    );

    const merged = useMemo(() => {
        return devices.map(d => ({
            ...d,
            status: (statusMap[d.id]?.status || "offline").toLowerCase(),
            value: valueMap[d.id]?.value,
            unit: valueMap[d.id]?.unit,
            sparkline: valueMap[d.id]?.sparkline || [],
        }));
    }, [devices, statusMap, valueMap]);

    const allKnownRoles = useMemo(() => {
        const keys = new Set(["producer", "consumer", "battery", "grid", "sensor"]);
        (structure?.roles || []).forEach(r => {
            if (r.key) keys.add(r.key);
        });
        merged.forEach(d => {
            if (d.config?.role?.key) keys.add(d.config.role.key);
        });
        return Array.from(keys);
    }, [structure?.roles, merged]);

    const activeRoles = useMemo(
        () => settings.roles ?? allKnownRoles,
        [settings.roles, allKnownRoles]
    );


    const roleStats = useMemo(() => {
        const map = {};

        merged.forEach(d => {
            const key = d.config?.is_grid_source
                ? "grid"
                : d.config?.role?.key;

            if (!key) {
                return;
            }

            map[key] = (map[key] || 0) + 1;
        });

        return map;
    }, [merged]);

    const statusStats = useMemo(() => {

        return {

            online: merged.filter(
                d => d.status === "online"
            ).length,

            offline: merged.filter(
                d => d.status !== "online"
            ).length,

            missing: merged.filter(d =>
                isIncomplete(d.config)
            ).length,

        };

    }, [merged]);

    const availableFloorsList = useMemo(() => {
        const map = new Map();
        (structure?.floors || []).forEach(f => {
            if (f.name) map.set(f.name, f);
        });
        merged.forEach(d => {
            const f = d.config?.floor;
            if (f?.name && !map.has(f.name)) {
                map.set(f.name, f);
            }
        });
        return Array.from(map.values()).sort((a, b) => (a.name || "").localeCompare(b.name || "", "de"));
    }, [structure?.floors, merged]);

    const availableRoomsList = useMemo(() => {
        const map = new Map();
        (structure?.rooms || []).forEach(r => {
            if (r.name) map.set(r.name, r);
        });
        merged.forEach(d => {
            const r = d.config?.room;
            if (r?.name && !map.has(r.name)) {
                map.set(r.name, r);
            }
        });
        return Array.from(map.values()).sort((a, b) => (a.name || "").localeCompare(b.name || "", "de"));
    }, [structure?.rooms, merged]);

    /* ✅ FILTER */

    const filtered = useMemo(() => {

        let list = [...merged];

        if (filterText) {

            const t = filterText.trim().toLowerCase();

            list = list.filter(d =>
                (d.display_name || "").toLowerCase().includes(t) ||
                (d.identifier || "").toLowerCase().includes(t)
            );
        }

        if (statusFilter === "online") {
            list = list.filter(d => d.status === "online");
        }

        if (statusFilter === "offline") {
            list = list.filter(d => d.status !== "online");
        }

        if (statusFilter === "missing") {

            list = list.filter(d =>
                isIncomplete(d.config)
            );
        }

        if (selectedFloor !== "all") {
            list = list.filter(d => {
                const f = d.config?.floor;
                return (f?.name || "Ohne Etage") === selectedFloor || String(f?.id || "") === selectedFloor;
            });
        }

        if (selectedRoom !== "all") {
            list = list.filter(d => {
                const r = d.config?.room;
                return (r?.name || "Ohne Raum") === selectedRoom || String(r?.id || "") === selectedRoom;
            });
        }

        list = list.filter(d => {

            if (d.config?.is_grid_source) {
                return activeRoles.includes("grid");
            }

            const role = d.config?.role?.key;

            return role
                ? activeRoles.includes(role)
                : true;
        });


        return list;

    }, [
        merged,
        filterText,
        statusFilter,
        selectedFloor,
        selectedRoom,
        activeRoles,
    ]);

    /* ✅ BANNER */

    const unconfiguredDevices = useMemo(() => {

        return filtered.filter(d =>
            isIncomplete(d.config)
        );

    }, [filtered]);

    /* ✅ GROUPING */

    const grouped = useMemo(() => {

        return filtered.reduce((acc, d) => {

            const floor = showFloors
                ? (d.config?.floor?.name || t("devices.no_floor", "Ohne Etage"))
                : t("devices.filter_all", "Alle Geräte");

            const room = showRooms
                ? (d.config?.room?.name || t("devices.no_room", "Ohne Raum"))
                : "__ALL__";

            acc[floor] = acc[floor] || {};
            acc[floor][room] = acc[floor][room] || [];
            acc[floor][room].push(d);

            return acc;

        }, {});

    }, [
        filtered,
        showFloors,
        showRooms,
        t,
    ]);

    const allFloorIds = useMemo(() => {

        const floors = {};

        merged.forEach(d => {

            const floor = d.config?.floor;

            if (floor?.id) {
                floors[floor.id] = floor.name;
            }

        });

        return Object.entries(floors)
            .sort(([, a], [, b]) =>
                a.localeCompare(b, "de")
            )
            .map(([id]) => Number(id));

    }, [merged]);

    const allRoomIds = useMemo(() => {

        const rooms = {};

        merged.forEach(d => {

            const room = d.config?.room;

            if (room?.id) {
                rooms[room.id] = room.name;
            }

        });

        return Object.entries(rooms)
            .sort(([, a], [, b]) =>
                a.localeCompare(b, "de")
            )
            .map(([id]) => Number(id));

    }, [merged]);

    const allDeviceIds = useMemo(() => {

        return [...merged]
            .sort((a, b) =>
                (a.display_name || "").localeCompare(
                    b.display_name || "",
                    "de"
                )
            )
            .map(d => d.id);

    }, [merged]);

    useEffect(() => {

        if (!merged.length) {
            return;
        }

        const nextFloorOrder = ensureOrder(
            allFloorIds.map(id => ({ id })),
            floorOrder
        );

        const nextRoomOrder = ensureOrder(
            allRoomIds.map(id => ({ id })),
            roomOrder
        );

        const nextDeviceOrder = ensureOrder(
            allDeviceIds.map(id => ({ id })),
            deviceOrder
        );

        const changed =
            JSON.stringify(nextFloorOrder) !== JSON.stringify(floorOrder) ||
            JSON.stringify(nextRoomOrder) !== JSON.stringify(roomOrder) ||
            JSON.stringify(nextDeviceOrder) !== JSON.stringify(deviceOrder);

        if (!changed) {
            return;
        }

        saveSettings({
            ...settings,
            floorOrder: nextFloorOrder,
            roomOrder: nextRoomOrder,
            deviceOrder: nextDeviceOrder,
        });

    }, [
        merged,
        floorOrder,
        roomOrder,
        deviceOrder,
        allFloorIds,
        allRoomIds,
        allDeviceIds,
        settings,
        saveSettings,
    ]);

    if (
        devicesQuery.isLoading ||
        valuesQuery.isLoading ||
        settingsLoading
    ) {
        return (
            <div className="p-6 max-w-7xl mx-auto space-y-6 animate-pulse">
                <div className="flex justify-between items-center">
                    <div className="space-y-2">
                        <div className="h-7 w-48 bg-slate-200 rounded-lg" />
                        <div className="h-4 w-72 bg-slate-100 rounded-md" />
                    </div>
                    <div className="h-10 w-36 bg-slate-200 rounded-xl" />
                </div>
                <div className="h-10 w-full bg-slate-100 rounded-xl" />
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <div key={i} className="h-44 bg-slate-100 rounded-2xl border border-slate-200/60 p-4 space-y-3">
                            <div className="h-4 w-32 bg-slate-200 rounded-md" />
                            <div className="h-6 w-20 bg-slate-300 rounded-md" />
                            <div className="h-16 w-full bg-slate-200/50 rounded-xl" />
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">

            {/* TOP ACTION HEADER */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <span>📟</span> {t("devices.title", "Geräteübersicht")}
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">
                        {t("devices.subtitle", "Verwalte und überwache alle angeschlossenen Sensoren und Aktoren.")}
                    </p>
                </div>

                <div className="flex items-center gap-2.5 shrink-0">
                    {/* Secondary Actions Group */}
                    <div className="inline-flex bg-white border border-gray-200 rounded-xl shadow-2xs divide-x divide-gray-100">
                        <button
                            type="button"
                            onClick={() => setOpenTrashBin(true)}
                            className="px-3.5 py-2 hover:bg-gray-50 text-xs font-semibold text-gray-700 flex items-center gap-1.5 transition rounded-l-xl cursor-pointer"
                            title={t("nav.trash_bin", "Papierkorb")}
                        >
                            <span>♻️</span>
                            <span>{t("nav.trash_bin", "Papierkorb")}</span>
                            {trashCount > 0 && (
                                <span className="px-1.5 py-0.2 rounded-full bg-rose-100 text-rose-700 text-[10px] font-bold">
                                    {trashCount}
                                </span>
                            )}
                        </button>

                        <button
                            type="button"
                            onClick={() => setOpenRemoveDevice(true)}
                            className="px-3.5 py-2 hover:bg-rose-50 text-xs font-semibold text-gray-700 hover:text-rose-600 flex items-center gap-1.5 transition rounded-r-xl cursor-pointer"
                            title={t("nav.remove_device", "Geräte entfernen")}
                        >
                            <span>🗑️</span>
                            <span>{t("nav.remove_device", "Gerät entfernen")}</span>
                        </button>
                    </div>

                    {/* Primary Add Button */}
                    <button
                        type="button"
                        onClick={() => setOpenAddDevice(true)}
                        className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-xs hover:shadow-sm flex items-center gap-1.5 transition cursor-pointer"
                    >
                        <span>➕</span>
                        <span>{t("nav.add_device", "Neues Gerät")}</span>
                    </button>
                </div>
            </div>

            {/* SEARCH & STRUCTURE SELECT FILTERS */}
            <div className="flex flex-wrap items-center gap-2.5">
                <div className="relative">
                    <input
                        placeholder={t("devices.search_placeholder", "🔍 Gerät suchen...")}
                        value={filterText}
                        onChange={(e) => setFilterText(e.target.value)}
                        className="border border-gray-200 px-3.5 py-1.5 rounded-xl text-xs font-medium w-64 bg-white shadow-2xs focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
                    />
                    {filterText && (
                        <button
                            type="button"
                            onClick={() => setFilterText("")}
                            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-xs"
                        >
                            ✕
                        </button>
                    )}
                </div>

                {/* Etagen-Filter */}
                <div className="flex items-center gap-1.5 bg-white border border-gray-200 px-3 py-1.5 rounded-xl shadow-2xs">
                    <span className="text-xs font-semibold text-gray-500">🏢 Etage:</span>
                    <select
                        value={selectedFloor}
                        onChange={(e) => setSelectedFloor(e.target.value)}
                        className="text-xs font-bold text-gray-800 bg-transparent border-none focus:outline-hidden cursor-pointer"
                    >
                        <option value="all">{t("devices.all_floors", "Alle Etagen")}</option>
                        {availableFloorsList.map((f) => (
                            <option key={f.id || f.name} value={f.name}>
                                {f.name}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Räume-Filter */}
                <div className="flex items-center gap-1.5 bg-white border border-gray-200 px-3 py-1.5 rounded-xl shadow-2xs">
                    <span className="text-xs font-semibold text-gray-500">🚪 Raum:</span>
                    <select
                        value={selectedRoom}
                        onChange={(e) => setSelectedRoom(e.target.value)}
                        className="text-xs font-bold text-gray-800 bg-transparent border-none focus:outline-hidden cursor-pointer"
                    >
                        <option value="all">{t("devices.all_rooms", "Alle Räume")}</option>
                        {availableRoomsList.map((r) => (
                            <option key={r.id || r.name} value={r.name}>
                                {r.name}
                            </option>
                        ))}
                    </select>
                </div>

                {(selectedFloor !== "all" || selectedRoom !== "all" || filterText) && (
                    <button
                        type="button"
                        onClick={() => {
                            setSelectedFloor("all");
                            setSelectedRoom("all");
                            setFilterText("");
                        }}
                        className="text-xs font-bold text-indigo-600 hover:text-indigo-800 transition cursor-pointer px-2 py-1 bg-indigo-50/60 rounded-lg hover:bg-indigo-100"
                    >
                        ✕ Filter zurücksetzen
                    </button>
                )}
            </div>

            {/* SEGMENTED FILTER CHIPS BAR */}
            <div className="flex flex-wrap items-center gap-2 p-2 bg-slate-50 border border-slate-200/70 rounded-2xl">

                {/* Status Filter Group */}
                <div className="flex flex-wrap items-center gap-1.5">
                    {statusOptions.map((option) => (
                        <button
                            key={option.key}
                            title={option.title}
                            type="button"
                            onClick={() =>
                                saveSettings({
                                    ...settings,
                                    statusFilter: statusFilter === option.key ? null : option.key,
                                })
                            }
                            className={`
                                px-2.5 py-1
                                rounded-xl
                                text-xs font-semibold
                                border
                                flex items-center gap-1.5
                                transition cursor-pointer
                                ${statusFilter === option.key
                                    ? "bg-indigo-600 text-white border-indigo-600 shadow-2xs"
                                    : "bg-white hover:bg-slate-100/80 border-gray-200 text-gray-700"}
                            `}
                        >
                            <span>{option.icon}</span>
                            <span>{option.label}</span>
                            <span className="opacity-70 font-mono text-[10px]">
                                ({statusStats[option.key] || 0})
                            </span>
                        </button>
                    ))}
                </div>

                {/* Subtle Divider */}
                <div className="h-4 w-px bg-slate-300 mx-1 hidden sm:block" />

                {/* Role Filter Group */}
                <div className="flex flex-wrap items-center gap-1.5">
                    {allKnownRoles
                        .filter((role) => ["producer", "consumer", "battery", "grid", "sensor"].includes(role) || (roleStats[role] || 0) > 0)
                        .map((role) => {
                            const active = activeRoles.includes(role);
                            const config = roleOptions[role] || {
                                icon: "📟",
                                label: role.charAt(0).toUpperCase() + role.slice(1),
                                title: `${role} anzeigen`,
                            };

                            return (
                                <button
                                    key={role}
                                    type="button"
                                    title={config.title}
                                    onClick={() => {
                                        const nextRoles = active
                                            ? activeRoles.filter((r) => r !== role)
                                            : [...activeRoles, role];
                                        saveSettings({
                                            ...settings,
                                            roles: nextRoles,
                                        });
                                    }}
                                    className={`
                                        px-2.5 py-1
                                        rounded-xl
                                        text-xs font-semibold
                                        border
                                        flex items-center gap-1.5
                                        transition cursor-pointer
                                        ${active
                                            ? "bg-slate-800 text-white border-slate-800 shadow-2xs"
                                            : "bg-white hover:bg-slate-100/80 border-gray-200 text-gray-700"}
                                    `}
                                >
                                    <span>{config.icon}</span>
                                    <span>{config.label}</span>
                                    <span className="opacity-70 font-mono text-[10px]">
                                        ({roleStats[role] || 0})
                                    </span>
                                </button>
                            );
                        })}
                </div>

                {/* Subtle Divider */}
                <div className="h-4 w-px bg-slate-300 mx-1 hidden sm:block" />

                {/* Structure View Toggles */}
                <div className="flex items-center gap-1.5 ml-auto">
                    <button
                        type="button"
                        title={t("devices.group_by_floors", "Geräte nach Etagen gruppieren")}
                        onClick={() =>
                            saveSettings({
                                ...settings,
                                showFloors: !showFloors,
                            })
                        }
                        className={`
                            px-2.5 py-1
                            rounded-xl
                            text-xs font-semibold
                            border
                            flex items-center gap-1.5
                            transition cursor-pointer
                            ${showFloors
                                ? "bg-indigo-600 text-white border-indigo-600 shadow-2xs"
                                : "bg-white hover:bg-slate-100/80 border-gray-200 text-gray-700"}
                        `}
                    >
                        🏢 {t("structure.floor", "Etage")}
                    </button>

                    <button
                        type="button"
                        title={t("devices.group_by_rooms", "Geräte nach Räumen gruppieren")}
                        onClick={() =>
                            saveSettings({
                                ...settings,
                                showRooms: !showRooms,
                            })
                        }
                        className={`
                            px-2.5 py-1
                            rounded-xl
                            text-xs font-semibold
                            border
                            flex items-center gap-1.5
                            transition cursor-pointer
                            ${showRooms
                                ? "bg-indigo-600 text-white border-indigo-600 shadow-2xs"
                                : "bg-white hover:bg-slate-100/80 border-gray-200 text-gray-700"}
                        `}
                    >
                        🚪 {t("structure.rooms", "Räume")}
                    </button>
                </div>

            </div>

            {/* BANNER */}
            {unconfiguredDevices.length > 0 && (
                <div
                    onClick={() => {
                        setModalMode("bulk");
                        setEditingDevice(null);
                    }}
                    className="p-4 rounded-2xl border border-amber-300 bg-amber-50 flex items-center justify-between cursor-pointer hover:bg-amber-100/80 transition shadow-2xs"
                >
                    <div className="text-amber-900 text-xs sm:text-sm font-semibold flex items-center gap-2">
                        <span>⚠</span>
                        <span>{t("devices.unconfigured_banner", { count: unconfiguredDevices.length, defaultValue: `${unconfiguredDevices.length} Gerät(e) nicht vollständig konfiguriert` })}</span>
                    </div>

                    <span className="text-xs font-bold text-white bg-amber-600 hover:bg-amber-700 px-3.5 py-1.5 rounded-xl shadow-2xs transition">
                        {t("devices.configure_now", "Jetzt konfigurieren")}
                    </span>
                </div>
            )}

            {/* EMPTY FILTER STATE */}
            {filtered.length === 0 && (
                <div className="bg-white border border-dashed border-gray-200 rounded-3xl p-10 text-center space-y-3">
                    <span className="text-3xl p-3 bg-slate-50 rounded-2xl inline-block border border-slate-100">🔍</span>
                    <h3 className="text-base font-bold text-gray-800">
                        {t("devices.no_matches_title", "Keine passenden Geräte gefunden")}
                    </h3>
                    <p className="text-xs text-gray-500 max-w-md mx-auto">
                        {t("devices.no_matches_desc", "Für die aktuelle Filterkombination oder Suche liegen keine Geräte vor.")}
                    </p>
                    <button
                        type="button"
                        onClick={() => {
                            setSelectedFloor("all");
                            setSelectedRoom("all");
                            setFilterText("");
                            saveSettings({
                                ...settings,
                                statusFilter: null,
                                roles: allKnownRoles,
                            });
                        }}
                        className="px-4 py-2 bg-indigo-50 text-indigo-700 font-bold text-xs rounded-xl hover:bg-indigo-100 transition cursor-pointer"
                    >
                        ✕ Filter zurücksetzen
                    </button>
                </div>
            )}

            {/* GRID */}
            {filtered.length > 0 && Object.entries(grouped)
                .sort(([a], [b]) => a.localeCompare(b, "de"))
                .map(([floor, rooms]) => (

                    <div key={floor} className="space-y-3">

                        {showFloors && (
                            <h2 className="text-xs font-bold uppercase tracking-wider text-gray-500 flex items-center gap-1.5">
                                <span>🏢</span> {floor}
                            </h2>
                        )}

                        {Object.entries(rooms)
                            .sort(([a], [b]) => a.localeCompare(b, "de"))
                            .map(([room, devices]) => (
                                <div key={room} className="space-y-2">

                                    {showRooms && room !== "__ALL__" && (
                                        <h3 className="text-xs font-semibold text-gray-400 flex items-center gap-1.5 pl-2">
                                            <span>🚪</span> {room}
                                        </h3>
                                    )}

                                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3.5">
                                        {[...devices]
                                            .sort((a, b) =>
                                                (a.display_name || "").localeCompare(
                                                    b.display_name || "",
                                                    "de"
                                                )
                                            )
                                            .map((d) => (
                                                <DeviceCard
                                                    key={d.id}
                                                    device={d}
                                                    onSelect={setChartDevice}
                                                    onBaseline={setBaselineDevice}
                                                    onEdit={(dev) => {
                                                        setEditingDevice(dev);
                                                        setModalMode("single");
                                                    }}
                                                    onDelete={handleQuickDelete}
                                                />
                                            ))}
                                    </div>

                                </div>
                            ))}

                    </div>
                ))}

            <DeviceSetupModal
                open={!!modalMode}
                onClose={() => {
                    setModalMode(null);
                    setEditingDevice(null);
                }}
                onDeviceUpdated={handleDeviceUpdated}
                mode={modalMode || "bulk"}
                singleDevice={editingDevice}
            />

            {chartDevice && (
                <DeviceChartModal
                    device={chartDevice}
                    onClose={() => setChartDevice(null)}
                />
            )}

            {baselineDevice && (
                <DeviceBaselineModal
                    device={baselineDevice}
                    isOpen={!!baselineDevice}
                    onClose={() => setBaselineDevice(null)}
                />
            )}

            <AddDeviceModal
                open={openAddDevice}
                onClose={() => setOpenAddDevice(false)}
                onCreated={() => {
                    devicesQuery.refetch();
                    valuesQuery.refetch();
                }}
            />


            <RemoveDevicesModal
                open={openRemoveDevice}
                onClose={() => setOpenRemoveDevice(false)}
            />

            <TrashBinModal
                open={openTrashBin}
                onClose={() => setOpenTrashBin(false)}
                onChanged={() => {
                    devicesQuery.refetch();
                    valuesQuery.refetch();
                    trashQuery.refetch();
                }}
            />

        </div>
    );
}
