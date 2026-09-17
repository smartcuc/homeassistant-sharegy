import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import { useSubscription } from "../../../hooks/useSubscription";
import ProBadge from "../../../components/common/ProBadge";
import ProUpgradeModal from "../../../components/common/ProUpgradeModal";
import WallboxCard from "../../energy/components/WallboxCard";
import FuelRadarCard from "../../control/components/FuelRadarCard";
import AddWallboxModal from "../../devices/components/AddWallboxModal";

export default function MobilityPage() {
    const { t } = useTranslation();
    const { isPro, proYearlyMonthlyEquiv } = useSubscription();
    const [addWallboxOpen, setAddWallboxOpen] = useState(false);
    const [proModalOpen, setProModalOpen] = useState(false);

    // Live-Daten aus dem Spritpreis- & Mobilitätsradar abrufen
    const radarQuery = useQuery({
        queryKey: ["fuel-radar", 5.0, "all"],
        queryFn: () => apiFetch("/api/energy/fuel-radar/?radius_km=5.0&fuel_type=all"),
        staleTime: 60000,
    });

    const costComp = radarQuery.data?.cost_comparison_100km || {};
    const pvCost = costComp.ev_solar_cost_eur !== undefined 
        ? `${costComp.ev_solar_cost_eur.toFixed(2).replace(".", ",")} €` 
        : "1,44 €";
    const spotCost = costComp.ev_spot_night_cost_eur !== undefined 
        ? `${costComp.ev_spot_night_cost_eur.toFixed(2).replace(".", ",")} €` 
        : "3,24 €";
    const annualSavings = costComp.savings_annual_15k_km_eur !== undefined 
        ? `${Math.round(costComp.savings_annual_15k_km_eur).toLocaleString("de-DE")} €` 
        : "1.641 €";
    const advantagePct = costComp.solar_advantage_pct !== undefined 
        ? t("mobility.vs_combustion", { pct: costComp.solar_advantage_pct, defaultValue: `-${costComp.solar_advantage_pct}% vs. Verbrenner` })
        : t("mobility.vs_combustion", { pct: 88, defaultValue: "-88% vs. Verbrenner" });

    return (
        <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 text-white flex items-center justify-center text-2xl shadow-lg shadow-sky-500/20">
                        🚗
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h1 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
                                {t("mobility.title", "E-Mobilität & Spritpreis-Radar")}
                            </h1>
                            <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-sky-50 dark:bg-sky-950/50 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-800">
                                {t("mobility.badge", "Smart Mobility Hub")}
                            </span>
                            {!isPro && <ProBadge size="sm" />}
                        </div>
                        <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
                            {t("mobility.subtitle", "OCPP-Wallbox-Steuerung, PV-Überschussladung & Echtzeit-Spritpreisvergleich (Tankerkönig MTS-K).")}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {!isPro ? (
                        <button
                            type="button"
                            onClick={() => setProModalOpen(true)}
                            className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 text-xs font-black rounded-2xl shadow-md shadow-amber-500/20 transition cursor-pointer flex items-center gap-1.5 shrink-0"
                        >
                            <span>⭐</span>
                            <span>Auf Pro upgraden (ab {proYearlyMonthlyEquiv} €/M)</span>
                        </button>
                    ) : (
                        <button
                            type="button"
                            onClick={() => setAddWallboxOpen(true)}
                            className="px-4 py-2.5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition shadow-lg shadow-indigo-600/20 flex items-center gap-2 cursor-pointer shrink-0"
                        >
                            <span>⚡</span>
                            <span>{t("mobility.connect_wallbox", "Wallbox anbinden")}</span>
                        </button>
                    )}
                </div>
            </div>

            {/* 👑 PRO PAYWALL HERO BANNER FOR FREE USERS */}
            {!isPro && (
                <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-950 border border-indigo-500/40 rounded-3xl p-8 sm:p-10 shadow-2xl text-white relative overflow-hidden space-y-8 animate-in fade-in duration-300">
                    {/* Background glow */}
                    <div className="absolute top-0 right-0 w-96 h-96 bg-sky-500/15 rounded-full blur-3xl pointer-events-none" />
                    <div className="absolute bottom-0 left-0 w-72 h-72 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

                    <div className="relative z-10 max-w-3xl space-y-4">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-400/30 text-xs font-bold uppercase tracking-wider">
                            <span>⭐</span>
                            <span>{t("mobility.pro_exclusive", "Sharegy Pro Exklusiv")}</span>
                        </div>
                        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-white leading-tight">
                            {t("mobility.hero_title", "Lade dein E-Auto kostenlos mit 100% Sonnenstrom & günstigsten Börsenstunden")}
                        </h2>
                        <p className="text-indigo-200/80 text-sm sm:text-base leading-relaxed">
                            Automatische Phasenumschaltung, stufenlose Ampere-Steuerung (1,4–11 kW) und intelligentes Laden bei Negativpreisen. Spare bis zu 1.500 € Kraftstoffkosten jedes Jahr.
                        </p>
                    </div>

                    {/* Features Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 relative z-10">
                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">☀️</div>
                            <h3 className="text-sm font-bold text-white">{t("mobility.pv_surplus_title", "Reines PV-Überschussladen")}</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Startet den Ladevorgang erst, wenn echte Solar-Überschüsse anliegen – ohne teuren Netzstrom.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">💶</div>
                            <h3 className="text-sm font-bold text-white">{t("mobility.dynamic_spot_title", "Dynamischer Börsenstrom-Autopilot")}</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Lädt nachts vollautomatisch in den günstigsten Börsenstunden oder bei negativen Strompreisen.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">⚡</div>
                            <h3 className="text-sm font-bold text-white">{t("mobility.ocpp_shelly_title", "OCPP (1.6 / 2.0.1 / 2.1) & Shelly Support")}</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Kompatibel mit allen gängigen Wallboxen (go-e, Easee, Heidelberg, Webasto, Wallbe, Keba u.v.m.).
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">🎯</div>
                            <h3 className="text-sm font-bold text-white">{t("mobility.target_charge_title", "Zielladung & Abfahrtszeit")}</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Gib an, wann du losfahren möchtest – Sharegy berechnet den optimalen, günstigsten Ladeslot.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">⛽</div>
                            <h3 className="text-sm font-bold text-white">{t("mobility.fuel_radar_title", "MTS-K Live-Spritpreisradar")}</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Vergleicht deine 100-km-Stromladekosten in Echtzeit mit Benzin & Diesel aller Tankstellen im Umkreis.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">📊</div>
                            <h3 className="text-sm font-bold text-white">{t("mobility.trip_history_title", "Fahrten- & Ladehistorie")}</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Lückenlose Aufzeichnung aller Ladevorgänge, geladener Kilowattstunden und realisierter Ersparnisse.
                            </p>
                        </div>
                    </div>

                    {/* CTA Actions */}
                    <div className="pt-4 border-t border-indigo-800/40 relative z-10 flex flex-col sm:flex-row items-center justify-between gap-4">
                        <div className="text-xs text-indigo-200/70 text-center sm:text-left">
                            Bereits ab <strong className="text-white font-mono">{proYearlyMonthlyEquiv} €</strong> / Monat (jährliche Zahlweise) · 14 Tage kostenlos testen · Jederzeit kündbar
                        </div>
                        <div className="flex items-center gap-3 w-full sm:w-auto">
                            <button
                                type="button"
                                onClick={() => setProModalOpen(true)}
                                className="w-full sm:w-auto px-6 py-3.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 text-sm font-black rounded-2xl shadow-xl shadow-amber-500/20 transition cursor-pointer flex items-center justify-center gap-2"
                            >
                                <span>⭐</span>
                                <span>{t("mobility.unlock_pro", "E-Mobilität mit Sharegy Pro freischalten")}</span>
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* 🚗 DASHBOARD CONTENT: ECHTE DATEN BZW. GELOCKTE DEMO-VORSCHAU */}
            <div className={`space-y-6 ${!isPro ? "relative" : ""}`}>
                {!isPro && (
                    <div 
                        onClick={() => setProModalOpen(true)}
                        className="absolute inset-0 z-20 bg-slate-950/20 backdrop-blur-[1.5px] rounded-3xl cursor-pointer flex flex-col items-center justify-start pt-24 p-6 text-center hover:bg-slate-950/30 transition group"
                    >
                        <div className="px-5 py-3 rounded-2xl bg-slate-900/95 border border-indigo-500/40 shadow-2xl text-white flex items-center gap-3 transform group-hover:scale-105 transition">
                            <span className="text-xl">🔒</span>
                            <div className="text-left">
                                <div className="text-xs font-bold text-white flex items-center gap-1.5">
                                    <span>Interaktive Demo-Vorschau</span>
                                    <ProBadge size="xs" />
                                </div>
                                <div className="text-[11px] text-indigo-200/80">
                                    Klicke hier, um alle Lade- und Mobilitätsoptionen mit Sharegy Pro freizuschalten
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Quick Mobility Overview Banner (Live Berechnet) */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
                        <div className="w-11 h-11 rounded-2xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-xl shrink-0">
                            ☀️
                        </div>
                        <div>
                            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">{t("mobility.pv_charging", "PV-Überschuss Laden")}</div>
                            <div className="text-base font-black text-slate-900 dark:text-white font-mono">{pvCost} <span className="text-xs font-normal text-slate-500">/ 100 km</span></div>
                            <div className="text-[11px] text-emerald-600 dark:text-emerald-400 font-bold">{advantagePct}</div>
                        </div>
                    </div>

                    <div className="p-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
                        <div className="w-11 h-11 rounded-2xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-xl shrink-0">
                            🌙
                        </div>
                        <div>
                            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">{t("mobility.spot_tariff", "Spot-Nachttarif")}</div>
                            <div className="text-base font-black text-slate-900 dark:text-white font-mono">{spotCost} <span className="text-xs font-normal text-slate-500">/ 100 km</span></div>
                            <div className="text-[11px] text-indigo-600 dark:text-indigo-400 font-bold">{t("mobility.cheapest_hours", "Günstigste Börsenstunden")}</div>
                        </div>
                    </div>

                    <div className="p-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
                        <div className="w-11 h-11 rounded-2xl bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 flex items-center justify-center text-xl shrink-0">
                            💶
                        </div>
                        <div>
                            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">{t("mobility.savings_potential", "Ersparnis-Potenzial")}</div>
                            <div className="text-base font-black text-slate-900 dark:text-white font-mono">{annualSavings} <span className="text-xs font-normal text-slate-500">/ Jahr</span></div>
                            <div className="text-[11px] text-slate-500">{t("mobility.per_15k_km", "bei 15.000 km Fahrleistung")}</div>
                        </div>
                    </div>
                </div>

                {/* Main Cards Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* 🚗 Wallbox / OCPP E-Auto Ladekarte */}
                    <div className="space-y-4">
                        <WallboxCard onOpenAddModal={() => setAddWallboxOpen(true)} />
                    </div>

                    {/* ⛽ Mobilitäts- & Spritpreis-Radar (MTS-K / Tankerkönig) */}
                    <div className="space-y-4">
                        <FuelRadarCard />
                    </div>
                </div>
            </div>

            {/* Modal: Wallbox anbinden */}
            {addWallboxOpen && (
                <AddWallboxModal isOpen={addWallboxOpen} onClose={() => setAddWallboxOpen(false)} />
            )}

            {/* Pro Upgrade Modal */}
            <ProUpgradeModal
                open={proModalOpen}
                onClose={() => setProModalOpen(false)}
                featureName="Smart E-Mobilität & Wallbox-Autopilot"
                featureDesc="Optimiere deine Wallbox mit automatischem PV-Überschussladen, dynamischen Börsen-Nachttarifen und spare bis zu 1.500 € Kraftstoffkosten im Jahr."
            />
        </div>
    );
}
