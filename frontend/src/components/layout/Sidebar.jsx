/*
# src/components/layout/Sidebar.jsx
*/

import { NavLink } from "react-router-dom";
import { useUnconfiguredDevices } from "../../hooks/useUnconfiguredDevices";
import { useState, useMemo } from "react";
import { useTranslation } from "react-i18next";
import DeviceSetupModal from "../device/DeviceSetupModal";

export default function Sidebar() {
    const { t } = useTranslation();
    const query = useUnconfiguredDevices();

    const isLoaded = query?.isSuccess;
    const count = query?.data?.count ?? 0;
    const [openSetup, setOpenSetup] = useState(false);

    const sections = useMemo(() => [
        {
            title: null,
            items: [
                { name: t("nav.dashboard", "Dashboard"), path: "/app/dashboard", icon: "🏠" },
            ],
        },
        {
            title: `📊 ${t("nav.analytics", "Analysen & Historie")}`,
            items: [
                { name: t("energy.energy_balance", "Energiebilanz"), path: "/app/energy", icon: "⚡" },
                { name: t("nav.solar_forecast", "Solar-Prognose"), path: "/app/solarforecast", icon: "☀️" },
                { name: t("nav.metrics", "Messwert-Explorer"), path: "/app/metrics", icon: "📈" },
            ],
        },
        {
            title: `🏡 ${t("nav.assets_group", "Anlagen & Gebäude")}`,
            items: [
                {
                    name: t("nav.all_devices", "Geräte"),
                    path: "/app/devices",
                    icon: "📟",
                    badge: count > 0 ? count : null,
                },
                { name: t("nav.producers", "Erzeugeranlagen"), path: "/app/producers", icon: "☀️" },
                { name: t("nav.floors", "Etagen & Räume"), path: "/app/structure", icon: "🏢" },
            ],
        },
        {
            title: `⚙️ ${t("nav.settings_group", "System & Tarife")}`,
            items: [
                { name: t("nav.tariffs", "Strompreise & Tarife"), path: "/app/tariff", icon: "💶" },
                { name: t("nav.mqtt_interfaces", "Schnittstellen & MQTT"), path: "/app/interfaces", icon: "📡" },
                { name: t("nav.app_settings", "Einstellungen"), path: "/app/settings", icon: "⚙️" },
            ],
        },
    ], [t, count]);

    return (
        <div className="w-64 bg-white border-r flex flex-col shrink-0">
            {/* ✅ Logo */}
            <div className="h-14 flex items-center px-4 border-b">
                <span className="font-bold text-lg bg-gradient-to-r from-indigo-500 to-purple-600 text-transparent bg-clip-text flex items-center gap-1.5">
                    <span>⚡</span> <span>Sharegy</span>
                </span>
            </div>

            {/* ✅ Navigation */}
            <div className="flex-1 overflow-y-auto p-3 space-y-5">
                {sections.map((section, idx) => (
                    <div key={idx}>
                        {/* Section Title */}
                        {section.title && (
                            <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider px-2.5 mb-1.5">
                                {section.title}
                            </div>
                        )}

                        {/* Items */}
                        <div className="space-y-1">
                            {section.items.map((item) => (
                                <NavLink
                                    key={item.path}
                                    to={item.path}
                                    className={({ isActive }) =>
                                        `flex items-center justify-between px-3 py-2 rounded-xl text-sm font-medium transition ${isActive
                                            ? "bg-indigo-50 text-indigo-700 font-semibold shadow-2xs"
                                            : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                                        }`
                                    }
                                >
                                    <div className="flex items-center gap-2.5 truncate">
                                        <span className="text-base">{item.icon}</span>
                                        <span className="truncate">{item.name}</span>
                                    </div>

                                    {/* Unconfigured Count Badge */}
                                    {item.badge && isLoaded && (
                                        <button
                                            onClick={(e) => {
                                                e.preventDefault();
                                                e.stopPropagation();
                                                setOpenSetup(true);
                                            }}
                                            title="Unkonfigurierte Geräte einrichten"
                                            className="text-[11px] font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full hover:bg-amber-200 transition"
                                        >
                                            {item.badge}
                                        </button>
                                    )}
                                </NavLink>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            {/* ✅ MODAL FOR UNCONFIGURED DEVICES */}
            <DeviceSetupModal
                open={openSetup}
                onClose={() => setOpenSetup(false)}
            />
        </div>
    );
}
