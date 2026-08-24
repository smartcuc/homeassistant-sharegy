/*
# src/pages/DevicesPage.jsx
*/

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useMemo, useEffect } from "react";
import { apiFetch } from "../api/client";
import KPISparklineECharts from "../components/ui/KPISparklineECharts";
import DeviceChartModal from "../components/device/DeviceChartModal";
import DeviceSetupModal from "../components/device/DeviceSetupModal";
import AddDeviceModal from "../components/device/AddDeviceModal";
import RemoveDevicesModal from "../components/device/RemoveDevicesModal";
import TrashBinModal from "../components/device/TrashBinModal";
import { useTrashCount } from "../hooks/useTrashDevices";
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
            text: "text-emerald-600",
            bg: "bg-emerald-50",
            ring: "hover:ring-emerald-200",
            chart: "#10b981",
        };
    }

    switch (config?.role?.key) {

        case "producer":
            return {
                text: "text-amber-500",
                bg: "bg-amber-50",
                ring: "hover:ring-amber-200",
                chart: "#f59e0b",
            };

        case "consumer":
            return {
                text: "text-blue-600",
                bg: "bg-blue-50",
                ring: "hover:ring-blue-200",
                chart: "#2563eb",
            };

        case "battery":
            return {
                text: "text-purple-600",
                bg: "bg-purple-50",
                ring: "hover:ring-purple-200",
                chart: "#8b5cf6",
            };

        default:
            return {
                text: "text-gray-500",
                bg: "bg-white",
                ring: "hover:ring-gray-200",
                chart: "#64748b",
            };
    }
}

/* =========================================================
   DEVICE CARD
========================================================= */
function DeviceCard({ device, onSelect, onEdit, onDelete }) {

    const { t } = useTranslation();
    const config = device.config || {};
    const isOnline = device.status === "online";
    const missing = isIncomplete(config);

    const roleStyle = getRoleColor(config);

    function getIcon(config) {

        if (config?.is_grid_source) {
            return "🔌";
        }

        switch (config?.role?.key) {

            case "producer":
                return "☀️";

            case "consumer":
                return "⚡";

            case "battery":
                return "🔋";

            default:
                return "🔧";
        }
    }

    return (
        <div
            onClick={() => onSelect(device)}
            className={`
                cursor-pointer
                border
                rounded-xl
                p-4
                shadow-sm
                transition
                hover:shadow-md
                hover:ring-2
                ${roleStyle.ring}
                ${missing
                    ? "border-yellow-300 bg-yellow-50"
                    : `border-gray-200 ${roleStyle.bg}`
                }
            `}
        >
            <div className="flex justify-between mb-2 items-start">

                <div>
                    <div className={`font-semibold flex items-center gap-2 ${roleStyle.text}`}>
                        {getIcon(config)}
                        {device.display_name}
                        {missing && <span className="text-yellow-600 text-sm">⚠</span>}
                    </div>

                    <div className="text-xs text-gray-400">
                        {device.identifier}
                    </div>
                </div>

                <div className="flex items-center gap-1.5">
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            onEdit(device);
                        }}
                        className="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-gray-100"
                        title={t("devices.setup_title", "Konfigurieren")}
                    >
                        ⚙️
                    </button>

                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            onDelete(device);
                        }}
                        className="text-gray-400 hover:text-rose-600 p-1 rounded hover:bg-gray-100"
                        title={t("nav.remove_device", "In den Papierkorb verschieben")}
                    >
                        🗑️
                    </button>

                    <div className={`w-2.5 h-2.5 rounded-full ml-1 ${isOnline ? "bg-green-500" : "bg-gray-300"}`} />
                </div>
            </div>

            <div className={`text-sm mb-2 ${roleStyle.text}`}>
                {
                    config.is_grid_source
                        ? t("devices.role_grid", "Netz")
                        : (config.role?.label || "–")
                }
            </div>

            <div className={`text-xl font-bold ${roleStyle.text}`}>
                {device.value != null ? (
                    `${device.value} ${device.unit || ""}`
                ) : device.status === "stale" ? (
                    <span className="text-gray-400">
                        {t("common.no_recent_data", "Keine aktuellen Daten")}
                    </span>
                ) : device.status === "offline" ? (
                    <span className="text-gray-400">
                        {t("common.offline", "Offline")}
                    </span>
                ) : (
                    <span className="text-gray-400">
                        {t("common.no_data", "Keine Daten")}
                    </span>
                )}
            </div>

            {device.sparkline?.length > 0 && (
                <div className="mt-1">
                    <KPISparklineECharts
                        values={device.sparkline}
                        color={roleStyle.chart}
                        unit={device.unit}
                    />
                </div>
            )}

            {missing && (
                <div className="text-xs text-yellow-700 mt-2">
                    {t("devices.incomplete_badge", "⚠ Unvollständig konfiguriert")}
                </div>
            )}
        </div>
    );
}

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
    }), [t]);

    const [chartDevice, setChartDevice] = useState(null);
    const [modalMode, setModalMode] = useState(null);
    const [editingDevice, setEditingDevice] = useState(null);
    const [openAddDevice, setOpenAddDevice] = useState(false);
    const [openRemoveDevice, setOpenRemoveDevice] = useState(false);
    const [openTrashBin, setOpenTrashBin] = useState(false);
    const trashQuery = useTrashCount();
    const trashCount = trashQuery?.data?.count ?? 0;

    function handleDeviceUpdated(device) {

        queryClient.setQueryData(
            ["devices"],
            old => old?.map(d =>
                d.id === device.id ? device : d
            ) || []
        );
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

    const activeRoles = useMemo(
        () =>
            settings.roles ?? [
                "producer",
                "consumer",
                "battery",
                "grid",
            ],
        [settings.roles]
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
        return <div className="p-6">{t("common.loading", "Lade Geräte…")}</div>;
    }

    return (
        <div className="p-6 max-w-6xl space-y-4">

            {/* TOP ACTION HEADER */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-2">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <span>📟</span> {t("devices.title", "Geräteübersicht")}
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">
                        {t("devices.subtitle", "Verwalte und überwache alle angeschlossenen Sensoren und Aktoren.")}
                    </p>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                    <button
                        onClick={() => setOpenTrashBin(true)}
                        className="px-3.5 py-2 rounded-xl border border-gray-200 hover:bg-gray-50 text-sm font-medium text-gray-700 flex items-center gap-1.5 transition"
                        title={t("nav.trash_bin", "Papierkorb")}
                    >
                        <span>♻️</span>
                        <span>{t("nav.trash_bin", "Papierkorb")}</span>
                        {trashCount > 0 && (
                            <span className="px-1.5 py-0.5 rounded-full bg-rose-100 text-rose-700 text-xs font-bold">
                                {trashCount}
                            </span>
                        )}
                    </button>

                    <button
                        onClick={() => setOpenRemoveDevice(true)}
                        className="px-3.5 py-2 rounded-xl border border-gray-200 hover:bg-rose-50 hover:border-rose-200 text-sm font-medium text-gray-700 hover:text-rose-600 flex items-center gap-1.5 transition"
                        title={t("nav.remove_device", "Geräte entfernen")}
                    >
                        <span>🗑️</span>
                        <span>{t("nav.remove_device", "Gerät entfernen")}</span>
                    </button>

                    <button
                        onClick={() => setOpenAddDevice(true)}
                        className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold shadow-xs flex items-center gap-1.5 transition"
                    >
                        <span>➕</span>
                        <span>{t("nav.add_device", "Neues Gerät")}</span>
                    </button>
                </div>
            </div>

            {/* FILTER BAR */}
            <div className="mb-3">

                <input
                    placeholder={t("devices.search_placeholder", "🔍 Gerät suchen...")}
                    value={filterText}
                    onChange={(e) => setFilterText(e.target.value)}
                    className="border px-3 py-2 rounded w-64"
                />

            </div>

            <div className="flex flex-wrap gap-2 mb-6">

                {/* STATUS */}
                {statusOptions.map(option => (

                    <button
                        key={option.key}
                        title={option.title}
                        onClick={() =>
                            saveSettings({
                                ...settings,
                                statusFilter:
                                    statusFilter === option.key
                                        ? null
                                        : option.key,
                            })
                        }

                        className={`
                            px-2.5 py-1
                            rounded-full
                            text-xs
                            border
                            flex items-center gap-1
                            transition
                            ${statusFilter === option.key
                                ? "bg-indigo-600 text-white border-indigo-600"
                                : "bg-white hover:bg-gray-50 border-gray-200"}
                        `}
                    >
                        <span>{option.icon}</span>
                        <span>{option.label}</span>
                        <span className="opacity-70">
                            ({statusStats[option.key] || 0})
                        </span>

                    </button>

                ))}

                {/* ROLE CHIPS */}
                {["producer", "consumer", "battery", "grid"].map(role => {

                    const active = activeRoles.includes(role);
                    const config = roleOptions[role];

                    return (
                        <button
                            key={role}
                            title={config.title}
                            onClick={() => {

                                const nextRoles =
                                    active
                                        ? activeRoles.filter(r => r !== role)
                                        : [...activeRoles, role];

                                saveSettings({
                                    ...settings,
                                    roles: nextRoles,
                                });

                            }}
                            className={`
                                px-2.5 py-1
                                rounded-full
                                text-xs
                                border
                                flex items-center gap-1
                                transition
                                ${active
                                    ? "bg-indigo-600 text-white border-indigo-600"
                                    : "bg-white hover:bg-gray-50 border-gray-200"}
                            `}
                        >
                            <span>{config.icon}</span>
                            <span>{config.label}</span>
                            <span className="opacity-70">
                                ({roleStats[role] || 0})
                            </span>
                        </button>
                    );

                })}

                {/* STRUCTURE TOGGLES */}

                <button
                    title="Geräte nach Etagen gruppieren"
                    onClick={() =>
                        saveSettings({
                            ...settings,
                            showFloors: !showFloors,
                        })
                    }
                    className={`
                        px-2.5 py-1
                        rounded-full
                        text-xs
                        border
                        flex items-center gap-1
                        transition
                        ${showFloors
                            ? "bg-indigo-600 text-white border-indigo-600"
                            : "bg-white hover:bg-gray-50 border-gray-200"}
                    `}
                >
                    🏢 {t("nav.floors", "Etagen")}
                </button>

                <button
                    title="Geräte nach Räumen gruppieren"
                    onClick={() =>
                        saveSettings({
                            ...settings,
                            showRooms: !showRooms,
                        })
                    }
                    className={`
                        px-2.5 py-1
                        rounded-full
                        text-xs
                        border
                        flex items-center gap-1
                        transition
                        ${showRooms
                            ? "bg-indigo-600 text-white border-indigo-600"
                            : "bg-white hover:bg-gray-50 border-gray-200"}
                    `}
                >
                    🚪 {t("structure.title", "Räume")}
                </button>

            </div>

            {/* BANNER */}
            {unconfiguredDevices.length > 0 && (
                <div
                    onClick={() => {
                        setModalMode("bulk");
                        setEditingDevice(null);
                    }}
                    className="mb-6 p-4 rounded-lg border border-yellow-300 bg-yellow-50 flex items-center justify-between cursor-pointer hover:bg-yellow-100"
                >
                    <div className="text-yellow-800 text-sm">
                        ⚠ {t("devices.unconfigured_banner", { count: unconfiguredDevices.length, defaultValue: `${unconfiguredDevices.length} Gerät(e) nicht vollständig konfiguriert` })}
                    </div>

                    <span className="text-sm text-white bg-yellow-500 px-3 py-1 rounded">
                        {t("devices.configure_now", "Jetzt konfigurieren")}
                    </span>
                </div>
            )}

            {/* GRID */}
            {Object.entries(grouped)
                .sort(([a], [b]) => a.localeCompare(b, "de"))
                .map(([floor, rooms]) => (

                    <div key={floor} className="mb-6">

                        {showFloors && (
                            <h2 className="text-sm text-gray-500 mb-2">{floor}</h2>
                        )}

                        {Object.entries(rooms)
                            .sort(([a], [b]) => a.localeCompare(b, "de"))
                            .map(([room, devices]) => (
                                <div key={room} className="mb-4">

                                    {showRooms && room !== "__ALL__" && (
                                        <h3 className="text-xs text-gray-400 mb-2">{room}</h3>
                                    )}

                                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                                        {[...devices]
                                            .sort((a, b) =>
                                                (a.display_name || "").localeCompare(
                                                    b.display_name || "",
                                                    "de"
                                                )
                                            )
                                            .map(d => (
                                                <DeviceCard
                                                    key={d.id}
                                                    device={d}
                                                    onSelect={setChartDevice}
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
