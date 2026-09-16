import { Routes, Route, Navigate } from "react-router-dom";
import AdminLayout from "./components/admin/AdminLayout";
import AdminDashboard from "./pages/admin/AdminDashboard";
import TrackingDashboard from "./pages/admin/TrackingDashboard";
import TenantDashboard from "./pages/TenantDashboard";
import CommunitiesManagementHub from "./pages/admin/CommunitiesManagementHub";
import VppFleetAdminPage from "./pages/admin/VppFleetAdminPage";
import AgentSupportHubPage from "./features/support/pages/AgentSupportHubPage";
import PartnerDashboard from "./features/partner/PartnerDashboard";
import { useUser } from "./hooks/useUser";

export default function AdminApp() {
    const { user, loading } = useUser();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center text-gray-400">
                Sharegy lädt…
            </div>
        );
    }

    if (!user) return <Navigate to="/" replace />;
    if (!user.is_staff && !user.is_superuser) return <Navigate to="/app/dashboard" replace />;

    return (
        <AdminLayout>
            <Routes>
                <Route index element={<Navigate to="communities" replace />} />
                <Route path="communities" element={<CommunitiesManagementHub />} />
                <Route path="vpp" element={<VppFleetAdminPage />} />
                <Route path="dashboard" element={<AdminDashboard />} />
                <Route path="tracking" element={<TrackingDashboard />} />
                <Route path="tenants" element={<TenantDashboard />} />
                <Route path="partners" element={<PartnerDashboard />} />
                <Route path="support" element={<AgentSupportHubPage />} />
                <Route path="*" element={<Navigate to="communities" replace />} />
            </Routes>
        </AdminLayout>
    );
}


