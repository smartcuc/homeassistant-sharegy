/*
# src/features/forecast/ForecastPage.jsx
*/

import { useState } from "react";
import ForecastChart from "./ForecastChart";
import { useSolarForecast } from "./hooks/useSolarForecast";
import { useTimezone } from "../../hooks/useTimezone";
import { useSubscription } from "../../hooks/useSubscription";
import { formatHour, formatNumber } from "../../utils/format";
import { useTranslation } from "react-i18next";
import HouseholdLoadForecastCard from "./components/HouseholdLoadForecastCard";
import SolarForecastAccuracyCard from "./components/SolarForecastAccuracyCard";
import ProBadge from "../../components/common/ProBadge";
import ProUpgradeModal from "../../components/common/ProUpgradeModal";

export default function ForecastPage() {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const [selectedString, setSelectedString] = useState("all");
    const [horizonHours, setHorizonHours] = useState(24);
    const [proModalOpen, setProModalOpen] = useState(false);
    const timezone = useTimezone();

    const query = useSolarForecast(selectedString, horizonHours);

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

    const handleHorizonChange = (h) => {
        if (h === 48 && !isPro) {
            setProModalOpen(true);
            return;
        }
        setHorizonHours(h);
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        ☀️ {t("forecast.title", "Solar Forecast")}
                    </h1>
                    <p className="text-gray-500 text-sm">
                        {t("forecast.subtitle", "Hybrid ML & Physik-Prognose")} · {horizonHours} Stunden
                    </p>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                    {/* Horizon Selector (24h vs 48h Pro) */}
                    <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200/80">
                        <button
                            type="button"
                            onClick={() => handleHorizonChange(24)}
                            className={`px-3 py-1 text-xs font-bold rounded-lg transition cursor-pointer ${
                                horizonHours === 24
                                    ? "bg-white text-gray-900 shadow-2xs"
                                    : "text-gray-600 hover:text-gray-900"
                            }`}
                        >
                            24h
                        </button>
                        <button
                            type="button"
                            onClick={() => handleHorizonChange(48)}
                            className={`px-3 py-1 text-xs font-bold rounded-lg transition flex items-center gap-1.5 cursor-pointer ${
                                horizonHours === 48
                                    ? "bg-white text-gray-900 shadow-2xs"
                                    : "text-gray-600 hover:text-gray-900"
                            }`}
                        >
                            <span>48h</span>
                            {!isPro && <ProBadge size="xs" />}
                        </button>
                    </div>

                    {strings.length > 0 && (
                        <div className="flex items-center gap-2">
                            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider hidden sm:inline">
                                {t("forecast.installation_label", "Anlage:")}
                            </label>
                            <select
                                value={selectedString}
                                onChange={(e) => setSelectedString(e.target.value)}
                                className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm bg-white font-medium shadow-xs hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500"
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
                        <div className="bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-yellow-500/10 border border-amber-200/80 rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
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
                                        ⏱ {t("forecast.next_hour", "Nächste Stunde")}
                                    </div>
                                    <div className="text-3xl font-bold text-gray-900 mt-1">
                                        {nextHour ? formatNumber(nextHour.v, 2) : "0,00"}{" "}
                                        <span className="text-sm font-normal text-gray-500">kWh</span>
                                    </div>
                                </div>

                                <div className="bg-white rounded-xl shadow-xs border border-gray-100 p-5">
                                    <div className="text-sm font-medium text-gray-500">
                                        ⚡ {t("forecast.peak_production", "Spitzenertrag")}
                                    </div>
                                    <div className="text-3xl font-bold text-gray-900 mt-1">
                                        {peak ? formatNumber(peak.v, 2) : "0,00"}{" "}
                                        <span className="text-sm font-normal text-gray-500">kWh</span>
                                    </div>
                                    {peak && (
                                        <div className="text-xs text-gray-400 mt-1">
                                            {t("forecast.at_hour", "um")} {formatHour(peak.t, timezone)} Uhr
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Chart */}
                            <div className="bg-white rounded-xl shadow-xs border border-gray-100 p-6">
                                <ForecastChart
                                    points={points}
                                    timezone={timezone}
                                    title={`${homeName} · ${source.toUpperCase()} ${t("forecast.model", "Modell")}`}
                                />
                            </div>
                        </>
                    )}
                </>
            )}

            {/* Haushalt-Lastprognose & Treffgenauigkeit */}
            <HouseholdLoadForecastCard
                horizon={horizonHours}
                onHorizonChange={handleHorizonChange}
            />
            <SolarForecastAccuracyCard stringId={selectedString} />

            {/* Pro Upgrade Modal */}
            <ProUpgradeModal
                open={proModalOpen}
                onClose={() => setProModalOpen(false)}
                featureName="48-Stunden Solar- & Lastprognose"
                featureDesc="Erweitere deinen Vorhersagehorizont auf volle 48 Stunden, um Batterieladungen und flexible Verbraucher zwei Tage im Voraus optimal zu timen."
            />
        </div>
    );
}
