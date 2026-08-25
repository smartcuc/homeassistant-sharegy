/*
# src/features/market/components/HomeTariffSettingsCard.jsx
*/

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Card from "../../../components/ui/Card";
import { fetchHomeTariff, saveHomeTariff, deleteHomeTariff } from "../api";
import { useTranslation } from "react-i18next";

function parseCt(val) {
    if (val === null || val === undefined || val === "") return null;
    const normalized = String(val).replace(",", ".").trim();
    const num = Number(normalized);
    return isNaN(num) ? null : num;
}

function HomeTariffForm({ initialData, onSaved }) {
    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const todayStr = new Date().toISOString().slice(0, 10);
    const [validFrom, setValidFrom] = useState(initialData?.valid_from || todayStr);
    const [tariffType, setTariffType] = useState(initialData?.tariff_type || "dynamic");
    const [staticPriceCt, setStaticPriceCt] = useState(
        initialData?.static_price_ct != null ? String(initialData.static_price_ct) : "32.00"
    );
    const [feedInTariffType, setFeedInTariffType] = useState(initialData?.feed_in_tariff_type || "static");
    const [feedInPriceCt, setFeedInPriceCt] = useState(
        initialData?.feed_in_tariff_ct != null ? String(initialData.feed_in_tariff_ct) : "8.20"
    );
    const [showBreakdown, setShowBreakdown] = useState(false);
    const [statusMsg, setStatusMsg] = useState(null);
    const [isSaving, setIsSaving] = useState(false);

    const priceConfig = initialData?.price_config;

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
            valid_from: validFrom || todayStr,
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

            if (onSaved) {
                onSaved(updated);
            }

            setStatusMsg({ type: "success", text: t("tariffs.save_success", "Strom- & Einspeisetarif mit Gültigkeitsdatum erfolgreich gespeichert!") });
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

    return (
        <form onSubmit={handleSave} className="space-y-6">
            {/* =========================================================
                SECTION 0: GÜLTIGKEITSDATUM (VALID FROM)
            ========================================================= */}
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div>
                        <label htmlFor="valid_from" className="text-xs font-bold text-gray-900 uppercase tracking-wider block">
                            📅 {t("tariffs.valid_from_label", "Gültig ab (Datum des Tarifwechsels):")}
                        </label>
                        <p className="text-xs text-gray-500 mt-0.5">
                            {t("tariffs.valid_from_hint", "Alle Verbrauchsdaten vor diesem Datum werden mit dem vorherigen Tarif, ab diesem Datum mit dem neuen Tarif berechnet.")}
                        </p>
                    </div>
                    <div className="flex items-center gap-2">
                        <input
                            type="date"
                            id="valid_from"
                            value={validFrom}
                            onChange={(e) => setValidFrom(e.target.value)}
                            className="px-3 py-1.5 text-sm bg-white font-bold text-gray-900 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-500 shadow-2xs"
                        />
                        <button
                            type="button"
                            onClick={() => setValidFrom(todayStr)}
                            className="text-xs px-2.5 py-1.5 rounded-lg bg-gray-200 hover:bg-gray-300 font-semibold text-gray-700 transition cursor-pointer"
                            title="Auf heutigen Tag setzen"
                        >
                            Heute
                        </button>
                    </div>
                </div>
            </div>

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
                    {isSaving ? t("common.saving", "Speichern…") : t("tariffs.save_tariff", "Tarif-Einstellungen für dieses Datum speichern")}
                </button>
            </div>
        </form>
    );
}

export default function HomeTariffSettingsCard() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const [selectedEntry, setSelectedEntry] = useState(null);
    const [historyStatusMsg, setHistoryStatusMsg] = useState(null);

    const { data: tariffData, isLoading, isError } = useQuery({
        queryKey: ["home-tariff"],
        queryFn: fetchHomeTariff,
    });

    const deleteMutation = useMutation({
        mutationFn: (tariffId) => deleteHomeTariff(tariffId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["home-tariff"] });
            queryClient.invalidateQueries({ queryKey: ["energy-balance"] });
            setHistoryStatusMsg({ type: "success", text: t("tariffs.delete_success", "Tarifeintrag erfolgreich gelöscht.") });
            setTimeout(() => setHistoryStatusMsg(null), 4000);
        },
        onError: (err) => {
            setHistoryStatusMsg({
                type: "error",
                text: err?.data?.detail || err?.detail || err?.message || t("tariffs.delete_error", "Fehler beim Löschen des Tarifs."),
            });
            setTimeout(() => setHistoryStatusMsg(null), 5000);
        },
    });

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

    const historyList = tariffData?.history || [];
    const activeFormData = selectedEntry || tariffData;
    const formKey = `${activeFormData?.home_id || "home"}-${activeFormData?.valid_from || "today"}-${activeFormData?.tariff_type || "t"}-${activeFormData?.static_price_ct || "p"}-${activeFormData?.feed_in_tariff_type || "f"}-${activeFormData?.feed_in_tariff_ct || "fp"}`;

    return (
        <Card>
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h2 className="font-semibold text-gray-900 text-base">
                        ⚡ {t("tariffs.model_title", "Strombezug & Tarifmodell")}
                    </h2>
                    <p className="text-xs text-gray-500 mt-0.5">
                        {t("tariffs.model_desc", { home: tariffData?.home_name || t("profile.home_single", "dein Zuhause"), defaultValue: `Definiere dein Bezugs- und Einspeisemodell für ${tariffData?.home_name || "dein Zuhause"}, um Stromkosten und Einsparungen exakt nach Datum zu berechnen.` })}
                    </p>
                </div>
            </div>

            <HomeTariffForm
                key={formKey}
                initialData={activeFormData}
                onSaved={() => setSelectedEntry(null)}
            />

            {/* =========================================================
                SECTION 3: TARIF-HISTORIE & GEPLANTE WECHSEL
            ========================================================= */}
            {historyList.length > 0 && (
                <div className="mt-8 pt-6 border-t border-gray-200 space-y-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                                <span>📜</span> {t("tariffs.history_title", "Tarif-Historie & Geplante Wechsel")}
                            </h3>
                            <p className="text-xs text-gray-500 mt-0.5">
                                {t("tariffs.history_subtitle", "Übersicht aller hinterlegten Tarifzeiträume für dieses Haus.")}
                            </p>
                        </div>
                    </div>

                    {historyStatusMsg && (
                        <div
                            className={`p-3 rounded-lg text-xs font-medium ${historyStatusMsg.type === "success"
                                ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                                : "bg-red-50 text-red-800 border border-red-200"
                                }`}
                        >
                            {historyStatusMsg.text}
                        </div>
                    )}

                    <div className="space-y-2.5">
                        {historyList.map((entry) => (
                            <div
                                key={entry.id}
                                className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition-all ${entry.is_active
                                        ? "bg-emerald-50/50 border-emerald-300 shadow-2xs"
                                        : entry.is_future
                                            ? "bg-indigo-50/50 border-indigo-200 shadow-2xs"
                                            : "bg-gray-50/70 border-gray-200 opacity-80"
                                    }`}
                            >
                                <div className="flex items-start sm:items-center gap-3">
                                    <div className="text-xl">
                                        {entry.is_active ? "🟢" : entry.is_future ? "🔵" : "⚪"}
                                    </div>
                                    <div>
                                        <div className="flex flex-wrap items-center gap-2">
                                            <span className="font-bold text-sm text-gray-900">
                                                Gültig ab {new Date(entry.valid_from).toLocaleDateString([], { day: "2-digit", month: "2-digit", year: "numeric" })}
                                            </span>
                                            {entry.is_active && (
                                                <span className="text-[10px] px-2 py-0.5 font-bold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                                                    Aktuell aktiv
                                                </span>
                                            )}
                                            {entry.is_future && (
                                                <span className="text-[10px] px-2 py-0.5 font-bold rounded-full bg-indigo-100 text-indigo-800 border border-indigo-200">
                                                    Geplant (Zukunft)
                                                </span>
                                            )}
                                        </div>
                                        <div className="text-xs text-gray-600 mt-1 flex flex-wrap items-center gap-x-4 gap-y-1">
                                            <span>
                                                ⚡ <strong>Bezug:</strong> {entry.tariff_type === "static" ? `Festpreis (${entry.static_price_ct?.toFixed(2)} ct/kWh)` : "Dynamischer Börsentarif"}
                                            </span>
                                            <span>
                                                ☀️ <strong>Einspeisung:</strong> {entry.feed_in_tariff_type === "static" ? `EEG (${entry.feed_in_tariff_ct?.toFixed(2)} ct/kWh)` : entry.feed_in_tariff_type === "dynamic" ? "Marktwert Solar" : "Nulleinspeisung (0 ct)"}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-2 self-end sm:self-auto">
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setSelectedEntry({
                                                ...tariffData,
                                                valid_from: entry.valid_from,
                                                tariff_type: entry.tariff_type,
                                                static_price_ct: entry.static_price_ct,
                                                feed_in_tariff_type: entry.feed_in_tariff_type,
                                                feed_in_tariff_ct: entry.feed_in_tariff_ct,
                                            });
                                            window.scrollTo({ top: 0, behavior: "smooth" });
                                        }}
                                        className="text-xs px-3 py-1.5 rounded-lg bg-white border border-gray-200 font-semibold text-gray-700 hover:bg-gray-100 transition cursor-pointer shadow-2xs"
                                        title="Diesen Tarif im Formular bearbeiten"
                                    >
                                        Bearbeiten
                                    </button>
                                    {historyList.length > 1 && (
                                        <button
                                            type="button"
                                            onClick={() => {
                                                if (window.confirm(`Möchtest du den Tarifeintrag ab ${entry.valid_from} wirklich löschen?`)) {
                                                    deleteMutation.mutate(entry.id);
                                                }
                                            }}
                                            disabled={deleteMutation.isPending}
                                            className="text-xs px-2.5 py-1.5 rounded-lg bg-rose-50 border border-rose-200 font-semibold text-rose-700 hover:bg-rose-100 transition cursor-pointer"
                                            title="Tarifeintrag löschen"
                                        >
                                            Löschen
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </Card>
    );
}
