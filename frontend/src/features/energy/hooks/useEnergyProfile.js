import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

/**
 * useEnergyProfile
 * 
 * Zentraler Hook zur Bereitstellung des aktuellen Energie-Profils (A.1 bis F.1),
 * der Hardware-Ausstattung, berechneter Sparpotenziale und optimierter Tarif-Empfehlungen.
 */
export function useEnergyProfile() {
    const { i18n } = useTranslation();
    const activeLang = (i18n.language || "de").split("-")[0];

    const {
        data: profile,
        isLoading,
        isError,
        error,
        refetch,
    } = useQuery({
        queryKey: ["energy-profile", activeLang],
        queryFn: () => apiFetch(`/api/energy/profile/?lang=${activeLang}`),
        staleTime: 1000 * 60 * 5, // 5 Minuten Cache
        refetchOnWindowFocus: false,
    });

    const profileCode = profile?.profile_code || "A.1";
    const archetype = profileCode.charAt(0).toUpperCase(); // "A", "B", "C", "D", "E", "F"
    const solarType = profile?.solar_type || "none";
    const hasBattery = Boolean(profile?.has_battery);
    const hasEv = Boolean(profile?.has_ev);
    const hasHeatpump = Boolean(profile?.has_heatpump);
    const tariffType = profile?.tariff_type || "static";
    const isDynamicTariff = tariffType === "dynamic";
    const recommendedTariff = profile?.recommended_tariff || "static";
    const isDynamicRecommended = recommendedTariff === "dynamic";
    const isStaticRecommended = recommendedTariff === "static";

    // Rechner-Ergebnisse
    const savingsAmount = profile?.estimated_savings_eur_year ?? 80;
    const shiftableKwh = profile?.shiftable_kwh_year ?? 200;
    const actionLinks = profile?.action_links || [];
    const savingsBreakdown = profile?.savings_breakdown || [];
    const helpArticleSlug = profile?.help_article_slug || "tarif-und-ersparnis-kompass-matrix";

    return {
        profile,
        isLoading,
        isError,
        error,
        refetch,
        profileCode,
        archetype,
        solarType,
        hasSolar: solarType !== "none",
        hasBkw: solarType === "bkw",
        hasPv: solarType === "pv",
        hasBattery,
        hasEv,
        hasHeatpump,
        tariffType,
        isDynamicTariff,
        recommendedTariff,
        isDynamicRecommended,
        isStaticRecommended,
        savingsAmount,
        shiftableKwh,
        actionLinks,
        savingsBreakdown,
        helpArticleSlug,
    };
}
