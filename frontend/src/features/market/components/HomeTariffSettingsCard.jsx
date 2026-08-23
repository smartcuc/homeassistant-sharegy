/*
# src/features/market/components/HomeTariffSettingsCard.jsx
*/

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Card from "../../../components/ui/Card";
import Button from "../../../components/ui/Button";
import { fetchHomeTariff, saveHomeTariff } from "../api";
import { useTranslation } from "react-i18next";

export default function HomeTariffSettingsCard() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const { data: tariffData, isLoading, isError } = useQuery({
        queryKey: ["home-tariff"],
        queryFn: fetchHomeTariff,
        staleTime: 1000 * 60 * 5,
    });

    const [selectedType, setSelectedType] = useState(null);
    const [customPriceCt, setCustomPriceCt] = useState(null);
    const [showBreakdown, setShowBreakdown] = useState(false);
    const [statusMsg, setStatusMsg] = useState(null);

    const tariffType = selectedType ?? tariffData?.tariff_type ?? "dynamic";
    const staticPriceCt = customPriceCt ?? (tariffData?.static_price_ct != null ? String(tariffData.static_price_ct) : "");

    const mutation = useMutation({
        mutationFn: saveHomeTariff,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["home-tariff"] });
            queryClient.invalidateQueries({ queryKey: ["spot-price-chart"] });
            queryClient.invalidateQueries({ queryKey: ["energy-data"] });
            setStatusMsg({ type: "success", text: t("tariffs.save_success", "Stromtarif erfolgreich gespeichert!") });
            setTimeout(() => setStatusMsg(null), 4000);
        },
        onError: (err) => {
            setStatusMsg({
                type: "error",
                text: err?.detail || err?.message || t("tariffs.save_error", "Fehler beim Speichern des Tarifs."),
            });
            setTimeout(() => setStatusMsg(null), 5000);
        },
    });

    function handleSave(e) {
        e.preventDefault();
        if (tariffType === "static" && (!staticPriceCt || isNaN(Number(staticPriceCt)))) {
            setStatusMsg({ type: "error", text: t("tariffs.invalid_price", "Bitte einen gültigen Arbeitspreis in ct/kWh eingeben.") });
            return;
        }

        mutation.mutate({
            tariff_type: tariffType,
            static_price_ct: tariffType === "static" ? Number(staticPriceCt) : null,
        });
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
                        ⚡ {t("tariffs.model_title", "Stromtarif & Abrechnungsmodell")}
                    </h2>
                    <p className="text-xs text-gray-500 mt-0.5">
                        {t("tariffs.model_desc", { home: tariffData?.home_name || t("profile.home_single", "dein Zuhause"), defaultValue: `Definiere dein Tarifmodell für ${tariffData?.home_name || "dein Zuhause"}, um Stromkosten und Einsparungen exakt zu berechnen.` })}
                    </p>
                </div>
            </div>

            <form onSubmit={handleSave} className="space-y-4">
                {/* 1. OPTION: DYNAMISCH */}
                <div
                    onClick={() => setSelectedType("dynamic")}
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
                            onChange={() => setSelectedType("dynamic")}
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
                                        className="text-xs font-medium text-emerald-700 hover:text-emerald-800 underline inline-flex items-center gap-1"
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

                {/* 2. OPTION: STATISCH */}
                <div
                    onClick={() => setSelectedType("static")}
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
                            onChange={() => setSelectedType("static")}
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
                                            type="number"
                                            id="static_price"
                                            step="0.01"
                                            min="0"
                                            max="100"
                                            value={staticPriceCt}
                                            onChange={(e) => setCustomPriceCt(e.target.value)}
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
                    <Button
                        type="submit"
                        variant="primary"
                        onClick={handleSave}
                    >
                        {mutation.isPending ? t("common.saving", "Speichern…") : t("tariffs.save_tariff", "Tarif speichern")}
                    </Button>
                </div>
            </form>
        </Card>
    );
}
