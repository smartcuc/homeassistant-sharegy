/*
# src/pages/Onboarding.jsx
*/

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useSettings } from "../hooks/useSettings";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export default function Onboarding() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const { settings } = useSettings();

    const detectedTimezone =
        Intl.DateTimeFormat().resolvedOptions().timeZone || "Europe/Berlin";

    // Schritt im Onboarding Wizard: 0 = Intro, 1 = Hardware, 2 = Tarif, 3 = Ergebnis
    const [wizardStep, setWizardStep] = useState(0);

    // Formular-Zustand für 3-Klick Setup
    const [solarType, setSolarType] = useState("none"); // "none", "bkw", "pv"
    const [hasBattery, setHasBattery] = useState(false);
    const [hasEv, setHasEv] = useState(false);
    const [hasHeatpump, setHasHeatpump] = useState(false);
    const [tariffType, setTariffType] = useState("static"); // "static", "dynamic"

    // Errechnetes Profil
    const [calculatedProfile, setCalculatedProfile] = useState(null);
    const [isCalculating, setIsCalculating] = useState(false);

    const finishMutation = useMutation({
        mutationFn: async () => {
            // 1. Zeitzone speichern
            try {
                await apiFetch("/api/timezone/", {
                    method: "POST",
                    body: JSON.stringify({ timezone: detectedTimezone }),
                });
            } catch (e) {
                console.warn("Timezone save failed:", e);
            }

            // 2. Energie-Profil speichern
            try {
                await apiFetch("/api/energy/profile/", {
                    method: "POST",
                    body: JSON.stringify({
                        solar_type: solarType,
                        has_battery: hasBattery,
                        has_ev: hasEv,
                        has_heatpump: hasHeatpump,
                        tariff_type: tariffType,
                    }),
                });
            } catch (e) {
                console.warn("Energy profile save failed:", e);
            }

            // 3. Onboarding als 'done' markieren
            await apiFetch("/api/onboarding-step/", {
                method: "POST",
                body: JSON.stringify({ onboarding_step: "done" }),
            });
        },
        onSuccess: () => {
            queryClient.setQueryData(["settings"], (old) => {
                if (!old) return old;
                return { ...old, onboarding_step: "done" };
            });
            queryClient.invalidateQueries({ queryKey: ["settings"] });
            queryClient.invalidateQueries({ queryKey: ["energy-profile"] });
            queryClient.invalidateQueries({ queryKey: ["system-setup-status"] });
            navigate("/app/dashboard", { replace: true });
        },
    });

    useEffect(() => {
        if (!settings) return;
        if (settings.onboarding_step === "done") {
            navigate("/app/dashboard", { replace: true });
        }
    }, [settings, navigate]);

    // Wenn Schritt 3 erreicht wird: Berechne Profil
    const calculateProfilePreview = async () => {
        setIsCalculating(true);
        try {
            const res = await apiFetch("/api/energy/profile/", {
                method: "POST",
                body: JSON.stringify({
                    solar_type: solarType,
                    has_battery: hasBattery,
                    has_ev: hasEv,
                    has_heatpump: hasHeatpump,
                    tariff_type: tariffType,
                }),
            });
            setCalculatedProfile(res);
        } catch (e) {
            console.error("Profile calculation error:", e);
        } finally {
            setIsCalculating(false);
            setWizardStep(3);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-slate-900 to-indigo-950 flex items-center justify-center p-4 sm:p-6">
            <div className="bg-white dark:bg-slate-900 w-full max-w-2xl rounded-3xl shadow-2xl border border-slate-100 dark:border-slate-800 p-6 sm:p-8 overflow-hidden relative">
                
                {/* PROGRESS BAR */}
                {wizardStep > 0 && (
                    <div className="mb-6">
                        <div className="flex items-center justify-between text-xs font-bold text-slate-400 mb-2">
                            <span>{t("onboarding.step_indicator", { current: wizardStep, total: 3, defaultValue: `Schritt ${wizardStep} von 3` })}</span>
                            <span>{wizardStep === 1 ? t("onboarding.step_1_title", "Hardware") : wizardStep === 2 ? t("onboarding.step_2_title", "Stromtarif") : t("onboarding.step_3_title", "Dein Energie-Profil")}</span>
                        </div>
                        <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div
                                className="bg-indigo-600 h-full transition-all duration-300 rounded-full"
                                style={{ width: `${(wizardStep / 3) * 100}%` }}
                            />
                        </div>
                    </div>
                )}

                {/* =========================================================
                    SCHRITT 0: WILLKOMMEN
                ========================================================= */}
                {wizardStep === 0 && (
                    <div className="text-center space-y-6 animate-fade-in">
                        <div className="w-16 h-16 mx-auto bg-indigo-50 dark:bg-indigo-950/60 rounded-2xl flex items-center justify-center text-3xl shadow-inner border border-indigo-100 dark:border-indigo-900/50">
                            ⚡
                        </div>

                        <div className="space-y-2">
                            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
                                {t("onboarding.welcome_title", "Willkommen bei Sharegy ⚡")}
                            </h1>
                            <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto">
                                {t("onboarding.welcome_subtitle_custom", "In nur 3 kurzen Klicks ermitteln wir dein persönliches Energie-Profil und das maximale Sparpotenzial.")}
                            </p>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
                            <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700">
                                <span className="text-xl">📊</span>
                                <div className="font-bold text-xs text-slate-900 dark:text-white mt-1">Echtzeit-Übersicht</div>
                                <div className="text-[11px] text-slate-500 dark:text-slate-400">Solar, Netz & Lasten live</div>
                            </div>
                            <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700">
                                <span className="text-xl">💡</span>
                                <div className="font-bold text-xs text-slate-900 dark:text-white mt-1">Tarif-Kompass</div>
                                <div className="text-[11px] text-slate-500 dark:text-slate-400">Festpreis vs. Börsenpreis</div>
                            </div>
                            <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700">
                                <span className="text-xl">💰</span>
                                <div className="font-bold text-xs text-slate-900 dark:text-white mt-1">Ersparnis-Rechner</div>
                                <div className="text-[11px] text-slate-500 dark:text-slate-400">Bis zu hunderte Euro/Jahr</div>
                            </div>
                        </div>

                        <button
                            type="button"
                            onClick={() => setWizardStep(1)}
                            className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-bold text-sm shadow-md transition transform active:scale-[0.99] cursor-pointer"
                        >
                            {t("onboarding.get_started_btn", "Setup in 3 Klicks starten →")}
                        </button>
                    </div>
                )}

                {/* =========================================================
                    SCHRITT 1: HARDWARE AUSWAHL
                ========================================================= */}
                {wizardStep === 1 && (
                    <div className="space-y-5 animate-fade-in">
                        <div className="text-center space-y-1">
                            <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
                                {t("onboarding.step_1_heading", "1. Welche Ausstattung hast du?")}
                            </h2>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                {t("onboarding.step_1_sub", "Wähle deine Solaranlage und vorhandene Großverbraucher aus.")}
                            </p>
                        </div>

                        {/* SOLAR AUSWAHL */}
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">
                                Solaranlage
                            </label>
                            <div className="grid grid-cols-3 gap-2.5">
                                {[
                                    { key: "none", icon: "🏢", label: "Kein Solar", desc: "Wohnung / Dach frei" },
                                    { key: "bkw", icon: "☀️", label: "Balkonkraftwerk", desc: "Stecker-Solar 800W" },
                                    { key: "pv", icon: "🏡", label: "PV-Anlage", desc: "Dach-Solaranlage" },
                                ].map((item) => (
                                    <button
                                        key={item.key}
                                        type="button"
                                        onClick={() => setSolarType(item.key)}
                                        className={`p-3 rounded-2xl border-2 text-left transition cursor-pointer flex flex-col justify-between ${
                                            solarType === item.key
                                                ? "border-indigo-600 bg-indigo-50/70 dark:bg-indigo-950/60 shadow-xs"
                                                : "border-slate-200 dark:border-slate-700 hover:border-slate-300 bg-white dark:bg-slate-900"
                                        }`}
                                    >
                                        <span className="text-2xl">{item.icon}</span>
                                        <div className="mt-2">
                                            <div className="font-bold text-xs text-slate-900 dark:text-white">{item.label}</div>
                                            <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">{item.desc}</div>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* WEITERE GERÄTE (SCHALTER / CARDS) */}
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">
                                Weitere Komponenten (Zutreffendes antippen)
                            </label>

                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                                {/* BATTERIESPEICHER */}
                                <button
                                    type="button"
                                    onClick={() => setHasBattery(!hasBattery)}
                                    className={`p-3 rounded-2xl border-2 text-left transition cursor-pointer flex items-center gap-3 ${
                                        hasBattery
                                            ? "border-emerald-600 bg-emerald-50/70 dark:bg-emerald-950/60 shadow-xs"
                                            : "border-slate-200 dark:border-slate-700 hover:border-slate-300 bg-white dark:bg-slate-900"
                                    }`}
                                >
                                    <span className="text-2xl">🔋</span>
                                    <div>
                                        <div className="font-bold text-xs text-slate-900 dark:text-white">Batteriespeicher</div>
                                        <div className="text-[10px] text-slate-500 dark:text-slate-400">{hasBattery ? "Aktiv ✓" : "Nicht vorhanden"}</div>
                                    </div>
                                </button>

                                {/* E-AUTO */}
                                <button
                                    type="button"
                                    onClick={() => setHasEv(!hasEv)}
                                    className={`p-3 rounded-2xl border-2 text-left transition cursor-pointer flex items-center gap-3 ${
                                        hasEv
                                            ? "border-emerald-600 bg-emerald-50/70 dark:bg-emerald-950/60 shadow-xs"
                                            : "border-slate-200 dark:border-slate-700 hover:border-slate-300 bg-white dark:bg-slate-900"
                                    }`}
                                >
                                    <span className="text-2xl">🚗</span>
                                    <div>
                                        <div className="font-bold text-xs text-slate-900 dark:text-white">E-Auto / Wallbox</div>
                                        <div className="text-[10px] text-slate-500 dark:text-slate-400">{hasEv ? "Aktiv ✓" : "Nicht vorhanden"}</div>
                                    </div>
                                </button>

                                {/* WÄRMEPUMPE */}
                                <button
                                    type="button"
                                    onClick={() => setHasHeatpump(!hasHeatpump)}
                                    className={`p-3 rounded-2xl border-2 text-left transition cursor-pointer flex items-center gap-3 ${
                                        hasHeatpump
                                            ? "border-emerald-600 bg-emerald-50/70 dark:bg-emerald-950/60 shadow-xs"
                                            : "border-slate-200 dark:border-slate-700 hover:border-slate-300 bg-white dark:bg-slate-900"
                                    }`}
                                >
                                    <span className="text-2xl">♨️</span>
                                    <div>
                                        <div className="font-bold text-xs text-slate-900 dark:text-white">Wärmepumpe</div>
                                        <div className="text-[10px] text-slate-500 dark:text-slate-400">{hasHeatpump ? "Aktiv ✓" : "Nicht vorhanden"}</div>
                                    </div>
                                </button>
                            </div>
                        </div>

                        <div className="flex gap-2 pt-2">
                            <button
                                type="button"
                                onClick={() => setWizardStep(0)}
                                className="px-4 py-3 border border-slate-200 dark:border-slate-700 rounded-2xl text-xs font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition cursor-pointer"
                            >
                                ← Zurück
                            </button>
                            <button
                                type="button"
                                onClick={() => setWizardStep(2)}
                                className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-bold text-xs shadow-md transition cursor-pointer"
                            >
                                Weiter zum Stromtarif (Schritt 2) →
                            </button>
                        </div>
                    </div>
                )}

                {/* =========================================================
                    SCHRITT 2: STROMTARIF AUSWAHL
                ========================================================= */}
                {wizardStep === 2 && (
                    <div className="space-y-5 animate-fade-in">
                        <div className="text-center space-y-1">
                            <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
                                {t("onboarding.step_2_heading", "2. Welchen Stromtarif nutzt du aktuell?")}
                            </h2>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                {t("onboarding.step_2_sub", "Dies hilft uns bei der Empfehlung, ob sich ein dynamischer Börsentarif für dich lohnt.")}
                            </p>
                        </div>

                        <div className="space-y-3">
                            {/* OPTION FESTPREIS */}
                            <div
                                onClick={() => setTariffType("static")}
                                className={`p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                                    tariffType === "static"
                                        ? "border-indigo-600 bg-indigo-50/70 dark:bg-indigo-950/60 shadow-xs"
                                        : "border-slate-200 dark:border-slate-700 hover:border-slate-300 bg-white dark:bg-slate-900"
                                }`}
                            >
                                <div className="flex items-start gap-3">
                                    <input
                                        type="radio"
                                        checked={tariffType === "static"}
                                        onChange={() => setTariffType("static")}
                                        className="mt-1 h-4 w-4 text-indigo-600"
                                    />
                                    <div>
                                        <div className="font-bold text-sm text-slate-900 dark:text-white">
                                            🔒 Klassischer Festpreis-Tarif (~30–35 ct/kWh)
                                        </div>
                                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                            Konstanter Strompreis rund um die Uhr (z. B. Stadtwerke, Grundversorger, Standard-Stromtarif).
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* OPTION DYNAMISCH */}
                            <div
                                onClick={() => setTariffType("dynamic")}
                                className={`p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                                    tariffType === "dynamic"
                                        ? "border-emerald-600 bg-emerald-50/70 dark:bg-emerald-950/60 shadow-xs"
                                        : "border-slate-200 dark:border-slate-700 hover:border-slate-300 bg-white dark:bg-slate-900"
                                }`}
                            >
                                <div className="flex items-start gap-3">
                                    <input
                                        type="radio"
                                        checked={tariffType === "dynamic"}
                                        onChange={() => setTariffType("dynamic")}
                                        className="mt-1 h-4 w-4 text-emerald-600"
                                    />
                                    <div>
                                        <div className="font-bold text-sm text-slate-900 dark:text-white">
                                            ⚡ Dynamischer Börsenstromtarif (z. B. Tibber, Rabot, Ostrom)
                                        </div>
                                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                            Stündlich/viertelstündlich wechselnde Börsenpreise der Strombörse EPEX Spot.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="flex gap-2 pt-2">
                            <button
                                type="button"
                                onClick={() => setWizardStep(1)}
                                className="px-4 py-3 border border-slate-200 dark:border-slate-700 rounded-2xl text-xs font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition cursor-pointer"
                            >
                                ← Zurück
                            </button>
                            <button
                                type="button"
                                onClick={calculateProfilePreview}
                                disabled={isCalculating}
                                className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-bold text-xs shadow-md transition cursor-pointer disabled:opacity-50"
                            >
                                {isCalculating ? "Berechne Profil..." : "Auswertung anzeigen (Schritt 3) →"}
                            </button>
                        </div>
                    </div>
                )}

                {/* =========================================================
                    SCHRITT 3: ERGEBNIS & PROFIL
                ========================================================= */}
                {wizardStep === 3 && calculatedProfile && (
                    <div className="space-y-5 animate-fade-in">
                        <div className="text-center space-y-1">
                            <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
                                🚀 {t("onboarding.step_3_heading", "Dein persönliches Energie-Profil:")}
                            </h2>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                {t("onboarding.step_3_sub", "Basierend auf deinen Angaben haben wir dein Einsparpotenzial ermittelt.")}
                            </p>
                        </div>

                        {/* RESULT CARD */}
                        <div className="p-5 rounded-3xl bg-gradient-to-br from-indigo-900 to-slate-900 text-white border border-indigo-800/60 shadow-xl space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-indigo-500/30 text-indigo-300 border border-indigo-400/30">
                                    Energie-Profil: {calculatedProfile.profile_code}
                                </span>
                                <span className="text-xs font-bold text-emerald-400">
                                    ~{calculatedProfile.shiftable_kwh_year.toLocaleString()} kWh/a flexibel
                                </span>
                            </div>

                            <div>
                                <h3 className="text-xl font-black text-white">
                                    {calculatedProfile.profile_name}
                                </h3>
                                <p className="text-xs text-indigo-200 mt-1">
                                    {calculatedProfile.profile_subtitle}
                                </p>
                            </div>

                            <div className="p-3.5 rounded-2xl bg-white/10 backdrop-blur-md border border-white/10 flex items-center justify-between">
                                <div>
                                    <div className="text-[10px] uppercase font-bold text-indigo-200">
                                        Geschätzte Ersparnis
                                    </div>
                                    <div className="text-2xl font-black text-emerald-400">
                                        ca. {calculatedProfile.estimated_savings_eur_year} €
                                        <span className="text-xs font-normal text-slate-300"> / Jahr</span>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-[10px] uppercase font-bold text-indigo-200">
                                        Tarif-Empfehlung
                                    </div>
                                    <div className="text-xs font-bold text-white">
                                        {calculatedProfile.recommended_tariff === "dynamic" ? "⚡ Dynamisch" : "🔒 Festpreis"}
                                    </div>
                                </div>
                            </div>

                            <div className="text-[11px] text-slate-300 leading-relaxed bg-black/20 p-3 rounded-xl">
                                💡 <strong>Hinweis:</strong> {calculatedProfile.tariff_verdict_reason}
                            </div>
                        </div>

                        <button
                            type="button"
                            onClick={() => finishMutation.mutate()}
                            disabled={finishMutation.isLoading}
                            className="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl font-bold text-sm shadow-md transition transform active:scale-[0.99] cursor-pointer disabled:opacity-50"
                        >
                            {finishMutation.isLoading ? "Speichere..." : "Dashboard mit diesem Profil starten 🚀"}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
