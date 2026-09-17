/*
# src/pages/EnergyPage.jsx
*/

import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import EnergyFlow from "../components/EnergyFlow";

export default function EnergyPage() {
    const { t } = useTranslation();
    const { tenantSlug } = useParams();

    return (
        <div style={{ padding: "2rem" }}>
            <h2>{t("energy.understand_sharing", "Energy Sharing verstehen")}</h2>
            <p>{t("energy.how_distributed", "So wird Energie in deiner Community verteilt:")}</p>

            <EnergyFlow
                data={{
                    endpoint: `/api/v1/energy-flow/${tenantSlug}/`
                }}
            />
        </div>
    );
}