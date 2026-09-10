/*
# src/features/market/components/TariffProfileRecommendationBanner.jsx
*/

import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useEnergyProfile } from "../../energy/hooks/useEnergyProfile";

export default function TariffProfileRecommendationBanner() {
    const { t } = useTranslation();
    const {
        profile,
        profileCode,
        isDynamicTariff,
        isDynamicRecommended,
        savingsAmount,
        isLoading,
    } = useEnergyProfile();

    if (isLoading && !profile) {
        return null;
    }

    return (
        <div className="p-5 sm:p-6 rounded-3xl bg-gradient-to-br from-indigo-900 via-slate-900 to-indigo-950 text-white shadow-lg border border-indigo-700/50 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1.5 max-w-2xl">
                    <div className="flex flex-wrap items-center gap-2">
                        <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold uppercase bg-indigo-500/30 text-indigo-300 border border-indigo-400/30">
                            {t("energy_profile.badge_label", "Energie-Profil")}: {profileCode}
                        </span>
                        <span className="text-xs font-bold text-white">
                            {profile?.profile_name}
                        </span>
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-extrabold border ${
                            isDynamicRecommended
                                ? "bg-amber-500/20 text-amber-300 border-amber-400/30"
                                : "bg-emerald-500/20 text-emerald-300 border-emerald-400/30"
                        }`}>
                            {isDynamicRecommended
                                ? t("energy_profile.tag_dynamic_recommended", "⚡ Dynamischer Tarif empfohlen")
                                : t("energy_profile.tag_static_recommended", "🔒 Fester Tarif empfohlen")}
                        </span>
                    </div>

                    <h2 className="text-lg sm:text-xl font-black text-white flex items-center gap-2">
                        <span>💡</span>
                        <span>{profile?.tariff_verdict_title}</span>
                    </h2>
                    <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
                        {profile?.tariff_verdict_reason}
                    </p>
                </div>

                <div className="shrink-0 flex flex-col sm:flex-row md:flex-col items-start md:items-end gap-2">
                    <div className="px-3.5 py-2 rounded-xl bg-white/10 backdrop-blur-xs border border-white/15 text-left md:text-right">
                        <span className="text-[10px] uppercase font-bold text-indigo-200 block">
                            {t("energy_profile.savings_potential", "Sparpotenzial")}
                        </span>
                        <span className="text-lg font-black text-emerald-400">
                            ca. {savingsAmount} €{t("energy_profile.per_year", "/Jahr")}
                        </span>
                    </div>

                    <Link
                        to="/app/energy-profile"
                        className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition shadow-xs flex items-center gap-1.5 cursor-pointer"
                    >
                        <span>🎛️</span>
                        <span>{t("energy_profile.adjust_equipment_btn", "Ausstattung & Profil anpassen")}</span>
                        <span>→</span>
                    </Link>
                </div>
            </div>

            {/* Alternativen-Box (2. Zähler / Kaskadenschaltung) */}
            <div className="p-3.5 rounded-2xl bg-white/5 border border-white/10 text-xs space-y-1">
                <div className="font-bold text-indigo-200 flex items-center gap-1.5 text-[11px]">
                    <span>ℹ️</span>
                    <span>{t("energy_profile.alt_tariff_title", "Alternative: Fester Tarif mit günstigem Lade-/Wärmetarif")}</span>
                </div>
                <p className="text-[11px] text-slate-300 leading-relaxed">
                    {profile?.alternative_tariff_hint}
                </p>
            </div>
        </div>
    );
}
