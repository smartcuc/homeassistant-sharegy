/*
# src/pages/StructurePage.jsx
*/

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
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

    // Group devices by Floor -> Room
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
            name: t("devices.no_floor", "Ohne Etage"),
            rooms: {},
            unassignedDevices: [],
        };

        // Assign devices to floors & rooms
        devices.forEach((dev) => {
            const config = dev.config || {};
            const floorId = config.floor?.id || "unassigned";
            const floorName = config.floor?.name || t("devices.no_floor", "Ohne Etage");
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

        return Object.values(floorMap).filter((f) => {
            // Keep floors that have rooms or devices, or are official floors
            return Object.keys(f.rooms).length > 0 || f.unassignedDevices.length > 0 || f.id !== "unassigned";
        });
    }, [devices, floors, t]);

    // Stats
    const totalFloorsCount = floors.length;
    const totalRoomsCount = rooms.length;
    const assignedDevicesCount = devices.filter((d) => d.config?.room && d.config?.floor).length;
    const unassignedDevicesCount = devices.length - assignedDevicesCount;

    return (
        <div className="p-6 space-y-6 max-w-7xl">
            {/* HEADER */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <span>🏡</span> {t("structure.title", "Etagen & Räume")}
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">
                        {t("structure.subtitle", "Strukturiere deine Gebäude und ordne Geräte Räumen zu.")}
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    <input
                        type="text"
                        placeholder={t("common.search", "Suchen...")}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="px-3.5 py-2 border rounded-xl text-sm w-48 sm:w-64"
                    />
                </div>
            </div>

            {/* KPI STATS */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-xs">
                    <div className="text-xs font-semibold uppercase text-gray-500">
                        {t("structure.title", "Etagen")}
                    </div>
                    <div className="text-2xl font-bold text-gray-900 mt-1">
                        {totalFloorsCount}
                    </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-xs">
                    <div className="text-xs font-semibold uppercase text-gray-500">
                        Räume
                    </div>
                    <div className="text-2xl font-bold text-gray-900 mt-1">
                        {totalRoomsCount}
                    </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-xs">
                    <div className="text-xs font-semibold uppercase text-gray-500">
                        Zugeordnet
                    </div>
                    <div className="text-2xl font-bold text-emerald-600 mt-1">
                        {assignedDevicesCount} <span className="text-xs text-gray-400 font-normal">/ {devices.length}</span>
                    </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-xs">
                    <div className="text-xs font-semibold uppercase text-gray-500">
                        Offene Zuordnungen
                    </div>
                    <div className="text-2xl font-bold text-amber-600 mt-1">
                        {unassignedDevicesCount}
                    </div>
                </div>
            </div>

            {/* BUILDING HIERARCHY CARDS */}
            <div className="space-y-6">
                {structureTree.map((floor) => {
                    const roomList = Object.values(floor.rooms);
                    const totalFloorDevices =
                        roomList.reduce((acc, r) => acc + r.devices.length, 0) + floor.unassignedDevices.length;

                    return (
                        <div key={floor.id} className="bg-white border border-gray-200 rounded-2xl p-5 shadow-xs">
                            {/* Floor Title */}
                            <div className="flex items-center justify-between border-b pb-3 mb-4">
                                <div className="flex items-center gap-2">
                                    <span className="text-lg">🏢</span>
                                    <h2 className="text-base font-bold text-gray-900">{floor.name}</h2>
                                    <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-semibold">
                                        {totalFloorDevices} {totalFloorDevices === 1 ? "Gerät" : "Geräte"}
                                    </span>
                                </div>
                            </div>

                            {/* Rooms Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {roomList.map((room) => (
                                    <div
                                        key={room.id}
                                        className="bg-slate-50/80 border border-slate-200/70 rounded-xl p-4 space-y-3"
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="font-semibold text-sm text-gray-800 flex items-center gap-1.5">
                                                <span>🚪</span>
                                                <span>{room.name}</span>
                                            </div>
                                            <span className="text-xs text-gray-400 font-medium">
                                                {room.devices.length} {room.devices.length === 1 ? "Gerät" : "Geräte"}
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
                                                        className="flex items-center justify-between p-2 bg-white rounded-lg border border-gray-100 hover:border-indigo-300 hover:shadow-xs transition cursor-pointer text-xs"
                                                    >
                                                        <div className="flex items-center gap-1.5 truncate">
                                                            <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
                                                            <span className="font-medium text-gray-800 truncate">
                                                                {dev.display_name || dev.identifier}
                                                            </span>
                                                        </div>
                                                        <div className="font-mono font-semibold text-gray-700 shrink-0 ml-2">
                                                            {power !== null && power !== undefined ? `${Number(power).toFixed(0)} W` : "-"}
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                ))}

                                {/* Unassigned to Room in this Floor */}
                                {floor.unassignedDevices.length > 0 && (
                                    <div className="bg-amber-50/50 border border-amber-200/60 rounded-xl p-4 space-y-3">
                                        <div className="flex items-center justify-between">
                                            <div className="font-semibold text-sm text-amber-800 flex items-center gap-1.5">
                                                <span>⚠️</span>
                                                <span>{t("devices.no_room", "Ohne Raum")}</span>
                                            </div>
                                            <span className="text-xs text-amber-600 font-medium">
                                                {floor.unassignedDevices.length}
                                            </span>
                                        </div>

                                        <div className="space-y-1.5">
                                            {floor.unassignedDevices.map((dev) => (
                                                <div
                                                    key={dev.id}
                                                    onClick={() => setSelectedDeviceForSetup(dev)}
                                                    className="flex items-center justify-between p-2 bg-white rounded-lg border border-amber-200 hover:border-amber-400 hover:shadow-xs transition cursor-pointer text-xs"
                                                >
                                                    <span className="font-medium text-gray-800 truncate">
                                                        {dev.display_name || dev.identifier}
                                                    </span>
                                                    <span className="text-[11px] text-amber-700 font-medium">
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
