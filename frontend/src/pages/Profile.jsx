/*
# src/pages/Profile.jsx
*/

import { useState } from "react";
import { Link } from "react-router-dom";
import Card from "../components/ui/Card";
import { apiFetch } from "../api/client";
import { useSettings } from "../hooks/useSettings";
import { useUser } from "../hooks/useUser";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import i18n from "../i18n";

export default function Profile() {
    const { user } = useUser();
    const queryClient = useQueryClient();
    const { settings } = useSettings();
    const { t } = useTranslation();

    const [selectedTimezone, setSelectedTimezone] = useState(null);
    const [saved, setSaved] = useState(false);
    const [savingTimezone, setSavingTimezone] = useState(false);

    const timezoneQuery = useQuery({
        queryKey: ["timezones"],
        queryFn: () => apiFetch("/api/timezones/"),
        staleTime: Infinity,
    });

    const subscriptionQuery = useQuery({
        queryKey: ["billingOverview"],
        queryFn: () => apiFetch("/api/billing/subscription/me/"),
    });

    const commonTimezones =
        timezoneQuery.data?.filter((tz) =>
            tz.startsWith("Europe/") || tz === "UTC"
        ) || [];

    const activeTimezone = selectedTimezone ?? settings?.timezone ?? "";

    async function handleLanguageChange(langId) {
        await i18n.changeLanguage(langId);
        localStorage.setItem("i18nextLng", langId);

        queryClient.setQueryData(["settings"], (old) => {
            if (!old) return old;
            return {
                ...old,
                language: langId,
            };
        });

        try {
            await apiFetch("/api/language/", {
                method: "POST",
                body: JSON.stringify({ language: langId }),
            });
        } catch {
            // Ignore fallback
        }

        setSaved(true);
        setTimeout(() => setSaved(false), 2500);
    }

    async function saveTimezone() {
        setSavingTimezone(true);
        try {
            await apiFetch("/api/timezone/", {
                method: "POST",
                body: JSON.stringify({ timezone: activeTimezone }),
            });
            await queryClient.invalidateQueries({ queryKey: ["settings"] });
            setSelectedTimezone(null);
            setSaved(true);
            setTimeout(() => setSaved(false), 2500);
        } finally {
            setSavingTimezone(false);
        }
    }

    const currentLang = (i18n.resolvedLanguage || i18n.language || "de").substring(0, 2);

    return (
        <div className="max-w-4xl mx-auto p-6 space-y-6">

            {/* HEADER */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                    <span>👤</span> {t("profile.title", "Benutzerprofil")}
                </h1>
                <p className="text-gray-500 mt-1">
                    {t("profile.subtitle", "Persönliche Daten, Sprache und regionale Einstellungen.")}
                </p>
            </div>

            {saved && (
                <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-emerald-800 text-sm font-semibold flex items-center gap-2">
                    <span>✅</span> {t("common.saved", "Einstellungen wurden gespeichert.")}
                </div>
            )}

            <div className="grid gap-6 md:grid-cols-2">

                {/* USER DATA */}
                <Card>
                    <h2 className="text-base font-bold text-gray-900 mb-3 flex items-center gap-2">
                        <span>📧</span> {t("profile.account_info", "Kontoinformationen")}
                    </h2>
                    <div className="space-y-3 text-sm">
                        <div>
                            <span className="text-xs text-gray-400 block uppercase font-bold">{t("profile.email", "E-Mail-Adresse")}</span>
                            <span className="font-medium text-gray-800">{user?.email}</span>
                        </div>
                        <div>
                            <span className="text-xs text-gray-400 block uppercase font-bold">{t("profile.name", "Name")}</span>
                            <span className="font-medium text-gray-800">
                                {user?.first_name ? `${user.first_name} ${user.last_name || ""}` : t("profile.not_specified", "Nicht angegeben")}
                            </span>
                        </div>
                        <div>
                            <span className="text-xs text-gray-400 block uppercase font-bold">{t("profile.homes", "Haushalte")}</span>
                            <span className="font-medium text-gray-800">
                                {user?.homes?.length || 1} {user?.homes?.length === 1 ? t("profile.home_single", "Haushalt") : t("profile.home_multi", "Haushalte")}
                            </span>
                        </div>
                    </div>
                </Card>

                {/* SUBSCRIPTION & BILLING SUMMARY */}
                <Card>
                    <div className="flex items-center justify-between mb-3">
                        <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
                            <span>💳</span> {t("profile.subscription_title", "Abonnement & Tarif")}
                        </h2>
                        <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${subscriptionQuery.data?.subscription?.is_pro
                            ? "bg-emerald-100 text-emerald-800 border-emerald-300"
                            : "bg-gray-100 text-gray-700 border-gray-200"
                            }`}>
                            {subscriptionQuery.data?.subscription?.plan_name || "Sharegy Free"}
                        </span>
                    </div>
                    <div className="space-y-3 text-sm">
                        <div>
                            <span className="text-xs text-gray-400 block uppercase font-bold">{t("common.status", "Status")}</span>
                            <span className="font-medium text-gray-800">
                                {subscriptionQuery.data?.subscription?.status === "active" ? `🟢 ${t("common.active", "Aktiv")}` : t("common.inactive", "Inaktiv")}
                            </span>
                        </div>
                        <div>
                            <span className="text-xs text-gray-400 block uppercase font-bold">{t("billing.invoices_title", "Rechnungen")}</span>
                            <span className="font-medium text-gray-800">
                                {t("profile.invoices_count", { count: subscriptionQuery.data?.invoices?.length || 0, defaultValue: `${subscriptionQuery.data?.invoices?.length || 0} archivierte Belege` })}
                            </span>
                        </div>
                        <div className="pt-2">
                            <Link
                                to="/app/billing"
                                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold rounded-xl text-xs border border-indigo-200 transition"
                            >
                                {t("profile.manage_plans_link", "Tarife verwalten & Rechnungen ansehen →")}
                            </Link>
                        </div>
                    </div>
                </Card>

                {/* LANGUAGE SELECTION */}
                <Card>
                    <h2 className="text-base font-bold text-gray-900 mb-1 flex items-center gap-2">
                        <span>🌐</span> {t("profile.ui_language", "Sprache der Benutzeroberfläche")}
                    </h2>
                    <p className="text-xs text-gray-500 mb-4">
                        {t("profile.ui_language_desc", "Wähle deine bevorzugte Sprache. Die Änderung wird sofort aktiv.")}
                    </p>

                    <div className="flex flex-col gap-2.5">
                        {[
                            { id: "de", label: "🇩🇪 Deutsch", desc: "Standard (Deutschland, Österreich, Schweiz)" },
                            { id: "en", label: "🇬🇧 English", desc: "International English" },
                            { id: "pl", label: "🇵🇱 Polski", desc: "Język polski" },
                        ].map((lang) => {
                            const isActive = currentLang === lang.id;
                            return (
                                <button
                                    key={lang.id}
                                    type="button"
                                    onClick={() => handleLanguageChange(lang.id)}
                                    className={`p-3 rounded-xl border text-left transition flex items-center justify-between ${isActive
                                        ? "border-indigo-600 bg-indigo-50/80 ring-2 ring-indigo-500/20 shadow-xs"
                                        : "border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50"
                                        }`}
                                >
                                    <div>
                                        <div className="font-semibold text-sm text-gray-900">
                                            {lang.label}
                                        </div>
                                        <div className="text-[11px] text-gray-500">
                                            {lang.desc}
                                        </div>
                                    </div>
                                    {isActive && (
                                        <span className="text-xs font-bold text-indigo-700 bg-white px-2 py-0.5 rounded-full border border-indigo-200">
                                            {t("common.active", "Aktiv")}
                                        </span>
                                    )}
                                </button>
                            );
                        })}
                    </div>
                </Card>

            </div>

            {/* TIMEZONE SETTINGS */}
            <Card>
                <h2 className="text-base font-bold text-gray-900 mb-1 flex items-center gap-2">
                    <span>🕒</span> {t("profile.timezone_title", "Zeitzone & Region")}
                </h2>
                <p className="text-xs text-gray-500 mb-4">
                    {t("profile.timezone_desc", "Wichtig für korrekte Zeitachsen in Diagrammen und stundengenaue Strompreis-Analysen.")}
                </p>

                <div className="max-w-md space-y-3">
                    <select
                        value={activeTimezone}
                        onChange={(e) => setSelectedTimezone(e.target.value)}
                        className="w-full border rounded-xl px-3.5 py-2.5 bg-white text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                        <option value="">{t("profile.select_prompt", "Bitte auswählen")}</option>
                        {commonTimezones.map((tz) => (
                            <option key={tz} value={tz}>{tz}</option>
                        ))}
                    </select>

                    <div className="flex gap-2 pt-1">
                        <button
                            type="button"
                            onClick={() => setSelectedTimezone(Intl.DateTimeFormat().resolvedOptions().timeZone)}
                            className="px-3.5 py-2 border rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-50 transition"
                        >
                            {t("common.auto_detect", "Automatisch erkennen")}
                        </button>

                        <button
                            type="button"
                            onClick={saveTimezone}
                            disabled={savingTimezone}
                            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs transition"
                        >
                            {savingTimezone ? t("common.saving", "Speichere...") : t("profile.save_timezone", "Zeitzone speichern")}
                        </button>
                    </div>
                </div>
            </Card>

        </div>
    );
}
