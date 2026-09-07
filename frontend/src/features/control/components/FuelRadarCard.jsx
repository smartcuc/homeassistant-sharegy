import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function FuelRadarCard() {
    const { t } = useTranslation();
    const [radiusKm, setRadiusKm] = useState(5.0);
    const [fuelType, setFuelType] = useState("e10"); // "e10", "e5", "diesel"

    const radarQuery = useQuery({
        queryKey: ["fuel-radar", radiusKm, fuelType],
        queryFn: () => apiFetch(`/api/energy/fuel-radar/?radius_km=${radiusKm}&fuel_type=${fuelType}`),
        refetchInterval: 60000,
    });

    const data = radarQuery.data || {};
    const bestPrices = data.best_prices || {};
    const timing = data.timing_advice || {};
    const costComp = data.cost_comparison_100km || {};
    const stations = data.stations || [];
    const location = data.location || {};

    const currentBest = bestPrices[fuelType] || null;

    // Dynamisch berechnete Balken-Breiten
    const maxCost = Math.max(costComp.gasoline_e10_cost_eur || 12.0, costComp.diesel_cost_eur || 9.5, 1.0);
    const solarWidthPct = Math.max(8, Math.min(100, Math.round(((costComp.ev_solar_cost_eur || 1.44) / maxCost) * 100)));
    const spotWidthPct = Math.max(12, Math.min(100, Math.round(((costComp.ev_spot_night_cost_eur || 3.24) / maxCost) * 100)));
    const dieselWidthPct = Math.max(20, Math.min(100, Math.round(((costComp.diesel_cost_eur || 9.53) / maxCost) * 100)));

    return (
        <div className="relative overflow-hidden bg-white dark:bg-slate-900/90 rounded-3xl border border-slate-200/80 dark:border-slate-800 p-5 sm:p-6 shadow-xs backdrop-blur-xl transition-all hover:border-emerald-500/40">
            {/* Header: Title & Radius Filter */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-3">
                    <div className="w-11 h-11 rounded-2xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 flex items-center justify-center text-xl shadow-inner">
                        ⛽
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h3 className="text-base font-bold text-slate-900 dark:text-white">
                                {t("control.fuel_radar", "Mobilitäts- & Spritpreis-Radar")}
                            </h3>
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30">
                                <span>MTS-K Live</span>
                            </span>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                            {location.city || location.postal_code 
                                ? `Günstigste Tankstellen in ${location.postal_code} ${location.city} & 100km Kostenvergleich`
                                : t("control.fuel_radar_desc", "Günstigste Tankstellen im Umkreis & 100km Real-Kostenvergleich")
                            }
                        </p>
                    </div>
                </div>

                {/* Radius Buttons */}
                <div className="flex items-center gap-1 self-start sm:self-auto bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
                    {[5.0, 10.0, 25.0].map((r) => (
                        <button
                            key={r}
                            onClick={() => setRadiusKm(r)}
                            className={`px-2.5 py-1 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
                                radiusKm === r
                                    ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-2xs font-bold"
                                    : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                            }`}
                        >
                            {r} km
                        </button>
                    ))}
                </div>
            </div>

            {/* Fuel Type Switcher Tabs */}
            <div className="grid grid-cols-3 gap-2 mb-4">
                {[
                    { key: "e10", label: "Super E10", icon: "⛽", price: bestPrices.e10?.price, bestSt: bestPrices.e10?.station },
                    { key: "e5", label: "Super E5", icon: "🔵", price: bestPrices.e5?.price, bestSt: bestPrices.e5?.station },
                    { key: "diesel", label: "Diesel", icon: "🛢️", price: bestPrices.diesel?.price, bestSt: bestPrices.diesel?.station },
                ].map((f) => (
                    <button
                        key={f.key}
                        onClick={() => setFuelType(f.key)}
                        className={`p-2.5 rounded-2xl border text-left transition-all cursor-pointer ${
                            fuelType === f.key
                                ? "bg-emerald-50/80 dark:bg-emerald-950/40 border-emerald-500/50 shadow-xs"
                                : "bg-slate-50/80 dark:bg-slate-800/40 border-slate-200/60 dark:border-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800"
                        }`}
                    >
                        <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
                            <span>{f.icon} {f.label}</span>
                            <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400">ab</span>
                        </div>
                        <div className="text-base font-black text-slate-900 dark:text-white mt-0.5 font-mono">
                            {f.price ? `${f.price.toFixed(3)} €` : "—"}
                        </div>
                        <div className="text-[10px] text-slate-400 truncate">
                            {f.bestSt ? `bester Preis bei ${f.bestSt}` : "Suche..."}
                        </div>
                    </button>
                ))}
            </div>

            {/* Top Stations Grid */}
            <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-[11px] font-bold text-slate-700 dark:text-slate-300">
                    <span>Günstigste Tankstellen ({fuelType.toUpperCase()}):</span>
                    <span className="text-slate-400 font-normal">Sortiert nach Entfernung</span>
                </div>

                {radarQuery.isLoading ? (
                    <div className="p-6 text-center text-xs text-slate-400 animate-pulse">
                        Lade aktuelle Kraftstoffpreise via MTS-K...
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {stations.slice(0, 4).map((st, idx) => {
                            const price = st[fuelType];
                            const isCheapest = price && currentBest && price <= (currentBest.price || 99);

                            return (
                                <div
                                    key={st.id || idx}
                                    className={`p-3 rounded-2xl border flex items-center justify-between gap-2 transition-all ${
                                        isCheapest
                                            ? "bg-emerald-50/40 dark:bg-emerald-950/20 border-emerald-500/40"
                                            : "bg-slate-50/70 dark:bg-slate-800/50 border-slate-200/60 dark:border-slate-800/60"
                                    }`}
                                >
                                    <div className="min-w-0">
                                        <div className="flex items-center gap-1.5">
                                            <span className="font-bold text-xs text-slate-900 dark:text-white truncate">
                                                {st.name || st.brand}
                                            </span>
                                            {isCheapest && (
                                                <span className="text-[9px] font-extrabold px-1.5 py-0.2 rounded bg-emerald-500 text-white shrink-0">
                                                    TIEFSTPREIS
                                                </span>
                                            )}
                                        </div>
                                        <div className="text-[10px] text-slate-400 truncate">
                                            {st.street ? `${st.street} · ` : ""}<strong className="text-slate-600 dark:text-slate-300">{st.dist_km} km</strong>
                                        </div>
                                    </div>

                                    <div className="text-right shrink-0">
                                        <div className="text-sm font-black text-slate-900 dark:text-white font-mono">
                                            {price ? `${price.toFixed(3)} €` : "—"}
                                        </div>
                                        <div className="text-[9px] font-semibold text-emerald-600 dark:text-emerald-400">
                                            {st.is_open ? "🟢 Geöffnet" : "🔴 Geschlossen"}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* ⚡ MOBILITÄTS-KOSTENVERGLEICH (100 KM) */}
            <div className="mb-4 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-950 rounded-2xl p-4 text-white border border-indigo-500/30 shadow-md">
                <div className="flex items-center justify-between text-xs mb-3">
                    <span className="font-bold text-indigo-200 flex items-center gap-1.5">
                        <span>⚡</span> 100-km Real-Kostenvergleich (EV vs. Verbrenner)
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 font-bold">
                        -{costComp.solar_advantage_pct || 88}% mit Solar
                    </span>
                </div>

                <div className="space-y-2 text-xs">
                    {/* 1. E-Auto Solar */}
                    <div>
                        <div className="flex justify-between text-[11px] mb-0.5">
                            <span className="text-emerald-400 font-bold flex items-center gap-1">
                                <span>☀️</span> E-Auto (Solar-Überschuss 8 ct)
                            </span>
                            <span className="font-black text-emerald-400 font-mono">{costComp.ev_solar_cost_eur !== undefined ? costComp.ev_solar_cost_eur.toFixed(2) : "1.44"} € / 100 km</span>
                        </div>
                        <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div className="bg-emerald-500 h-full rounded-full transition-all duration-500" style={{ width: `${solarWidthPct}%` }}></div>
                        </div>
                    </div>

                    {/* 2. E-Auto Börsentarif */}
                    <div>
                        <div className="flex justify-between text-[11px] mb-0.5">
                            <span className="text-indigo-300 font-semibold flex items-center gap-1">
                                <span>🌙</span> E-Auto (Börsen-Nachtladen)
                            </span>
                            <span className="font-bold text-indigo-200 font-mono">{costComp.ev_spot_night_cost_eur !== undefined ? costComp.ev_spot_night_cost_eur.toFixed(2) : "3.24"} € / 100 km</span>
                        </div>
                        <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div className="bg-indigo-400 h-full rounded-full transition-all duration-500" style={{ width: `${spotWidthPct}%` }}></div>
                        </div>
                    </div>

                    {/* 3. Diesel */}
                    <div>
                        <div className="flex justify-between text-[11px] mb-0.5">
                            <span className="text-slate-400 flex items-center gap-1">
                                <span>🛢️</span> Diesel ({bestPrices.diesel?.price ? bestPrices.diesel.price.toFixed(3) : "1.589"} €/l · 6.0 l)
                            </span>
                            <span className="font-semibold text-slate-300 font-mono">{costComp.diesel_cost_eur !== undefined ? costComp.diesel_cost_eur.toFixed(2) : "9.53"} € / 100 km</span>
                        </div>
                        <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div className="bg-amber-500 h-full rounded-full transition-all duration-500" style={{ width: `${dieselWidthPct}%` }}></div>
                        </div>
                    </div>

                    {/* 4. Benziner E10 */}
                    <div>
                        <div className="flex justify-between text-[11px] mb-0.5">
                            <span className="text-slate-400 flex items-center gap-1">
                                <span>⛽</span> Benziner E10 ({bestPrices.e10?.price ? bestPrices.e10.price.toFixed(3) : "1.719"} €/l · 7.2 l)
                            </span>
                            <span className="font-semibold text-slate-300 font-mono">{costComp.gasoline_e10_cost_eur !== undefined ? costComp.gasoline_e10_cost_eur.toFixed(2) : "12.38"} € / 100 km</span>
                        </div>
                        <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div className="bg-red-500 h-full rounded-full transition-all duration-500" style={{ width: "100%" }}></div>
                        </div>
                    </div>
                </div>

                {/* Savings Callout Banner */}
                <div className="mt-3 pt-2.5 border-t border-indigo-900/60 flex items-center justify-between text-xs">
                    <span className="text-indigo-200/80">Ersparnis mit PV-Laden:</span>
                    <span className="font-black text-emerald-400 font-mono">
                        ~{costComp.savings_vs_gasoline_per_100km_eur !== undefined ? costComp.savings_vs_gasoline_per_100km_eur.toFixed(2) : "10.94"} € / 100 km · ~{costComp.savings_annual_15k_km_eur !== undefined ? Math.round(costComp.savings_annual_15k_km_eur).toLocaleString("de-DE") : "1.641"} € / Jahr
                    </span>
                </div>
            </div>

            {/* Timing Advice Footer */}
            <div className="text-xs bg-slate-100/70 dark:bg-slate-800/70 text-slate-600 dark:text-slate-300 p-2.5 rounded-xl flex items-center justify-between gap-2 border border-slate-200/50 dark:border-slate-700/50">
                <div className="flex items-center gap-2">
                    <span className="text-sm">💡</span>
                    <span className="font-medium">{timing.text || "Preise sinken zum Abend hin ab 18:00 Uhr."}</span>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-lg bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 shrink-0">
                    {timing.badge || "Günstiges Fenster"}
                </span>
            </div>
        </div>
    );
}
