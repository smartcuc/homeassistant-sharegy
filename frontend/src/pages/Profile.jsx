/*
# src/pages/Profile.jsx
*/

import { useState } from "react";
import { Link } from "react-router-dom";
import Card from "../components/ui/Card";
import PushNotificationSettings from "../features/alerts/components/PushNotificationSettings";
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
        } finally {
            setSavingTimezone(false);
        }
    }

    const [exporting, setExporting] = useState(false);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [deleteConfirmation, setDeleteConfirmation] = useState("");
    const [deleting, setDeleting] = useState(false);
    const [deleteError, setDeleteError] = useState(null);

    async function handleExportData() {
        setExporting(true);
        try {
            const data = await apiFetch("/api/gdpr/export/");
            const jsonStr = JSON.stringify(data, null, 2);
            const blob = new Blob([jsonStr], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `sharegy_datenexport_${user?.email?.replace("@", "_at_") || "me"}_${new Date().toISOString().slice(0, 10)}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error("Failed to export data:", err);
            alert(t("gdpr.export_failed", "Fehler beim Exportieren der Daten. Bitte versuche es später erneut."));
        } finally {
            setExporting(false);
        }
    }

    async function handleDeleteAccount() {
        setDeleting(true);
        setDeleteError(null);
        try {
            await apiFetch("/api/gdpr/delete-account/", {
                method: "POST",
                body: JSON.stringify({ confirmation: deleteConfirmation.trim() }),
            });
            localStorage.clear();
            sessionStorage.clear();
            window.location.href = "/?deleted=1";
        } catch (err) {
            setDeleteError(err?.data?.error || err?.message || t("gdpr.delete_failed", "Löschung fehlgeschlagen."));
            setDeleting(false);
        }
    }

    const currentLang = (i18n.resolvedLanguage || i18n.language || "de").substring(0, 2);

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">

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
                        <span>📧</span> {t("profile.profile_info", "Profilinformationen")}
                    </h2>
                    <div className="space-y-3 text-sm">
                        <div>
                            <span className="text-xs text-gray-400 block uppercase font-bold">{t("profile.email", "E-Mail-Adresse")}</span>
                            <span className="font-medium text-gray-800">{user?.email}</span>
                        </div>
                        <div>
                            <span className="text-xs text-gray-400 block uppercase font-bold">{t("profile.profile_name", "Profilname")}</span>
                            <span className="font-medium text-gray-800">
                                {user?.first_name ? `${user.first_name} ${user.last_name || ""}`.trim() : t("profile.not_specified", "Nicht angegeben")}
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

            </div>

            {/* PUSH NOTIFICATIONS & REALTIME ALERTS (FULL WIDTH CARD) */}
            <PushNotificationSettings />

            <div className="grid gap-6 md:grid-cols-2">

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

                {/* TIMEZONE SETTINGS */}
                <Card>
                    <h2 className="text-base font-bold text-gray-900 mb-1 flex items-center gap-2">
                        <span>🕒</span> {t("profile.timezone_title", "Zeitzone & Region")}
                    </h2>
                    <p className="text-xs text-gray-500 mb-4">
                        {t("profile.timezone_desc", "Wichtig für korrekte Zeitachsen in Diagrammen und stundengenaue Strompreis-Analysen.")}
                    </p>

                    <div className="space-y-3">
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
                                className="px-3.5 py-2 border rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-50 transition cursor-pointer"
                            >
                                {t("common.auto_detect", "Automatisch erkennen")}
                            </button>

                            <button
                                type="button"
                                onClick={saveTimezone}
                                disabled={savingTimezone}
                                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs transition cursor-pointer"
                            >
                                {savingTimezone ? t("common.saving", "Speichere...") : t("profile.save_timezone", "Zeitzone speichern")}
                            </button>
                        </div>
                    </div>
                </Card>

            </div>

            {/* GDPR / PRIVACY & DATA RIGHTS (Art. 15, Art. 20, Art. 17 DSGVO) */}
            <Card>
                <div className="border-b border-gray-100 pb-4 mb-5">
                    <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-md bg-indigo-50 text-indigo-700 text-xs font-bold mb-2">
                        <span>🛡️</span>
                        <span>{t("gdpr.badge", "Datenschutz & Betroffenenrechte (DSGVO)")}</span>
                    </div>
                    <h2 className="text-lg font-bold text-gray-900">
                        {t("gdpr.title", "Deine Daten & Privatsphäre")}
                    </h2>
                    <p className="text-xs text-gray-500 mt-1">
                        {t("gdpr.subtitle", "Transparenz über alle gespeicherten Datenkategorien, Datenexport und Kontolöschung gem. Art. 15, 17 und 20 DSGVO.")}
                    </p>
                </div>

                {/* 1. STORED DATA OVERVIEW (Art. 15 DSGVO) */}
                <div className="space-y-3 mb-6">
                    <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                        <span>📋</span>
                        <span>{t("gdpr.stored_data_title", "Übersicht gespeicherter Datenkategorien (Art. 15 DSGVO)")}</span>
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-xs space-y-1.5">
                            <div className="font-bold text-gray-900 flex items-center gap-1.5">
                                <span>👤</span>
                                <span>{t("gdpr.cat_profile", "Benutzer- & Stammdaten")}</span>
                            </div>
                            <p className="text-gray-600 leading-relaxed">
                                E-Mail-Adresse (<code className="font-mono text-indigo-600">{user?.email}</code>), Registrierungsdatum, hinterlegte Sprache & Zeitzone.
                            </p>
                            <span className="inline-block text-[10px] text-gray-400 font-semibold">Rechtsgrundlage: Art. 6 (1) lit. b DSGVO</span>
                        </div>

                        <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-xs space-y-1.5">
                            <div className="font-bold text-gray-900 flex items-center gap-1.5">
                                <span>⚡</span>
                                <span>{t("gdpr.cat_energy", "Energie- & Telemetriedaten")}</span>
                            </div>
                            <p className="text-gray-600 leading-relaxed">
                                Verknüpfte Zähler, Wechselrichter, Batteriespeicher, OBIS-Messzeitreihen (1.8.0/2.8.0) und MQTT/OCPP/WSS-Konfigurationen.
                            </p>
                            <span className="inline-block text-[10px] text-gray-400 font-semibold">Rechtsgrundlage: Art. 6 (1) lit. b DSGVO</span>
                        </div>

                        <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-xs space-y-1.5">
                            <div className="font-bold text-gray-900 flex items-center gap-1.5">
                                <span>🔐</span>
                                <span>{t("gdpr.cat_security", "Sicherheit & Sessions")}</span>
                            </div>
                            <p className="text-gray-600 leading-relaxed">
                                Magic-Link-Anmeldetokens (temporär), Zeitstempel des letzten Logins, IP-Adresse und User-Agent zur Betrugsprävention.
                            </p>
                            <span className="inline-block text-[10px] text-gray-400 font-semibold">Rechtsgrundlage: Art. 6 (1) lit. f DSGVO</span>
                        </div>

                        <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-xs space-y-1.5">
                            <div className="font-bold text-gray-900 flex items-center gap-1.5">
                                <span>💳</span>
                                <span>{t("gdpr.cat_billing", "Abrechnung & Verträge")}</span>
                            </div>
                            <p className="text-gray-600 leading-relaxed">
                                Aktiver Tarif (<span className="font-semibold">{subscriptionQuery.data?.plan === "pro" ? "Sharegy Pro" : "Sharegy Free"}</span>), Rechnungsbelege und steuerliche Nachweise.
                            </p>
                            <span className="inline-block text-[10px] text-gray-400 font-semibold">Rechtsgrundlage: Art. 6 (1) lit. c DSGVO (§ 147 AO)</span>
                        </div>
                    </div>
                </div>

                {/* 2. DATA EXPORT & DELETION ACTIONS */}
                <div className="border-t border-gray-100 pt-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div>
                        <h3 className="text-sm font-bold text-gray-900">
                            {t("gdpr.export_title", "Datenübertragbarkeit (Art. 20 DSGVO)")}
                        </h3>
                        <p className="text-xs text-gray-500">
                            {t("gdpr.export_desc", "Lade alle über dich gespeicherten Daten in einem maschinenlesbaren JSON-Format herunter.")}
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={handleExportData}
                        disabled={exporting}
                        className="px-4 py-2.5 rounded-xl border border-gray-300 hover:border-gray-400 bg-white text-gray-800 text-xs font-bold shadow-2xs hover:bg-gray-50 transition cursor-pointer flex items-center gap-2 shrink-0"
                    >
                        <span>📥</span>
                        <span>{exporting ? t("gdpr.exporting", "Exportiere Daten...") : t("gdpr.export_button", "Meine Daten exportieren (JSON)")}</span>
                    </button>
                </div>

                {/* 3. DANGER ZONE: ACCOUNT DELETION (Art. 17 DSGVO) */}
                <div className="border-t border-rose-100 bg-rose-50/50 -mx-6 -mb-6 p-6 mt-6 rounded-b-3xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div>
                        <h3 className="text-sm font-bold text-rose-900 flex items-center gap-1.5">
                            <span>⚠️</span>
                            <span>{t("gdpr.delete_title", "Konto & alle Daten löschen (Art. 17 DSGVO)")}</span>
                        </h3>
                        <p className="text-xs text-rose-700/80 mt-0.5">
                            {t("gdpr.delete_desc", "Löscht dein Benutzerkonto, alle Geräteverknüpfungen, Verlaufsdaten und Einstellungen unwiderruflich.")}
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={() => setShowDeleteModal(true)}
                        className="px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold shadow-xs transition cursor-pointer shrink-0"
                    >
                        {t("gdpr.delete_button", "Konto unwiderruflich löschen")}
                    </button>
                </div>
            </Card>

            {/* DELETE ACCOUNT CONFIRMATION MODAL */}
            {showDeleteModal && (
                <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-fade-in">
                    <div className="bg-white rounded-3xl shadow-2xl border border-rose-200 w-full max-w-lg overflow-hidden flex flex-col">
                        <div className="p-6 bg-rose-50 border-b border-rose-100 flex items-center gap-3">
                            <span className="text-3xl p-2 bg-rose-100 text-rose-600 rounded-2xl">⚠️</span>
                            <div>
                                <h3 className="text-base font-bold text-rose-950">
                                    {t("gdpr.modal_delete_title", "Konto & Daten unwiderruflich löschen?")}
                                </h3>
                                <p className="text-xs text-rose-700">
                                    {t("gdpr.modal_delete_warning", "Diese Aktion kann nicht rückgängig gemacht werden!")}
                                </p>
                            </div>
                        </div>

                        <div className="p-6 space-y-4 text-xs sm:text-sm text-gray-700">
                            <p>
                                {t(
                                    "gdpr.modal_delete_text",
                                    "Wenn du fortfährst, werden dein Benutzerkonto, alle konfigurierten Zähler, Wechselrichter, historische Diagramme und Benachrichtigungen sofort gelöscht."
                                )}
                            </p>

                            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-xs text-gray-600">
                                {t("gdpr.modal_delete_prompt", "Zur Bestätigung gib bitte deine E-Mail-Adresse")} (<strong>{user?.email}</strong>) {t("gdpr.modal_delete_or", "oder")} <strong>LÖSCHEN</strong> {t("gdpr.modal_delete_in_field", "ein:")}
                            </div>

                            <input
                                type="text"
                                value={deleteConfirmation}
                                onChange={(e) => setDeleteConfirmation(e.target.value)}
                                placeholder={user?.email || "LÖSCHEN"}
                                className="w-full border border-gray-300 rounded-xl px-3.5 py-2.5 text-sm font-medium focus:ring-2 focus:ring-rose-500 focus:outline-none"
                            />

                            {deleteError && (
                                <p className="text-xs font-bold text-rose-600 bg-rose-50 p-2.5 rounded-xl border border-rose-200">
                                    {deleteError}
                                </p>
                            )}
                        </div>

                        <div className="p-4 bg-slate-50 border-t border-gray-100 flex items-center justify-end gap-3">
                            <button
                                type="button"
                                onClick={() => {
                                    setShowDeleteModal(false);
                                    setDeleteConfirmation("");
                                    setDeleteError(null);
                                }}
                                className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 bg-white border border-gray-200 hover:bg-gray-100 transition cursor-pointer"
                            >
                                {t("common.cancel", "Abbrechen")}
                            </button>

                            <button
                                type="button"
                                onClick={handleDeleteAccount}
                                disabled={
                                    deleting ||
                                    (deleteConfirmation.trim().toLowerCase() !== user?.email?.toLowerCase() &&
                                        deleteConfirmation.trim().toUpperCase() !== "LÖSCHEN" &&
                                        deleteConfirmation.trim().toUpperCase() !== "DELETE")
                                }
                                className="px-5 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold shadow-xs transition cursor-pointer"
                            >
                                {deleting ? t("gdpr.deleting", "Lösche Konto...") : t("gdpr.confirm_delete", "Endgültig löschen")}
                            </button>
                        </div>
                    </div>
                </div>
            )}

        </div>
    );
}
