/*
# src/features/market/components/HomeTariffSettingsCard.jsx
*/

import { useState, useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import Card from "../../../components/ui/Card";
import { fetchHomeTariff, saveHomeTariff } from "../api";
import { useTranslation } from "react-i18next";

function parseCt(val) {
    if (val === null || val === undefined || val === "") return null;
    const normalized = String(val).replace(",", ".").trim();
    const num = Number(normalized);
    return isNaN(num) ? null : num;
}

export default function HomeTariffSettingsCard() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const { data: tariffData, isLoading, isError } = useQuery({
        queryKey: ["home-tariff"],
        queryFn: fetchHomeTariff,
    });

    const [tariffType, setTariffType] = useState("dynamic");
    const [staticPriceCt, setStaticPriceCt] = useState("32.00");
    const [feedInTariffType, setFeedInTariffType] = useState("static");
    const [feedInPriceCt, setFeedInPriceCt] = useState("8.20");
    const [showBreakdown, setShowBreakdown] = useState(false);
    const [statusMsg, setStatusMsg] = useState(null);
    const [isSaving, setIsSaving] = useState(false);

    // Synchronize local form state with fetched tariff data
    useEffect(() => {
        if (tariffData) {
            setTariffType(tariffData.tariff_type || "dynamic");
            if (tariffData.static_price_ct != null) {
                setStaticPriceCt(String(tariffData.static_price_ct));
            }
            setFeedInTariffType(tariffData.feed_in_tariff_type || "static");
            if (tariffData.feed_in_tariff_ct != null) {
                setFeedInPriceCt(String(tariffData.feed_in_tariff_ct));
            }
        }
    }, [tariffData]);

    async function handleSave(e) {
        if (e && typeof e.preventDefault === "function") {
            e.preventDefault();
        }

        const parsedStaticPrice = parseCt(staticPriceCt);
        if (tariffType === "static" && (parsedStaticPrice === null || parsedStaticPrice <= 0)) {
            setStatusMsg({ type: "error", text: t("tariffs.invalid_price", "Bitte einen gültigen Arbeitspreis in ct/kWh eingeben.") });
            return;
        }

        const parsedFeedInPrice = parseCt(feedInPriceCt);
        if (feedInTariffType === "static" && (parsedFeedInPrice === null || parsedFeedInPrice < 0)) {
            setStatusMsg({ type: "error", text: t("tariffs.invalid_feedin_price", "Bitte eine gültige Einspeisevergütung in ct/kWh eingeben.") });
            return;
        }

        const payload = {
            tariff_type: tariffType,
            static_price_ct: tariffType === "static" ? parsedStaticPrice : null,
            feed_in_tariff_type: feedInTariffType,
            feed_in_tariff_ct: feedInTariffType === "static" ? parsedFeedInPrice : 0,
        };

        setIsSaving(true);
        setStatusMsg(null);

        try {
            const updated = await saveHomeTariff(payload);
            queryClient.setQueryData(["home-tariff"], updated);
            queryClient.invalidateQueries({ queryKey: ["home-tariff"] });
            queryClient.invalidateQueries({ queryKey: ["spot-price-chart"] });
            queryClient.invalidateQueries({ queryKey: ["energy-data"] });
            queryClient.invalidateQueries({ queryKey: ["energy-balance"] });

            if (updated) {
                setTariffType(updated.tariff_type || "dynamic");
                if (updated.static_price_ct != null) {
                    setStaticPriceCt(String(updated.static_price_ct));
                }
                setFeedInTariffType(updated.feed_in_tariff_type || "static");
                if (updated.feed_in_tariff_ct != null) {
                    setFeedInPriceCt(String(updated.feed_in_tariff_ct));
                }
            }

            setStatusMsg({ type: "success", text: t("tariffs.save_success", "Strom- & Einspeisetarif erfolgreich gespeichert!") });
            setTimeout(() => setStatusMsg(null), 4000);
        } catch (err) {
            setStatusMsg({
                type: "error",
                text: err?.data?.detail || err?.data?.error || err?.detail || err?.message || t("tariffs.save_error", "Fehler beim Speichern des Tarifs."),
            });
            setTimeout(() => setStatusMsg(null), 5000);
        } finally {
            setIsSaving(false);
        }
    }

    if (isLoading) {
        return (
            <Card>
                <div className="p-4 text-sm text-gray-400 animate-pulse">
                    {t("tariffs.loading", "Lade Stromtarif-Einstellungen…")}
                </div>
            </Card>
        );
    }

    if (isError) {
        return null;
    }

    const priceConfig = tariffData?.price_config;

    return (
        <Card>
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h2 className="font-semibold text-gray-900 text-base">
                        ⚡ {t("tariffs.model_title", "Strombezug & Tarifmodell")}
                    </h2>
                    <p className="text-xs text-gray-500 mt-0.5">
                        {t("tariffs.model_desc", { home: tariffData?.home_name || t("profile.home_single", "dein Zuhause"), defaultValue: `Definiere dein Bezugs- und Einspeisemodell für ${tariffData?.home_name || "dein Zuhause"}, um Stromkosten und Einsparungen exakt zu berechnen.` })}
                    </p>
                </div>
            </div>

            <form onSubmit={handleSave} className="space-y-6">
                {/* =========================================================
                    SECTION 1: STROMBEZUGSTARIF
                ========================================================= */}
                <div className="space-y-3">
                    <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                        1. {t("tariffs.section_import", "Strombezug (Netzstrom)")}
                    </h3>

                    {/* 1.1 OPTION: DYNAMISCH */}
                    <div
                        onClick={() => setTariffType("dynamic")}
                        className={`
                            p-4 rounded-xl border-2 cursor-pointer transition-all duration-150
                            ${tariffType === "dynamic"
                                ? "border-emerald-500 bg-emerald-50/50 shadow-sm"
                                : "border-gray-200 hover:border-gray-300 bg-white"}
                        `}
                    >
                        <div className="flex items-start gap-3">
                            <input
                                type="radio"
                                id="tariff_dynamic"
                                name="tariff_type"
                                value="dynamic"
                                checked={tariffType === "dynamic"}
                                onChange={() => setTariffType("dynamic")}
                                className="mt-1 h-4 w-4 text-emerald-600 focus:ring-emerald-500 border-gray-300"
                            />
                            <div className="flex-1">
                                <div className="flex items-center gap-2">
                                    <label htmlFor="tariff_dynamic" className="font-medium text-sm text-gray-900 cursor-pointer">
                                        {t("tariffs.dynamic_title", "Dynamischer Börsenstrompreis (z. B. Tibber, Rabot, Ostrom)")}
                                    </label>
                                    <span className="text-[10px] px-2 py-0.5 font-medium rounded-full bg-emerald-100 text-emerald-800">
                                        EPEX Spot
                                    </span>
                                </div>
                                <p className="text-xs text-gray-500 mt-1">
                                    {t("tariffs.dynamic_desc", "Abrechnung viertelstündlich / stündlich nach dem aktuellen Börsenstrompreis zzgl. gesetzlicher Abgaben, Netzentgelte und Steuern.")}
                                </p>

                                {/* Preisbestandteile Detail-Toggle */}
                                {priceConfig && (
                                    <div className="mt-3">
                                        <button
                                            type="button"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setShowBreakdown(!showBreakdown);
                                            }}
                                            className="text-xs font-medium text-emerald-700 hover:text-emerald-800 underline inline-flex items-center gap-1 cursor-pointer"
                                        >
                                            {showBreakdown ? t("tariffs.hide_breakdown", "▲ Feste Preisbestandteile ausblenden") : `${t("tariffs.show_breakdown", "▼ Feste Preisbestandteile anzeigen")} (~${priceConfig.additional_costs_ct.toFixed(2)} ct/kWh netto)`}
                                        </button>

                                        {showBreakdown && (
                                            <div className="mt-2 p-3 bg-white/80 rounded-lg border border-emerald-200 text-xs space-y-1 text-gray-600">
                                                <div className="flex justify-between">
                                                    <span>{t("tariffs.grid_fees", "Netzentgelte:")}</span>
                                                    <span className="font-medium text-gray-900">{priceConfig.grid_fee_ct.toFixed(2)} ct/kWh</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>{t("tariffs.electricity_tax", "Stromsteuer:")}</span>
                                                    <span className="font-medium text-gray-900">{priceConfig.electricity_tax_ct.toFixed(2)} ct/kWh</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>{t("tariffs.concession_fee", "Konzessionsabgabe:")}</span>
                                                    <span className="font-medium text-gray-900">{priceConfig.concession_fee_ct.toFixed(2)} ct/kWh</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>{t("tariffs.levies", "Umlagen (KWK, §19, Offshore):")}</span>
                                                    <span className="font-medium text-gray-900">
                                                        {(priceConfig.kwk_levy_ct + priceConfig.special_grid_levy_ct + priceConfig.offshore_levy_ct).toFixed(2)} ct/kWh
                                                    </span>
                                                </div>
                                                <div className="flex justify-between pt-1 border-t border-gray-200 font-semibold text-gray-900">
                                                    <span>{t("tariffs.total_additional_costs", "Nebenkosten gesamt")} (brutto inkl. {priceConfig.vat_percent}% MwSt.):</span>
                                                    <span className="text-emerald-700">
                                                        {(priceConfig.additional_costs_ct * (1 + priceConfig.vat_percent / 100)).toFixed(2)} ct/kWh
                                                    </span>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* 1.2 OPTION: STATISCH */}
                    <div
                        onClick={() => setTariffType("static")}
                        className={`
                            p-4 rounded-xl border-2 cursor-pointer transition-all duration-150
                            ${tariffType === "static"
                                ? "border-blue-500 bg-blue-50/50 shadow-sm"
                                : "border-gray-200 hover:border-gray-300 bg-white"}
                        `}
                    >
                        <div className="flex items-start gap-3">
                            <input
                                type="radio"
                                id="tariff_static"
                                name="tariff_type"
                                value="static"
                                checked={tariffType === "static"}
                                onChange={() => setTariffType("static")}
                                className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                            />
                            <div className="flex-1">
                                <div className="flex items-center gap-2">
                                    <label htmlFor="tariff_static" className="font-medium text-sm text-gray-900 cursor-pointer">
                                        {t("tariffs.static_title", "Klassischer Festpreis-Tarif")}
                                    </label>
                                    <span className="text-[10px] px-2 py-0.5 font-medium rounded-full bg-blue-100 text-blue-800">
                                        Fixpreis
                                    </span>
                                </div>
                                <p className="text-xs text-gray-500 mt-1">
                                    {t("tariffs.static_desc", "Konstanter Stromarbeitspreis rund um die Uhr (z. B. Stadtwerke oder Grundversorgung).")}
                                </p>

                                {tariffType === "static" && (
                                    <div className="mt-3 flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                                        <label htmlFor="static_price" className="text-xs font-medium text-gray-700 whitespace-nowrap">
                                            {t("tariffs.work_price", "Arbeitspreis (brutto):")}
                                        </label>
                                        <div className="relative w-36">
                                            <input
                                                type="text"
                                                inputMode="decimal"
                                                id="static_price"
                                                value={staticPriceCt}
                                                onChange={(e) => setStaticPriceCt(e.target.value)}
                                                placeholder="32.00"
                                                className="w-full px-3 py-1.5 text-sm rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-12 font-medium"
                                            />
                                            <span className="absolute right-3 top-1.5 text-xs text-gray-400 font-medium">
                                                ct/kWh
                                            </span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* =========================================================
                    SECTION 2: EINSPEISEVERGÜTUNG & EEG-MODELL
                ========================================================= */}
                <div className="space-y-3 pt-3 border-t border-gray-200">
                    <div>
                        <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                            2. {t("tariffs.section_feedin", "Einspeisevergütung & PV-Überschuss")}
                        </h3>
                        <p className="text-xs text-gray-500 mt-0.5">
                            {t("tariffs.feedin_subtitle", "Vergütungsmodell für eingespeisten PV-Strom (EEG-Bestandsschutz, Direktvermarktung oder Nulleinspeisung).")}
                        </p>
                    </div>

                    {/* 2.1 Feste EEG-Vergütung */}
                    <div
                        onClick={() => setFeedInTariffType("static")}
                        className={`
                            p-4 rounded-xl border-2 cursor-pointer transition-all duration-150
                            ${feedInTariffType === "static"
                                ? "border-amber-500 bg-amber-50/50 shadow-sm"
                                : "border-gray-200 hover:border-gray-300 bg-white"}
                        `}
                    >
                        <div className="flex items-start gap-3">
                            <input
                                type="radio"
                                id="feedin_static"
                                name="feed_in_tariff_type"
                                value="static"
                                checked={feedInTariffType === "static"}
                                onChange={() => setFeedInTariffType("static")}
                                className="mt-1 h-4 w-4 text-amber-600 focus:ring-amber-500 border-gray-300"
                            />
                            <div className="flex-1">
                                <div className="flex items-center gap-2">
                                    <label htmlFor="feedin_static" className="font-medium text-sm text-gray-900 cursor-pointer">
                                        {t("tariffs.feedin_static_title", "Feste EEG-Einspeisevergütung (Bestandsanlagen bis 2026)")}
                                    </label>
                                    <span className="text-[10px] px-2 py-0.5 font-medium rounded-full bg-amber-100 text-amber-800">
                                        20 Jahre Garantie
                                    </span>
                                </div>
                                <p className="text-xs text-gray-500 mt-1">
                                    {t("tariffs.feedin_static_desc", "Gesetzlich garantierter Festsatz nach § 25 EEG (z. B. 8,20 ct/kWh für Neuanlagen oder bis 28 ct/kWh für Altanlagen).")}
                                </p>

                                {feedInTariffType === "static" && (
                                    <div className="mt-3 flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                                        <label htmlFor="feedin_price" className="text-xs font-medium text-gray-700 whitespace-nowrap">
                                            {t("tariffs.feedin_price_label", "Vergütungssatz:")}
                                        </label>
                                        <div className="relative w-36">
                                            <input
                                                type="text"
                                                inputMode="decimal"
                                                id="feedin_price"
                                                value={feedInPriceCt}
                                                onChange={(e) => setFeedInPriceCt(e.target.value)}
                                                placeholder="8.20"
                                                className="w-full px-3 py-1.5 text-sm rounded-lg border border-gray-300 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 pr-12 font-medium"
                                            />
                                            <span className="absolute right-3 top-1.5 text-xs text-gray-400 font-medium">
                                                ct/kWh
                                            </span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* 2.2 Dynamischer Börsen-Marktwert Solar */}
                    <div
                        onClick={() => setFeedInTariffType("dynamic")}
                        className={`
                            p-4 rounded-xl border-2 cursor-pointer transition-all duration-150
                            ${feedInTariffType === "dynamic"
                                ? "border-purple-500 bg-purple-50/50 shadow-sm"
                                : "border-gray-200 hover:border-gray-300 bg-white"}
                        `}
                    >
                        <div className="flex items-start gap-3">
                            <input
                                type="radio"
                                id="feedin_dynamic"
                                name="feed_in_tariff_type"
                                value="dynamic"
                                checked={feedInTariffType === "dynamic"}
                                onChange={() => setFeedInTariffType("dynamic")}
                                className="mt-1 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300"
                            />
                            <div className="flex-1">
                                <div className="flex items-center gap-2">
                                    <label htmlFor="feedin_dynamic" className="font-medium text-sm text-gray-900 cursor-pointer">
                                        {t("tariffs.feedin_dynamic_title", "Börsen-Marktwert Solar (Direktvermarktung & Post-EEG)")}
                                    </label>
                                    <span className="text-[10px] px-2 py-0.5 font-medium rounded-full bg-purple-100 text-purple-800">
                                        Marktwert Solar
                                    </span>
                                </div>
                                <p className="text-xs text-gray-500 mt-1">
                                    {t("tariffs.feedin_dynamic_desc", "Vergütung richtet sich nach dem stündlichen Marktwert an der Strombörse EPEX Spot.")}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* 2.3 Keine Vergütung / Nulleinspeisung */}
                    <div
                        onClick={() => setFeedInTariffType("none")}
                        className={`
                            p-4 rounded-xl border-2 cursor-pointer transition-all duration-150
                            ${feedInTariffType === "none"
                                ? "border-slate-500 bg-slate-50 shadow-sm"
                                : "border-gray-200 hover:border-gray-300 bg-white"}
                        `}
                    >
                        <div className="flex items-start gap-3">
                            <input
                                type="radio"
                                id="feedin_none"
                                name="feed_in_tariff_type"
                                value="none"
                                checked={feedInTariffType === "none"}
                                onChange={() => setFeedInTariffType("none")}
                                className="mt-1 h-4 w-4 text-slate-600 focus:ring-slate-500 border-gray-300"
                            />
                            <div className="flex-1">
                                <div className="flex items-center gap-2">
                                    <label htmlFor="feedin_none" className="font-medium text-sm text-gray-900 cursor-pointer">
                                        {t("tariffs.feedin_none_title", "Keine Einspeisevergütung (Nulleinspeisung / 0,00 ct)")}
                                    </label>
                                    <span className="text-[10px] px-2 py-0.5 font-medium rounded-full bg-slate-200 text-slate-700">
                                        0,00 ct
                                    </span>
                                </div>
                                <p className="text-xs text-gray-500 mt-1">
                                    {t("tariffs.feedin_none_desc", "Für Balkonkraftwerke ohne Zählertausch oder Anlagen mit reiner Eigenverbrauchsoptimierung.")}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* STATUS MESSAGE */}
                {statusMsg && (
                    <div
                        className={`p-3 rounded-lg text-xs font-medium ${statusMsg.type === "success"
                            ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                            : "bg-red-50 text-red-800 border border-red-200"
                            }`}
                    >
                        {statusMsg.text}
                    </div>
                )}

                {/* ACTION BUTTON */}
                <div className="pt-2 flex justify-end">
                    <button
                        type="submit"
                        disabled={isSaving}
                        className="px-5 py-2.5 rounded-xl font-semibold text-sm bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition active:scale-[0.98] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isSaving ? t("common.saving", "Speichern…") : t("tariffs.save_tariff", "Tarif-Einstellungen speichern")}
                    </button>
                </div>
            </form>
        </Card>
    );
}
