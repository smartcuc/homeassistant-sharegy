import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function GridCo2Card() {
    const { t } = useTranslation();

    const co2Query = useQuery({
        queryKey: ["grid-co2"],
        queryFn: () => apiFetch("/api/market/co2/"),
        refetchInterval: 60000,
    });

    const data = co2Query.data || {};
    const timeline = data.timeline || [];
    const insights = data.insights || [];

    if (co2Query.isLoading) {
        return (
            <div className="p-6 bg-white rounded-3xl border border-slate-200/80 shadow-xs animate-pulse">
                <div className="h-5 bg-slate-200 rounded w-1/3 mb-4"></div>
                <div className="h-24 bg-slate-100 rounded-xl"></div>
            </div>
        );
    }

    const levelBadgeColor =
        data.current_level === "green"
            ? "bg-emerald-100 text-emerald-800 border-emerald-200"
            : data.current_level === "red"
                ? "bg-rose-100 text-rose-800 border-rose-200"
                : "bg-amber-100 text-amber-800 border-amber-200";

    return (
        <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-slate-300 dark:hover:border-slate-700 transition-all">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-teal-50 dark:bg-teal-950/40 border border-teal-100 dark:border-teal-800/60 flex items-center justify-center text-xl shadow-2xs">
                        🌿
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h2 className="text-base font-bold text-slate-900 dark:text-white">
                                {t("co2.title", "Live CO₂-Grid-Signal & Grünstrom-Index")}
                            </h2>
                            <span className={`px-2 py-0.5 rounded-full text-[11px] font-extrabold border ${levelBadgeColor}`}>
                                {data.current_level_label}
                            </span>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            {t("co2.subtitle", "Echtzeit-Emissionsintensität des deutschen Stromnetzes für umweltoptimiertes Laden.")}
                        </p>
                    </div>
                </div>

                <div className="text-right self-start sm:self-auto bg-teal-50/70 dark:bg-teal-950/40 border border-teal-100/80 dark:border-teal-800/60 px-3.5 py-1.5 rounded-2xl">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-teal-700 dark:text-teal-400">
                        {t("co2.renewable_share", "Erneuerbaren-Anteil")}
                    </div>
                    <div className="text-lg font-black text-teal-900 dark:text-teal-200">
                        {data.current_renewable_share_pct || "65.0"} <span className="text-xs font-semibold text-teal-600 dark:text-teal-400">{t("co2_grid.green_share", "% Grünstrom")}</span>
                    </div>
                </div>
            </div>

            {/* KPI Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
                <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800">
                    <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        {t("co2_grid.live_intensity", "⚡ Live CO₂-Intensität")}
                    </div>
                    <div className="text-xl font-black mt-1" style={{ color: data.current_color || "#10B981" }}>
                        {data.current_co2_intensity_g_per_kwh || 220}{" "}
                        <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">g/kWh</span>
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 font-medium mt-0.5">
                        {t("co2.current_grid_mix", "Aktueller Netzmix DE")}
                    </div>
                </div>

                <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800">
                    <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        {t("co2_grid.best_eco_window", "🌱 Bestes Öko-Fenster")}
                    </div>
                    <div className="text-lg font-extrabold text-emerald-700 dark:text-emerald-400 mt-1 truncate" title={data.best_eco_window}>
                        {data.best_eco_window || "12:00 - 15:00"}
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 font-medium mt-0.5">
                        {t("co2.min_emissions", "Minimale Emissionen")}
                    </div>
                </div>

                <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800">
                    <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        📊 {t("co2.avg_24h", "24h-Durchschnitt")}
                    </div>
                    <div className="text-lg font-extrabold text-slate-800 dark:text-slate-200 mt-1">
                        {data.avg_co2_intensity_g_per_kwh || 310} <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">g/kWh</span>
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 font-medium mt-0.5">
                        {t("co2.daily_forecast", "Tagesprognose")}
                    </div>
                </div>

                <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800">
                    <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        {t("co2_grid.avg_green_share", "🔋 Ø Grünstromanteil")}
                    </div>
                    <div className="text-lg font-extrabold text-teal-700 dark:text-teal-400 mt-1">
                        {data.avg_renewable_share_pct || 62.5} %
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 font-medium mt-0.5">
                        Wind + PV + Wasser
                    </div>
                </div>
            </div>

            {/* Timeline */}
            {timeline.length > 0 && (
                <div className="mt-5">
                    <div className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2 flex items-center justify-between">
                        <span>{t("co2.timeline_title", "24h CO₂-Emissions-Timeline (g CO₂ / kWh)")}</span>
                        <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                            {t("co2_grid.legend", "🟢 < 250g (Grün) · 🟡 250-420g · 🔴 > 420g")}
                        </span>
                    </div>

                    <div className="grid grid-cols-6 sm:grid-cols-12 gap-1.5 bg-slate-50 dark:bg-slate-800/50 p-2.5 rounded-2xl border border-slate-100 dark:border-slate-800">
                        {timeline.slice(0, 12).map((slot, idx) => (
                            <div
                                key={idx}
                                className={`p-2 rounded-xl text-center border transition-all ${slot.level === "green"
                                        ? "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/50"
                                        : slot.level === "red"
                                            ? "bg-rose-50 dark:bg-rose-950/40 text-rose-900 dark:text-rose-300 border-rose-200 dark:border-rose-800/50"
                                            : "bg-amber-50 dark:bg-amber-950/40 text-amber-900 dark:text-amber-300 border-amber-200 dark:border-amber-800/50"
                                    }`}
                            >
                                <div className="text-[10px] font-bold opacity-80">{slot.time_label}</div>
                                <div className="text-xs font-black mt-0.5">{slot.co2_intensity_g_per_kwh}g</div>
                                <div className="text-[9px] truncate font-semibold mt-0.5 opacity-90">
                                    {slot.renewable_share_pct}%
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Insights */}
            {insights.length > 0 && (
                <div className="mt-4 p-3.5 bg-teal-50/60 dark:bg-teal-950/30 rounded-2xl border border-teal-100 dark:border-teal-900/40 text-xs text-teal-900 dark:text-teal-200 space-y-1">
                    {insights.map((ins, i) => (
                        <div key={i} className="flex items-start gap-2">
                            <span className="text-teal-600 dark:text-teal-400 font-bold">🌿</span>
                            <span>{ins}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
