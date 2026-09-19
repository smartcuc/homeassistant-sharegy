/*
# src/hooks/useUser.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";


async function fetchUser() {
    try {
        const userData = await apiFetch("/api/auth/me/");

        return {
            ...userData,
            memberships: userData.memberships || [],
            is_authenticated: true,
        };

    } catch (err) {
        // ✅ Auth verloren → null
        if (err?.type === "auth") {
            return null;
        }

        throw err;
    }
}


export function useUser() {
    const query = useQuery({
        queryKey: ["user"],
        queryFn: fetchUser,

        // ✅ wichtig für dein Setup
        retry: 1,
        staleTime: 1000 * 60 * 5,   // 5 Minuten Cache
        refetchOnWindowFocus: false,
    });

    const user = query.data ?? null;

    const isSuperAdmin = Boolean(user?.is_superuser || user?.platform_role === "system_admin");
    const isStaffOrAdmin = Boolean(user?.is_staff || user?.is_superuser || user?.is_platform_admin);
    const isDispatcher = Boolean(
        isSuperAdmin ||
        user?.is_dispatcher ||
        user?.platform_role === "dispatcher" ||
        user?.memberships?.some((m) => ["admin", "dispatcher"].includes(m.role))
    );
    const isBillingSpecialist = Boolean(
        isSuperAdmin ||
        user?.is_finance_admin ||
        user?.platform_role === "finance" ||
        user?.memberships?.some((m) => ["admin", "billing", "auditor"].includes(m.role))
    );
    const isFieldTechnician = Boolean(
        isSuperAdmin ||
        user?.is_field_technician ||
        user?.platform_role === "installer" ||
        user?.memberships?.some((m) => ["admin", "installer"].includes(m.role))
    );
    const isAuditor = Boolean(
        isSuperAdmin ||
        user?.is_auditor ||
        user?.platform_role === "auditor" ||
        user?.memberships?.some((m) => ["admin", "auditor"].includes(m.role))
    );
    const isHelpdesk = Boolean(isStaffOrAdmin || user?.is_platform_helpdesk);
    const isFinanceAdmin = Boolean(user?.is_superuser || user?.is_platform_admin || user?.is_finance_admin);
    const isGlobalUserAdmin = Boolean(user?.is_superuser || user?.is_platform_admin || user?.is_global_user_admin);
    const hasCommunityAdminAccess = Boolean(
        isStaffOrAdmin ||
        isGlobalUserAdmin ||
        user?.memberships?.some((m) => ["admin", "user_admin"].includes(m.role)) ||
        user?.usage_mode === "hybrid" ||
        user?.usage_mode === "landlord"
    );
    const isPartner = Boolean(
        isStaffOrAdmin ||
        isFieldTechnician ||
        user?.is_partner ||
        user?.platform_role === "partner" ||
        user?.memberships?.some((m) => ["admin", "installer", "helpdesk", "user_admin"].includes(m.role))
    );
    const canAccessSupportHub = Boolean(isStaffOrAdmin || isHelpdesk || isPartner);
    const canAccessVpp = Boolean(isStaffOrAdmin || isDispatcher);
    const canAccessBilling = Boolean(isStaffOrAdmin || isBillingSpecialist || isAuditor);

    return {
        user,
        loading: query.isLoading,
        isRefreshing: query.isFetching,

        // ✅ Ersatz für dein refreshUser
        refreshUser: query.refetch,

        // 🛡️ Enterprise Berechtigungs-Helfer
        isSuperAdmin,
        isStaffOrAdmin,
        isDispatcher,
        isBillingSpecialist,
        isFieldTechnician,
        isAuditor,
        isHelpdesk,
        isFinanceAdmin,
        isGlobalUserAdmin,
        hasCommunityAdminAccess,
        isPartner,
        canAccessSupportHub,
        canAccessVpp,
        canAccessBilling,
    };
}
