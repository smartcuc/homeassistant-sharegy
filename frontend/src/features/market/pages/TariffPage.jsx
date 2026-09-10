/*
# src/features/market/pages/TariffPage.jsx
*/

import HomeTariffSettingsCard from "../components/HomeTariffSettingsCard";
import TibberSettingsCard from "../components/TibberSettingsCard";
import TariffProfileRecommendationBanner from "../components/TariffProfileRecommendationBanner";
import { useTranslation } from "react-i18next";

export default function TariffPage() {
    const { t } = useTranslation();

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* HEADER */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <span>💶</span> {t("tariffs.title", "Strompreise & Tarife")}
                </h1>
                <p className="text-sm text-gray-500 dark:text-slate-400 mt-1">
                    {t("tariffs.subtitle", "Konfiguriere deinen Stromvertrag (Börsenstromtarif vs. Festpreis) und verknüpfe deinen Tibber-Account für automatische Abrechnung und Smart-Charging.")}
                </p>
            </div>

            {/* 🌟 PROFIL-BASIERTE TARIF-EMPFEHLUNG (KOMPASS) */}
            <TariffProfileRecommendationBanner />

            {/* 1. STROMTARIF CARD */}
            <HomeTariffSettingsCard />

            {/* 2. TIBBER CARD */}
            <TibberSettingsCard />
        </div>
    );
}
