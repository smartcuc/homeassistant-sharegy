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
        <div className="p-6 bg-white rounded-3xl border border-slate-200/80 shadow-xs hover:border-slate-300 transition-all">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-teal-50 border border-teal-100 flex items-center justify-center text-xl shadow-2xs">
                        🌿
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h2 className="text-base font-bold text-gray-900">
                                {t("co2.title", "Live CO₂-Grid-Signal & Grünstrom-Index")}
                            </h2>
                            <span className={`px-2 py-0.5 rounded-full text-[11px] font-extrabold border ${levelBadgeColor}`}>
                                {data.current_level_label}
                            </span>
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">
                            {t("co2.subtitle", "Echtzeit-Emissionsintensität des deutschen Stromnetzes für umweltoptimiertes Laden.")}
                        </p>
                    </div>
                </div>

                <div className="text-right self-start sm:self-auto bg-teal-50/70 border border-teal-100/80 px-3.5 py-1.5 rounded-xl">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-teal-700">
                        Erneuerbaren-Anteil
                    </div>
                    <div className="text-lg font-black text-teal-900">
                        {data.current_renewable_share_pct || "65.0"} <span className="text-xs font-semibold text-teal-600">% Grünstrom</span>
                    </div>
                </div>
            </div>

            {/* KPI Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
                <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100">
                    <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                        ⚡ Live CO₂-Intensität
                    </div>
                    <div className="text-xl font-black mt-1" style={{ color: data.current_color || "#10B981" }}>
                        {data.current_co2_intensity_g_per_kwh || 220}{" "}
                        <span className="text-xs font-semibold text-slate-500">g/kWh</span>
                    </div>
                    <div className="text-[11px] text-slate-500 font-medium mt-0.5">
                        Aktueller Netzmix DE
                    </div>
                </div>

                <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100">
                    <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                        🌱 Bestes Öko-Fenster
                    </div>
                    <div className="text-lg font-extrabold text-emerald-700 mt-1 truncate" title={data.best_eco_window}>
                        {data.best_eco_window || "12:00 - 15:00"}
                    </div>
                    <div className="text-[11px] text-slate-500 font-medium mt-0.5">
                        Minimale Emissionen
                    </div>
                </div>

                <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100">
                    <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                        📊 24h-Durchschnitt
                    </div>
                    <div className="text-lg font-extrabold text-slate-800 mt-1">
                        {data.avg_co2_intensity_g_per_kwh || 310} <span className="text-xs font-semibold text-slate-500">g/kWh</span>
                    </div>
                    <div className="text-[11px] text-slate-500 font-medium mt-0.5">
                        Tagesprognose
                    </div>
                </div>

                <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100">
                    <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                        🔋 Ø Grünstromanteil
                    </div>
                    <div className="text-lg font-extrabold text-teal-700 mt-1">
                        {data.avg_renewable_share_pct || 62.5} %
                    </div>
                    <div className="text-[11px] text-slate-500 font-medium mt-0.5">
                        Wind + PV + Wasser
                    </div>
                </div>
            </div>

            {/* Timeline */}
            {timeline.length > 0 && (
                <div className="mt-5">
                    <div className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center justify-between">
                        <span>24h CO₂-Emissions-Timeline (g CO₂ / kWh)</span>
                        <span className="text-[11px] font-semibold text-emerald-600">
                            🟢 &lt; 250g (Grün) · 🟡 250-420g · 🔴 &gt; 420g
                        </span>
                    </div>

                    <div className="grid grid-cols-6 sm:grid-cols-12 gap-1.5 bg-slate-50 p-2.5 rounded-2xl border border-slate-100">
                        {timeline.slice(0, 12).map((slot, idx) => (
                            <div
                                key={idx}
                                className={`p-2 rounded-xl text-center border transition-all ${
                                    slot.level === "green"
                                        ? "bg-emerald-50 text-emerald-900 border-emerald-200"
                                        : slot.level === "red"
                                        ? "bg-rose-50 text-rose-900 border-rose-200"
                                        : "bg-amber-50 text-amber-900 border-amber-200"
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
                <div className="mt-4 p-3 bg-teal-50/60 rounded-2xl border border-teal-100 text-xs text-teal-900 space-y-1">
                    {insights.map((ins, i) => (
                        <div key={i} className="flex items-start gap-2">
                            <span className="text-teal-600 font-bold">🌿</span>
                            <span>{ins}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
