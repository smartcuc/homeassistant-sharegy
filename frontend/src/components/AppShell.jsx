/*
# components/AppShell.jsx
*/

import { useUser } from "../hooks/useUser";
import AppTopbar from "../components/layout/Topbar";
import Sidebar from "../components/layout/Sidebar";
import Dashboard from "../pages/dashboard/Dashboard";
import BackToTopButton from "../components/common/BackToTopButton";
import { useRef, useEffect, lazy, Suspense } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";

// ⚡ LAZY LOADED ROUTE MODULES
const OverviewPage = lazy(() => import("../pages/dashboard/overview/OverviewPage"));
const InterfacesPage = lazy(() => import("../pages/InterfacesPage"));
const EnergyDashboard = lazy(() => import("../features/energy/EnergyDashboard"));
const ProducerPage = lazy(() => import("../features/producer/pages/ProducerPage"));
const ControlPage = lazy(() => import("../features/control/pages/ControlPage"));
const TariffPage = lazy(() => import("../features/market/pages/TariffPage"));
const DevicesPage = lazy(() => import("../pages/DevicesPage"));
const ForecastPage = lazy(() => import("../features/forecast/ForecastPage"));
const MetricsPage = lazy(() => import("../pages/MetricsPage"));
const StructurePage = lazy(() => import("../pages/StructurePage"));
const AlertsPage = lazy(() => import("../features/alerts/pages/AlertsPage"));
const HelpCenterPage = lazy(() => import("../features/help/pages/HelpCenterPage"));
const HelpArticleDetailPage = lazy(() => import("../features/help/pages/HelpArticleDetailPage"));
const BillingPage = lazy(() => import("../features/billing/pages/BillingPage"));
const SystemStatusPage = lazy(() => import("../pages/SystemStatusPage"));
const Profile = lazy(() => import("../pages/Profile"));
const AgentSupportHubPage = lazy(() => import("../features/support/pages/AgentSupportHubPage"));
const AdminDashboard = lazy(() => import("../pages/admin/AdminDashboard"));
const TrackingDashboard = lazy(() => import("../pages/admin/TrackingDashboard"));
const TenantDashboard = lazy(() => import("../pages/TenantDashboard"));
const CommunitiesManagementHub = lazy(() => import("../pages/admin/CommunitiesManagementHub"));

function PageSuspenseLoader() {
    return (
        <div className="p-8 max-w-7xl mx-auto space-y-6 animate-pulse">
            <div className="h-8 bg-gray-200/80 dark:bg-slate-800 rounded-xl w-1/3"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="h-32 bg-gray-100 dark:bg-slate-850 rounded-2xl"></div>
                <div className="h-32 bg-gray-100 dark:bg-slate-850 rounded-2xl"></div>
                <div className="h-32 bg-gray-100 dark:bg-slate-850 rounded-2xl"></div>
            </div>
            <div className="h-96 bg-gray-100 dark:bg-slate-850 rounded-2xl"></div>
        </div>
    );
}

export default function AppShell() {

    const { user, loading, isStaffOrAdmin, hasCommunityAdminAccess } = useUser();
    const location = useLocation();
    const contentRef = useRef(null);

    // 🔄 Bei jedem Navigationswechsel sofort nach ganz oben scrollen
    useEffect(() => {
        if (contentRef.current) {
            contentRef.current.scrollTop = 0;
        }
    }, [location.pathname]);

    if (loading) {
        return <div className="p-6">Loading...</div>;
    }

    if (!user) {
        return <Navigate to="/" replace />;
    }

    return (
        <div className="flex h-screen">

            {/* ✅ SIDEBAR */}
            <Sidebar />

            <div className="flex-1 flex flex-col">

                {/* ✅ TOPBAR */}
                <AppTopbar />

                {/* ✅ CONTENT */}
                <div ref={contentRef} className="flex-1 overflow-auto">
                    <Suspense fallback={<PageSuspenseLoader />}>
                        <Routes>


                            {/* ✅ DEFAULT */}
                            <Route index element={<Navigate to="/app/dashboard" replace />} />

                            <Route path="dashboard" element={<Dashboard user={user} />} />
                            <Route path="profile" element={<Profile />} />
                            <Route path="billing" element={<BillingPage />} />

                            <Route path="overview" element={<OverviewPage />} />
                            <Route path="energy" element={<EnergyDashboard />} />
                            <Route path="devices" element={<DevicesPage />} />
                            <Route path="producers" element={<ProducerPage />} />
                            <Route path="control" element={<ControlPage />} />
                            <Route path="tariff" element={<TariffPage />} />
                            <Route path="interfaces" element={<InterfacesPage />} />
                            <Route path="status" element={<SystemStatusPage />} />
                            <Route path="settings" element={<Navigate to="/app/status" replace />} />


                            <Route path="solarforecast" element={<ForecastPage />} />
                            <Route path="metrics" element={<MetricsPage />} />
                            <Route path="structure" element={<StructurePage />} />
                            <Route path="alerts" element={<AlertsPage />} />

                            {/* 📚 HELP CENTER & KNOWLEDGE BASE */}
                            <Route path="help" element={<HelpCenterPage />} />
                            <Route path="help/:slug" element={<HelpArticleDetailPage />} />

                            {/* 🛟 SUPPORT & INCIDENT HUB (STAFF ONLY) */}
                            <Route 
                                path="support" 
                                element={isStaffOrAdmin ? <AgentSupportHubPage /> : <Navigate to="/app/dashboard" replace />} 
                            />
                            <Route 
                                path="support-hub" 
                                element={isStaffOrAdmin ? <AgentSupportHubPage /> : <Navigate to="/app/dashboard" replace />} 
                            />

                            {/* 🛡️ ADMIN & TENANT MANAGEMENT */}
                            <Route path="admin" element={<Navigate to="/app/admin/dashboard" replace />} />
                            <Route 
                                path="admin/dashboard" 
                                element={isStaffOrAdmin ? <AdminDashboard /> : <Navigate to="/app/dashboard" replace />} 
                            />
                            <Route 
                                path="admin/tracking" 
                                element={isStaffOrAdmin ? <TrackingDashboard /> : <Navigate to="/app/dashboard" replace />} 
                            />
                            <Route 
                                path="admin/communities" 
                                element={isStaffOrAdmin ? <CommunitiesManagementHub /> : <Navigate to="/app/dashboard" replace />} 
                            />
                            <Route 
                                path="communities" 
                                element={isStaffOrAdmin ? <CommunitiesManagementHub /> : <Navigate to="/app/dashboard" replace />} 
                            />
                            <Route path="tenant" element={<TenantDashboard />} />
                            <Route path="tenant-management" element={<TenantDashboard />} />
                            <Route path="community" element={<TenantDashboard />} />


                            {/* ✅ FALLBACK IMMER UNTEN */}
                            <Route path="*" element={<Navigate to="/app/dashboard" replace />} />

                        </Routes>
                    </Suspense>
                </div>

                {/* 🔝 GLOBAL BACK TO TOP BUTTON */}
                <BackToTopButton scrollContainerRef={contentRef} threshold={160} />

            </div>
        </div>
    );

}


// {isRefreshing && <span className="text-xs text-gray-400">Syncing...</span>} muss noch iregenwo in
// der UI eingebaut werden