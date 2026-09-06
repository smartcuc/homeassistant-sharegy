export function translateInsight(text, t) {
    if (!text || typeof text !== "string") return text;

    // 1. Empty period data
    if (text.includes("Noch keine Messdaten für diesen Zeitraum vorhanden") || text.includes("Verbinde deine Geräte unter 'Geräte'")) {
        return t("energy.no_measurements_period", "Noch keine Messdaten für diesen Zeitraum vorhanden. Verbinde deine Geräte unter 'Geräte', um deine Energieflüsse live zu erfassen.");
    }
    if (text.includes("Noch keine Messdaten vorhanden. Sobald deine PV-Anlage Strom erzeugt")) {
        return t("forecast.no_measurements_pv", "Noch keine Messdaten vorhanden. Sobald deine PV-Anlage Strom erzeugt, wird hier die Prognosegüte analysiert.");
    }

    // 2. Autarky insights
    if (text.startsWith("Exzellente Autarkie:")) {
        const match = text.match(/([0-9]+(?:\.[0-9]+)?)\s*%/);
        const rate = match ? match[1] : "";
        return t("energy.insight_autarky_excellent", { rate, defaultValue: text });
    }
    if (text.startsWith("Gute Eigenversorgung:")) {
        const match = text.match(/([0-9]+(?:\.[0-9]+)?)\s*%/);
        const rate = match ? match[1] : "";
        return t("energy.insight_autarky_good", { rate, defaultValue: text });
    }
    if (text.startsWith("Hoher Netzbezug:")) {
        const match = text.match(/([0-9]+(?:\.[0-9]+)?)\s*%/);
        const rate = match ? match[1] : "";
        return t("energy.insight_autarky_low", { rate, defaultValue: text });
    }

    // 3. Top consumer insights
    if (text.startsWith("Größter Verbraucher:")) {
        const match = text.match(/Größter Verbraucher:\s*([^(]+?)\s*mit\s*([0-9]+(?:\.[0-9]+)?)\s*%\s*des Gesamtstroms\s*\(([0-9]+(?:\.[0-9]+)?)\s*%\s*Solaranteil\)/);
        if (match) {
            return t("energy.insight_top_consumer", { 
                name: match[1].trim(), 
                share: match[2], 
                solar: match[3], 
                defaultValue: text 
            });
        }
    }

    // 4. Financial benefit insights
    if (text.startsWith("Finanzieller Vorteil:")) {
        const match = text.match(/([0-9]+(?:\.[0-9]+)?)\s*€/);
        const amount = match ? match[1] : "";
        return t("energy.insight_financial_benefit", { amount, defaultValue: text });
    }

    return text;
}
