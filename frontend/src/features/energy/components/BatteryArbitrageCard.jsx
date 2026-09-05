import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import { useSubscription } from "../../../hooks/useSubscription";
import ProBadge from "../../../components/common/ProBadge";
import ProUpgradeModal from "../../../components/common/ProUpgradeModal";

export default function BatteryArbitrageCard() {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const [proModalOpen, setProModalOpen] = useState(false);

    const arbitrageQuery = useQuery({
        queryKey: ["battery-arbitrage"],
        queryFn: () => apiFetch("/api/energy/battery-arbitrage/"),
        refetchInterval: 30000,
        enabled: isPro,
    });

    const data = arbitrageQuery.data || {};
    const timeline = data.timeline || [];
    const advice = data.advice || [];

    if (!isPro) {
        return (
            <div className="p-6 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 rounded-3xl border border-indigo-500/30 shadow-xl text-white relative overflow-hidden flex flex-col justify-between">
                {/* Background ambient glow */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

                <div className="space-y-4 relative z-10">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-2xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-xl shadow-2xs">
                                🔋
                            </div>
                            <div>
                                <div className="flex items-center gap-2">
                                    <h2 className="text-base font-bold text-white">
                                        {t("arbitrage.title", "Grid-Charging Arbitrage & Speicher-Simulator")}
                                    </h2>
                                    <ProBadge size="sm" />
                                </div>
                                <p className="text-xs text-indigo-200/70 mt-0.5">
                                    {t("arbitrage.subtitle", "Intelligentes Laden des Hausspeichers bei Tiefstpreisen und Entladen in Spitzenzeiten.")}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-xs space-y-2.5">
                        <div className="flex items-center justify-between text-xs text-indigo-200">
                            <span>⚡ Durchschnittlicher Preis-Spread:</span>
                            <span className="font-bold text-emerald-400 font-mono">+14,8 ct / kWh</span>
                        </div>
                        <div className="flex items-center justify-between text-xs text-indigo-200">
                            <span>📈 Mögliche Netto-Ersparnis:</span>
                            <span className="font-bold text-amber-300 font-mono">bis zu 350 € / Jahr</span>
                        </div>
                        <div className="flex items-center justify-between text-xs text-indigo-200">
                            <span>🔄 Dynamische Börsenpreis-Steuerung:</span>
                            <span className="font-bold text-indigo-300">Automatischer Ladefahrplan</span>
                        </div>
                    </div>
                </div>

                <div className="pt-5 mt-4 border-t border-indigo-800/40 relative z-10 flex items-center justify-between gap-4">
                    <span className="text-xs text-indigo-200/60 hidden sm:inline">
                        Exklusiv für Pro-Abonnenten verfügbar
                    </span>
                    <button
                        type="button"
                        onClick={() => setProModalOpen(true)}
                        className="w-full sm:w-auto px-5 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 text-xs font-black rounded-xl shadow-lg shadow-amber-500/20 transition cursor-pointer flex items-center justify-center gap-2"
                    >
                        <span>⭐</span>
                        <span>{t("arbitrage.unlock_pro", "Speicher-Arbitrage freischalten")}</span>
                    </button>
                </div>

                <ProUpgradeModal
                    open={proModalOpen}
                    onClose={() => setProModalOpen(false)}
                    featureName="Batterie-Arbitrage & Grid-Charging Simulator"
                    featureDesc="Simuliere und automatisiere die Beladung deines Heimspeichers bei negativen oder extrem günstigen Börsenstrompreisen für maximale finanzielle Rendite."
                />
            </div>
        );
    }

    if (arbitrageQuery.isLoading) {
        return (
            <div className="p-6 bg-white rounded-3xl border border-slate-200/80 shadow-xs animate-pulse">
                <div className="h-5 bg-slate-200 rounded w-1/3 mb-4"></div>
                <div className="h-24 bg-slate-100 rounded-xl"></div>
            </div>
        );
    }

    return (
        <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-slate-300 dark:hover:border-slate-700 transition-all">
            {/* Header */}
            <div className="border-b border-slate-100 dark:border-slate-800 pb-4 space-y-2">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-100 dark:border-indigo-800/60 flex items-center justify-center text-xl shadow-2xs shrink-0">
                        🔋
                    </div>
                    <div className="min-w-0">
                        <h2 className="text-base font-bold text-slate-900 dark:text-white">
                            {t("arbitrage.title", "Grid-Charging Arbitrage & Speicher-Simulator")}
                        </h2>
                    </div>
                </div>

                <p className="text-xs text-slate-500 dark:text-slate-400">
                    {t("arbitrage.subtitle", "Intelligentes Laden des Hausspeichers bei Tiefstpreisen und Entladen in Spitzenzeiten.")}
                </p>

                {/* Subtitle Details: Rentabel & Zusatzerlös */}
                <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                    <div className="flex items-center gap-2">
                        {data.is_arbitrage_profitable ? (
                            <span className="px-2.5 py-1 rounded-xl text-xs font-extrabold bg-emerald-100 dark:bg-emerald-950/50 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/60">
                                🟢 {t("arbitrage.profitable", "Rentabel")} (+{data.price_spread_ct_per_kwh} ct/kWh)
                            </span>
                        ) : (
                            <span className="px-2.5 py-1 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                                {t("arbitrage.pv_priority", "⚪ PV-Priorität")}
                            </span>
                        )}
                    </div>

                    <div className="flex items-center gap-2 bg-indigo-50/70 dark:bg-indigo-950/40 border border-indigo-100/80 dark:border-indigo-800/60 px-3 py-1.5 rounded-xl">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-700 dark:text-indigo-400">
                            {t("arbitrage.savings_projected", "Zusatzerlös / Ersparnis")}:
                        </span>
                        <span className="text-sm font-black text-indigo-900 dark:text-indigo-200 font-mono">
                            ~{data.projected_yearly_savings_eur?.toFixed(0) || "0"} € <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">{t("arbitrage.per_year", "/ Jahr")}</span>
                        </span>
                    </div>
                </div>
            </div>

            {/* KPI Grid (2 rows of 2 boxes) */}
            <div className="grid grid-cols-2 gap-3 mt-4">
                <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800">
                    <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        {t("arbitrage.best_charge_price", "🌙 Günstigster Ladepreis")}
                    </div>
                    <div className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5 font-mono">
                        {data.best_charge_window?.price_ct_per_kwh !== undefined && data.best_charge_window?.price_ct_per_kwh !== null
                            ? `${Number(data.best_charge_window.price_ct_per_kwh).toFixed(1)} ct/kWh`
                            : data.avg_charge_price_ct !== undefined && data.avg_charge_price_ct !== null
                                ? `${Number(data.avg_charge_price_ct).toFixed(1)} ct/kWh`
                                : "--"}
                    </div>
                    <div className="text-[11px] text-slate-400 dark:text-slate-500 font-medium mt-0.5 truncate">
                        {data.best_charge_window?.window_label || (typeof data.best_charge_window === "string" ? data.best_charge_window : (data.best_charge_window?.start_time ? `um ${data.best_charge_window.start_time} Uhr` : "--"))}
                    </div>
                </div>

                <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800">
                    <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        {t("arbitrage.best_discharge_price", "⚡ Höchster Entladepreis")}
                    </div>
                    <div className="text-lg font-extrabold text-indigo-600 dark:text-indigo-400 mt-0.5 font-mono">
                        {data.best_discharge_window?.price_ct_per_kwh !== undefined && data.best_discharge_window?.price_ct_per_kwh !== null
                            ? `${Number(data.best_discharge_window.price_ct_per_kwh).toFixed(1)} ct/kWh`
                            : data.avg_discharge_price_ct !== undefined && data.avg_discharge_price_ct !== null
                                ? `${Number(data.avg_discharge_price_ct).toFixed(1)} ct/kWh`
                                : "--"}
                    </div>
                    <div className="text-[11px] text-slate-400 dark:text-slate-500 font-medium mt-0.5 truncate">
                        {data.best_discharge_window?.window_label || (typeof data.best_discharge_window === "string" ? data.best_discharge_window : (data.best_discharge_window?.start_time ? `um ${data.best_discharge_window.start_time} Uhr` : "--"))}
                    </div>
                </div>

                <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800">
                    <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        {t("arbitrage.price_spread", "📊 Preis-Spread")}
                    </div>
                    <div className="text-lg font-extrabold text-slate-900 dark:text-white mt-0.5 font-mono">
                        {data.price_spread_ct_per_kwh !== undefined ? Number(data.price_spread_ct_per_kwh).toFixed(1) : "0.0"} <span className="text-xs font-normal text-slate-400">ct/kWh</span>
                    </div>
                    <div className="text-[11px] text-slate-400 dark:text-slate-500 font-medium mt-0.5">
                        {t("arbitrage.gross_spread", "Brutto-Differenz")}
                    </div>
                </div>

                <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800">
                    <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        {t("arbitrage.cycle_loss", "🔌 Verlustbereinigt")}
                    </div>
                    <div className="text-lg font-extrabold text-emerald-700 dark:text-emerald-400 mt-0.5 font-mono">
                        {data.is_arbitrage_profitable && data.price_spread_ct_per_kwh > 0
                            ? `+${(Number(data.price_spread_ct_per_kwh) * 0.88).toFixed(1)}`
                            : "0.0"} <span className="text-xs font-normal text-slate-400">ct/kWh</span>
                    </div>
                    <div className="text-[11px] text-slate-400 dark:text-slate-500 font-medium mt-0.5">
                        {t("arbitrage.efficiency_note", "inkl. 88% Speichereffizienz")}
                    </div>
                </div>
            </div>

            {/* Recommendations / Advice List */}
            {advice.length > 0 && (
                <div className="mt-4 space-y-2">
                    <div className="text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                        {t("arbitrage.strategy_advice", "💡 Handlungsempfehlungen für deinen Speicher")}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {advice.map((item, idx) => {
                            const isString = typeof item === "string";
                            const type = isString ? "general" : item.type;
                            const icon = isString ? "💡" : (item.icon || "ℹ️");
                            const title = isString ? (item.split(":")[0] || "Empfehlung") : item.title;
                            const description = isString ? (item.includes(":") ? item.split(":").slice(1).join(":") : item) : item.description;

                            return (
                                <div
                                    key={idx}
                                    className={`p-3 rounded-2xl border text-xs flex items-start gap-2.5 ${type === "charge"
                                        ? "bg-emerald-50/60 dark:bg-emerald-950/30 border-emerald-200/80 dark:border-emerald-800/50 text-emerald-900 dark:text-emerald-200"
                                        : type === "discharge"
                                            ? "bg-indigo-50/60 dark:bg-indigo-950/30 border-indigo-200/80 dark:border-indigo-800/50 text-indigo-900 dark:text-indigo-200"
                                            : "bg-slate-50 dark:bg-slate-800/40 border-slate-200/80 dark:border-slate-700/50 text-slate-800 dark:text-slate-200"
                                        }`}
                                >
                                    <span className="text-base leading-none shrink-0">{icon}</span>
                                    <div className="space-y-0.5">
                                        <div className="font-bold">{title}</div>
                                        <div className="text-slate-600 dark:text-slate-400 leading-relaxed">{description}</div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Full-width status message at the bottom */}
            {data.status_message && (
                <div className="mt-4 p-3 bg-indigo-50/60 dark:bg-indigo-950/30 rounded-2xl border border-indigo-100 dark:border-indigo-900/40 text-xs text-indigo-900 dark:text-indigo-200 flex items-center gap-2">
                    <span className="text-indigo-600 dark:text-indigo-400 font-bold shrink-0">ℹ️</span>
                    <span>{data.status_message}</span>
                </div>
            )}
        </div>
    );
}
