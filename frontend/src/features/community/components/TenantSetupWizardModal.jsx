import useModalDismiss from "../../../hooks/useModalDismiss";
/*
# src/features/community/components/TenantSetupWizardModal.jsx
# Geführter 3-Schritte Einrichtungs-Assistent (Model-Aware: Mieterstrom § 42a, GGV § 42b, Energy Sharing)
*/

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function TenantSetupWizardModal({ isOpen, onClose, onComplete, existingTenant }) {
    const { t } = useTranslation();
    useModalDismiss(isOpen, onClose);
    const [step, setStep] = useState(1);
    const [saving, setSaving] = useState(false);

    const modelType = existingTenant?.model_type || "energy_sharing";
    const isMieterstrom = modelType === "mieterstrom";
    const isGgv = modelType === "ggv";

    // Schritt 1: Stammdaten & Erzeugung
    const [buildingData, setBuildingData] = useState({
        name: existingTenant?.name || (isMieterstrom ? "Quartier Sonnenfeld 1" : isGgv ? "WEG Lindenallee 12" : "Bürgerenergie Region Nord eG"),
        address: existingTenant?.address || "Sonnenallee 42, 10115 Berlin",
        pv_capacity_kwp: existingTenant?.pv_capacity_kwp || 25,
        battery_capacity_kwh: existingTenant?.battery_capacity_kwh || 15,
        allocation_model: existingTenant?.allocation_model || (isGgv ? "static" : "dynamic"),
    });

    // Schritt 2: Parteien / Mitglieder & Zähler
    const [apartments, setApartments] = useState([
        { id: 1, name: isMieterstrom ? "Top 1 (EG links)" : isGgv ? "Wohnung 1 (EG links)" : "Mitglied 1 (Haushalt Schmidt)", email: "schmidt@beispiel.de", mea_share: 25.0, meter_id: "1EMH0011223344" },
        { id: 2, name: isMieterstrom ? "Top 2 (EG rechts)" : isGgv ? "Wohnung 2 (EG rechts)" : "Mitglied 2 (Haushalt Weber)", email: "weber@beispiel.de", mea_share: 25.0, meter_id: "1EMH0011223345" },
        { id: 3, name: isMieterstrom ? "Top 3 (1. OG links)" : isGgv ? "Wohnung 3 (1. OG links)" : "Mitglied 3 (Haushalt Müller)", email: "mueller@beispiel.de", mea_share: 25.0, meter_id: "1EMH0011223346" },
        { id: 4, name: isMieterstrom ? "Top 4 (1. OG rechts)" : isGgv ? "Wohnung 4 (1. OG rechts)" : "Mitglied 4 (Haushalt Meier)", email: "meier@beispiel.de", mea_share: 25.0, meter_id: "1EMH0011223347" },
    ]);

    // Schritt 3: Tarife
    const [tariffs, setTariffs] = useState({
        solar_rate_ct: isMieterstrom ? 18.0 : isGgv ? 14.0 : 16.5,
        grid_rate_ct: 32.0,
        base_fee_monthly_eur: isMieterstrom ? 8.50 : isGgv ? 4.00 : 5.00,
    });

    if (!isOpen) return null;

    // Einheit hinzufügen
    function addApartment() {
        const nextId = apartments.length + 1;
        const equalShare = Number((100 / nextId).toFixed(2));
        const defaultName = isMieterstrom 
            ? `Top ${nextId} (Wohnung ${nextId})`
            : isGgv 
            ? `Wohnung ${nextId} (WEG ${nextId})`
            : `Mitglied ${nextId}`;

        setApartments([
            ...apartments.map(a => ({ ...a, mea_share: equalShare })),
            {
                id: Date.now(),
                name: defaultName,
                email: "",
                mea_share: equalShare,
                meter_id: `1EMH001122${nextId + 50}`,
            }
        ]);
    }

    // Einheit entfernen
    function removeApartment(id) {
        if (apartments.length <= 1) return;
        const remaining = apartments.filter(a => a.id !== id);
        const equalShare = Number((100 / remaining.length).toFixed(2));
        setApartments(remaining.map(a => ({ ...a, mea_share: equalShare })));
    }

    // Einheit aktualisieren
    function updateApartment(id, field, val) {
        setApartments(apartments.map(a => a.id === id ? { ...a, [field]: val } : a));
    }

    // Ersparnisberechnung
    const estimatedYearlySolarKwh = buildingData.pv_capacity_kwp * 950;
    const estimatedSharedKwh = estimatedYearlySolarKwh * 0.75;
    const priceDiffCt = Math.max(0, tariffs.grid_rate_ct - tariffs.solar_rate_ct);
    const estimatedYearlyCommunitySavingsEur = Math.round((estimatedSharedKwh * priceDiffCt) / 100);

    // Speichern
    async function handleFinish() {
        setSaving(true);
        try {
            await apiFetch("/api/billing/community/tariffs/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    tenant_id: existingTenant?.id,
                    solar_rate_ct: tariffs.solar_rate_ct,
                    grid_rate_ct: tariffs.grid_rate_ct,
                    base_fee_monthly_eur: tariffs.base_fee_monthly_eur,
                })
            }).catch(() => null);

            if (onComplete) onComplete({ buildingData, apartments, tariffs });
            onClose();
        } catch (err) {
            console.error("Wizard error:", err);
            onClose();
        } finally {
            setSaving(false);
        }
    }

    // Model-spezifische Texte
    const wizardTitle = isMieterstrom
        ? t("wizard.mieterstrom_title", "🏢 Mieterstrom-Einrichtungs-Assistent (§ 42a EnWG)")
        : isGgv
        ? t("wizard.ggv_title", "⚖️ GGV-Gebäude-Assistent (§ 42b EnWG)")
        : t("wizard.sharing_title", "⚡ Bürgerenergie-Assistent (Energy Sharing)");

    const wizardSubtitle = isMieterstrom
        ? t("wizard.mieterstrom_sub", "Richte dein Mieterstrom-Objekt, die Wohneinheiten und den Vollversorgertarif in 3 einfachen Schritten ein.")
        : isGgv
        ? t("wizard.ggv_sub", "Richte deine WEG / Liegenschaft, Miteigentumsanteile (MEA) und das Vor-Ort-Solarentgelt in 3 Schritten ein.")
        : t("wizard.sharing_sub", "Richte deine Bürgerenergiegenossenschaft, Erzeugungsanlagen und Mitglieder in 3 Schritten ein.");

    const step1Title = isMieterstrom 
        ? t("wizard.step1_mieterstrom", "Liegenschaft & Solaranlage") 
        : isGgv 
        ? t("wizard.step1_ggv", "WEG-Gebäude & PV") 
        : t("wizard.step1_sharing", "Genossenschaft & Anlagen");

    const step2Title = isMieterstrom 
        ? `${t("wizard.step2_mieterstrom", "Wohnungen & Zähler")} (${apartments.length})` 
        : isGgv 
        ? `${t("wizard.step2_ggv", "Eigentümer & MEA")} (${apartments.length})` 
        : `${t("wizard.step2_sharing", "Mitglieder & iMSys")} (${apartments.length})`;

    const step3Title = isMieterstrom 
        ? t("wizard.step3_mieterstrom", "Vollversorgertarif & Sparrechnung") 
        : isGgv 
        ? t("wizard.step3_ggv", "Solar-Nutzungsentgelt & Umlagen") 
        : t("wizard.step3_sharing", "Sharing-Tarif & Netzentgelt");

    const legalExplainText = isMieterstrom
        ? t("wizard.legal_mieterstrom", "Mieterstrom-Vollversorgung nach § 42a EnWG: Als Vermieter/Contractor belieferst du die Mieter mit Solarstrom vom Dach und Reststrom aus dem Netz in einer gemeinsamen Abrechnung inkl. Mieterstromzuschlag.")
        : isGgv
        ? t("wizard.legal_ggv", "Gemeinschaftliche Gebäudeversorgung nach § 42b EnWG: Reine Vor-Ort-Aufteilung des Solarstroms nach Miteigentumsanteilen (MEA). Die Teilnehmer behalten ihren eigenen Reststromvertrag ohne Lieferantenpflichten für die WEG.")
        : t("wizard.legal_sharing", "Regionales Energy Sharing: 15-minütige Verrechnung und Allokation von Erzeugung und Verbrauch über das Verteilnetz mit Netzentgeltreduktion und automatisiertem BNetzA MSCONS Datenaustausch.");

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/75 backdrop-blur-md animate-fade-in" onClick={onClose}>
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-3xl w-full shadow-2xl overflow-hidden flex flex-col max-h-[90vh]" onClick={(e) => e.stopPropagation()}>
                
                {/* MODAL HEADER */}
                <div className="p-5 sm:p-6 border-b border-slate-100 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 flex items-center justify-between shrink-0">
                    <div>
                        <h2 className="text-base sm:text-lg font-black text-slate-900 dark:text-white">
                            {wizardTitle}
                        </h2>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            {wizardSubtitle}
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-lg font-bold p-1 rounded-lg cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                {/* PROGRESS STEPPER */}
                <div className="grid grid-cols-3 border-b border-slate-100 dark:border-slate-800 text-xs font-bold shrink-0">
                    <button
                        onClick={() => setStep(1)}
                        className={`p-3 sm:p-3.5 flex items-center justify-center gap-1.5 sm:gap-2 border-b-2 transition cursor-pointer text-center ${
                            step === 1
                                ? "border-indigo-600 text-indigo-600 dark:text-indigo-400 bg-indigo-50/30 dark:bg-indigo-950/20"
                                : "border-transparent text-slate-400 hover:text-slate-600"
                        }`}
                    >
                        <span className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-[10px] shrink-0">1</span>
                        <span className="truncate">{step1Title}</span>
                    </button>
                    <button
                        onClick={() => setStep(2)}
                        className={`p-3 sm:p-3.5 flex items-center justify-center gap-1.5 sm:gap-2 border-b-2 transition cursor-pointer text-center ${
                            step === 2
                                ? "border-indigo-600 text-indigo-600 dark:text-indigo-400 bg-indigo-50/30 dark:bg-indigo-950/20"
                                : "border-transparent text-slate-400 hover:text-slate-600"
                        }`}
                    >
                        <span className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-[10px] shrink-0">2</span>
                        <span className="truncate">{step2Title}</span>
                    </button>
                    <button
                        onClick={() => setStep(3)}
                        className={`p-3 sm:p-3.5 flex items-center justify-center gap-1.5 sm:gap-2 border-b-2 transition cursor-pointer text-center ${
                            step === 3
                                ? "border-indigo-600 text-indigo-600 dark:text-indigo-400 bg-indigo-50/30 dark:bg-indigo-950/20"
                                : "border-transparent text-slate-400 hover:text-slate-600"
                        }`}
                    >
                        <span className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-[10px] shrink-0">3</span>
                        <span className="truncate">{step3Title}</span>
                    </button>
                </div>

                {/* BODY CONTENT (SCROLLABLE) */}
                <div className="p-5 sm:p-6 overflow-y-auto space-y-6 flex-1">
                    
                    {/* ======================================================== */}
                    {/* SCHRITT 1: STAMMDATEN & PV-ANLAGE */}
                    {/* ======================================================== */}
                    {step === 1 && (
                        <div className="space-y-4 animate-fade-in">
                            <div className="bg-indigo-500/10 border border-indigo-500/20 p-4 rounded-2xl">
                                <h3 className="text-sm font-bold text-indigo-900 dark:text-indigo-200 flex items-center gap-1.5">
                                    <span>💡</span> {t("wizard.how_it_works", "Wie funktioniert das?")}
                                </h3>
                                <p className="text-xs text-indigo-700/90 dark:text-indigo-300/90 mt-1 leading-relaxed">
                                    {legalExplainText}
                                </p>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        {isMieterstrom ? t("wizard.name_mieterstrom", "Name der Liegenschaft / Quartier") : isGgv ? t("wizard.name_ggv", "Name der WEG / Liegenschaft") : t("wizard.name_sharing", "Name der Energiegenossenschaft")}
                                    </label>
                                    <input
                                        type="text"
                                        value={buildingData.name}
                                        onChange={(e) => setBuildingData({ ...buildingData, name: e.target.value })}
                                        placeholder={t("wizard.placeholder_name", "z.B. Mehrfamilienhaus Sonnenweg 8")}
                                        className="w-full text-sm font-semibold p-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-indigo-500 dark:text-white"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        {t("wizard.address_label", "Adresse (Straße, PLZ, Ort)")}
                                    </label>
                                    <input
                                        type="text"
                                        value={buildingData.address}
                                        onChange={(e) => setBuildingData({ ...buildingData, address: e.target.value })}
                                        placeholder="Sonnenallee 42, 10115 Berlin"
                                        className="w-full text-sm font-semibold p-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-indigo-500 dark:text-white"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                                <div>
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        {t("wizard.pv_capacity_label", "☀️ PV-Leistung")}
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            value={buildingData.pv_capacity_kwp}
                                            onChange={(e) => setBuildingData({ ...buildingData, pv_capacity_kwp: Number(e.target.value) })}
                                            className="w-full text-sm font-bold p-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-xl dark:text-white"
                                        />
                                        <span className="absolute right-3 top-3.5 text-xs text-slate-400 font-bold">kWp</span>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        {t("wizard.battery_capacity_label", "🔋 Batteriespeicher")}
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            value={buildingData.battery_capacity_kwh}
                                            onChange={(e) => setBuildingData({ ...buildingData, battery_capacity_kwh: Number(e.target.value) })}
                                            className="w-full text-sm font-bold p-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-xl dark:text-white"
                                        />
                                        <span className="absolute right-3 top-3.5 text-xs text-slate-400 font-bold">kWh</span>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        {t("wizard.allocation_logic_label", "⚖️ Aufteilungs-Logik")}
                                    </label>
                                    <select
                                        value={buildingData.allocation_model}
                                        onChange={(e) => setBuildingData({ ...buildingData, allocation_model: e.target.value })}
                                        className="w-full text-sm font-semibold p-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-xl dark:text-white cursor-pointer"
                                    >
                                        <option value="dynamic">{t("wizard.alloc_dynamic", "⚡ Dynamisch (15m Lastgang)")}</option>
                                        <option value="static">{t("wizard.alloc_static", "📐 Statisch (Nach MEA / Quote)")}</option>
                                        <option value="hybrid">{t("wizard.alloc_hybrid", "🤝 Hybrid (Quote + Überlauf)")}</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* ======================================================== */}
                    {/* SCHRITT 2: PARTEIEN & ZÄHLER */}
                    {/* ======================================================== */}
                    {step === 2 && (
                        <div className="space-y-4 animate-fade-in">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                                        {isMieterstrom ? t("wizard.step2_heading_mieterstrom", "Wohnungen & Mieter") : isGgv ? t("wizard.step2_heading_ggv", "Wohnungseigentümer & Anteile") : t("wizard.step2_heading_sharing", "Genossenschaftsmitglieder")} ({t("wizard.units_count", "{{count}} Einheiten", { count: apartments.length })})
                                    </h3>
                                    <p className="text-xs text-slate-500">
                                        {t("wizard.step2_desc", "Trage hier die Einheiten, Zählernummern und {{shareType}} ein.", {
                                            shareType: isGgv ? t("wizard.share_type_mea", "Miteigentumsanteile (MEA %)") : t("wizard.share_type_quotes", "Aufteilungsquoten (%)")
                                        })}
                                    </p>
                                </div>
                                <button
                                    onClick={addApartment}
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-3 py-2 rounded-xl transition cursor-pointer flex items-center gap-1.5"
                                >
                                    <span>+</span> {isMieterstrom ? t("wizard.add_apartment", "+ Wohnung hinzufügen") : isGgv ? t("wizard.add_owner", "+ Eigentümer hinzufügen") : t("wizard.add_member", "+ Mitglied hinzufügen")}
                                </button>
                            </div>

                            <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
                                {apartments.map((apt) => (
                                    <div
                                        key={apt.id}
                                        className="grid grid-cols-12 gap-2 p-3 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-2xl items-center"
                                    >
                                        <div className="col-span-3">
                                            <input
                                                type="text"
                                                value={apt.name}
                                                onChange={(e) => updateApartment(apt.id, "name", e.target.value)}
                                                placeholder={t("wizard.placeholder_unit_name", "Name")}
                                                className="w-full text-xs font-bold p-2 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-lg dark:text-white"
                                            />
                                        </div>
                                        <div className="col-span-3">
                                            <input
                                                type="email"
                                                value={apt.email}
                                                onChange={(e) => updateApartment(apt.id, "email", e.target.value)}
                                                placeholder="kontakt@beispiel.de"
                                                className="w-full text-xs p-2 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-lg dark:text-white"
                                            />
                                        </div>
                                        <div className="col-span-3">
                                            <input
                                                type="text"
                                                value={apt.meter_id}
                                                onChange={(e) => updateApartment(apt.id, "meter_id", e.target.value)}
                                                placeholder={t("wizard.placeholder_meter_id", "Zählernummer")}
                                                className="w-full text-xs font-mono p-2 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-lg dark:text-white"
                                            />
                                        </div>
                                        <div className="col-span-2">
                                            <div className="relative">
                                                <input
                                                    type="number"
                                                    value={apt.mea_share}
                                                    onChange={(e) => updateApartment(apt.id, "mea_share", Number(e.target.value))}
                                                    className="w-full text-xs font-bold p-2 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-lg dark:text-white"
                                                />
                                                <span className="absolute right-2 top-2 text-[10px] text-slate-400 font-bold">%</span>
                                            </div>
                                        </div>
                                        <div className="col-span-1 text-right">
                                            <button
                                                onClick={() => removeApartment(apt.id)}
                                                disabled={apartments.length <= 1}
                                                className="text-red-500 hover:text-red-700 text-xs font-bold p-1 rounded hover:bg-red-50 dark:hover:bg-red-950/20 disabled:opacity-30 cursor-pointer"
                                            >
                                                ✕
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* ======================================================== */}
                    {/* SCHRITT 3: TARIFE & PROGNOSE */}
                    {/* ======================================================== */}
                    {step === 3 && (
                        <div className="space-y-4 animate-fade-in">
                            <div className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-2xl flex items-center justify-between">
                                <div>
                                    <div className="text-xs font-bold text-emerald-800 dark:text-emerald-300">
                                        {t("wizard.savings_title", "🎉 Prognostizierter Kostenvorteil")}
                                    </div>
                                    <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-0.5">
                                        ~{estimatedYearlyCommunitySavingsEur.toLocaleString("de-DE")} € <span className="text-xs font-normal text-slate-500">{t("wizard.savings_per_year", "Ersparnis pro Jahr")}</span>
                                    </div>
                                </div>
                                <div className="text-3xl">💰</div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                <div className="p-4 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 rounded-2xl">
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        {isMieterstrom ? t("wizard.rate_solar_mieterstrom", "☀️ Solarstrom-Preis") : isGgv ? t("wizard.rate_solar_ggv", "☀️ Solar-Nutzungsentgelt") : t("wizard.rate_solar_sharing", "☀️ Sharing-Bezugspreis")}
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            step="0.1"
                                            value={tariffs.solar_rate_ct}
                                            onChange={(e) => setTariffs({ ...tariffs, solar_rate_ct: Number(e.target.value) })}
                                            className="w-full text-base font-black p-3 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl dark:text-white"
                                        />
                                        <span className="absolute right-3 top-3.5 text-xs text-slate-400 font-bold">ct/kWh</span>
                                    </div>
                                    <p className="text-[10px] text-slate-400 mt-1">
                                        {isMieterstrom ? t("wizard.desc_solar_mieterstrom", "Mieterpreis für den Dach-Solarstrom.") : isGgv ? t("wizard.desc_solar_ggv", "Umlage für die Solaranlagennutzung.") : t("wizard.desc_solar_sharing", "Preis für Energie aus dem Sharing-Pool.")}
                                    </p>
                                </div>

                                <div className="p-4 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 rounded-2xl">
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        {isGgv ? t("wizard.rate_grid_ggv", "🔌 Referenz-Reststrom") : t("wizard.rate_grid_default", "🔌 Netz-Reststrom")}
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            step="0.1"
                                            value={tariffs.grid_rate_ct}
                                            onChange={(e) => setTariffs({ ...tariffs, grid_rate_ct: Number(e.target.value) })}
                                            className="w-full text-base font-black p-3 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl dark:text-white"
                                        />
                                        <span className="absolute right-3 top-3.5 text-xs text-slate-400 font-bold">ct/kWh</span>
                                    </div>
                                    <p className="text-[10px] text-slate-400 mt-1">
                                        {isGgv ? t("wizard.desc_grid_ggv", "Externer Vergleichstarif der Bewohner.") : t("wizard.desc_grid_default", "Preis für Netzbezug bei Bewölkung.")}
                                    </p>
                                </div>

                                <div className="p-4 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 rounded-2xl">
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        {t("wizard.base_fee_label", "🏛️ Grundgebühr / Umlage")}
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            step="0.5"
                                            value={tariffs.base_fee_monthly_eur}
                                            onChange={(e) => setTariffs({ ...tariffs, base_fee_monthly_eur: Number(e.target.value) })}
                                            className="w-full text-base font-black p-3 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl dark:text-white"
                                        />
                                        <span className="absolute right-3 top-3.5 text-xs text-slate-400 font-bold">€/Monat</span>
                                    </div>
                                    <p className="text-[10px] text-slate-400 mt-1">{t("wizard.base_fee_desc", "Für Messstellenbetrieb & Plattform.")}</p>
                                </div>
                            </div>
                        </div>
                    )}

                </div>

                {/* MODAL FOOTER */}
                <div className="p-4 sm:p-5 border-t border-slate-100 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 flex items-center justify-between shrink-0">
                    <div>
                        {step > 1 && (
                            <button
                                onClick={() => setStep(step - 1)}
                                className="px-4 py-2 text-xs font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition cursor-pointer"
                            >
                                {t("wizard.back", "← Zurück")}
                            </button>
                        )}
                    </div>

                    <div className="flex gap-2">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 text-xs font-bold text-slate-500 hover:text-slate-700 dark:hover:text-slate-200 cursor-pointer"
                        >
                            {t("common.cancel", "Abbrechen")}
                        </button>

                        {step < 3 ? (
                            <button
                                onClick={() => setStep(step + 1)}
                                className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-5 py-2.5 rounded-xl transition cursor-pointer flex items-center gap-1.5"
                            >
                                {t("wizard.next_step", "Weiter zu Schritt {{next}} →", { next: step + 1 })}
                            </button>
                        ) : (
                            <button
                                onClick={handleFinish}
                                disabled={saving}
                                className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-black px-6 py-2.5 rounded-xl transition shadow-md hover:shadow-lg cursor-pointer flex items-center gap-2"
                            >
                                {saving ? t("common.saving", "Speichere...") : isMieterstrom ? t("wizard.submit_mieterstrom", "🚀 Mieterstrom jetzt aktivieren") : isGgv ? t("wizard.submit_ggv", "🚀 GGV-Liegenschaft aktivieren") : t("wizard.submit_sharing", "🚀 Bürgerenergie jetzt aktivieren")}
                            </button>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}
