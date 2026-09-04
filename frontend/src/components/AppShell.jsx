/*
# components/AppShell.jsx
*/

import { useUser } from "../hooks/useUser";
import AppTopbar from "../components/layout/Topbar";
import Profile from "../pages/Profile";
import Sidebar from "../components/layout/Sidebar";

import Dashboard from "../pages/dashboard/Dashboard";
import OverviewPage from "../pages/dashboard/overview/OverviewPage";
import InterfacesPage from "../pages/InterfacesPage";
import EnergyDashboard from "../features/energy/EnergyDashboard";
import ProducerPage from "../features/producer/pages/ProducerPage";
import ControlPage from "../features/control/pages/ControlPage";
import TariffPage from "../features/market/pages/TariffPage";

import DevicesPage from "../pages/DevicesPage";
import ForecastPage from "../features/forecast/ForecastPage";
import MetricsPage from "../pages/MetricsPage";
import StructurePage from "../pages/StructurePage";
import AlertsPage from "../features/alerts/pages/AlertsPage";
import HelpCenterPage from "../features/help/pages/HelpCenterPage";
import HelpArticleDetailPage from "../features/help/pages/HelpArticleDetailPage";
import BillingPage from "../features/billing/pages/BillingPage";
import SystemStatusPage from "../pages/SystemStatusPage";

import AgentSupportHubPage from "../features/support/pages/AgentSupportHubPage";
import AdminDashboard from "../pages/admin/AdminDashboard";
import TrackingDashboard from "../pages/admin/TrackingDashboard";
import TenantDashboard from "../pages/TenantDashboard";
import CommunitiesManagementHub from "../pages/admin/CommunitiesManagementHub";
import BackToTopButton from "../components/common/BackToTopButton";
import { useRef, useEffect } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";


export default function AppShell() {

    const { user, loading } = useUser();
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

                        {/* 🛟 SUPPORT & INCIDENT HUB */}
                        <Route path="support" element={<AgentSupportHubPage />} />
                        <Route path="support-hub" element={<AgentSupportHubPage />} />

                        {/* 🛡️ ADMIN & TENANT MANAGEMENT */}
                        <Route path="admin" element={<Navigate to="/app/admin/dashboard" replace />} />
                        <Route path="admin/dashboard" element={<AdminDashboard />} />
                        <Route path="admin/tracking" element={<TrackingDashboard />} />
                        <Route path="admin/communities" element={<CommunitiesManagementHub />} />
                        <Route path="communities" element={<CommunitiesManagementHub />} />
                        <Route path="tenant" element={<TenantDashboard />} />
                        <Route path="tenant-management" element={<TenantDashboard />} />
                        <Route path="community" element={<TenantDashboard />} />


                        {/* ✅ FALLBACK IMMER UNTEN */}
                        <Route path="*" element={<Navigate to="/app/dashboard" replace />} />

                    </Routes>
                </div>

                {/* 🔝 GLOBAL BACK TO TOP BUTTON */}
                <BackToTopButton scrollContainerRef={contentRef} threshold={160} />

            </div>
        </div>
    );

}


// {isRefreshing && <span className="text-xs text-gray-400">Syncing...</span>} muss noch iregenwo in
// der UI eingebaut werden