/*
# frontend/src/context/UserNavigationContext.jsx
# Zentraler reaktiver Context für rollen- und kontextbasierte Navigation
*/

import React, { createContext, useContext, useState, useMemo, useEffect, useCallback } from "react";
import { useUser } from "../hooks/useUser";
import { useHomes } from "../hooks/useHomes";
import { NAV_MODES, MODE_METADATA } from "../config/navigationConfig";
import { getAppFlavor } from "../config/appFlavor";

const STORAGE_KEY = "sharegy_nav_context_mode";

const UserNavigationContext = createContext(null);

export function UserNavigationProvider({ children }) {
    const { user, isStaffOrAdmin, hasCommunityAdminAccess } = useUser();
    const { homes = [] } = useHomes();

    const isDemoUser = Boolean(
        user?.is_demo ||
        user?.email?.includes("demo") ||
        user?.username?.includes("demo") ||
        isStaffOrAdmin ||
        user?.is_superuser
    );

    // 1. Erkennung der Fähigkeiten & Berechtigungen
    const hasEms = useMemo(() => {
        if (isDemoUser) return true;
        if (homes.length > 0) return true;
        if (user?.usage_mode && ["private", "prosumer", "hybrid", "commercial"].includes(user.usage_mode)) return true;
        if (isStaffOrAdmin) return true;
        return user?.customer_type !== "tenant_only";
    }, [homes, user, isStaffOrAdmin, isDemoUser]);

    const hasEnergySharing = useMemo(() => {
        if (isDemoUser) return true;
        if (user?.memberships && user.memberships.length > 0) return true;
        if (hasCommunityAdminAccess) return true;
        if (user?.usage_mode && ["tenant", "sharing", "hybrid", "landlord"].includes(user.usage_mode)) return true;
        return false;
    }, [user, hasCommunityAdminAccess, isDemoUser]);

    const isPartner = useMemo(() => {
        if (isDemoUser) return true;
        return Boolean(
            user?.is_partner ||
            user?.platform_role === "partner" ||
            user?.memberships?.some((m) => m.role === "partner_admin" || m.role === "technician")
        );
    }, [user, isDemoUser]);

    const isAdmin = Boolean(isDemoUser || isStaffOrAdmin || user?.is_superuser || user?.is_platform_admin);

    // Ermitteln des genauen Community-Modus (Mieterstrom, GGV oder Energy Sharing)
    const userCommunityMode = useMemo(() => {
        const tenantModel = user?.tenant?.model_type || user?.memberships?.[0]?.tenant?.model_type;
        if (tenantModel === "mieterstrom") return NAV_MODES.MIETERSTROM;
        if (tenantModel === "ggv") return NAV_MODES.GGV;
        return NAV_MODES.ENERGY_SHARING;
    }, [user]);

    // 2. Verfügbare Modi für diesen Benutzer ermitteln
    const availableModes = useMemo(() => {
        if (isDemoUser) {
            return [
                NAV_MODES.HYBRID,
                NAV_MODES.EMS_ONLY,
                NAV_MODES.MIETERSTROM,
                NAV_MODES.GGV,
                NAV_MODES.ENERGY_SHARING,
                NAV_MODES.PARTNER,
                NAV_MODES.ADMIN,
            ];
        }

        const modes = [];
        if (hasEms && !hasEnergySharing) {
            modes.push(NAV_MODES.EMS_ONLY);
        } else if (!hasEms && hasEnergySharing) {
            modes.push(userCommunityMode);
        } else if (hasEms && hasEnergySharing) {
            modes.push(NAV_MODES.HYBRID);
            modes.push(NAV_MODES.EMS_ONLY);
            modes.push(userCommunityMode);
        } else {
            modes.push(NAV_MODES.EMS_ONLY);
        }

        if (isPartner) {
            modes.push(NAV_MODES.PARTNER);
        }
        if (isAdmin) {
            modes.push(NAV_MODES.ADMIN);
        }

        return Array.from(new Set(modes));
    }, [isDemoUser, hasEms, hasEnergySharing, userCommunityMode, isPartner, isAdmin]);

    const defaultMode = useMemo(() => {
        if (getAppFlavor() === "pro") return NAV_MODES.PARTNER;
        if (hasEms && hasEnergySharing) return NAV_MODES.HYBRID;
        if (hasEnergySharing && !hasEms) return userCommunityMode;
        if (isPartner && !hasEms) return NAV_MODES.PARTNER;
        if (isAdmin && !hasEms) return NAV_MODES.ADMIN;
        return NAV_MODES.EMS_ONLY;
    }, [hasEms, hasEnergySharing, userCommunityMode, isPartner, isAdmin]);

    const [activeMode, setActiveMode] = useState(() => {
        const saved = localStorage.getItem(STORAGE_KEY);
        return saved && availableModes.includes(saved) ? saved : defaultMode;
    });

    useEffect(() => {
        if (!availableModes.includes(activeMode)) {
            setActiveMode(defaultMode);
            localStorage.setItem(STORAGE_KEY, defaultMode);
        }
    }, [availableModes, activeMode, defaultMode]);

    const switchMode = useCallback((newMode) => {
        if (availableModes.includes(newMode)) {
            setActiveMode(newMode);
            localStorage.setItem(STORAGE_KEY, newMode);
        }
    }, [availableModes]);

    const value = useMemo(() => ({
        activeMode,
        availableModes,
        switchMode,
        hasEms,
        hasEnergySharing,
        isPartner,
        isAdmin,
        activeMetadata: MODE_METADATA[activeMode] || MODE_METADATA[NAV_MODES.EMS_ONLY],
        allMetadata: MODE_METADATA,
        isMultiMode: availableModes.length > 1,
    }), [activeMode, availableModes, switchMode, hasEms, hasEnergySharing, isPartner, isAdmin]);

    return (
        <UserNavigationContext.Provider value={value}>
            {children}
        </UserNavigationContext.Provider>
    );
}

export function useUserNavigation() {
    const context = useContext(UserNavigationContext);
    if (!context) {
        throw new Error("useUserNavigation must be used within a UserNavigationProvider");
    }
    return context;
}
