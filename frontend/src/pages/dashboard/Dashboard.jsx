/*
# src/pages/dashboard/Dashboard.jsx
*/

import { useEffect } from "react";
import { trackEvent } from "../../lib/track";

import DashboardUser from "./DashboardUser";
import DashboardTenant from "./DashboardTenant";
import DashboardHybrid from "./DashboardHybrid";


export default function Dashboard({ user }) {

    // ✅ TRACK
    useEffect(() => {
        if (user) {
            trackEvent("dashboard_view", {
                usage_mode: user.usage_mode
            });
        }
    }, [user]);

    // ✅ wichtig
    if (!user) return null;

    if (user.usage_mode === "hybrid") {
        return <DashboardHybrid />;
    }

    if (user.usage_mode === "tenant") {
        return <DashboardTenant />;
    }

    return <DashboardUser />;
}
