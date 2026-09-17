/*
# src/pages/TenantDashboard.jsx
# Smart Model Router & Dispatcher for Sharegy Admin Pages:
# - Mieterstrom (§ 42a EnWG) -> MieterstromAdminPage
# - GGV (§ 42b EnWG) -> GgvAdminPage
# - Energy Sharing (eG) -> SharingAdminPage
*/

import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../api/client";
import { Link } from "react-router-dom";
import MieterstromAdminPage from "./admin/MieterstromAdminPage";
import GgvAdminPage from "./admin/GgvAdminPage";
import SharingAdminPage from "./admin/SharingAdminPage";

export default function TenantDashboard() {
    const { t } = useTranslation();
    const [tenant, setTenant] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let isMounted = true;
        async function fetchTenantInfo() {
            try {
                const data = await apiFetch("/api/my-tenant/");
                if (isMounted) {
                    setTenant(data.tenant);
                }
            } catch (err) {
                console.error("Tenant fetch failed:", err);
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        }
        fetchTenantInfo();
        return () => {
            isMounted = false;
        };
    }, []);

    if (loading) {
        return (
            <div className="p-12 text-center text-slate-400 text-sm animate-pulse">
                {t("tenant_dashboard.loading_admin", "Lade Verwaltungs-Cockpit...")}
            </div>
        );
    }

    if (!tenant) {
        return (
            <div className="p-8 max-w-xl mx-auto text-center space-y-4 my-8 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xs">
                <div className="text-4xl">🏛️</div>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                    {t("tenant_dashboard.no_org_title", "Keine aktive Organisation zugewiesen")}
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                    {t("tenant_dashboard.no_org_desc", "Du bist aktuell noch keiner Organisation (Mieterstrom, GGV oder Energy Sharing) zugewiesen.")}
                </p>
                <div className="pt-2">
                    <Link
                        to="/app/dashboard"
                        className="inline-block px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-xs transition"
                    >
                        {t("tenant_dashboard.back_to_dashboard", "Zurück zum Dashboard")}
                    </Link>
                </div>
            </div>
        );
    }

    // ✅ DISPATCH TO DEDICATED ADMIN PAGES
    if (tenant.model_type === "mieterstrom") {
        return <MieterstromAdminPage />;
    }

    if (tenant.model_type === "ggv") {
        return <GgvAdminPage />;
    }

    // Default to Energy Sharing (Genossenschaft / Bürgerenergie)
    return <SharingAdminPage />;
}
