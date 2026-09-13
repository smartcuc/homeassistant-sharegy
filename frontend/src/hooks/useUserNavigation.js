/*
# frontend/src/hooks/useUserNavigation.js
# Hook für rollen- und kontextbasierte Navigationslogik (User 1: EMS, User 2: Sharing, User 3: Hybrid)
*/

import { useState, useMemo, useEffect, useCallback } from "react";
import { useUser } from "./useUser";
import { useHomes } from "./useHomes";
import { NAV_MODES, MODE_METADATA } from "../config/navigationConfig";
import { getAppFlavor } from "../config/appFlavor";

const STORAGE_KEY = "sharegy_nav_context_mode";

export function useUserNavigation() {
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
        // Standardmäßig bei registrierten Nutzern aktiv, es sei denn sie sind reiner Mieter
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

    // 2. Verfügbare Modi für diesen Benutzer ermitteln
    const availableModes = useMemo(() => {
        if (isDemoUser) {
            // Im Demo-Modus oder für Admins/Tester stehen ALLE 5 Modi für interaktive Tests zur Verfügung!
            return [
                NAV_MODES.HYBRID,
                NAV_MODES.EMS_ONLY,
                NAV_MODES.SHARING_ONLY,
                NAV_MODES.PARTNER,
                NAV_MODES.ADMIN,
            ];
        }

        const modes = [];

        if (hasEms && !hasEnergySharing) {
            // User 1: Nur EMS
            modes.push(NAV_MODES.EMS_ONLY);
        } else if (!hasEms && hasEnergySharing) {
            // User 2: Nur Energy-Sharing
            modes.push(NAV_MODES.SHARING_ONLY);
        } else if (hasEms && hasEnergySharing) {
            // User 3: Beides (Hybrid) - bietet schnellen Wechsel zwischen Ansichten
            modes.push(NAV_MODES.HYBRID);
            modes.push(NAV_MODES.EMS_ONLY);
            modes.push(NAV_MODES.SHARING_ONLY);
        } else {
            // Fallback (z.B. neuer User) -> EMS
            modes.push(NAV_MODES.EMS_ONLY);
        }

        if (isPartner) {
            modes.push(NAV_MODES.PARTNER);
        }

        if (isAdmin) {
            modes.push(NAV_MODES.ADMIN);
        }

        // Duplikate entfernen
        return Array.from(new Set(modes));
    }, [isDemoUser, hasEms, hasEnergySharing, isPartner, isAdmin]);

    // Standard-Modus bestimmen
    const defaultMode = useMemo(() => {
        if (getAppFlavor() === "pro") return NAV_MODES.PARTNER;
        if (hasEms && hasEnergySharing) return NAV_MODES.HYBRID;
        if (hasEnergySharing && !hasEms) return NAV_MODES.SHARING_ONLY;
        if (isPartner && !hasEms) return NAV_MODES.PARTNER;
        if (isAdmin && !hasEms) return NAV_MODES.ADMIN;
        return NAV_MODES.EMS_ONLY;
    }, [hasEms, hasEnergySharing, isPartner, isAdmin]);

    // 3. Aktiven Modus aus localStorage oder Default laden
    const [activeMode, setActiveMode] = useState(() => {
        const saved = localStorage.getItem(STORAGE_KEY);
        return saved && availableModes.includes(saved) ? saved : defaultMode;
    });

    // Validieren, falls sich die Berechtigungen ändern
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

    return {
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
    };
}
