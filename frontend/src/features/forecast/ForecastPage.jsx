/*
# src/features/forecast/ForecastPage.jsx
*/

import { useState } from "react";
import ForecastChart from "./ForecastChart";
import { useSolarForecast } from "./hooks/useSolarForecast";
import { useTimezone } from "../../hooks/useTimezone";
import { formatHour, formatNumber } from "../../utils/format";

export default function ForecastPage() {
    const [selectedString, setSelectedString] = useState("all");
    const timezone = useTimezone();

    const query = useSolarForecast(selectedString);

    const points = query.data?.points || [];
    const strings = query.data?.strings || [];
    const homeName = query.data?.home_name || "Meine PV-Anlage";
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
                        ☀️ Solar Forecast
                    </h1>
                    <p className="text-gray-500 text-sm">
                        {source === "hybrid" ? "Hybrid ML & Physik-Prognose" : "Physikalische Prognose"} · nächste 24 Stunden
                    </p>
                </div>

                {strings.length > 0 && (
                    <div className="flex items-center gap-2">
                        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                            Anlage:
                        </label>
                        <select
                            value={selectedString}
                            onChange={(e) => setSelectedString(e.target.value)}
                            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm bg-white font-medium shadow-sm hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500"
                        >
                            <option value="all">⚡ Gesamtanlage (Alle Strings)</option>
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
                <div className="bg-white rounded-xl shadow p-6 text-gray-500 animate-pulse">
                    Forecast wird geladen...
                </div>
            )}

            {query.isError && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-600">
                    Forecast konnte nicht geladen werden.
                </div>
            )}

            {!query.isLoading && !query.isError && (
                <>
                    {!points.length && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-yellow-800">
                            ⚠️ Keine Forecast-Daten verfügbar. Führe ein Update der Wetterprognose durch.
                        </div>
                    )}

                    {points.length > 0 && (
                        <>
                            {/* KPIs */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
                                    <div className="text-sm font-medium text-gray-500">
                                        ☀️ Tagesertrag (24h)
                                    </div>
                                    <div className="text-3xl font-bold text-amber-600 mt-1">
                                        {formatNumber(totalForecast, 2)} <span className="text-sm font-normal text-gray-500">kWh</span>
                                    </div>
                                </div>

                                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
                                    <div className="text-sm font-medium text-gray-500">
                                        📈 Peak-Leistung
                                    </div>
                                    <div className="text-3xl font-bold text-orange-500 mt-1">
                                        {peak ? formatNumber(peak.v, 2) : "0,00"} <span className="text-sm font-normal text-gray-500">kW</span>
                                    </div>
                                </div>

                                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
                                    <div className="text-sm font-medium text-gray-500">
                                        🕒 Peak-Uhrzeit
                                    </div>
                                    <div className="text-3xl font-bold text-slate-700 mt-1">
                                        {peak ? formatHour(peak.t * 1000, timezone) : "--:--"}
                                    </div>
                                </div>

                                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
                                    <div className="text-sm font-medium text-gray-500">
                                        ⚡ Nächste Stunde
                                    </div>
                                    <div className="text-3xl font-bold text-blue-600 mt-1">
                                        {nextHour ? formatNumber(nextHour.v, 2) : "0,00"} <span className="text-sm font-normal text-gray-500">kW</span>
                                    </div>
                                </div>
                            </div>

                            {/* CHART */}
                            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
                                <div className="flex items-center justify-between mb-4">
                                    <div>
                                        <div className="font-semibold text-base text-gray-800">
                                            {selectedString === "all"
                                                ? `${homeName} · Gesamtanlage`
                                                : strings.find((s) => s.id === selectedString)?.name || "PV-String"}
                                        </div>
                                        <div className="text-sm text-gray-500">
                                            Ertragsprognose stundenweise
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
        </div>
    );
}
