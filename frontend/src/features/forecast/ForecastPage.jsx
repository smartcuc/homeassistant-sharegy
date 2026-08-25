/*
# src/features/forecast/ForecastPage.jsx
*/

import { useState } from "react";
import ForecastChart from "./ForecastChart";
import { useSolarForecast } from "./hooks/useSolarForecast";
import { useTimezone } from "../../hooks/useTimezone";
import { formatHour, formatNumber } from "../../utils/format";
import { useTranslation } from "react-i18next";
import HouseholdLoadForecastCard from "./components/HouseholdLoadForecastCard";

export default function ForecastPage() {
    const { t } = useTranslation();
    const [selectedString, setSelectedString] = useState("all");
    const timezone = useTimezone();

    const query = useSolarForecast(selectedString);

    const points = query.data?.points || [];
    const strings = query.data?.strings || [];
    const homeName = query.data?.home_name || t("producers.empty", "Meine PV-Anlage");
    const source = query.data?.source || "hybrid";

    const totalForecast = query.data?.total_kwh ?? points.reduce(
        (sum, p) => sum + Number(p.v || 0),
        0
    );

    const peak = points.length > 0
        ? points.reduce((a, b) => (b.v > a.v ? b : a))
        : null;

    const nextHour = points.length > 0 ? points[0] : null;

    return (
        <div className="p-6 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        ☀️ {t("forecast.title", "Solar Forecast")}
                    </h1>
                    <p className="text-gray-500 text-sm">
                        {t("forecast.subtitle", "Hybrid ML & Physik-Prognose · nächste 24 Stunden")}
                    </p>
                </div>

                {strings.length > 0 && (
                    <div className="flex items-center gap-2">
                        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                            {t("forecast.installation_label", "Anlage:")}
                        </label>
                        <select
                            value={selectedString}
                            onChange={(e) => setSelectedString(e.target.value)}
                            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm bg-white font-medium shadow-sm hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500"
                        >
                            <option value="all">⚡ {t("forecast.all_strings", "Gesamtanlage (Alle Strings)")}</option>
                            {strings.map((s) => (
                                <option key={s.id} value={s.id}>
                                    ☀️ {s.name} ({s.peak_power_kwp} kWp, {s.orientation})
                                </option>
                            ))}
                        </select>
                    </div>
                )}
            </div>

            {query.isLoading && (
                <div className="bg-white rounded-xl shadow-xs p-6 text-gray-500 animate-pulse">
                    {t("forecast.loading", "Forecast wird geladen...")}
                </div>
            )}

            {query.isError && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-600">
                    {t("forecast.error", "Forecast konnte nicht geladen werden.")}
                </div>
            )}

            {!query.isLoading && !query.isError && (
                <>
                    {!points.length && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-yellow-800">
                            ⚠️ {t("forecast.no_data", "Keine Forecast-Daten verfügbar. Führe ein Update der Wetterprognose durch.")}
                        </div>
                    )}

                    {points.length > 0 && (
                        <>
                            {/* KPIs */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div className="bg-white rounded-xl shadow-xs border border-gray-100 p-5">
                                    <div className="text-sm font-medium text-gray-500">
                                        📊 {t("forecast.total_today", "Erwartete Erzeugung")}
                                    </div>
                                    <div className="text-3xl font-bold text-gray-900 mt-1">
                                        {formatNumber(totalForecast, 2)} <span className="text-sm font-normal text-gray-500">kWh</span>
                                    </div>
                                </div>

                                <div className="bg-white rounded-xl shadow-xs border border-gray-100 p-5">
                                    <div className="text-sm font-medium text-gray-500">
                                        🚀 {t("forecast.peak_today", "Maximaler Peak")}
                                    </div>
                                    <div className="text-3xl font-bold text-amber-600 mt-1">
                                        {peak ? formatNumber(peak.v, 2) : "0,00"} <span className="text-sm font-normal text-gray-500">kW</span>
                                    </div>
                                    {peak && (
                                        <div className="text-xs text-gray-500 mt-0.5">
                                            {formatHour(peak.t * 1000, timezone)}
                                        </div>
                                    )}
                                </div>

                                <div className="bg-white rounded-xl shadow-xs border border-gray-100 p-5">
                                    <div className="text-sm font-medium text-gray-500">
                                        ⚡ {t("forecast.next_hour", "Nächste Stunde")}
                                    </div>
                                    <div className="text-3xl font-bold text-blue-600 mt-1">
                                        {nextHour ? formatNumber(nextHour.v, 2) : "0,00"} <span className="text-sm font-normal text-gray-500">kW</span>
                                    </div>
                                </div>
                            </div>

                            {/* CHART */}
                            <div className="bg-white rounded-xl shadow-xs border border-gray-100 p-5">
                                <div className="flex items-center justify-between mb-4">
                                    <div>
                                        <div className="font-semibold text-base text-gray-800">
                                            {selectedString === "all"
                                                ? `${homeName} · ${t("forecast.all_strings", "Gesamtanlage")}`
                                                : strings.find((s) => s.id === selectedString)?.name || "PV-String"}
                                        </div>
                                        <div className="text-sm text-gray-500">
                                            {t("forecast.hourly_yield", "Ertragsprognose stundenweise")}
                                        </div>
                                    </div>
                                    <span className="text-xs bg-amber-100 text-amber-800 font-semibold px-2.5 py-1 rounded-full uppercase tracking-wide">
                                        {source} Model
                                    </span>
                                </div>

                                <ForecastChart points={points} />
                            </div>
                        </>
                    )}
                </>
            )}

            {/* =========================================================
                HOUSEHOLD LOAD FORECAST (TASK 5.2)
            ========================================================= */}
            <HouseholdLoadForecastCard />
        </div>
    );
}
