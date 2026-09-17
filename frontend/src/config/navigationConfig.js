/*
# frontend/src/config/navigationConfig.js
# Zentrale deklarative Konfiguration aller Navigations-Items und Rollen-/Modus-Filter
*/

export const NAV_MODES = {
    EMS_ONLY: "ems_only",         // User 1: Nur EMS (Eigenheim / Prosumer ohne Community)
    SHARING_ONLY: "sharing_only", // User 2: Nur Energy-Sharing (Mieter in WEG / Community-Consumer)
    HYBRID: "hybrid",             // User 3: Beides (EMS Prosumer + Energy Sharing)
    PARTNER: "partner",           // Partner / Installateur Flotten-Management
    ADMIN: "admin",               // Plattform- & Mandanten-Administration
};

export const MODE_METADATA = {
    [NAV_MODES.EMS_ONLY]: {
        id: NAV_MODES.EMS_ONLY,
        labelKey: "nav.mode_ems",
        defaultLabel: "Privates EMS",
        icon: "🏠",
        description: "PV-Anlage, Heimspeicher, Wallbox & Börsenstrom",
        defaultPath: "/app/dashboard",
    },
    [NAV_MODES.SHARING_ONLY]: {
        id: NAV_MODES.SHARING_ONLY,
        labelKey: "nav.mode_sharing",
        defaultLabel: "Community & Mieterstrom",
        icon: "🏢",
        description: "Mein Verbrauch, Solarstrom-Anteil & Monatsabrechnungen",
        defaultPath: "/app/tenant",
    },
    [NAV_MODES.HYBRID]: {
        id: NAV_MODES.HYBRID,
        labelKey: "nav.mode_hybrid",
        defaultLabel: "EMS & Community Hub",
        icon: "⚡",
        description: "Kombinierte Ansicht: Eigenes EMS & Energy Sharing",
        defaultPath: "/app/dashboard",
    },
    [NAV_MODES.PARTNER]: {
        id: NAV_MODES.PARTNER,
        labelKey: "nav.mode_partner",
        defaultLabel: "Partner-Cockpit",
        icon: "🔧",
        description: "Kunden-Flottenübersicht, Onboarding & Diagnostik",
        defaultPath: "/app/partner",
    },
    [NAV_MODES.ADMIN]: {
        id: NAV_MODES.ADMIN,
        labelKey: "nav.mode_admin",
        defaultLabel: "Admin-Zentrale",
        icon: "🛡️",
        description: "Mandanten, Support-Zentrale & Systemverwaltung",
        defaultPath: "/app/admin/dashboard",
    },
};

/**
 * Erzeugt die gefilterten Navigations-Abschnitte für die Desktop-Sidebar und das Mobile Menü.
 */
export function getNavigationSections({
    activeMode = NAV_MODES.EMS_ONLY,
    t = (k, def) => def,
    isPro = false,
    alertCount = 0,
    alertBadgeClass = "",
    unconfiguredDevicesCount = 0,
    isStaffOrAdmin = false,
    hasCommunityAdminAccess = false,
}) {
    const sections = [];

    // -------------------------------------------------------------
    // MODUS 1: SHARING ONLY (User 2: Mieter / Consumer ohne eigenes EMS)
    // -------------------------------------------------------------
    if (activeMode === NAV_MODES.SHARING_ONLY) {
        sections.push(
            {
                title: null,
                items: [
                    { name: t("nav.community_overview", "Community Cockpit"), path: "/app/tenant", icon: "🏢" },
                ],
            },
            {
                title: `📊 ${t("nav.tenant_analytics", "Mein Verbrauch & Sharing")}`,
                items: [
                    { name: t("energy.energy_balance", "Energiefluss & Solaranteil"), path: "/app/energy", icon: "⚡" },
                    { name: t("nav.tariffs_and_settlement", "Tarife & Abrechnungen"), path: "/app/tenant?tab=settlement", icon: "💰" },
                ],
            },
            {
                title: `⚙️ ${t("nav.account_settings", "Mein Konto")}`,
                items: [
                    { name: t("nav.profile", "Profil & Stammdaten"), path: "/app/profile", icon: "👤" },
                    { name: t("nav.manual", "Handbuch"), path: "/app/help", icon: "📖" },
                ],
            }
        );
        return sections;
    }

    // -------------------------------------------------------------
    // MODUS 2: PARTNER (Installateur / Flotten-Manager)
    // -------------------------------------------------------------
    if (activeMode === NAV_MODES.PARTNER) {
        sections.push(
            {
                title: null,
                items: [
                    { name: t("nav.partner_fleet", "Flotten-Cockpit"), path: "/app/partner", icon: "🔧" },
                ],
            },
            {
                title: `🛠️ ${t("nav.partner_tools", "Service & Onboarding")}`,
                items: [
                    { name: t("nav.devices", "Geräte & Schnittstellen"), path: "/app/devices", icon: "📟" },
                    { name: t("nav.mqtt_interfaces", "WSS & MQTT Anbindungen"), path: "/app/interfaces", icon: "📡" },
                    { name: t("nav.system_status", "Gateway-Status"), path: "/app/status", icon: "🌐" },
                ],
            },
            {
                title: `🛟 ${t("nav.partner_support", "Support & Diagnose")}`,
                items: [
                    { name: t("nav.agent_support_hub", "Support-Zentrale"), path: "/app/support-hub", icon: "🛟" },
                ],
            }
        );
        return sections;
    }

    // -------------------------------------------------------------
    // MODUS 3: ADMIN (Plattform & Mandanten Administration)
    // -------------------------------------------------------------
    if (activeMode === NAV_MODES.ADMIN) {
        sections.push(
            {
                title: `🛡️ ${t("nav.admin_group", "Administration")}`,
                items: [
                    { name: t("nav.communities_hub", "Energiegemeinschaften"), path: "/app/admin/communities", icon: "🏘️" },
                    { name: t("nav.admin_vpp", "VPP & Flex-Zentrale"), path: "/app/admin/vpp", icon: "⚡" },
                    { name: t("nav.admin_dashboard", "Admin Dashboard"), path: "/app/admin/dashboard", icon: "📊" },
                    { name: t("nav.admin_tracking", "Event & Tracking"), path: "/app/admin/tracking", icon: "📈" },
                    { name: t("nav.tenant_management", "Mandanten & Mieter"), path: "/app/tenant", icon: "👥" },
                    { name: t("nav.partner_fleet", "Partner-Flotten"), path: "/app/partner", icon: "🔧" },
                    { name: t("nav.agent_support_hub", "Support-Zentrale"), path: "/app/support-hub", icon: "🛟" },
                    {
                        name: "Django Backend",
                        path: "/admin/",
                        icon: "⚙️",
                        isExternal: true,
                    },
                ],
            }
        );
        return sections;
    }

    // -------------------------------------------------------------
    // MODUS 4 & 5: EMS_ONLY (User 1) & HYBRID (User 3)
    // -------------------------------------------------------------
    // Haupt-Dashboard
    sections.push({
        title: null,
        items: [
            { name: t("nav.dashboard", "Dashboard"), path: "/app/dashboard", icon: "🏠" },
        ],
    });

    // Analysen & Monitoring
    sections.push({
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
    });

    // Steuerung & Geräte (EMS Kernfunktionen)
    const controlItems = [
        {
            name: t("nav.energy_control", "Energiesteuerung (EMS)"),
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
            badge: unconfiguredDevicesCount > 0 ? unconfiguredDevicesCount : null,
            isDeviceSetupBadge: true,
        },
        { name: t("nav.producers", "Erzeuger & Speicher"), path: "/app/producers", icon: "🔋" },
    ];

    // Wenn HYBRID (User 3) oder Tenant-Access vorhanden ist: Community-Sharing Reiter einbinden
    if (activeMode === NAV_MODES.HYBRID || (hasCommunityAdminAccess && !isStaffOrAdmin)) {
        controlItems.push({
            name: t("nav.tenant_management", "Community & Sharing"),
            path: "/app/tenant",
            icon: "👥",
        });
    }

    sections.push({
        title: `🎛️ ${t("nav.assets_group", "Steuerung & Geräte")}`,
        items: controlItems,
    });

    // Systemeinstellungen
    sections.push({
        title: `⚙️ ${t("nav.settings_group", "Systemeinstellungen")}`,
        items: [
            { name: t("nav.energy_profile", "Energie-Profil"), path: "/app/energy-profile", icon: "🏡" },
            { name: t("nav.tariffs", "Strompreise & Tarife"), path: "/app/tariff", icon: "💶" },
            { name: t("nav.mqtt_interfaces", "Schnittstellen"), path: "/app/interfaces", icon: "📡" },
            { name: t("nav.system_status", "Systemstatus (Server)"), path: "/app/status", icon: "🌐" },
            { name: t("nav.manual", "Handbuch"), path: "/app/help", icon: "📖" },
        ],
    });

    return sections;
}
