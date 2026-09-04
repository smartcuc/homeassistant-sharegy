/*
# src/pages/dashboard/overview/OverviewPage.jsx
*/

import { useState } from "react";

import { useTrackingKPIs, useTrackingFunnel } from "../../../hooks/useTracking";
import { useDeviceSummary } from "../../../hooks/useDevices";

import KPI from "../../../components/tracking/KPI";
import DaysFilter from "../../../components/tracking/DaysFilter";
import TrackingFunnel from "../../../components/tracking/FunnelChart";

export default function OverviewPage() {

    const [days, setDays] = useState(7);

    const { data: kpis, isLoading: kpisLoading } = useTrackingKPIs(days);
    const { data: funnel, isLoading: funnelLoading } = useTrackingFunnel(days);
    const { data: deviceSummary, isLoading: devicesLoading } = useDeviceSummary();

    const loading = kpisLoading || funnelLoading || devicesLoading;

    if (loading) {
        return (
            <div className="p-6">
                Loading...
            </div>
        );
    }

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">

            {/* Header */}
            <div className="flex justify-between items-center">
                <h1 className="text-xl font-semibold">Overview</h1>
                <DaysFilter value={days} onChange={setDays} />
            </div>

            {/* =========================
                KPI SECTION
            ========================= */}
            <div className="grid grid-cols-3 gap-4">

                <KPI
                    label="DAU"
                    value={kpis?.dau}
                />

                <KPI
                    label="Landing → Signup"
                    value={`${kpis?.conversion_landing_signup}%`}
                />

                <KPI
                    label="Signup → Login"
                    value={`${kpis?.conversion_signup_login}%`}
                />

            </div>


            {/* =========================
                DEVICES + FUNNEL
            ========================= */}
            <div className="grid grid-cols-2 gap-4">

                {/* Devices */}
                <div className="bg-white p-4 rounded-xl shadow">
                    <h3 className="mb-4 font-semibold">Devices</h3>

                    <div className="space-y-1">
                        <div>
                            Online: <strong>{deviceSummary?.online}</strong>
                        </div>
                        <div>
                            Offline: <strong>{deviceSummary?.offline}</strong>
                        </div>
                        <div>
                            Stale: <strong>{deviceSummary?.stale}</strong>
                        </div>
                        <div className="pt-2 text-gray-400 text-sm">
                            Total: {deviceSummary?.total}
                        </div>
                    </div>
                </div>

                {/* Funnel */}
                <TrackingFunnel data={funnel} />

            </div>

        </div>
    );
}
