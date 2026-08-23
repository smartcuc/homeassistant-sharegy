/*
# src/features/energy/EnergyDashboard.jsx
*/

import EnergySankey from "./components/EnergySankey";
import EnergyChart from "./components/EnergyChart";
import useEnergyInsights from "./hooks/useEnergyInsights";
import useEnergyOptimization from "./hooks/useEnergyOptimization";
import { useTranslation } from "react-i18next";

export default function EnergyDashboard() {
    const { t } = useTranslation();
    const insights = useEnergyInsights();
    const opt = useEnergyOptimization();

    return (
        <div className="p-6 space-y-6 max-w-6xl">

            {/* ✅ HEADER */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                    <span>⚡</span> {t("energy.title", "Energie-Dashboard")}
                </h1>
                <p className="text-sm text-gray-500 mt-1">
                    {t("energy.subtitle", "Detaillierte Analyse von Energieflüssen, Erzeugung und Verbrauch.")}
                </p>
            </div>

            {/* ✅ KPI SECTION */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                <div className="p-3 bg-amber-50 border border-amber-100 rounded-xl">
                    <div className="text-[10px] font-bold uppercase text-amber-700">{t("dashboard.pv_short", "PV")}</div>
                    <div className="text-lg font-bold text-gray-900">{opt.pv.toFixed(0)} W</div>
                </div>
                <div className="p-3 bg-blue-50 border border-blue-100 rounded-xl">
                    <div className="text-[10px] font-bold uppercase text-blue-700">{t("dashboard.load_short", "Verbrauch")}</div>
                    <div className="text-lg font-bold text-gray-900">{opt.consumption.toFixed(0)} W</div>
                </div>
                <div className="p-3 bg-emerald-50 border border-emerald-100 rounded-xl">
                    <div className="text-[10px] font-bold uppercase text-emerald-700">{t("dashboard.battery_short", "Batterie")}</div>
                    <div className="text-lg font-bold text-gray-900">{opt.battery.toFixed(0)} W</div>
                </div>
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                    <div className="text-[10px] font-bold uppercase text-gray-500">{t("energy.self_consumption", "Eigenverbrauch")}</div>
                    <div className="text-lg font-bold text-gray-900">{opt.selfConsumptionRate.toFixed(0)}%</div>
                </div>
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                    <div className="text-[10px] font-bold uppercase text-gray-500">{t("energy.autarky", "Autarkie")}</div>
                    <div className="text-lg font-bold text-gray-900">{opt.selfSufficiency.toFixed(0)}%</div>
                </div>
                <div className="p-3 bg-indigo-50 border border-indigo-100 rounded-xl">
                    <div className="text-[10px] font-bold uppercase text-indigo-700">Ersparnis</div>
                    <div className="text-lg font-bold text-indigo-900">{opt.savings.toFixed(2)} €</div>
                </div>
            </div>

            {/* ✅ INSIGHTS */}
            {insights.length > 0 && (
                <div className="p-4 bg-indigo-50/50 border border-indigo-100 rounded-xl text-xs text-indigo-900 space-y-1">
                    {insights.map((text, i) => (
                        <div key={i} className="flex items-center gap-1.5">
                            <span>💡</span> <span>{text}</span>
                        </div>
                    ))}
                </div>
            )}

            {/* ✅ SANKEY */}
            <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-sm">
                <h2 className="text-base font-bold text-gray-900 mb-3">
                    {t("dashboard.live_energy_flow", "Energiefluss")}
                </h2>
                <EnergySankey />
            </div>

            {/* ✅ CHART */}
            <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-sm">
                <h2 className="text-base font-bold text-gray-900 mb-3">
                    {t("energy.energy_balance", "Energiebilanz")}
                </h2>
                <EnergyChart />
            </div>

        </div>
    );
}
