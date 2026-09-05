/*
# src/pages/StructurePage.jsx
*/

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { apiFetch } from "../api/client";
import DeviceSetupModal from "../components/device/DeviceSetupModal";

export default function StructurePage() {
    const { t } = useTranslation();
    const [selectedDeviceForSetup, setSelectedDeviceForSetup] = useState(null);
    const [searchQuery, setSearchQuery] = useState("");

    // Devices & Structure
    const devicesQuery = useQuery({
        queryKey: ["devices"],
        queryFn: () => apiFetch("/api/devices/"),
        refetchInterval: 5000,
    });

    const setupOptionsQuery = useQuery({
        queryKey: ["setup-options"],
        queryFn: () => apiFetch("/api/devices/setup-options/"),
    });

    const valuesQuery = useQuery({
        queryKey: ["device-dashboard-values"],
        queryFn: () => apiFetch("/api/devices/dashboard/"),
        refetchInterval: 3000,
    });

    const devices = useMemo(() => devicesQuery.data || [], [devicesQuery.data]);
    const floors = useMemo(() => setupOptionsQuery.data?.floors || [], [setupOptionsQuery.data?.floors]);
    const rooms = useMemo(() => setupOptionsQuery.data?.rooms || [], [setupOptionsQuery.data?.rooms]);

    const valueMap = useMemo(() => {
        const map = {};
        if (Array.isArray(valuesQuery.data)) {
            valuesQuery.data.forEach((v) => {
                map[v.device] = v;
            });
        }
        return map;
    }, [valuesQuery.data]);

    // Group devices by Floor -> Room (Nur Etagen anzeigen, auf denen mindestens 1 Gerät liegt!)
    const structureTree = useMemo(() => {
        const floorMap = {};

        // Pre-fill known floors
        floors.forEach((f) => {
            floorMap[f.id] = {
                id: f.id,
                name: f.name,
                rooms: {},
                unassignedDevices: [],
            };
        });

        // "Ohne Etage" bucket
        floorMap["unassigned"] = {
            id: "unassigned",
            name: t("devices.no_floor", "Ohne Etage (Nicht zugewiesen)"),
            rooms: {},
            unassignedDevices: [],
        };

        // Assign devices to floors & rooms
        devices.forEach((dev) => {
            const config = dev.config || {};
            const floorId = config.floor?.id || "unassigned";
            const floorName = config.floor?.name || t("devices.no_floor", "Ohne Etage (Nicht zugewiesen)");
            const roomId = config.room?.id || "unassigned";
            const roomName = config.room?.name || t("devices.no_room", "Ohne Raum");

            if (!floorMap[floorId]) {
                floorMap[floorId] = {
                    id: floorId,
                    name: floorName,
                    rooms: {},
                    unassignedDevices: [],
                };
            }

            const currentFloor = floorMap[floorId];

            if (roomId === "unassigned") {
                currentFloor.unassignedDevices.push(dev);
            } else {
                if (!currentFloor.rooms[roomId]) {
                    currentFloor.rooms[roomId] = {
                        id: roomId,
                        name: roomName,
                        devices: [],
                    };
                }
                currentFloor.rooms[roomId].devices.push(dev);
            }
        });

        // 🎯 FILTER: Nur Etagen behalten, die mindestens 1 Gerät enthalten!
        return Object.values(floorMap).filter((f) => {
            const roomDevicesCount = Object.values(f.rooms).reduce(
                (acc, r) => acc + (r.devices?.length || 0),
                0
            );
            const totalDevices = roomDevicesCount + (f.unassignedDevices?.length || 0);

            // Wenn Suchfilter aktiv ist, prüfen wir auch den Namen
            if (searchQuery.trim()) {
                const query = searchQuery.toLowerCase();
                const matchesFloor = f.name.toLowerCase().includes(query);
                const matchesRoom = Object.values(f.rooms).some(r => r.name.toLowerCase().includes(query));
                const matchesDev = f.unassignedDevices.some(d => (d.display_name || d.identifier || "").toLowerCase().includes(query)) ||
                    Object.values(f.rooms).some(r => r.devices.some(d => (d.display_name || d.identifier || "").toLowerCase().includes(query)));

                return totalDevices > 0 && (matchesFloor || matchesRoom || matchesDev);
            }

            return totalDevices > 0;
        });
    }, [devices, floors, searchQuery, t]);

    // Stats
    const activeFloorsCount = structureTree.filter((f) => f.id !== "unassigned").length;
    const activeRoomsCount = structureTree.reduce((acc, f) => acc + Object.keys(f.rooms).length, 0);
    const assignedDevicesCount = devices.filter((d) => d.config?.room && d.config?.floor).length;
    const unassignedDevicesCount = devices.length - assignedDevicesCount;

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* HEADER */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                        <span>🏡</span> {t("structure.title", "Etagen & Räume")}
                    </h1>
                    <p className="text-sm text-gray-500 dark:text-slate-400 mt-1">
                        {t("structure.subtitle", "Übersicht aller belegten Etagen, Räume und zugeordneten Smart Devices.")}
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    <input
                        type="text"
                        placeholder={t("common.search", "Suchen (Etage, Raum, Gerät)...")}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="px-3.5 py-2 border border-slate-200 dark:border-slate-700 rounded-xl text-sm w-48 sm:w-72 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 shadow-2xs focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                    />
                </div>
            </div>

            {/* KPI STATS */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-xs">
                    <div className="text-xs font-semibold uppercase text-gray-500 dark:text-slate-400">
                        Belegte Etagen
                    </div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                        {activeFloorsCount} <span className="text-xs text-gray-400 dark:text-slate-500 font-normal">/ {floors.length} verfügbar</span>
                    </div>
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-xs">
                    <div className="text-xs font-semibold uppercase text-gray-500 dark:text-slate-400">
                        Belegte Räume
                    </div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                        {activeRoomsCount} <span className="text-xs text-gray-400 dark:text-slate-500 font-normal">/ {rooms.length} verfügbar</span>
                    </div>
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-xs">
                    <div className="text-xs font-semibold uppercase text-gray-500 dark:text-slate-400">
                        Zugeordnet
                    </div>
                    <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
                        {assignedDevicesCount} <span className="text-xs text-gray-400 dark:text-slate-500 font-normal">/ {devices.length} Geräte</span>
                    </div>
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-xs">
                    <div className="text-xs font-semibold uppercase text-gray-500 dark:text-slate-400">
                        Offene Zuordnungen
                    </div>
                    <div className="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1">
                        {unassignedDevicesCount}
                    </div>
                </div>
            </div>

            {/* BUILDING HIERARCHY CARDS */}
            {structureTree.length === 0 ? (
                <div className="bg-white dark:bg-slate-900 border border-dashed border-slate-300 dark:border-slate-700 rounded-2xl p-8 text-center space-y-3">
                    <div className="text-4xl">🏢</div>
                    <h3 className="font-bold text-base text-gray-900 dark:text-white">
                        {searchQuery ? "Keine passenden Geräte oder Etagen gefunden" : "Noch keine Geräte auf Etagen zugeordnet"}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-slate-400 max-w-md mx-auto">
                        {searchQuery
                            ? "Passe deinen Suchbegriff an oder setze die Suche zurück."
                            : "Ordne deine Smart-Plugs, Zähler und Wechselrichter unter 'Geräte' Räumen und Etagen zu, um sie hier übersichtlich zu gruppieren."}
                    </p>
                    <div className="pt-2">
                        {searchQuery ? (
                            <button
                                onClick={() => setSearchQuery("")}
                                className="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-semibold rounded-xl transition cursor-pointer"
                            >
                                Suche zurücksetzen
                            </button>
                        ) : (
                            <Link
                                to="/app/devices"
                                className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-xl shadow-xs transition"
                            >
                                <span>⚡</span> Zu den Geräten
                            </Link>
                        )}
                    </div>
                </div>
            ) : (
                <div className="space-y-6">
                    {structureTree.map((floor) => {
                        const roomList = Object.values(floor.rooms);
                        const totalFloorDevices =
                            roomList.reduce((acc, r) => acc + r.devices.length, 0) + floor.unassignedDevices.length;

                        return (
                            <div key={floor.id} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs">
                                {/* Floor Title */}
                                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3 mb-4">
                                    <div className="flex items-center gap-2">
                                        <span className="text-lg">
                                            {floor.id === "unassigned" ? "📦" : "🏢"}
                                        </span>
                                        <h2 className="text-base font-bold text-gray-900 dark:text-white">{floor.name}</h2>
                                        <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-semibold">
                                            {t("structure.devices_count", {
                                                count: totalFloorDevices,
                                                defaultValue: `${totalFloorDevices} ${totalFloorDevices === 1 ? "Gerät" : "Geräte"}`,
                                            })}
                                        </span>
                                    </div>
                                </div>

                                {/* Rooms Grid */}
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {roomList.map((room) => (
                                        <div
                                            key={room.id}
                                            className="bg-slate-50/80 dark:bg-slate-800/40 border border-slate-200/70 dark:border-slate-700/60 rounded-xl p-4 space-y-3"
                                        >
                                            <div className="flex items-center justify-between">
                                                <div className="font-semibold text-sm text-gray-800 dark:text-slate-200 flex items-center gap-1.5">
                                                    <span>🚪</span>
                                                    <span>{room.name}</span>
                                                </div>
                                                <span className="text-xs text-gray-400 dark:text-slate-500 font-medium">
                                                    {t("structure.devices_count", {
                                                        count: room.devices.length,
                                                        defaultValue: `${room.devices.length} ${room.devices.length === 1 ? "Gerät" : "Geräte"}`,
                                                    })}
                                                </span>
                                            </div>

                                            {/* Device Pills */}
                                            <div className="space-y-1.5">
                                                {room.devices.map((dev) => {
                                                    const devVals = valueMap[dev.id] || {};
                                                    const power = devVals.value !== undefined ? devVals.value : devVals.power;

                                                    return (
                                                        <div
                                                            key={dev.id}
                                                            onClick={() => setSelectedDeviceForSetup(dev)}
                                                            className="flex items-center justify-between p-2 bg-white dark:bg-slate-800 rounded-lg border border-gray-100 dark:border-slate-700/60 hover:border-indigo-300 dark:hover:border-indigo-500 hover:shadow-xs transition cursor-pointer text-xs"
                                                        >
                                                            <div className="flex items-center gap-1.5 truncate">
                                                                <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
                                                                <span className="font-medium text-gray-800 dark:text-slate-200 truncate">
                                                                    {dev.display_name || dev.identifier}
                                                                </span>
                                                            </div>
                                                            <div className="font-mono font-semibold text-gray-700 dark:text-slate-300 shrink-0 ml-2">
                                                                {power !== null && power !== undefined
                                                                    ? `${Number(power).toFixed(0)} W`
                                                                    : "-"}
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    ))}

                                    {/* Unassigned to Room in this Floor */}
                                    {floor.unassignedDevices.length > 0 && (
                                        <div className="bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-800/40 rounded-xl p-4 space-y-3">
                                            <div className="flex items-center justify-between">
                                                <div className="font-semibold text-sm text-amber-800 dark:text-amber-300 flex items-center gap-1.5">
                                                    <span>⚠️</span>
                                                    <span>{t("devices.no_room", "Ohne Raum")}</span>
                                                </div>
                                                <span className="text-xs text-amber-600 dark:text-amber-400 font-medium">
                                                    {floor.unassignedDevices.length}
                                                </span>
                                            </div>

                                            <div className="space-y-1.5">
                                                {floor.unassignedDevices.map((dev) => (
                                                    <div
                                                        key={dev.id}
                                                        onClick={() => setSelectedDeviceForSetup(dev)}
                                                        className="flex items-center justify-between p-2 bg-white dark:bg-slate-800 rounded-lg border border-amber-200 dark:border-amber-800/60 hover:border-amber-400 hover:shadow-xs transition cursor-pointer text-xs"
                                                    >
                                                        <span className="font-medium text-gray-800 dark:text-slate-200 truncate">
                                                            {dev.display_name || dev.identifier}
                                                        </span>
                                                        <span className="text-[11px] text-amber-700 dark:text-amber-400 font-medium">
                                                            Raum zuweisen →
                                                        </span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* SETUP MODAL */}
            {selectedDeviceForSetup && (
                <DeviceSetupModal
                    open={true}
                    mode="single"
                    singleDevice={selectedDeviceForSetup}
                    onClose={() => setSelectedDeviceForSetup(null)}
                    onDeviceUpdated={() => {
                        devicesQuery.refetch();
                    }}
                />
            )}
        </div>
    );
}
