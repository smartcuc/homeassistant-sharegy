/*
# components/AppShell.jsx
*/

import { useUser } from "../hooks/useUser";
import { useUserNavigation } from "../hooks/useUserNavigation";
import AppTopbar from "../components/layout/Topbar";
import Sidebar from "../components/layout/Sidebar";
import MobileBottomNav from "../components/layout/MobileBottomNav";
import MobileMenuDrawer from "../components/layout/MobileMenuDrawer";
import Dashboard from "../pages/dashboard/Dashboard";
import BackToTopButton from "../components/common/BackToTopButton";
import { useRef, useEffect, useState, lazy, Suspense } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";

// ⚡ LAZY LOADED ROUTE MODULES
const OverviewPage = lazy(() => import("../pages/dashboard/overview/OverviewPage"));
const InterfacesPage = lazy(() => import("../pages/InterfacesPage"));
const EnergyDashboard = lazy(() => import("../features/energy/EnergyDashboard"));
const ProducerPage = lazy(() => import("../features/producer/pages/ProducerPage"));
const ControlPage = lazy(() => import("../features/control/pages/ControlPage"));
const MobilityPage = lazy(() => import("../features/mobility/pages/MobilityPage"));
const HeatingPage = lazy(() => import("../features/heating/pages/HeatingPage"));
const TariffPage = lazy(() => import("../features/market/pages/TariffPage"));
const EnergyProfilePage = lazy(() => import("../features/energy/pages/EnergyProfilePage"));
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
const MieterstromAdminPage = lazy(() => import("../pages/admin/MieterstromAdminPage"));
const GgvAdminPage = lazy(() => import("../pages/admin/GgvAdminPage"));
const SharingAdminPage = lazy(() => import("../pages/admin/SharingAdminPage"));
const CommunityMemberDashboard = lazy(() => import("../features/community/pages/CommunityMemberDashboard"));
const CommunitiesManagementHub = lazy(() => import("../pages/admin/CommunitiesManagementHub"));
const PartnerDashboard = lazy(() => import("../features/partner/PartnerDashboard"));
const VppFleetAdminPage = lazy(() => import("../pages/admin/VppFleetAdminPage"));

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

    const { user, loading, isStaffOrAdmin, hasCommunityAdminAccess, canAccessSupportHub } = useUser();
    const { activeMetadata, activeMode } = useUserNavigation();
    const location = useLocation();
    const contentRef = useRef(null);
    const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

    // 🔄 Bei jedem Navigationswechsel sofort nach ganz oben scrollen & Mobile Drawer schließen
    useEffect(() => {
        if (contentRef.current) {
            contentRef.current.scrollTop = 0;
        }
        setMobileDrawerOpen(false);
    }, [location.pathname]);

    if (loading) {
        return <div className="p-6">Loading...</div>;
    }

    if (!user) {
        return <Navigate to="/" replace />;
    }

    const preferredLandingPath = localStorage.getItem("sharegy_preferred_landing_page");
    const defaultLandingPath = preferredLandingPath || activeMetadata?.defaultPath || "/app/dashboard";

    return (
        <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">

            {/* ✅ DESKTOP SIDEBAR (hidden on mobile) */}
            <Sidebar />

            {/* ✅ MOBILE SLIDE-OVER DRAWER */}
            <MobileMenuDrawer 
                isOpen={mobileDrawerOpen} 
                onClose={() => setMobileDrawerOpen(false)} 
            />

            <div className="flex-1 flex flex-col min-w-0 overflow-hidden">

                {/* ✅ TOPBAR */}
                <AppTopbar onOpenMobileMenu={() => setMobileDrawerOpen(true)} />

                {/* ✅ CONTENT WITH SAFE BOTTOM PADDING ON MOBILE FOR FIXED NAV */}
                <div ref={contentRef} className="flex-1 overflow-y-auto pb-20 lg:pb-0">
                    <Suspense fallback={<PageSuspenseLoader />}>
                        <Routes>


                            {/* ✅ INTELLIGENTES DEFAULT LANDING ROUTING */}
                            <Route index element={<Navigate to={defaultLandingPath} replace />} />

                            <Route path="dashboard" element={<Dashboard user={user} />} />
                            <Route path="profile" element={<Profile />} />
                            <Route path="billing" element={<BillingPage />} />

                            <Route path="overview" element={<OverviewPage />} />
                            <Route path="energy" element={<EnergyDashboard />} />
                            <Route path="devices" element={<DevicesPage />} />
                            <Route path="producers" element={<ProducerPage />} />
                            <Route path="control" element={<ControlPage />} />
                            <Route path="mobility" element={<MobilityPage />} />
                            <Route path="heating" element={<HeatingPage />} />
                            <Route path="tariff" element={<TariffPage />} />
                            <Route path="energy-profile" element={<EnergyProfilePage />} />
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

                            {/* 🛟 SUPPORT & INCIDENT HUB (STAFF & PARTNER) */}
                            <Route 
                                path="support" 
                                element={canAccessSupportHub ? <AgentSupportHubPage /> : <Navigate to="/app/help" replace />} 
                            />
                            <Route 
                                path="support-hub" 
                                element={canAccessSupportHub ? <AgentSupportHubPage /> : <Navigate to="/app/help" replace />} 
                            />

                            {/* 🛡️ ADMIN & TENANT MANAGEMENT */}
                            <Route path="admin" element={<Navigate to="/app/admin/dashboard" replace />} />
                            <Route 
                                path="admin/dashboard" 
                                element={isStaffOrAdmin ? <AdminDashboard /> : <Navigate to="/app/dashboard" replace />} 
                            />
                            <Route 
                                path="admin/vpp" 
                                element={isStaffOrAdmin ? <VppFleetAdminPage /> : <Navigate to="/app/dashboard" replace />} 
                            />
                            <Route 
                                path="vpp" 
                                element={isStaffOrAdmin ? <VppFleetAdminPage /> : <Navigate to="/app/dashboard" replace />} 
                            />
                            <Route 
                                path="admin/tracking" 
                                element={isStaffOrAdmin ? <TrackingDashboard /> : <Navigate to="/app/dashboard" replace />} 
                            />
                            <Route path="admin/communities" 
                                element={isStaffOrAdmin ? <CommunitiesManagementHub /> : <Navigate to="/app/dashboard" replace />} 
                            />
                            <Route 
                                path="communities" 
                                element={isStaffOrAdmin ? <CommunitiesManagementHub /> : <Navigate to="/app/dashboard" replace />} 
                            />
                            <Route path="admin/mieterstrom" element={<MieterstromAdminPage />} />
                            <Route path="admin/ggv" element={<GgvAdminPage />} />
                            <Route path="admin/sharing" element={<SharingAdminPage />} />
                            <Route path="tenant" element={<TenantDashboard />} />
                            <Route path="tenant-management" element={<TenantDashboard />} />
                            <Route path="community" element={<CommunityMemberDashboard />} />
                            <Route path="partner" element={<PartnerDashboard />} />
                            <Route path="installer" element={<PartnerDashboard />} />



                            {/* ✅ FALLBACK IMMER UNTEN */}
                            <Route path="*" element={<Navigate to="/app/dashboard" replace />} />

                        </Routes>
                    </Suspense>
                </div>

                {/* 🔝 GLOBAL BACK TO TOP BUTTON */}
                <BackToTopButton scrollContainerRef={contentRef} threshold={160} />

                {/* 📱 MOBILE BOTTOM NAVIGATION (< md screens) */}
                <MobileBottomNav onOpenMenu={() => setMobileDrawerOpen(true)} />

            </div>
        </div>
    );

}