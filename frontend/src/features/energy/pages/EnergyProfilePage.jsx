/*
# src/features/energy/pages/EnergyProfilePage.jsx
*/

import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import Card from "../../../components/ui/Card";
import { apiFetch } from "../../../api/client";

export default function EnergyProfilePage() {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const activeLang = (i18n.language || "de").split("-")[0];

    // 1. Energie-Profil Daten abrufen
    const { data: profile, isLoading } = useQuery({
        queryKey: ["energy-profile", activeLang],
        queryFn: () => apiFetch(`/api/energy/profile/?lang=${activeLang}`),
        staleTime: 30000,
    });

    // Formular-Zustand für Live-Anpassung
    const [solarType, setSolarType] = useState("none"); // "none", "bkw", "pv"
    const [hasBattery, setHasBattery] = useState(false);
    const [hasEv, setHasEv] = useState(false);
    const [hasHeatpump, setHasHeatpump] = useState(false);
    const [tariffType, setTariffType] = useState("static"); // "static", "dynamic"
    const [statusMsg, setStatusMsg] = useState(null);

    // Synchronisiere initialen Server-Zustand
    useEffect(() => {
        if (profile) {
            setSolarType(profile.solar_type || "none");
            setHasBattery(Boolean(profile.has_battery));
            setHasEv(Boolean(profile.has_ev));
            setHasHeatpump(Boolean(profile.has_heatpump));
            setTariffType(profile.tariff_type || "static");
        }
    }, [profile]);

    // Mutation zum Speichern
    const mutation = useMutation({
        mutationFn: (payload) =>
            apiFetch("/api/energy/profile/", {
                method: "POST",
                body: JSON.stringify({ ...payload, lang: activeLang }),
            }),
        onSuccess: (updatedProfile) => {
            queryClient.setQueryData(["energy-profile", activeLang], updatedProfile);
            queryClient.invalidateQueries({ queryKey: ["system-setup-status"] });
            queryClient.invalidateQueries({ queryKey: ["home-tariff"] });
            setStatusMsg({ type: "success", text: t("energy_profile.saved_success", "Energie-Profil erfolgreich gespeichert!") });
            setTimeout(() => setStatusMsg(null), 3500);
        },
        onError: (err) => {
            setStatusMsg({ type: "error", text: err?.message || t("common.error", "Fehler beim Speichern") });
            setTimeout(() => setStatusMsg(null), 4000);
        },
    });

    const handleToggle = (key, value) => {
        const nextState = {
            solar_type: key === "solar_type" ? value : solarType,
            has_battery: key === "has_battery" ? value : hasBattery,
            has_ev: key === "has_ev" ? value : hasEv,
            has_heatpump: key === "has_heatpump" ? value : hasHeatpump,
            tariff_type: key === "tariff_type" ? value : tariffType,
        };

        if (key === "solar_type") setSolarType(value);
        if (key === "has_battery") setHasBattery(value);
        if (key === "has_ev") setHasEv(value);
        if (key === "has_heatpump") setHasHeatpump(value);
        if (key === "tariff_type") setTariffType(value);

        mutation.mutate(nextState);
    };

    if (isLoading && !profile) {
        return (
            <div className="p-6 max-w-7xl mx-auto space-y-6 animate-pulse">
                <div className="h-8 bg-slate-200 dark:bg-slate-800 rounded-xl w-1/3"></div>
                <div className="h-64 bg-slate-100 dark:bg-slate-850 rounded-2xl"></div>
            </div>
        );
    }

    const currentCode = profile?.profile_code || "A.1";
    const isDynamic = tariffType === "dynamic";
    const recommendedIsDynamic = profile?.recommended_tariff === "dynamic";
    const savingsAmount = profile?.estimated_savings_eur_year || 80;
    const shiftableKwh = profile?.shiftable_kwh_year || 200;

    const solarOptions = [
        { key: "none", label: t("energy_profile.solar_none_label", "🏢 Kein Solar"), desc: t("energy_profile.solar_none_desc", "Haushalt ohne PV") },
        { key: "bkw", label: t("energy_profile.solar_bkw_label", "☀️ Balkonkraftwerk"), desc: t("energy_profile.solar_bkw_desc", "bis 800W Stecker-Solar") },
        { key: "pv", label: t("energy_profile.solar_pv_label", "🏡 PV-Anlage"), desc: t("energy_profile.solar_pv_desc", "große Solaranlage") },
    ];

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6 animate-fade-in">
            {/* HEADER */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-black text-slate-900 dark:text-white flex items-center gap-2.5">
                        <span className="text-3xl">🏡</span>
                        <span>{t("energy_profile.page_title", "Energie-Profil & Ersparnisrechner")}</span>
                    </h1>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                        {t("energy_profile.page_subtitle", "Verwalte deine Ausstattung, berechne dein Sparpotenzial und erhalte konkrete Tarif-Empfehlungen.")}
                    </p>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                    <Link
                        to="/app/help/tarif-und-ersparnis-kompass-matrix"
                        className="px-3.5 py-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 font-semibold text-xs border border-indigo-200/80 dark:border-indigo-800 transition flex items-center gap-1.5 shadow-2xs"
                    >
                        <span>📖</span>
                        <span>{t("energy_profile.view_matrix_guide", "Tarif- & Ersparnis-Kompass öffnen")}</span>
                    </Link>
                </div>
            </div>

            {/* STATUS MESSAGE */}
            {statusMsg && (
                <div
                    className={`p-3.5 rounded-xl text-xs font-semibold flex items-center justify-between shadow-2xs transition-all ${
                        statusMsg.type === "success"
                            ? "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"
                            : "bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-300 border border-rose-200 dark:border-rose-800"
                    }`}
                >
                    <div className="flex items-center gap-2">
                        <span>{statusMsg.type === "success" ? "✅" : "❌"}</span>
                        <span>{statusMsg.text}</span>
                    </div>
                </div>
            )}

            {/* 1. HAUPT-PROFIL BADGE & TARIF-VERDIKT BANNER */}
            <div className="p-6 rounded-3xl bg-gradient-to-br from-indigo-900 via-slate-900 to-indigo-950 text-white shadow-xl relative overflow-hidden border border-indigo-800/60">
                <div className="absolute -right-12 -bottom-12 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>

                <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                    <div className="space-y-3 max-w-2xl">
                        <div className="flex flex-wrap items-center gap-2.5">
                            <span className="px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wider bg-indigo-500/30 text-indigo-300 border border-indigo-400/30 backdrop-blur-xs">
                                {t("energy_profile.badge_label", "Energie-Profil")}: {currentCode}
                            </span>
                            <span className={`px-3 py-1 rounded-full text-xs font-extrabold border ${
                                recommendedIsDynamic
                                    ? "bg-amber-500/20 text-amber-300 border-amber-400/30"
                                    : "bg-emerald-500/20 text-emerald-300 border-emerald-400/30"
                            }`}>
                                {recommendedIsDynamic
                                    ? t("energy_profile.tag_dynamic_recommended", "⚡ Dynamischer Tarif empfohlen")
                                    : t("energy_profile.tag_static_recommended", "🔒 Fester Tarif empfohlen")}
                            </span>
                        </div>

                        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
                            {profile?.profile_name || t("energy_profile.default_profile_name", "Haushalt ohne Solar")}
                        </h2>
                        <p className="text-sm text-indigo-200/90 leading-relaxed">
                            {profile?.profile_subtitle}
                        </p>

                        <div className="p-4 rounded-2xl bg-white/10 backdrop-blur-md border border-white/10 space-y-1.5 mt-2">
                            <div className="text-xs font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1.5">
                                <span>💡</span>
                                <span>{profile?.tariff_verdict_title}</span>
                            </div>
                            <p className="text-xs text-slate-200 leading-relaxed">
                                {profile?.tariff_verdict_reason}
                            </p>
                        </div>
                    </div>

                    {/* SPAR-POTENZIAL KACHEL (RECHTS) */}
                    <div className="p-5 rounded-2xl bg-white/10 backdrop-blur-md border border-white/15 shrink-0 flex flex-col justify-center items-center text-center min-w-[240px] space-y-2">
                        <span className="text-xs font-bold uppercase tracking-wider text-indigo-200">
                            {t("energy_profile.estimated_annual_savings", "Geschätztes Sparpotenzial")}
                        </span>
                        <div className="text-4xl font-black text-emerald-400">
                            ca. {savingsAmount} €
                            <span className="text-sm font-semibold text-slate-300 block">{t("energy_profile.per_year", "/ Jahr")}</span>
                        </div>
                        <div className="text-xs text-indigo-200 pt-2 border-t border-white/10 w-full flex items-center justify-between">
                            <span>{t("energy_profile.shiftable_load", "Verschiebbare Last:")}</span>
                            <span className="font-bold text-white">~{shiftableKwh.toLocaleString()} kWh/a</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* 2. SCHALTER-ZENTRALE: AUSSTATTUNG & TARIF-TOGGLES */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 2.1 DEINE ENERGIE-AUSSTATTUNG */}
                <Card>
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h2 className="font-bold text-slate-900 dark:text-white text-base flex items-center gap-2">
                                <span>🎛️</span>
                                <span>{t("energy_profile.equipment_title", "Deine Energie-Ausstattung")}</span>
                            </h2>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                {t("energy_profile.equipment_desc", "Aktiviere oder deaktiviere Komponenten, um dein Profil und Sparpotenzial sofort neu zu berechnen.")}
                            </p>
                        </div>
                    </div>

                    <div className="space-y-3">
                        {/* SOLAR TYPE TOGGLE (3-Stufig) */}
                        <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
                            <label className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider block">
                                ☀️ {t("energy_profile.solar_presence", "Solarenergie")}
                            </label>
                            <div className="grid grid-cols-3 gap-2">
                                {solarOptions.map((opt) => (
                                    <button
                                        key={opt.key}
                                        type="button"
                                        onClick={() => handleToggle("solar_type", opt.key)}
                                        className={`p-2.5 rounded-xl border text-left transition cursor-pointer flex flex-col justify-between ${
                                            solarType === opt.key
                                                ? "bg-indigo-600 text-white border-indigo-600 shadow-xs"
                                                : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-indigo-300"
                                        }`}
                                    >
                                        <div className="font-bold text-xs">{opt.label}</div>
                                        <div className={`text-[10px] mt-0.5 ${solarType === opt.key ? "text-indigo-100" : "text-slate-400"}`}>{opt.desc}</div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* BATTERIESPEICHER */}
                        <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <span className="text-2xl">🔋</span>
                                <div>
                                    <div className="font-bold text-xs text-slate-900 dark:text-white">
                                        {t("energy_profile.battery_storage", "Batteriespeicher / Heimspeicher")}
                                    </div>
                                    <div className="text-[11px] text-slate-500 dark:text-slate-400">
                                        {t("energy_profile.battery_storage_desc", "Stationärer Akku zur Zwischenspeicherung")}
                                    </div>
                                </div>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={hasBattery}
                                    onChange={(e) => handleToggle("has_battery", e.target.checked)}
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-slate-300 peer-focus:outline-hidden rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-slate-600 peer-checked:bg-emerald-600"></div>
                            </label>
                        </div>

                        {/* E-AUTO / WALLBOX */}
                        <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <span className="text-2xl">🚗</span>
                                <div>
                                    <div className="font-bold text-xs text-slate-900 dark:text-white">
                                        {t("energy_profile.ev_wallbox", "E-Auto / Wallbox")}
                                    </div>
                                    <div className="text-[11px] text-slate-500 dark:text-slate-400">
                                        {t("energy_profile.ev_wallbox_desc", "Elektrofahrzeug mit intelligenter Lademöglichkeit")}
                                    </div>
                                </div>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={hasEv}
                                    onChange={(e) => handleToggle("has_ev", e.target.checked)}
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-slate-300 peer-focus:outline-hidden rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-slate-600 peer-checked:bg-emerald-600"></div>
                            </label>
                        </div>

                        {/* WÄRMEPUMPE */}
                        <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <span className="text-2xl">♨️</span>
                                <div>
                                    <div className="font-bold text-xs text-slate-900 dark:text-white">
                                        {t("energy_profile.heat_pump", "Wärmepumpe")}
                                    </div>
                                    <div className="text-[11px] text-slate-500 dark:text-slate-400">
                                        {t("energy_profile.heat_pump_desc", "Heizungs-Wärmepumpe oder Brauchwasser-Wärmepumpe")}
                                    </div>
                                </div>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={hasHeatpump}
                                    onChange={(e) => handleToggle("has_heatpump", e.target.checked)}
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-slate-300 peer-focus:outline-hidden rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-slate-600 peer-checked:bg-emerald-600"></div>
                            </label>
                        </div>
                    </div>
                </Card>

                {/* 2.2 AKTUELLER STROMTARIF & ALTERNATIVEN */}
                <Card>
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h2 className="font-bold text-slate-900 dark:text-white text-base flex items-center gap-2">
                                <span>💶</span>
                                <span>{t("energy_profile.tariff_selection_title", "Aktueller Stromtarif")}</span>
                            </h2>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                {t("energy_profile.tariff_selection_desc", "Welcher Vertrag liegt aktuell zugrunde?")}
                            </p>
                        </div>
                    </div>

                    <div className="space-y-3">
                        {/* FESTPREIS */}
                        <div
                            onClick={() => handleToggle("tariff_type", "static")}
                            className={`p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                                !isDynamic
                                    ? "border-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/40 shadow-xs"
                                    : "border-slate-200 dark:border-slate-700 hover:border-slate-300 bg-white dark:bg-slate-900"
                            }`}
                        >
                            <div className="flex items-start gap-3">
                                <input
                                    type="radio"
                                    checked={!isDynamic}
                                    onChange={() => handleToggle("tariff_type", "static")}
                                    className="mt-1 h-4 w-4 text-indigo-600"
                                />
                                <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                        <span className="font-bold text-xs text-slate-900 dark:text-white">
                                            🔒 {t("energy_profile.fixed_tariff_title", "Klassischer Festpreis-Tarif (~30–35 ct/kWh)")}
                                        </span>
                                    </div>
                                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                                        {t("energy_profile.fixed_tariff_desc", "Konstanter Arbeitspreis rund um die Uhr (z. B. Stadtwerke / Grundversorgung).")}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* DYNAMISCH */}
                        <div
                            onClick={() => handleToggle("tariff_type", "dynamic")}
                            className={`p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                                isDynamic
                                    ? "border-emerald-600 bg-emerald-50/50 dark:bg-emerald-950/40 shadow-xs"
                                    : "border-slate-200 dark:border-slate-700 hover:border-slate-300 bg-white dark:bg-slate-900"
                            }`}
                        >
                            <div className="flex items-start gap-3">
                                <input
                                    type="radio"
                                    checked={isDynamic}
                                    onChange={() => handleToggle("tariff_type", "dynamic")}
                                    className="mt-1 h-4 w-4 text-emerald-600"
                                />
                                <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                        <span className="font-bold text-xs text-slate-900 dark:text-white">
                                            ⚡ {t("energy_profile.dynamic_tariff_title", "Dynamischer Börsenstromtarif (z. B. Tibber, Rabot, Ostrom)")}
                                        </span>
                                    </div>
                                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                                        {t("energy_profile.dynamic_tariff_desc", "Viertelstündlich/stündlich schwankender Börsenpreis. Ideal für Lastverschiebung.")}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* ALTERNATIVE: 2. ZÄHLER / KASKADENMESSUNG HINWEIS */}
                        <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs space-y-1">
                            <div className="font-bold text-slate-900 dark:text-white flex items-center gap-1.5 text-[11px]">
                                <span>ℹ️</span>
                                <span>{t("energy_profile.alt_tariff_title", "Alternative: Fester Tarif mit günstigem Lade-/Wärmetarif")}</span>
                            </div>
                            <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                                {profile?.alternative_tariff_hint || t("energy_profile.alt_tariff_desc", "Ein separater Festpreis-Wärme- oder Autostromtarif ist möglich, erfordert jedoch einen 2. Zählerplatz (Kaskadenschaltung) mit Zusatzkosten von ca. 80–120 €/Jahr für Messstellenbetrieb und Grundgebühr. Bei einem dynamischen Börsenstromtarif genügt 1 intelligenter Zähler bei vollem § 14a Netzentgelt-Rabatt (~160 €/a).")}
                            </p>
                        </div>

                        {/* ACTION LINK ZU TARIFSEITE */}
                        <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 flex items-center justify-between text-xs">
                            <span className="text-slate-600 dark:text-slate-300">
                                {t("energy_profile.configure_exact_rates", "Genaue ct/kWh Arbeitspreise & Tibber Token einstellen:")}
                            </span>
                            <Link
                                to="/app/tariff"
                                className="font-bold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                            >
                                <span>{t("nav.tariffs", "Strompreise & Tarife")}</span>
                                <span>→</span>
                            </Link>
                        </div>
                    </div>
                </Card>
            </div>

            {/* 3. AUFSCHLÜSSELUNG DES SPAR-POTENZIALS */}
            <Card>
                <div className="mb-4">
                    <h2 className="font-bold text-slate-900 dark:text-white text-base flex items-center gap-2">
                        <span>📊</span>
                        <span>{t("energy_profile.savings_breakdown_title", "Aufschlüsselung deines Sparpotenzials")}</span>
                    </h2>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                        {t("energy_profile.savings_breakdown_desc", "So setzt sich deine jährliche Ersparnis bei optimaler Steuerung zusammen:")}
                    </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    {(profile?.savings_breakdown || []).map((item, idx) => (
                        <div
                            key={idx}
                            className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-850 border border-slate-200/80 dark:border-slate-800 flex flex-col justify-between space-y-2"
                        >
                            <div className="flex items-center justify-between">
                                <span className="text-2xl">{item.icon}</span>
                                <span className="text-sm font-black text-emerald-600 dark:text-emerald-400">
                                    +{item.amount_eur} €/a
                                </span>
                            </div>
                            <div className="text-xs font-bold text-slate-800 dark:text-slate-200">
                                {item.title}
                            </div>
                        </div>
                    ))}
                </div>
            </Card>

            {/* 4. NÄCHSTE EMPFOHLENE SCHRITTE / QUERVERWEISE */}
            <Card>
                <div className="mb-4">
                    <h2 className="font-bold text-slate-900 dark:text-white text-base flex items-center gap-2">
                        <span>🎯</span>
                        <span>{t("energy_profile.action_steps_title", "Empfohlene nächste Schritte für dein Profil")}</span>
                    </h2>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                        {t("energy_profile.action_steps_desc", "Nutze diese Funktionen in Sharegy, um dein errechnetes Sparpotenzial vollständig auszuschöpfen:")}
                    </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {(profile?.action_links || []).map((action, idx) => (
                        <Link
                            key={idx}
                            to={action.path}
                            className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-indigo-600 hover:shadow-md transition-all group flex items-start gap-3.5"
                        >
                            <span className="text-2xl p-2 rounded-xl bg-slate-50 dark:bg-slate-800 group-hover:scale-110 transition">
                                {action.icon}
                            </span>
                            <div className="flex-1 min-w-0">
                                <div className="text-xs font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition flex items-center justify-between">
                                    <span>{action.title}</span>
                                    <span>→</span>
                                </div>
                                <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed">
                                    {action.subtitle}
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            </Card>
        </div>
    );
}
