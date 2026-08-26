/*
# src/AdminApp.jsx
*/

import { Routes, Route, Navigate } from "react-router-dom";
import AdminLayout from "./components/admin/AdminLayout";
import AdminDashboard from "./pages/admin/AdminDashboard";
import TrackingDashboard from "./pages/admin/TrackingDashboard";
import TenantDashboard from "./pages/TenantDashboard";
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
                <Route index element={<Navigate to="dashboard" replace />} />
                <Route path="dashboard" element={<AdminDashboard />} />
                <Route path="tracking" element={<TrackingDashboard />} />
                <Route path="tenants" element={<TenantDashboard />} />
                <Route path="*" element={<Navigate to="dashboard" replace />} />
            </Routes>
        </AdminLayout>
    );
}
