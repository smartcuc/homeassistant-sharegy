/*
# components/AppShell.jsx
*/

import { useUser } from "../hooks/useUser";
import AppTopbar from "../components/layout/Topbar";
import Profile from "../pages/Profile";
import Sidebar from "../components/layout/Sidebar";

import Dashboard from "../pages/dashboard/Dashboard";
import OverviewPage from "../pages/dashboard/overview/OverviewPage";
import Settings from "../pages/Settings";
import InterfacesPage from "../pages/InterfacesPage";
import EnergyDashboard from "../features/energy/EnergyDashboard";
import ProducerPage from "../features/producer/pages/ProducerPage";
import TariffPage from "../features/market/pages/TariffPage";

import DevicesPage from "../pages/DevicesPage";
import ForecastPage from "../features/forecast/ForecastPage";
import MetricsPage from "../pages/MetricsPage";
import StructurePage from "../pages/StructurePage";
import AlertsPage from "../features/alerts/pages/AlertsPage";

import { Routes, Route, Navigate } from "react-router-dom";

export default function AppShell() {

    const { user, loading } = useUser();

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
                <div className="flex-1 overflow-auto">
                    <Routes>

                        {/* ✅ DEFAULT */}
                        <Route index element={<Navigate to="/app/dashboard" replace />} />

                        <Route path="dashboard" element={<Dashboard user={user} />} />
                        <Route path="profile" element={<Profile />} />

                        <Route path="overview" element={<OverviewPage />} />
                        <Route path="energy" element={<EnergyDashboard />} />
                        <Route path="devices" element={<DevicesPage />} />
                        <Route path="producers" element={<ProducerPage />} />
                        <Route path="tariff" element={<TariffPage />} />
                        <Route path="interfaces" element={<InterfacesPage />} />
                        <Route path="settings" element={<Settings />} />

                        <Route path="solarforecast" element={<ForecastPage />} />
                        <Route path="metrics" element={<MetricsPage />} />
                        <Route path="structure" element={<StructurePage />} />
                        <Route path="alerts" element={<AlertsPage />} />

                        {/* ✅ FALLBACK IMMER UNTEN */}
                        <Route path="*" element={<Navigate to="/app/dashboard" replace />} />

                    </Routes>
                </div>

            </div>
        </div>
    );
}


// {isRefreshing && <span className="text-xs text-gray-400">Syncing...</span>} muss noch iregenwo in
// der UI eingebaut werden