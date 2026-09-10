/*
# src/features/energy/components/ProfileHeroQuickActions.jsx
*/

import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useEnergyProfile } from "../hooks/useEnergyProfile";

export default function ProfileHeroQuickActions({ className = "" }) {
    const { t } = useTranslation();
    const {
        profile,
        profileCode,
        archetype,
        solarType,
        hasBattery,
        hasEv,
        hasHeatpump,
        isDynamicTariff,
        isDynamicRecommended,
        savingsAmount,
        shiftableKwh,
        actionLinks,
        helpArticleSlug,
        isLoading,
    } = useEnergyProfile();

    if (isLoading && !profile) {
        return null;
    }

    // Archetyp-Farben & Icons
    const archetypeConfig = {
        A: { badgeBg: "bg-blue-500/20 text-blue-300 border-blue-400/30", icon: "🏢", title: t("energy_profile.default_profile_name", "Haushalt ohne Solar") },
        B: { badgeBg: "bg-amber-500/20 text-amber-300 border-amber-400/30", icon: "☀️", title: t("energy_profile.bkw_profile_name", "Balkonkraftwerk-Haushalt") },
        C: { badgeBg: "bg-emerald-500/20 text-emerald-300 border-emerald-400/30", icon: "🚗", title: t("energy_profile.ev_profile_name", "E-Mobilitäts-Haushalt") },
        D: { badgeBg: "bg-rose-500/20 text-rose-300 border-rose-400/30", icon: "♨️", title: t("energy_profile.heatpump_profile_name", "Wärmepumpen-Haushalt") },
        E: { badgeBg: "bg-indigo-500/20 text-indigo-300 border-indigo-400/30", icon: "🏡", title: t("energy_profile.prosumer_profile_name", "PV-Prosumer") },
        F: { badgeBg: "bg-purple-500/20 text-purple-300 border-purple-400/30", icon: "⚡", title: t("energy_profile.all_in_profile_name", "Voll-Elektrifiziert (All-In)") },
    };

    const currentConfig = archetypeConfig[archetype] || archetypeConfig.A;

    return (
        <div className={`p-5 sm:p-6 rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white shadow-xl border border-indigo-800/40 relative overflow-hidden ${className}`}>
            {/* Ambient background glow */}
            <div className="absolute -right-10 -bottom-10 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>

            <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                {/* Left info column */}
                <div className="space-y-3 max-w-2xl">
                    <div className="flex flex-wrap items-center gap-2">
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-extrabold border ${currentConfig.badgeBg}`}>
                            {t("energy_profile.badge_label", "Energie-Profil")}: {profileCode}
                        </span>
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                            isDynamicRecommended
                                ? "bg-amber-500/20 text-amber-300 border-amber-400/30"
                                : "bg-emerald-500/20 text-emerald-300 border-emerald-400/30"
                        }`}>
                            {isDynamicRecommended
                                ? t("energy_profile.tag_dynamic_recommended", "⚡ Dynamischer Tarif empfohlen")
                                : t("energy_profile.tag_static_recommended", "🔒 Fester Tarif empfohlen")}
                        </span>
                    </div>

                    <div>
                        <h2 className="text-xl sm:text-2xl font-black text-white flex items-center gap-2">
                            <span>{currentConfig.icon}</span>
                            <span>{profile?.profile_name || currentConfig.title}</span>
                        </h2>
                        <p className="text-xs sm:text-sm text-indigo-200/90 mt-1 leading-relaxed">
                            {profile?.profile_subtitle}
                        </p>
                    </div>

                    {/* Tarif Empfehlungs-Kurzhinweis */}
                    <div className="p-3.5 rounded-2xl bg-white/5 backdrop-blur-xs border border-white/10 text-xs text-slate-200 flex items-start gap-2.5">
                        <span className="text-base shrink-0">💡</span>
                        <div className="space-y-0.5">
                            <span className="font-bold text-indigo-200 block">
                                {profile?.tariff_verdict_title}
                            </span>
                            <p className="text-[11px] text-slate-300 leading-relaxed">
                                {profile?.tariff_verdict_reason}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Right savings + actions column */}
                <div className="flex flex-col sm:flex-row lg:flex-col items-stretch sm:items-center lg:items-end justify-between gap-4 shrink-0">
                    <div className="p-4 rounded-2xl bg-white/10 backdrop-blur-md border border-white/15 text-center min-w-[200px]">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-200 block">
                            {t("energy_profile.estimated_annual_savings", "Geschätztes Sparpotenzial")}
                        </span>
                        <div className="text-3xl font-black text-emerald-400 mt-0.5">
                            ca. {savingsAmount} €
                            <span className="text-xs font-semibold text-slate-300 block">{t("energy_profile.per_year", "/ Jahr")}</span>
                        </div>
                        <div className="text-[11px] text-indigo-200/90 pt-1.5 mt-1.5 border-t border-white/10 flex items-center justify-between">
                            <span>{t("energy_profile.shiftable_load", "Verschiebbare Last:")}</span>
                            <span className="font-bold text-white">~{shiftableKwh} kWh/a</span>
                        </div>
                    </div>

                    <div className="flex flex-wrap sm:flex-nowrap lg:flex-col gap-2 w-full">
                        <Link
                            to="/app/energy-profile"
                            className="flex-1 lg:w-full px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold text-center transition shadow-xs flex items-center justify-center gap-1.5 cursor-pointer"
                        >
                            <span>🏡</span>
                            <span>{t("energy_profile.open_profile_btn", "Profil & Rechner öffnen")}</span>
                            <span>→</span>
                        </Link>
                        <Link
                            to={`/app/help/${helpArticleSlug}`}
                            className="px-3.5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-semibold text-center transition border border-white/15 flex items-center justify-center gap-1.5 cursor-pointer"
                        >
                            <span>📖</span>
                            <span>{t("energy_profile.view_guide_btn", "Leitfaden lesen")}</span>
                        </Link>
                    </div>
                </div>
            </div>

            {/* Quick Action Buttons for Profile Archetype */}
            {actionLinks.length > 0 && (
                <div className="mt-5 pt-4 border-t border-white/10">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-300 block mb-2.5">
                        {t("energy_profile.quick_actions_title", "Empfohlene Schnellaktionen für dein Profil:")}
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                        {actionLinks.map((action, idx) => (
                            <Link
                                key={idx}
                                to={action.path}
                                className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition flex items-center gap-3 cursor-pointer group"
                            >
                                <span className="text-xl p-2 rounded-lg bg-white/10 group-hover:scale-110 transition-transform shrink-0">
                                    {action.icon}
                                </span>
                                <div className="min-w-0 flex-1">
                                    <div className="font-bold text-xs text-white truncate flex items-center gap-1">
                                        <span>{action.title}</span>
                                        <span className="text-indigo-400 group-hover:translate-x-0.5 transition-transform">→</span>
                                    </div>
                                    <div className="text-[10px] text-indigo-200/80 truncate">
                                        {action.subtitle}
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
