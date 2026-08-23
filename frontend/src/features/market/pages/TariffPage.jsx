/*
# src/features/market/pages/TariffPage.jsx
*/

import HomeTariffSettingsCard from "../components/HomeTariffSettingsCard";
import TibberSettingsCard from "../components/TibberSettingsCard";
import { useTranslation } from "react-i18next";

export default function TariffPage() {
    const { t } = useTranslation();

    return (
        <div className="p-6 max-w-4xl space-y-8">
            {/* HEADER */}
            <div>
                <h1 className="text-2xl font-semibold text-gray-900">
                    💶 {t("tariffs.title", "Strompreise & Tarife")}
                </h1>
                <p className="text-sm text-gray-500 mt-1">
                    {t("tariffs.subtitle", "Konfiguriere deinen Stromvertrag (Börsenstromtarif vs. Festpreis) und verknüpfe deinen Tibber-Account für automatische Abrechnung und Smart-Charging.")}
                </p>
            </div>

            {/* 1. STROMTARIF CARD */}
            <HomeTariffSettingsCard />

            {/* 2. TIBBER CARD */}
            <TibberSettingsCard />
        </div>
    );
}
