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
import SolarForecastAccuracyCard from "./components/SolarForecastAccuracyCard";

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
        <div className="p-6 space-y-6 w-full max-w-full min-w-0">
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
                        <div className="bg-linear-to-r from-amber-500/10 via-orange-500/10 to-yellow-500/10 border border-amber-200/80 rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                            <div className="flex items-start gap-3.5">
                                <span className="text-3xl p-2.5 bg-white rounded-xl shadow-2xs border border-amber-100">☀️</span>
                                <div>
                                    <h3 className="text-base font-bold text-gray-900">
                                        {t("forecast.empty_title", "Keine PV-Anlage oder Ertragsdaten konfiguriert")}
                                    </h3>
                                    <p className="text-sm text-gray-600 mt-1 max-w-2xl">
                                        {t("forecast.empty_desc", "Richte deine Photovoltaikanlage und Strings unter 'Erzeuger & Speicher' ein, um standortgenaue Wetter- und Ertragsprognosen zu berechnen.")}
                                    </p>
                                </div>
                            </div>
                            <a
                                href="/app/producers"
                                className="px-4 py-2.5 bg-amber-600 hover:bg-amber-700 text-white text-sm font-semibold rounded-xl shadow-xs transition whitespace-nowrap flex items-center gap-2 shrink-0"
                            >
                                <span>➕</span>
                                <span>{t("forecast.configure_pv", "PV-Anlage einrichten")}</span>
                            </a>
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

                            {/* =========================================================
                                SOLAR FORECAST ACCURACY & IST-VS-SOLL (TASK 5.13)
                            ========================================================= */}
                            <SolarForecastAccuracyCard stringId={selectedString} />
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
