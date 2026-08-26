import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function BatteryArbitrageCard() {
    const { t } = useTranslation();

    const arbitrageQuery = useQuery({
        queryKey: ["battery-arbitrage"],
        queryFn: () => apiFetch("/api/energy/battery-arbitrage/"),
        refetchInterval: 30000,
    });

    const data = arbitrageQuery.data || {};
    const timeline = data.timeline || [];
    const advice = data.advice || [];

    if (arbitrageQuery.isLoading) {
        return (
            <div className="p-6 bg-white rounded-3xl border border-slate-200/80 shadow-xs animate-pulse">
                <div className="h-5 bg-slate-200 rounded w-1/3 mb-4"></div>
                <div className="h-24 bg-slate-100 rounded-xl"></div>
            </div>
        );
    }

    return (
        <div className="p-6 bg-white rounded-3xl border border-slate-200/80 shadow-xs hover:border-slate-300 transition-all">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-xl shadow-2xs">
                        🔋
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h2 className="text-base font-bold text-gray-900">
                                {t("arbitrage.title", "Grid-Charging Arbitrage & Speicher-Simulator")}
                            </h2>
                            {data.is_arbitrage_profitable ? (
                                <span className="px-2 py-0.5 rounded-full text-[11px] font-extrabold bg-emerald-100 text-emerald-800 border border-emerald-200">
                                    🟢 {t("arbitrage.profitable", "Rentabel")} (+{data.price_spread_ct_per_kwh} ct/kWh)
                                </span>
                            ) : (
                                <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-600">
                                    {t("arbitrage.pv_priority", "⚪ PV-Priorität")}
                                </span>
                            )}
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">
                            {t("arbitrage.subtitle", "Intelligentes Laden des Hausspeichers bei Tiefstpreisen und Entladen in Spitzenzeiten.")}
                        </p>
                    </div>
                </div>

                <div className="text-right self-start sm:self-auto bg-indigo-50/70 border border-indigo-100/80 px-3.5 py-1.5 rounded-xl">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-indigo-700">
                        {t("arbitrage.savings_projected", "Zusatzerlös / Ersparnis")}
                    </div>
                    <div className="text-lg font-black text-indigo-900">
                        ~{data.projected_yearly_savings_eur?.toFixed(0) || "0"} € <span className="text-xs font-semibold text-indigo-600">{t("arbitrage.per_year", "/ Jahr")}</span>
                    </div>
                </div>
            </div>

            {/* KPI Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
                <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100">
                    <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                        {t("arbitrage.best_charge_price", "🌙 Günstigster Ladepreis")}
                    </div>
                    <div className="text-lg font-extrabold text-indigo-600 mt-1">
                        {data.avg_charge_price_ct?.toFixed(1) || "12.0"} <span className="text-xs font-semibold">ct/kWh</span>
                    </div>
                    <div className="text-[11px] text-slate-500 font-medium mt-0.5">
                        {t("arbitrage.window", "Fenster")}: {data.best_charge_window || "-"}
                    </div>
                </div>

                <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100">
                    <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                        {t("arbitrage.avoided_peak_price", "⚡ Vermiedener Peak-Preis")}
                    </div>
                    <div className="text-lg font-extrabold text-amber-600 mt-1">
                        {data.avg_discharge_price_ct?.toFixed(1) || "34.5"} <span className="text-xs font-semibold">ct/kWh</span>
                    </div>
                    <div className="text-[11px] text-slate-500 font-medium mt-0.5">
                        {t("arbitrage.window", "Fenster")}: {data.best_discharge_window || "-"}
                    </div>
                </div>

                <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100">
                    <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                        {t("arbitrage.roundtrip_efficiency", "🔄 Wirkungsgrad (Roundtrip)")}
                    </div>
                    <div className="text-lg font-extrabold text-slate-800 mt-1">
                        {data.roundtrip_efficiency_pct || "90.0"} %
                    </div>
                    <div className="text-[11px] text-slate-500 font-medium mt-0.5">
                        {t("arbitrage.usable", "Nutzbar")}: {data.usable_capacity_kwh || "9.0"} kWh
                    </div>
                </div>

                <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100">
                    <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                        {t("arbitrage.profit_per_cycle", "💰 Ertrag pro Zyklus")}
                    </div>
                    <div className="text-lg font-extrabold text-emerald-600 mt-1">
                        +{data.daily_profit_eur?.toFixed(2) || "0.00"} €
                    </div>
                    <div className="text-[11px] text-emerald-700/80 font-medium mt-0.5">
                        {t("arbitrage.month_projected", { amount: data.projected_monthly_savings_eur?.toFixed(2) || "0.00", defaultValue: `Monat: ~${data.projected_monthly_savings_eur?.toFixed(2) || "0.00"} €` })}
                    </div>
                </div>
            </div>

            {/* Timeline Preview */}
            {timeline.length > 0 && (
                <div className="mt-5">
                    <div className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center justify-between">
                        <span>{t("arbitrage.schedule_24h", "24h Lade- & Arbitrage-Fahrplan")}</span>
                        <div className="flex items-center gap-3 text-[11px] font-semibold text-slate-500">
                            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-indigo-500"></span> {t("arbitrage.action_charge", "Netzladen")}</span>
                            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> {t("arbitrage.action_discharge", "Entladen")}</span>
                            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> {t("arbitrage.action_pv", "Solar")}</span>
                        </div>
                    </div>

                    <div className="grid grid-cols-6 sm:grid-cols-12 gap-1.5 bg-slate-50 p-2.5 rounded-2xl border border-slate-100">
                        {timeline.slice(0, 12).map((slot, idx) => (
                            <div
                                key={idx}
                                className={`p-2 rounded-xl text-center border transition-all ${slot.action === "grid_charge"
                                        ? "bg-indigo-600 text-white border-indigo-600 shadow-xs"
                                        : slot.action === "discharge"
                                            ? "bg-amber-500 text-white border-amber-500 shadow-xs"
                                            : slot.action === "solar_charge"
                                                ? "bg-emerald-500 text-white border-emerald-500 shadow-xs"
                                                : "bg-white text-slate-700 border-slate-200/80"
                                    }`}
                            >
                                <div className="text-[10px] font-bold opacity-80">{slot.time_label}</div>
                                <div className="text-xs font-black mt-0.5">{slot.effective_price_ct}</div>
                                <div className="text-[9px] truncate font-medium mt-0.5 opacity-90">
                                    {slot.action === "grid_charge" ? t("arbitrage.action_charge", "Laden") : slot.action === "discharge" ? t("arbitrage.action_peak", "Peak") : slot.action === "solar_charge" ? t("arbitrage.action_pv", "PV") : t("arbitrage.action_idle", "Standby")}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Advice / Hints */}
            {advice.length > 0 && (
                <div className="mt-4 p-3 bg-slate-50/80 rounded-2xl border border-slate-100 text-xs text-slate-600 space-y-1">
                    {advice.map((hint, i) => (
                        <div key={i} className="flex items-start gap-2">
                            <span className="text-indigo-600 font-bold">•</span>
                            <span>{hint}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
