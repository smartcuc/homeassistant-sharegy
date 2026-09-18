/*
# frontend/src/config/navigationConfig.js
# Zentrale deklarative Konfiguration aller Navigations-Items und Rollen-/Modus-Filter
*/

export const NAV_MODES = {
    EMS_ONLY: "ems_only",             // User 1: Nur EMS (Eigenheim / Prosumer ohne Community)
    MIETERSTROM: "mieterstrom",       // User 2a: Mieterstrom (§ 42a EnWG) - Vollversorgung
    GGV: "ggv",                       // User 2b: Gemeinschaftliche Gebäudeversorgung (§ 42b EnWG) - Vor-Ort-Aufteilung
    ENERGY_SHARING: "energy_sharing", // User 2c: Regionales Energy Sharing - Bürgerenergie / Genossenschaft
    SHARING_ONLY: "energy_sharing",   // Alias für Abwärtskompatibilität
    HYBRID: "hybrid",                 // User 3: Beides (EMS Prosumer + Energy Sharing)
    PARTNER: "partner",               // Partner / Installateur Flotten-Management
    ADMIN: "admin",                   // Plattform- & Mandanten-Administration
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
    [NAV_MODES.MIETERSTROM]: {
        id: NAV_MODES.MIETERSTROM,
        labelKey: "nav.mode_mieterstrom",
        defaultLabel: "Mieterstrom (§ 42a EnWG)",
        icon: "🏢",
        description: "Vollversorger: Solarstrom & Netzstrom in einer gemeinsamen Monatsabrechnung",
        defaultPath: "/app/community",
    },
    [NAV_MODES.GGV]: {
        id: NAV_MODES.GGV,
        labelKey: "nav.mode_ggv",
        defaultLabel: "Gebäudeversorgung (GGV § 42b EnWG)",
        icon: "⚖️",
        description: "Vor-Ort-Aufteilung des Solarstroms im Gebäude mit externem Reststromvertrag",
        defaultPath: "/app/community",
    },
    [NAV_MODES.ENERGY_SHARING]: {
        id: NAV_MODES.ENERGY_SHARING,
        labelKey: "nav.mode_sharing",
        defaultLabel: "Energy Sharing (Genossenschaft)",
        icon: "⚡",
        description: "15m Smart-Meter-Bilanzierung & Verteilnetz-Allokation der Bürgerenergie",
        defaultPath: "/app/community",
    },
    [NAV_MODES.HYBRID]: {
        id: NAV_MODES.HYBRID,
        labelKey: "nav.mode_hybrid",
        defaultLabel: "EMS & Sharing Hub",
        icon: "☀️",
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
    // MODUS 1a: MIETERSTROM (§ 42a EnWG - Vollversorger)
    // -------------------------------------------------------------
    if (activeMode === NAV_MODES.MIETERSTROM) {
        sections.push(
            {
                title: `🏢 ${t("nav.mieterstrom", "Mieterstrom (§ 42a EnWG)")}`,
                items: [
                    { name: t("nav.mieterstrom_overview", "Mieterstrom-Cockpit"), path: "/app/community", icon: "🏢" },
                ],
            },
            {
                title: `📊 ${t("nav.my_energy", "Mein Verbrauch")}`,
                items: [
                    { name: t("energy.energy_balance", "Energiefluss & Strommix"), path: "/app/energy", icon: "⚡" },
                ],
            }
        );

        if (isStaffOrAdmin || hasCommunityAdminAccess) {
            sections.push({
                title: `🛡️ ${t("nav.admin_group", "Administration")}`,
                items: [
                    { name: t("nav.tenant_management_mieterstrom", "Mieter & Wohnungsverwaltung"), path: "/app/admin/mieterstrom", icon: "🏢" },
                    ...(isStaffOrAdmin ? [{ name: t("nav.communities_hub", "Quartiere & Gemeinschaften (Portfolio)"), path: "/app/admin/communities", icon: "🏘️" }] : []),
                ],
            });
        }

        sections.push({
            title: `⚙️ ${t("nav.account_settings", "Mein Konto")}`,
            items: [
                { name: t("nav.profile", "Profil & Stammdaten"), path: "/app/profile", icon: "👤" },
                { name: t("nav.manual", "Handbuch"), path: "/app/help", icon: "📖" },
            ],
        });
        return sections;
    }

    // -------------------------------------------------------------
    // MODUS 1b: GGV (§ 42b EnWG - Vor-Ort-Aufteilung & Reststrom)
    // -------------------------------------------------------------
    if (activeMode === NAV_MODES.GGV) {
        sections.push(
            {
                title: `⚖️ ${t("nav.ggv", "Gebäudeversorgung (§ 42b EnWG)")}`,
                items: [
                    { name: t("nav.ggv_overview", "Gebäude-Solarcockpit"), path: "/app/community", icon: "⚖️" },
                ],
            },
            {
                title: `📊 ${t("nav.my_energy", "Mein Verbrauch")}`,
                items: [
                    { name: t("energy.energy_balance", "PV-Solaranteil & Reststrom"), path: "/app/energy", icon: "⚡" },
                ],
            }
        );

        if (isStaffOrAdmin || hasCommunityAdminAccess) {
            sections.push({
                title: `🛡️ ${t("nav.admin_group", "Administration")}`,
                items: [
                    { name: t("nav.tenant_management_ggv", "WEG & Gebäudeverwaltung"), path: "/app/admin/ggv", icon: "⚖️" },
                    ...(isStaffOrAdmin ? [{ name: t("nav.communities_hub", "Quartiere & Gemeinschaften (Portfolio)"), path: "/app/admin/communities", icon: "🏘️" }] : []),
                ],
            });
        }

        sections.push({
            title: `⚙️ ${t("nav.account_settings", "Mein Konto")}`,
            items: [
                { name: t("nav.profile", "Profil & Stammdaten"), path: "/app/profile", icon: "👤" },
                { name: t("nav.manual", "Handbuch"), path: "/app/help", icon: "📖" },
            ],
        });
        return sections;
    }

    // -------------------------------------------------------------
    // MODUS 1c: ENERGY SHARING (Regionales Verteilnetz / Genossenschaft)
    // -------------------------------------------------------------
    if (activeMode === NAV_MODES.ENERGY_SHARING || activeMode === "sharing_only") {
        sections.push(
            {
                title: `⚡ ${t("nav.community", "Regionales Energy Sharing")}`,
                items: [
                    { name: t("nav.community_overview", "Bürgerenergie-Cockpit"), path: "/app/community", icon: "⚡" },
                ],
            },
            {
                title: `📊 ${t("nav.my_energy", "Mein Verbrauch")}`,
                items: [
                    { name: t("energy.energy_balance", "15m Energiefluss & Zuteilung"), path: "/app/energy", icon: "📊" },
                ],
            }
        );

        if (isStaffOrAdmin || hasCommunityAdminAccess) {
            sections.push({
                title: `🛡️ ${t("nav.admin_group", "Administration")}`,
                items: [
                    { name: t("nav.tenant_management_sharing", "Genossenschaft & Mitglieder"), path: "/app/admin/sharing", icon: "👥" },
                    ...(isStaffOrAdmin ? [{ name: t("nav.communities_hub", "Quartiere & Gemeinschaften (Portfolio)"), path: "/app/admin/communities", icon: "🏘️" }] : []),
                ],
            });
        }

        sections.push({
            title: `⚙️ ${t("nav.account_settings", "Mein Konto")}`,
            items: [
                { name: t("nav.profile", "Profil & Stammdaten"), path: "/app/profile", icon: "👤" },
                { name: t("nav.manual", "Handbuch"), path: "/app/help", icon: "📖" },
            ],
        });
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
                    { name: t("nav.communities_hub", "Quartiere & Gemeinschaften (Portfolio)"), path: "/app/admin/communities", icon: "🏘️" },
                    { name: t("nav.tenant_management_mieterstrom", "🏢 Mieterstrom (§ 42a)"), path: "/app/admin/mieterstrom", icon: "🏢" },
                    { name: t("nav.tenant_management_ggv", "⚖️ GGV-Gebäude (§ 42b)"), path: "/app/admin/ggv", icon: "⚖️" },
                    { name: t("nav.tenant_management_sharing", "⚡ Energy Sharing (eG)"), path: "/app/admin/sharing", icon: "👥" },
                    { name: t("nav.admin_vpp", "VPP & Flex-Zentrale"), path: "/app/admin/vpp", icon: "⚡" },
                    { name: t("nav.admin_dashboard", "Admin Dashboard"), path: "/app/admin/dashboard", icon: "📊" },
                    { name: t("nav.admin_tracking", "Event & Tracking"), path: "/app/admin/tracking", icon: "📈" },
                    { name: t("nav.admin_audit_logs", "Audit Trail & Revision"), path: "/app/admin/audit-logs", icon: "🔒" },
                    { name: t("nav.partner_fleet", "Partner-Flotten"), path: "/app/partner", icon: "🔧" },
                    { name: t("nav.agent_support_hub", "Support-Zentrale"), path: "/app/support-hub", icon: "🛟" },
                    {
                        name: "Django Backend",
                        path: "/admin/",
                        icon: "⚙️",
                        isExternal: true,
                    },
                ],
            },
            {
                title: `⚙️ ${t("nav.account_settings", "Mein Konto & System")}`,
                items: [
                    { name: t("nav.profile", "Profil & Stammdaten"), path: "/app/profile", icon: "👤" },
                    { name: t("nav.system_status", "Systemstatus (Server)"), path: "/app/status", icon: "🌐" },
                    { name: t("nav.manual", "Handbuch"), path: "/app/help", icon: "📖" },
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
            name: (hasCommunityAdminAccess || isStaffOrAdmin) ? t("nav.tenant_management", "Mandanten & Communities") : t("nav.community_overview", "Energy Sharing"),
            path: (hasCommunityAdminAccess || isStaffOrAdmin) ? "/app/tenant" : "/app/community",
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
