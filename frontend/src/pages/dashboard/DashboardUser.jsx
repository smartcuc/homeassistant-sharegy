import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSettings } from "../../hooks/useSettings";
import DashboardLayout from "../../components/dashboard/DashboardLayout";
import UnconfiguredDevicesBanner from "../../components/dashboard/UnconfiguredDevicesBanner";
import TimezoneAlertBanner from "../../components/dashboard/TimezoneAlertBanner";
import DeviceSetupModal from "../../components/device/DeviceSetupModal";
import EnergyChartModal from "../../features/energy/components/EnergyChartModal";
import KPI from "../../components/ui/KPI";
import KPISparklineECharts from "../../components/ui/KPISparklineECharts";
import Card from "../../components/ui/Card";
import useUserPreference from "../../hooks/useUserPreference";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../../api/client";
import LiveEnergySankeyECharts from "../../features/energy/components/LiveEnergySankeyECharts";
import { useTranslation } from "react-i18next";
import SystemReadinessCard from "../../features/energy/components/SystemReadinessCard";

export default function DashboardUser() {

    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const [openSetup, setOpenSetup] = useState(false);

    const navigate = useNavigate();

    const {
        settings: userSettings,
    } = useSettings();

    const {
        value: settings,
        setValue: saveSettings,
    } = useUserPreference("sankey");

    const showFloors = settings.showFloors ?? true;
    const showRooms = settings.showRooms ?? true;

    const [activeSystemChart, setActiveSystemChart] = useState(null);

    const energyQuery = useQuery({
        queryKey: ["energy-dashboard"],
        queryFn: () => apiFetch("/api/energy/dashboard/me/"),
        refetchInterval: activeSystemChart ? false : 3000,
        refetchIntervalInBackground: true,
    });

    const kpis = energyQuery.data?.kpis || {};
    const charts = energyQuery.data?.charts || {};

    return (
        <DashboardLayout>

            {/* 🚨 Alert Banners Stack (kompakt ohne Extra-Padding) */}
            <div className="space-y-3">
                <UnconfiguredDevicesBanner onOpen={() => setOpenSetup(true)} />
                <DeviceSetupModal
                    open={openSetup}
                    onClose={() => setOpenSetup(false)}
                />

                <TimezoneAlertBanner
                    timezone={userSettings?.timezone}
                    onAccept={async (timezone) => {
                        await apiFetch("/api/timezone/", {
                            method: "POST",
                            body: JSON.stringify({
                                timezone,
                            }),
                        });

                        await queryClient.invalidateQueries({
                            queryKey: ["settings"],
                        });
                    }}
                    onSettings={() => {
                        navigate("/app/profile");
                    }}
                />
            </div>

            {/* 🏠 Dashboard Header */}
            <div>
                <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-gray-900">
                    {t("dashboard.title", "Deine Energiezentrale ⚡")}
                </h1>
                <p className="mt-1 text-sm text-gray-500">
                    {t("dashboard.subtitle", "Alle wichtigen Energiedaten auf einen Blick.")}
                </p>
            </div>

            {/* 🩺 System-Check & Einrichtungsgrad (4-Säulen-Omi-Check) */}
            <SystemReadinessCard onOpenAddDevice={() => setOpenSetup(true)} />

            {/* ⚡ Echtzeit-Status & KPIs */}
            <div>
                <div className="mb-3">
                    <h2 className="text-sm font-semibold tracking-wide text-gray-500">
                        {t("dashboard.realtime_status", "Echtzeit-Status")}
                    </h2>
                </div>

            {/* KPIs */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                <div
                    onClick={() =>
                        setActiveSystemChart({
                            metricKey: "load",
                            displayName: t("dashboard.load", "Hausbedarf"),
                            unit: "W",
                            color: "#2563eb",
                            currentValue: kpis.load,
                        })
                    }
                    className="cursor-pointer hover:opacity-90 transition-opacity"
                >

                    <KPI
                        label={t("dashboard.load_short", "Bedarf")}
                        value={
                            kpis.load != null
                                ? kpis.load.toLocaleString(undefined, {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2,
                                })
                                : "--"
                        }
                        unit="W"
                        icon="⚡"
                        chart={
                            <KPISparklineECharts
                                color="#2563eb"
                                values={charts.load || []}
                                unit="W"
                            />
                        }
                    />
                </div>

                <div
                    onClick={() =>
                        setActiveSystemChart({
                            metricKey: "pv",
                            displayName: t("dashboard.pv", "PV-Erzeugung"),
                            unit: "W",
                            color: "#f59e0b",
                            currentValue: kpis.pv,
                        })
                    }
                    className="cursor-pointer hover:opacity-90 transition-opacity"
                >

                    <KPI
                        label={t("dashboard.pv_short", "Erzeugung")}
                        value={
                            kpis.pv != null
                                ? kpis.pv.toLocaleString(undefined, {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2,
                                })
                                : "--"
                        }
                        unit="W"
                        icon="☀️"
                        chart={
                            <KPISparklineECharts
                                color="#f59e0b"
                                values={charts.pv || []}
                                unit="W"
                            />
                        }
                    />
                </div>
                {/* ✅ KACHEL 2: Grid */}
                <div
                    onClick={() =>
                        setActiveSystemChart({
                            metricKey: "grid",
                            displayName: t("dashboard.grid", "Netzanschluss"),
                            unit: "W",
                            color: "#10b981",
                            currentValue: kpis.grid,
                        })
                    }

                    className="cursor-pointer hover:opacity-90 transition-opacity"
                >

                    <KPI
                        label={
                            (kpis.grid ?? 0) >= 0
                                ? t("dashboard.grid_import", "Bezug")
                                : t("dashboard.grid_export", "Einspeisung")
                        }
                        value={
                            kpis.grid != null
                                ? Math.abs(kpis.grid).toLocaleString(undefined, {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2,
                                })
                                : "--"
                        }
                        unit="W"
                        icon="🔌"
                        chart={
                            <KPISparklineECharts
                                color="#10b981"
                                values={charts.grid || []}
                                unit="W"
                            />

                        }
                    />
                </div>

                {/* ✅ KACHEL 3: Speicher (Batterie) */}
                {kpis.battery != null && (
                    <div
                        onClick={() =>
                            setActiveSystemChart({
                                metricKey: "battery",
                                displayName: t("dashboard.battery", "Batteriespeicher"),
                                unit: "W",
                                color: "#34d399",
                                currentValue: kpis.battery,
                            })
                        }
                        className="cursor-pointer hover:opacity-90 transition-opacity"
                    >
                        <KPI
                            label={
                                (kpis.battery ?? 0) >= 0
                                    ? t("dashboard.battery_discharge", "Entladung")
                                    : t("dashboard.battery_charge", "Ladung")
                            }
                            value={
                                kpis.battery != null
                                    ? Math.abs(kpis.battery).toLocaleString(undefined, {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2,
                                    })
                                    : "--"
                            }
                            unit="W"
                            icon="🔋"
                            chart={
                                <KPISparklineECharts
                                    color="#34d399"
                                    values={charts.battery || []}
                                    unit="W"
                                />
                            }
                        />
                    </div>
                )}

                <div
                    onClick={() =>
                        setActiveSystemChart({
                            metricKey: "today",
                            displayName: t("energy.household_load", "Tagesverbrauch"),
                            unit: "kWh",
                            color: "#8b5cf6",
                            currentValue: kpis.today,
                        })
                    }
                    className="cursor-pointer hover:opacity-90 transition-opacity"
                >

                    <KPI
                        label={t("dashboard.today", "Heute")}
                        value={
                            kpis.today?.toLocaleString(undefined, {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                            })
                        }
                        unit="kWh"
                        icon="📈"
                        chart={
                            <KPISparklineECharts
                                color="#8b5cf6"
                                values={charts.today || []}
                                chartType="bar"
                                unit="kWh"
                            />
                        }
                    />

                </div>

            </div>
        </div>

            {/* Sankey Chart */}
            <div className="mt-6">
                <Card>

                    <div className="flex items-center justify-between mb-4">

                        <div>
                            <h2 className="text-xl font-semibold text-gray-900">
                                {t("dashboard.live_energy_flow", "Energiefluss (Live)")}
                            </h2>

                            <p className="text-sm text-gray-500">
                                {t("energy.subtitle", "Aktuelle Verteilung von Erzeugung und Verbrauch.")}
                            </p>
                        </div>

                        <div className="flex gap-2">

                            <button
                                title="Nach Etagen gruppieren"
                                onClick={async () => {
                                    await saveSettings({
                                        ...settings,
                                        showFloors: !showFloors,
                                    });

                                    energyQuery.refetch();
                                }}

                                className={`
                                        px-2.5 py-1
                                        rounded-full
                                        text-xs
                                        border
                                        flex items-center gap-1
                                        transition
                                        ${showFloors
                                        ? "bg-indigo-600 text-white border-indigo-600"
                                        : "bg-white hover:bg-gray-50 border-gray-200"}
                                `}
                            >
                                🏢 {t("structure.floor", "Etage")}
                            </button>

                            <button
                                title="Nach Räumen gruppieren"
                                onClick={async () => {
                                    await saveSettings({
                                        ...settings,
                                        showRooms: !showRooms,
                                    });

                                    queryClient.invalidateQueries({
                                        queryKey: ["energy-dashboard"],
                                    })

                                }}

                                className={`
                                        px-2.5 py-1
                                        rounded-full
                                        text-xs
                                        border
                                        flex items-center gap-1
                                        transition
                                        ${showRooms
                                        ? "bg-indigo-600 text-white border-indigo-600"
                                        : "bg-white hover:bg-gray-50 border-gray-200"}
                                `}
                            >
                                🚪 {t("structure.rooms", "Räume")}
                            </button>

                        </div>

                    </div>

                    {energyQuery.data?.ready ? (

                        <LiveEnergySankeyECharts
                            data={energyQuery.data?.sankey}
                        />

                    ) : (

                        <div className="h-40 flex flex-col items-center justify-center text-center text-gray-400 space-y-1">
                            <p className="text-gray-500 font-medium">Willkommen bei Sharegy 👋</p>
                            <p>📈 Dein Energiechart kommt, sobald wir uns besser kennengelernt haben.</p>
                        </div>

                    )}

                </Card>
            </div>

            {/* 💡 EMS SYSTEM CHART MODAL */}
            {activeSystemChart && (
                <EnergyChartModal
                    metricKey={activeSystemChart.metricKey}
                    displayName={activeSystemChart.displayName}
                    unit={activeSystemChart.unit}
                    color={activeSystemChart.color}
                    currentValue={activeSystemChart.currentValue}
                    onClose={() => setActiveSystemChart(null)}
                />
            )}

        </DashboardLayout>
    );
}

