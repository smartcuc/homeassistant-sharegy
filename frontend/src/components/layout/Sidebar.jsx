/*
# src/components/layout/Sidebar.jsx
*/

import { NavLink } from "react-router-dom";
import { useUnconfiguredDevices } from "../../hooks/useUnconfiguredDevices";
import { useUser } from "../../hooks/useUser";
import { useState, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../../api/client";
import DeviceSetupModal from "../device/DeviceSetupModal";
import { useSubscription } from "../../hooks/useSubscription";
import ProBadge from "../common/ProBadge";

export default function Sidebar() {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const { user, isStaffOrAdmin, hasCommunityAdminAccess } = useUser();
    const hasTenantAccess = hasCommunityAdminAccess;
    const query = useUnconfiguredDevices();

    const isLoaded = query?.isSuccess;
    const count = query?.data?.count ?? 0;
    const [openSetup, setOpenSetup] = useState(false);

    // 🚨 Aktive Haushalts-Alarme (Alarmzentrale)
    const alertsQuery = useQuery({
        queryKey: ["alerts-list"],
        queryFn: () => apiFetch("/api/alerts/"),
        refetchInterval: 30000,
    });

    const alertSummary = alertsQuery?.data?.summary || { critical: 0, warning: 0, info: 0, active_total: 0 };
    const alertCount = alertSummary.active_total;
    const alertBadgeClass = alertSummary.critical > 0
        ? "bg-rose-100 text-rose-700 border-rose-200 animate-pulse"
        : alertSummary.warning > 0
            ? "bg-amber-100 text-amber-800 border-amber-200"
            : "bg-emerald-100 text-emerald-800 border-emerald-200";

    const sections = useMemo(() => {
        const sec = [
            {
                title: null,
                items: [
                    { name: t("nav.dashboard", "Dashboard"), path: "/app/dashboard", icon: "🏠" },
                ],
            },
            {
                title: `📊 ${t("nav.analytics", "Analysen & Monitoring")}`,
                items: [
                    { name: t("energy.energy_balance", "Energiebilanz"), path: "/app/energy", icon: "⚡" },
                    { name: t("nav.solar_forecast", "Solar-Prognose"), path: "/app/solarforecast", icon: "☀️" },
                    {
                        name: t("nav.alerts", "Alarmzentrale"),
                        path: "/app/alerts",
                        icon: "🚨",
                        isProGated: true,
                        badge: isPro && alertCount > 0 ? alertCount : null,
                        badgeClass: alertBadgeClass,
                    },
                    { name: t("nav.metrics", "Messwert-Explorer"), path: "/app/metrics", icon: "📈" },
                ],
            },
            {
                title: `🎛️ ${t("nav.assets_group", "Steuerung & Geräte")}`,
                items: [
                    {
                        name: t("nav.energy_control", "Energiesteuerung (HEMS)"),
                        path: "/app/control",
                        icon: "🎛️",
                        isProGated: true,
                    },
                    {
                        name: t("nav.mobility", "E-Mobilität & Fuhrpark"),
                        path: "/app/mobility",
                        icon: "🚗",
                        isProGated: true,
                    },
                    {
                        name: t("nav.heating_climate", "Wärme & Raumklima"),
                        path: "/app/heating",
                        icon: "🌡️",
                        isProGated: true,
                    },
                    {
                        name: t("nav.all_devices", "Geräteübersicht"),
                        path: "/app/devices",
                        icon: "📟",
                        badge: count > 0 ? count : null,
                        isDeviceSetupBadge: true,
                    },
                    { name: t("nav.producers", "Erzeuger & Speicher"), path: "/app/producers", icon: "🔋" },
                    ...(hasTenantAccess && !isStaffOrAdmin
                        ? [{ name: t("nav.tenant_management", "Community & Mieter"), path: "/app/tenant", icon: "👥" }]
                        : []),
                ],
            },
            {
                title: `⚙️ ${t("nav.settings_group", "Systemeinstellungen")}`,
                items: [
                    { name: t("nav.tariffs", "Strompreise & Tarife"), path: "/app/tariff", icon: "💶" },
                    { name: t("nav.mqtt_interfaces", "Schnittstellen"), path: "/app/interfaces", icon: "📡" },
                    { name: t("nav.system_status", "Systemstatus (Server)"), path: "/app/status", icon: "🌐" },
                ],
            },

        ];

        // 🛡️ ADMIN & STAFF SECTION
        if (isStaffOrAdmin) {
            sec.push({
                title: `🛡️ ${t("nav.admin_group", "Administration & Staff")}`,
                items: [
                    { name: t("nav.agent_support_hub", "Support-Zentrale (Triage)"), path: "/app/support-hub", icon: "🛟" },
                    { name: t("nav.admin_dashboard", "Admin Dashboard"), path: "/app/admin/dashboard", icon: "📊" },
                    { name: t("nav.admin_tracking", "Event & Tracking"), path: "/app/admin/tracking", icon: "📈" },
                    { name: t("nav.tenant_management", "Mandanten & Mieter"), path: "/app/tenant", icon: "👥" },
                    {
                        name: "Django Backend",
                        path: "/admin/",
                        icon: "⚙️",
                        isExternal: true,
                    },
                ],
            });
        }

        return sec;
    }, [t, count, alertCount, alertBadgeClass, isStaffOrAdmin, hasTenantAccess, isPro]);

    return (
        <div className="hidden md:flex w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex-col shrink-0 transition-colors">
            {/* ✅ Logo -> Link zur Homepage */}
            <div className="h-14 flex items-center px-4 border-b border-slate-200 dark:border-slate-800">
                <NavLink
                    to="/"
                    title="Zur sharegy Startseite & Info"
                    className="font-bold text-lg bg-gradient-to-r from-indigo-500 to-purple-600 text-transparent bg-clip-text flex items-center gap-1.5 hover:opacity-80 transition cursor-pointer"
                >
                    <span>⚡</span> <span className="font-mono tracking-tight lowercase">sharegy</span>
                </NavLink>
            </div>

            {/* ✅ Navigation */}
            <div className="flex-1 overflow-y-auto p-3 space-y-5">
                {sections.map((section, idx) => (
                    <div key={idx}>
                        {/* Section Title */}
                        {section.title && (
                            <div className="text-[11px] font-semibold text-gray-400 dark:text-slate-500 uppercase tracking-wider px-2.5 mb-1.5">
                                {section.title}
                            </div>
                        )}

                        {/* Items */}
                        <div className="space-y-1">
                            {section.items.map((item, itemIdx) => {
                                if (item.isExternal) {
                                    return (
                                        <a
                                            key={item.path || itemIdx}
                                            href={item.path}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="flex items-center justify-between px-3 py-2 rounded-xl text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-800 hover:text-gray-900 dark:hover:text-white transition gap-2"
                                        >
                                            <div className="flex items-center gap-2.5 min-w-0 flex-1 truncate">
                                                <span className="text-base shrink-0">{item.icon}</span>
                                                <span className="truncate">{item.name}</span>
                                            </div>
                                            <span className="text-xs text-gray-400 dark:text-gray-500 shrink-0">↗</span>
                                        </a>
                                    );
                                }

                                return (
                                    <NavLink
                                        key={item.path}
                                        to={item.path}
                                        className={({ isActive }) =>
                                            `flex items-center justify-between px-3 py-2 rounded-xl text-sm font-medium transition gap-2 ${isActive
                                                ? "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-semibold shadow-2xs border border-indigo-100 dark:border-indigo-900/50"
                                                : "text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-800 hover:text-gray-900 dark:hover:text-white"
                                            }`
                                        }
                                    >
                                        <div className="flex items-center gap-2.5 min-w-0 flex-1 truncate">
                                            <span className="text-base shrink-0">{item.icon}</span>
                                            <span className="truncate">{item.name}</span>
                                            {item.isProGated && !isPro && <ProBadge size="xs" />}
                                        </div>

                                        {/* Unconfigured Count Badge vs Alert Badge */}
                                        {item.badge && (
                                            item.isDeviceSetupBadge && isLoaded ? (
                                                <button
                                                    onClick={(e) => {
                                                        e.preventDefault();
                                                        e.stopPropagation();
                                                        setOpenSetup(true);
                                                    }}
                                                    title="Unkonfigurierte Geräte einrichten"
                                                    className="text-[11px] font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full hover:bg-amber-200 transition shrink-0"
                                                >
                                                    {item.badge}
                                                </button>
                                            ) : (
                                                <span
                                                    className={`text-[11px] font-bold px-2 py-0.5 rounded-full border shrink-0 max-w-[85px] truncate ${item.badgeClass || "bg-indigo-100 text-indigo-800 border-indigo-200"}`}
                                                >
                                                    {item.badge}
                                                </span>
                                            )
                                        )}
                                    </NavLink>
                                );
                            })}
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
