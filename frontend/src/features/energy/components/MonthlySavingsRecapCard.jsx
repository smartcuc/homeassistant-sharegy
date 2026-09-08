import { useState } from "react";
import { useTranslation } from "react-i18next";
import { TrendingUp, Trees, ShieldCheck, Zap, Share2, Sparkles, Award } from "lucide-react";
import CommunityShareModal from "../../community/components/CommunityShareModal";

export default function MonthlySavingsRecapCard({
    kpis = {},
    period = "30d",
    gridPriceCt = 36.5,
    feedinTariffCt = 8.2,
    className = "",
    onOpenShareModal,
}) {
    const { t } = useTranslation();
    const [localShareOpen, setLocalShareOpen] = useState(false);

    // kWh calculations
    const solarGenKwh = Number(kpis.solar_generation_kwh || kpis.pv_kwh || 0);
    const solarExportKwh = Number(kpis.solar_feedin_kwh || kpis.export_kwh || 0);
    const houseLoadKwh = Number(kpis.house_consumption_kwh || kpis.load_kwh || 0);
    const gridImportKwh = Number(kpis.grid_import_kwh || kpis.import_kwh || 0);
    const selfConsumedKwh = Math.max(0, solarGenKwh - solarExportKwh);

    // Financial calculations
    const gridPriceEur = gridPriceCt / 100;
    const feedinEur = feedinTariffCt / 100;
    const baselineCost = (houseLoadKwh * gridPriceEur); // Was hätte man ohne Solar gezahlt
    const actualCost = (gridImportKwh * gridPriceEur) - (solarExportKwh * feedinEur);
    const savedEur = Math.max(0, baselineCost - actualCost);

    // Ratios
    const autarkyPct = houseLoadKwh > 0 ? Math.min(100, Math.round(((houseLoadKwh - gridImportKwh) / houseLoadKwh) * 100)) : 100;
    const selfConsumptionPct = solarGenKwh > 0 ? Math.min(100, Math.round((selfConsumedKwh / solarGenKwh) * 100)) : 100;

    // Environmental metrics
    const co2AvoidedKg = Math.round(solarGenKwh * 0.42); // ~420g CO2 pro kWh deutscher Strommix
    const treesEquivalent = Math.max(1, Math.round(co2AvoidedKg / 20)); // ~20kg CO2 Bindung pro Baum/Jahr

    const periodLabel = period === "today" 
        ? t("energy.period_today", "Heute") 
        : period === "7d" 
            ? t("energy.period_7d", "Letzte 7 Tage") 
            : period === "year" 
                ? t("energy.period_year", "Dieses Jahr") 
                : t("energy.period_30d", "Letzte 30 Tage");

    const handleShareClick = () => {
        if (typeof onOpenShareModal === "function") {
            onOpenShareModal();
        } else {
            setLocalShareOpen(true);
        }
    };

    return (
        <>
            <div className={`bg-gradient-to-br from-indigo-950 via-slate-900 to-slate-950 rounded-3xl p-6 text-white border border-indigo-500/30 shadow-xl relative overflow-hidden ${className}`}>
                {/* Background Glow */}
                <div className="absolute top-0 right-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
                <div className="absolute -bottom-10 -left-10 w-64 h-64 bg-indigo-500/15 rounded-full blur-3xl pointer-events-none" />

                <div className="relative z-10 space-y-5">
                    {/* Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-indigo-800/40 pb-4">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-400/30 flex items-center justify-center text-2xl shadow-inner">
                                💰
                            </div>
                            <div>
                                <div className="flex items-center gap-2">
                                    <h3 className="text-base sm:text-lg font-black tracking-tight text-white flex items-center gap-2">
                                        <span>{t("recap.title", "Ersparnis- & ROI-Recap")}</span>
                                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                                            {periodLabel}
                                        </span>
                                    </h3>
                                </div>
                                <p className="text-xs text-indigo-200/70 mt-0.5">
                                    {t("recap.subtitle", "Reale Netzkosten-Ersparnis gegenüber dem Standard-Grundversorgertarif.")}
                                </p>
                            </div>
                        </div>

                        <button
                            type="button"
                            onClick={handleShareClick}
                            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-200 hover:text-white border border-indigo-400/30 text-xs font-bold transition cursor-pointer self-start sm:self-center shadow-xs"
                        >
                            <Share2 className="w-3.5 h-3.5" />
                            <span>{t("recap.share_btn", "Erfolge teilen")}</span>
                        </button>
                    </div>

                    {/* Main Stats Grid */}
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
                        {/* 1. Netto-Ersparnis */}
                        <div className="bg-slate-900/60 border border-indigo-500/20 rounded-2xl p-4 hover:border-indigo-400/40 transition-colors shadow-xs">
                            <div className="text-xs font-medium text-indigo-200/80 flex items-center justify-between">
                                <span>{t("recap.cost_savings", "Kostenersparnis")}</span>
                                <TrendingUp className="w-4 h-4 text-emerald-400" />
                            </div>
                            <div className="text-2xl sm:text-3xl font-black font-mono text-emerald-400 mt-1 flex items-baseline gap-1">
                                <span>{savedEur.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                                <span className="text-xs font-normal text-indigo-200/70">€</span>
                            </div>
                            <div className="text-[11px] text-emerald-300/80 mt-1 font-semibold">
                                {t("recap.vs_grid", "✓ Gegenüber {{price}} ct/kWh Netz", { price: gridPriceCt.toFixed(1) })}
                            </div>
                        </div>

                        {/* 2. Autarkiegrad */}
                        <div className="bg-slate-900/60 border border-indigo-500/20 rounded-2xl p-4 hover:border-indigo-400/40 transition-colors shadow-xs">
                            <div className="text-xs font-medium text-indigo-200/80 flex items-center justify-between">
                                <span>{t("energy.autarky_rate", "Autarkiegrad")}</span>
                                <Award className="w-4 h-4 text-amber-400" />
                            </div>
                            <div className="text-2xl sm:text-3xl font-black font-mono text-amber-300 mt-1 flex items-baseline gap-1">
                                <span>{autarkyPct}</span>
                                <span className="text-xs font-normal text-indigo-200/70">%</span>
                            </div>
                            <div className="text-[11px] text-indigo-200/60 mt-1">
                                {t("recap.own_power", "Eigenstrom aus PV & Speicher")}
                            </div>
                        </div>

                        {/* 3. CO2-Vermeidung */}
                        <div className="bg-slate-900/60 border border-indigo-500/20 rounded-2xl p-4 hover:border-indigo-400/40 transition-colors shadow-xs">
                            <div className="text-xs font-medium text-indigo-200/80 flex items-center justify-between">
                                <span>{t("energy.co2_saved", "CO₂-Vermeidung")}</span>
                                <Trees className="w-4 h-4 text-teal-400" />
                            </div>
                            <div className="text-2xl sm:text-3xl font-black font-mono text-teal-300 mt-1 flex items-baseline gap-1">
                                <span>{co2AvoidedKg}</span>
                                <span className="text-xs font-normal text-indigo-200/70">kg</span>
                            </div>
                            <div className="text-[11px] text-teal-200/80 mt-1 font-semibold">
                                {t("recap.trees_equiv", "🌳 Äquivalent zu ~{{trees}} Bäumen", { trees: treesEquivalent })}
                            </div>
                        </div>

                        {/* 4. § 14a EnWG Netzentgelt-Vorteil */}
                        <div className="bg-slate-900/60 border border-indigo-500/20 rounded-2xl p-4 hover:border-indigo-400/40 transition-colors shadow-xs">
                            <div className="text-xs font-medium text-indigo-200/80 flex items-center justify-between">
                                <span>{t("recap.grid_fee_bonus", "§ 14a Netzentgelt")}</span>
                                <ShieldCheck className="w-4 h-4 text-indigo-400" />
                            </div>
                            <div className="text-2xl sm:text-3xl font-black font-mono text-indigo-300 mt-1 flex items-baseline gap-1">
                                <span>+160</span>
                                <span className="text-xs font-normal text-indigo-200/70">€/a</span>
                            </div>
                            <div className="text-[11px] text-indigo-300/80 mt-1 font-semibold">
                                {t("recap.modul1_badge", "🛡️ Modul 1 Pauschale aktiv")}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {!onOpenShareModal && localShareOpen && (
                <CommunityShareModal
                    isOpen={localShareOpen}
                    onClose={() => setLocalShareOpen(false)}
                    kpis={kpis}
                />
            )}
        </>
    );
}
