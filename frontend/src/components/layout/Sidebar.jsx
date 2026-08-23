import { NavLink } from "react-router-dom";
import { useUnconfiguredDevices } from "../../hooks/useUnconfiguredDevices";
import { useState, useMemo } from "react";
import { useTranslation } from "react-i18next";
import DeviceSetupModal from "../device/DeviceSetupModal";
import AddDeviceModal from "../device/AddDeviceModal";
import RemoveDevicesModal from "../device/RemoveDevicesModal";
import TrashBinModal from "../device/TrashBinModal";
import { useTrashCount } from "../../hooks/useTrashDevices";

export default function Sidebar() {
    const { t } = useTranslation();
    const query = useUnconfiguredDevices();

    const isLoaded = query?.isSuccess;
    const count = query?.data?.count ?? 0;
    const [openSetup, setOpenSetup] = useState(false);
    const [openAddDevice, setOpenAddDevice] = useState(false);
    const [openRemoveDevice, setOpenRemoveDevice] = useState(false);
    const [openTrashBin, setOpenTrashBin] = useState(false);

    const trashQuery = useTrashCount();
    const trashCount = trashQuery?.data?.count ?? 0;

    const sections = useMemo(() => [
        {
            title: null,
            items: [
                { name: t("nav.dashboard", "Dashboard"), path: "/app/dashboard", icon: "🏠" },
            ],
        },
        {
            title: t("nav.energy", "Energy"),
            items: [
                { name: t("nav.overview", "Overview"), path: "/app/energy", icon: "⚡" },
            ],
        },
        {
            title: t("nav.devices", "Devices"),
            items: [
                { name: t("nav.all_devices", "All Devices"), path: "/app/devices", icon: "📟" },
                { name: t("nav.add_device", "Add Device"), action: "add_device", icon: "➕" },
                { name: t("nav.remove_device", "Remove Device"), action: "remove_device", icon: "🗑️" },
                { name: t("nav.trash_bin", "Trash Bin"), action: "trash_bin", icon: "♻️" },
            ],
        },
        {
            title: `📡 ${t("nav.monitoring", "Monitoring")}`,
            items: [
                { name: t("nav.floors", "Floors"), path: "/app/structure", icon: "🏡" },
            ],
        },
        {
            title: `📊 ${t("nav.analytics", "Analytics")}`,
            items: [
                { name: t("nav.solar_forecast", "Solar Forecast"), path: "/app/solarforecast", icon: "☀️" },
                { name: t("nav.metrics", "Metrics"), path: "/app/metrics", icon: "📊" },
            ],
        },
        {
            title: `⚙️ ${t("nav.settings_group", "Einstellungen")}`,
            items: [
                {
                    name: t("nav.producers", "Erzeuger"),
                    path: "/app/producers",
                    icon: "☀️",
                },
                {
                    name: t("nav.tariffs", "Strompreise & Tarife"),
                    path: "/app/tariff",
                    icon: "💶",
                },
                {
                    name: t("nav.mqtt_interfaces", "MQTT & Schnittstellen"),
                    path: "/app/settings#mqtt",
                    icon: "📡",
                },
                {
                    name: t("nav.app_settings", "App-Einstellungen"),
                    path: "/app/settings",
                    icon: "⚙️",
                },
            ],
        },
    ], [t]);


    return (
        <div className="w-64 bg-white border-r flex flex-col">

            {/* ✅ Logo */}
            <div className="h-14 flex items-center px-4 border-b">
                <span className="font-bold text-lg bg-gradient-to-r from-indigo-500 to-purple-600 text-transparent bg-clip-text">
                    ⚡ Sharegy
                </span>
            </div>

            {/* ✅ Navigation */}
            <div className="flex-1 overflow-auto p-3 space-y-4">


                {sections.map((section, idx) => (
                    <div key={idx}>

                        {/* Section Title */}
                        {section.title && (
                            <div className="text-xs text-gray-400 uppercase px-2 mb-1">
                                {section.title}
                            </div>
                        )}

                        {/* Items */}
                        <div className="space-y-1">
                            {section.items.map((item) => (

                                item.action === "add_device" ? (

                                    <button
                                        onClick={() => setOpenAddDevice(true)}  // ✅ HIER    key="add"
                                        className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded w-full text-left"
                                    >
                                        <span>{item.icon}</span>
                                        {item.name}
                                    </button>

                                ) : item.action === "remove_device" ? (

                                    <button
                                        key="remove"
                                        onClick={() => setOpenRemoveDevice(true)}
                                        className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded w-full text-left"
                                    >
                                        <span>{item.icon}</span>
                                        {item.name}
                                    </button>

                                ) : item.action === "trash_bin" ? (
                                    <button
                                        key="trash"
                                        onClick={() => setOpenTrashBin(true)}
                                        className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded w-full text-left"
                                    >

                                        <span>{item.icon}</span>

                                        <span>{item.name}</span>

                                        {trashCount > 0 && (
                                            <span className="ml-auto text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                                                {trashCount}
                                            </span>
                                        )}
                                    </button>
                                ) : (
                                    <NavLink
                                        key={item.path}
                                        to={item.path}
                                        className={({ isActive }) =>
                                            `flex items-center gap-2 px-3 py-2 rounded text-sm transition ${isActive
                                                ? "bg-indigo-100 text-indigo-700"
                                                : "text-gray-600 hover:bg-gray-100"
                                            }`
                                        }
                                    >
                                        <span>{item.icon}</span>
                                        <span>{item.name}</span>

                                        {/* ✅ Badge */}
                                        {item.path === "/app/devices" && isLoaded && count > 0 && (

                                            <button
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    e.stopPropagation();
                                                    setOpenSetup(true);
                                                }}
                                                className="ml-auto text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full hover:bg-yellow-200"
                                            >
                                                {count}
                                            </button>

                                        )}

                                    </NavLink>

                                )
                            ))}
                        </div>

                    </div>
                ))}

            </div>

            {/* ✅ MODAL */}
            <DeviceSetupModal
                open={openSetup}
                onClose={() => setOpenSetup(false)}
            />

            <AddDeviceModal
                open={openAddDevice}
                onClose={() => setOpenAddDevice(false)}
            />

            <RemoveDevicesModal
                open={openRemoveDevice}
                onClose={() => setOpenRemoveDevice(false)}
            />

            <TrashBinModal
                key={openTrashBin ? "open" : "closed"}
                open={openTrashBin}
                onClose={() => setOpenTrashBin(false)}
            />

        </div>
    );
}
