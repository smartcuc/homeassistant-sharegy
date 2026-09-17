/*
# src/pages/Profile.jsx
*/

import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import Card from "../components/ui/Card";
import PushNotificationSettings from "../features/alerts/components/PushNotificationSettings";
import InvoicesListCard from "../features/billing/components/InvoicesListCard";
import { apiFetch } from "../api/client";
import { useSettings } from "../hooks/useSettings";
import { useUser } from "../hooks/useUser";
import { useSubscription } from "../hooks/useSubscription";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import i18n from "../i18n";
import { AVATAR_PRESETS, getAvatarConfig } from "../utils/avatars";
import FlagIcon from "../components/common/FlagIcon";

export default function Profile() {
    const { user } = useUser();
    const queryClient = useQueryClient();
    const { settings } = useSettings();
    const { t } = useTranslation();
    const { isPro, isLandlord, planName, invoices, refetch: refetchSubscription } = useSubscription();
    const [searchParams, setSearchParams] = useSearchParams();

    // Active tab from URL query param (e.g. ?tab=company) or default to 'profile'
    const initialTab = searchParams.get("tab") || "profile";
    const [activeTab, setActiveTab] = useState(initialTab);

    useEffect(() => {
        const tabParam = searchParams.get("tab");
        if (tabParam && tabParam !== activeTab) {
            setActiveTab(tabParam);
        }
    }, [searchParams]);

    const handleTabChange = (tabId) => {
        setActiveTab(tabId);
        setSearchParams({ tab: tabId }, { replace: true });
    };

    // Feedback States
    const [savedMsg, setSavedMsg] = useState("");
    const [errorMsg, setErrorMsg] = useState("");

    const showSuccess = (msg) => {
        setSavedMsg(msg);
        setErrorMsg("");
        setTimeout(() => setSavedMsg(""), 3500);
    };

    const showError = (msg) => {
        setErrorMsg(msg);
        setTimeout(() => setErrorMsg(""), 4000);
    };

    // --- 1. PROFILE & B2B COMPANY DATA QUERY ---
    const profileQuery = useQuery({
        queryKey: ["userProfile"],
        queryFn: () => apiFetch("/api/profile/"),
        staleTime: 1000 * 60 * 2,
    });

    // Form state for Personal & Company Info
    const [formData, setFormData] = useState({
        first_name: "",
        last_name: "",
        phone: "",
        avatar: "",
        customer_type: "private",
        company_name: "",
        billing_name: "",
        billing_email: "",
        vat_id: "",
        street: "",
        house_number: "",
        postal_code: "",
        city: "",
        country: "DE",
    });

    // Avatar Picker Modal State
    const [showAvatarModal, setShowAvatarModal] = useState(false);

    useEffect(() => {
        if (profileQuery.data) {
            setFormData({
                first_name: profileQuery.data.first_name || user?.first_name || "",
                last_name: profileQuery.data.last_name || user?.last_name || "",
                phone: profileQuery.data.phone || "",
                avatar: profileQuery.data.avatar || user?.avatar || user?.profile?.avatar || "",
                customer_type: profileQuery.data.customer_type || "private",
                company_name: profileQuery.data.company_name || "",
                billing_name: profileQuery.data.billing_name || "",
                billing_email: profileQuery.data.billing_email || "",
                vat_id: profileQuery.data.vat_id || "",
                street: profileQuery.data.street || "",
                house_number: profileQuery.data.house_number || "",
                postal_code: profileQuery.data.postal_code || "",
                city: profileQuery.data.city || "",
                country: profileQuery.data.country || "DE",
            });
        }
    }, [profileQuery.data, user]);

    const [savingProfile, setSavingProfile] = useState(false);

    const handleSaveProfile = async (e, customData = null) => {
        if (e) e.preventDefault();
        setSavingProfile(true);
        const base = customData || formData;
        const dataToSave = {
            ...base,
            customer_type: base.company_name?.trim() ? "business" : "private",
        };
        try {
            await apiFetch("/api/profile/", {
                method: "POST",
                body: JSON.stringify(dataToSave),
            });
            await queryClient.invalidateQueries({ queryKey: ["userProfile"] });
            await queryClient.invalidateQueries({ queryKey: ["user"] });
            await queryClient.invalidateQueries({ queryKey: ["me"] });
            showSuccess(t("profile.save_success", "Änderungen wurden erfolgreich gespeichert."));
        } catch (err) {
            showError(err?.data?.error || t("profile.save_error", "Fehler beim Speichern der Profildaten."));
        } finally {
            setSavingProfile(false);
        }
    };

    const handleSelectAvatar = async (avatarId) => {
        const updated = { ...formData, avatar: avatarId };
        setFormData(updated);
        setShowAvatarModal(false);
        await handleSaveProfile(null, updated);
    };

    // --- 2. TIMEZONE & LANGUAGE ---
    const [selectedTimezone, setSelectedTimezone] = useState(null);
    const [savingTimezone, setSavingTimezone] = useState(false);

    // --- EMAIL CHANGE WORKFLOW ---
    const [showEmailModal, setShowEmailModal] = useState(false);
    const [newEmailInput, setNewEmailInput] = useState("");
    const [requestingEmailChange, setRequestingEmailChange] = useState(false);
    const [emailChangeSuccess, setEmailChangeSuccess] = useState(false);

    // --- EMAIL NOTIFICATION PREFERENCES ---
    const [notifyWeekly, setNotifyWeekly] = useState(true);
    const [notifyCritical, setNotifyCritical] = useState(true);
    const [isSavingNotification, setIsSavingNotification] = useState(false);

    useEffect(() => {
        if (settings) {
            if (settings.notify_weekly_report !== undefined) {
                setNotifyWeekly(Boolean(settings.notify_weekly_report));
            }
            if (settings.notify_critical_alerts !== undefined) {
                setNotifyCritical(Boolean(settings.notify_critical_alerts));
            }
        }
    }, [settings]);

    const handleToggleNotification = async (key, val) => {
        const nextWeekly = key === "notify_weekly_report" ? val : notifyWeekly;
        const nextCritical = key === "notify_critical_alerts" ? val : notifyCritical;
        if (key === "notify_weekly_report") setNotifyWeekly(val);
        if (key === "notify_critical_alerts") setNotifyCritical(val);

        setIsSavingNotification(true);
        try {
            await apiFetch("/api/settings/", {
                method: "POST",
                body: JSON.stringify({
                    notify_weekly_report: nextWeekly,
                    notify_critical_alerts: nextCritical,
                }),
            });
            await queryClient.invalidateQueries({ queryKey: ["settings"] });
            showSuccess(t("profile.notification_saved", "E-Mail-Einstellungen gespeichert!"));
        } catch (err) {
            showError(t("profile.notification_save_error", "Fehler beim Speichern der Benachrichtigungseinstellungen."));
        } finally {
            setIsSavingNotification(false);
        }
    };

    // --- REVOKE MAGIC LINKS & LOGOUT WORKFLOW ---
    const [showRevokeModal, setShowRevokeModal] = useState(false);
    const [revokingLinks, setRevokingLinks] = useState(false);

    const handleRevokeMagicLinks = async () => {
        setRevokingLinks(true);
        try {
            await apiFetch("/api/auth/revoke-magic-links/", {
                method: "POST",
            });
            showSuccess(t("profile.revoke_success", "Alle Magic-Links wurden erfolgreich gelöscht. Du wirst nun abgemeldet."));
            setShowRevokeModal(false);
            queryClient.clear();
            setTimeout(() => {
                window.location.href = "/login?revoked=true";
            }, 1000);
        } catch (err) {
            showError(err?.data?.error || err?.message || t("profile.revoke_error", "Fehler beim Löschen der Magic-Links."));
            setRevokingLinks(false);
        }
    };

    const handleRequestEmailChange = async (e) => {
        if (e) e.preventDefault();
        const trimmed = newEmailInput.trim().toLowerCase();
        if (!trimmed || !trimmed.includes("@") || !trimmed.includes(".")) {
            showError("Bitte gib eine gültige E-Mail-Adresse ein.");
            return;
        }
        setRequestingEmailChange(true);
        try {
            await apiFetch("/api/change-email/", {
                method: "POST",
                body: JSON.stringify({ new_email: trimmed }),
            });
            setEmailChangeSuccess(true);
            showSuccess(`Bestätigungslink an ${trimmed} gesendet!`);
        } catch (err) {
            showError(err?.data?.error || err?.message || "Fehler beim Anfordern der E-Mail-Änderung.");
        } finally {
            setRequestingEmailChange(false);
        }
    };

    const timezoneQuery = useQuery({
        queryKey: ["timezones"],
        queryFn: () => apiFetch("/api/timezones/"),
        staleTime: Infinity,
    });

    const commonTimezones =
        timezoneQuery.data?.filter((tz) =>
            tz.startsWith("Europe/") || tz === "UTC"
        ) || [];

    const [preferredLandingPage, setPreferredLandingPage] = useState(() => {
        return localStorage.getItem("sharegy_preferred_landing_page") || "";
    });

    const handleLandingPageChange = (val) => {
        setPreferredLandingPage(val);
        if (val) {
            localStorage.setItem("sharegy_preferred_landing_page", val);
        } else {
            localStorage.removeItem("sharegy_preferred_landing_page");
        }
        showSuccess(t("profile.landing_page_saved", "Startseite nach dem Login gespeichert!"));
    };

    const activeTimezone = selectedTimezone ?? settings?.timezone ?? "";

    async function handleLanguageChange(langId) {
        await i18n.changeLanguage(langId);
        localStorage.setItem("i18nextLng", langId);

        queryClient.setQueryData(["settings"], (old) => {
            if (!old) return old;
            return { ...old, language: langId };
        });

        try {
            await apiFetch("/api/language/", {
                method: "POST",
                body: JSON.stringify({ language: langId }),
            });
        } catch {
            // Ignore fallback
        }
        showSuccess(t("profile.lang_saved", "Sprache wurde erfolgreich geändert."));
    }

    async function saveTimezone() {
        setSavingTimezone(true);
        try {
            await apiFetch("/api/timezone/", {
                method: "POST",
                body: JSON.stringify({ timezone: activeTimezone }),
            });
            await queryClient.invalidateQueries({ queryKey: ["settings"] });
            showSuccess(t("profile.timezone_saved", "Zeitzone wurde erfolgreich gespeichert."));
        } catch {
            showError(t("profile.timezone_error", "Fehler beim Speichern der Zeitzone."));
        } finally {
            setSavingTimezone(false);
        }
    }

    // --- 3. GDPR / DATA EXPORT & DELETE ---
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
            showSuccess(t("gdpr.export_success", "Datenexport wurde erfolgreich heruntergeladen."));
        } catch (err) {
            console.error("Failed to export data:", err);
            showError(t("gdpr.export_failed", "Fehler beim Exportieren der Daten."));
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

    const displayName = user?.first_name
        ? `${user.first_name} ${user.last_name || ""}`.trim()
        : user?.email;

    const initials = user?.first_name
        ? `${user.first_name[0]}${user.last_name?.[0] || ""}`.toUpperCase()
        : user?.email?.slice(0, 2).toUpperCase();

    const currentAvatarConfig = getAvatarConfig(formData.avatar || user?.avatar || user?.profile?.avatar);

    // Clean Tabs Definition
    const tabs = [
        { id: "profile", label: t("profile.tab_personal", "Persönliche Daten"), icon: "👤", badge: null },
        { id: "company", label: t("profile.tab_company", "Firmendaten"), icon: "🏢", badge: formData.company_name?.trim() ? "Firma" : null },
        { id: "invoices", label: t("profile.tab_invoices", "Rechnungen & Belege"), icon: "📄", badge: invoices?.length > 0 ? invoices.length : null },
        { id: "notifications", label: t("profile.tab_notifications", "Benachrichtigungen"), icon: "🔔", badge: null },
        { id: "security", label: t("profile.tab_security", "Sicherheit & Sitzung"), icon: "🔐", badge: null },
        { id: "privacy", label: t("profile.tab_privacy", "Datenschutz & Export"), icon: "🛡️", badge: null },
    ];

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6">

            {/* SLIM PAGE HEADER */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                    <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-gray-900 dark:text-white flex items-center gap-2.5">
                        <span>👤</span>
                        <span>{t("profile.header_title", "Mein Benutzerkonto")}</span>
                    </h1>
                    <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {t("profile.header_desc", "Verwalte deine persönlichen Stammdaten, Firmendaten, Rechnungen und Benachrichtigungen.")}
                    </p>
                </div>

                <div className="flex items-center gap-2 self-start sm:self-auto">
                    <span className={`text-[11px] font-bold px-3 py-1 rounded-full border ${
                        isLandlord
                            ? "bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border-indigo-300 dark:border-indigo-800"
                            : isPro
                                ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800"
                                : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700"
                    }`}>
                        {isLandlord ? "🏢 Vermieter & Quartiere" : isPro ? "⚡ Sharegy Pro" : "🌱 Sharegy Free"}
                    </span>
                    {user?.is_staff && (
                        <span className="text-[10px] font-bold bg-amber-500/20 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-700 px-2.5 py-1 rounded-full">
                            Admin
                        </span>
                    )}
                </div>
            </div>

            {/* TOAST / ALERTS */}
            {savedMsg && (
                <div className="rounded-2xl border border-emerald-200 bg-emerald-50 dark:bg-emerald-950/40 dark:border-emerald-800 px-4 py-3 text-emerald-800 dark:text-emerald-300 text-sm font-semibold flex items-center gap-2 shadow-sm animate-in fade-in slide-in-from-top-2">
                    <span>✅</span> <span>{savedMsg}</span>
                </div>
            )}
            {errorMsg && (
                <div className="rounded-2xl border border-rose-200 bg-rose-50 dark:bg-rose-950/40 dark:border-rose-800 px-4 py-3 text-rose-800 dark:text-rose-300 text-sm font-semibold flex items-center gap-2 shadow-sm animate-in fade-in slide-in-from-top-2">
                    <span>⚠️</span> <span>{errorMsg}</span>
                </div>
            )}

            {/* ENTERPRISE TAB NAVIGATION (6 CLEAN TABS) */}
            <div className="flex overflow-x-auto no-scrollbar gap-1.5 p-1.5 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl">
                {tabs.map((tab) => {
                    const isActive = activeTab === tab.id;
                    return (
                        <button
                            key={tab.id}
                            type="button"
                            onClick={() => handleTabChange(tab.id)}
                            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
                                isActive
                                    ? "bg-white dark:bg-slate-800 text-indigo-700 dark:text-indigo-400 shadow-sm border border-slate-200/80 dark:border-slate-700"
                                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200/60 dark:hover:bg-slate-800/50"
                            }`}
                        >
                            <span>{tab.icon}</span>
                            <span>{tab.label}</span>
                            {tab.badge && (
                                <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${
                                    isActive
                                        ? "bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300"
                                        : "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                                }`}>
                                    {tab.badge}
                                </span>
                            )}
                        </button>
                    );
                })}
            </div>

            {/* ========================================================= */}
            {/* TAB 1: EINSTELLUNGEN DES BENUTZERKONTOS & PERSÖNLICHE ANGABEN */}
            {/* ========================================================= */}
            {activeTab === "profile" && (
                <div className="grid gap-6 md:grid-cols-2 animate-in fade-in duration-200 items-start">
                    {/* 1. SPALTE LINKS: EINSTELLUNGEN DES BENUTZERKONTOS (ACCOUNT, SPRACHE, ZEITZONE) */}
                    <Card>
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                <span>⚙️</span> {t("profile.account_settings_heading", "Einstellungen des Benutzerkontos")}
                            </h2>
                            <span className="text-xs text-gray-400">ID: #{user?.id || "–"}</span>
                        </div>

                        <div className="space-y-5">
                            {/* SECTION 1: KONTO & IDENTIFIKATION */}
                            <div>
                                <h3 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase flex items-center gap-1.5 mb-3">
                                    <span>🔑</span> {t("profile.account_settings_title", "Konto & Identifikation")}
                                </h3>

                                <div className="space-y-3">
                                    {/* EMAIL WITH CHANGE WORKFLOW */}
                                    <div>
                                        <div className="flex items-center justify-between mb-1">
                                            <label className="block text-[11px] font-bold text-gray-600 dark:text-gray-400 uppercase">
                                                {t("profile.email", "E-Mail-Adresse (Login)")}
                                            </label>
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setShowEmailModal(true);
                                                    setEmailChangeSuccess(false);
                                                    setNewEmailInput("");
                                                }}
                                                className="text-xs font-bold text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 cursor-pointer flex items-center gap-1"
                                            >
                                                <span>✏️</span>
                                                <span>{t("profile.change_email_btn", "E-Mail ändern")}</span>
                                            </button>
                                        </div>
                                        <div className="relative">
                                            <input
                                                type="email"
                                                disabled
                                                value={user?.email || ""}
                                                className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-slate-600 dark:text-slate-300 cursor-not-allowed font-medium pr-24"
                                            />
                                            <span className="absolute right-3 top-2.5 text-[11px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded-md border border-emerald-200 dark:border-emerald-800">
                                                ✓ Verifiziert
                                            </span>
                                        </div>
                                    </div>

                                    {/* AVATAR PREVIEW IN FORM */}
                                    <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200 dark:border-slate-700 flex items-center justify-between gap-3">
                                        <div className="flex items-center gap-3 min-w-0">
                                            <div
                                                className="relative group cursor-pointer shrink-0"
                                                onClick={() => setShowAvatarModal(true)}
                                                title="Avatar oder Initialen ändern"
                                            >
                                                {currentAvatarConfig ? (
                                                    <div className={`w-11 h-11 rounded-xl bg-gradient-to-tr ${currentAvatarConfig.bg} flex items-center justify-center text-2xl shadow-xs shrink-0 transition-transform group-hover:scale-105`}>
                                                        <span>{currentAvatarConfig.emoji}</span>
                                                    </div>
                                                ) : (
                                                    <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-indigo-500 to-cyan-500 flex items-center justify-center text-sm font-black text-white shadow-xs shrink-0 transition-transform group-hover:scale-105">
                                                        {initials}
                                                    </div>
                                                )}
                                                <div className="absolute inset-0 bg-black/40 rounded-xl opacity-0 group-hover:opacity-100 flex items-center justify-center text-[10px] font-bold text-white transition-opacity backdrop-blur-2xs">
                                                    ✏️ Ändern
                                                </div>
                                            </div>
                                            <div className="min-w-0">
                                                <div className="text-xs font-bold text-gray-900 dark:text-white truncate">
                                                    {currentAvatarConfig ? currentAvatarConfig.label : "Namensinitialen"}
                                                </div>
                                                <div className="text-[11px] text-gray-500 dark:text-gray-400 truncate">
                                                    {currentAvatarConfig ? "Ausgewähltes Profil-Avatar" : "Standard-Initialen (z. B. RK)"}
                                                </div>
                                            </div>
                                        </div>
                                        <button
                                            type="button"
                                            onClick={() => setShowAvatarModal(true)}
                                            className="px-3 py-1.5 bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 hover:bg-gray-100 dark:hover:bg-slate-600 rounded-xl text-xs font-bold text-gray-800 dark:text-gray-200 transition cursor-pointer shrink-0 shadow-2xs"
                                        >
                                            🎨 Avatar wählen
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* SECTION 2: SPRACHE & LOKALISIERUNG */}
                            <div className="border-t border-gray-100 dark:border-slate-800 pt-4">
                                <h3 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase flex items-center gap-1.5 mb-1.5">
                                    <span>🌐</span> {t("profile.language_title", "Sprache & Lokalisierung")}
                                </h3>
                                <p className="text-[11px] text-gray-500 dark:text-gray-400 mb-3">
                                    {t("profile.language_desc", "Wähle deine bevorzugte Sprache für Benutzeroberfläche, Berichte und E-Mails.")}
                                </p>

                                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                                    {[
                                        { id: "de", label: "Deutsch", sub: "Standard" },
                                        { id: "en", label: "English", sub: "International" },
                                        { id: "pl", label: "Polski", sub: "Regional" },
                                        { id: "tr", label: "Türkçe", sub: "Regional" },
                                        { id: "ru", label: "Русский", sub: "Regional" },
                                        { id: "ro", label: "Română", sub: "Regional" },
                                    ].map((lang) => {
                                        const isSelected = currentLang === lang.id;
                                        return (
                                            <button
                                                key={lang.id}
                                                type="button"
                                                onClick={() => handleLanguageChange(lang.id)}
                                                className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer flex items-center gap-2.5 ${
                                                    isSelected
                                                        ? "bg-indigo-50/80 dark:bg-indigo-950/60 border-indigo-500 text-indigo-900 dark:text-indigo-200 ring-2 ring-indigo-500/20 shadow-xs"
                                                        : "bg-white dark:bg-slate-800/80 border-gray-200 dark:border-slate-700 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-slate-600"
                                                }`}
                                            >
                                                <FlagIcon code={lang.id} className="w-6 h-6" />
                                                <div className="min-w-0">
                                                    <div className="font-bold text-xs truncate">{lang.label}</div>
                                                    <div className="text-[9px] text-gray-400 dark:text-gray-500 truncate">{lang.sub}</div>
                                                </div>
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* SECTION 3: ZEITZONE */}
                            <div className="border-t border-gray-100 dark:border-slate-800 pt-4">
                                <h3 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase flex items-center gap-1.5 mb-1.5">
                                    <span>🕒</span> {t("profile.timezone_title", "Zeitzone & Zeitformat")}
                                </h3>
                                <p className="text-[11px] text-gray-500 dark:text-gray-400 mb-3">
                                    {t("profile.timezone_desc", "Rechtssichere Zeitstempel für 15-Minuten Lastgänge und Energie-Abrechnungen.")}
                                </p>

                                <div className="flex items-center gap-2">
                                    <select
                                        value={activeTimezone}
                                        onChange={(e) => setSelectedTimezone(e.target.value)}
                                        className="flex-1 border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2 text-sm text-gray-900 dark:text-white font-medium focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                    >
                                        <option value="">{t("profile.timezone_default", "Standard (Europe/Berlin)")}</option>
                                        {commonTimezones.map((tz) => (
                                            <option key={tz} value={tz}>
                                                {tz}
                                            </option>
                                        ))}
                                    </select>
                                    <button
                                        type="button"
                                        onClick={saveTimezone}
                                        disabled={savingTimezone}
                                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-xs transition cursor-pointer flex items-center gap-1.5 shrink-0"
                                    >
                                        <span>💾</span>
                                        <span>{savingTimezone ? t("common.saving", "Speichere...") : t("profile.save_timezone", "Speichern")}</span>
                                    </button>
                                </div>
                            </div>

                            {/* SECTION 4: STARTSEITE NACH DEM LOGIN */}
                            <div className="border-t border-gray-100 dark:border-slate-800 pt-4">
                                <h3 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase flex items-center gap-1.5 mb-1.5">
                                    <span>🚀</span> {t("profile.landing_page_title", "Startseite nach dem Login")}
                                </h3>
                                <p className="text-[11px] text-gray-500 dark:text-gray-400 mb-3">
                                    {t("profile.landing_page_desc", "Wähle deinen bevorzugten Einstiegsbereich beim Öffnen der Plattform.")}
                                </p>

                                <div>
                                    <select
                                        value={preferredLandingPage}
                                        onChange={(e) => handleLandingPageChange(e.target.value)}
                                        className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-xs font-semibold text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none cursor-pointer"
                                    >
                                        <option value="">⚙️ Automatisch (Rollen-Standard: Dashboard / Community / Mieterportal)</option>
                                        <option value="/app">📊 Live-Cockpit & Gesamtübersicht</option>
                                        <option value="/app/community">⚡ Energy Sharing & Genossenschaft</option>
                                        <option value="/app/tenant">🏢 Mieter- & Quartiersportal</option>
                                        <option value="/app/analytics">📈 Analysen & Lastgang-Visualisierung</option>
                                        <option value="/app/tariffs">💰 Tarife & Dynamic Pricing</option>
                                        <option value="/app/devices">🔌 Smart Meter & Steuerung</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </Card>

                    {/* 2. SPALTE RECHTS: PERSÖNLICHE ANGABEN & RECHNUNGSADRESSE FORM */}
                    <Card>
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                <span>👤</span> {t("profile.personal_info", "Persönliche Angaben & Anschrift")}
                            </h2>
                        </div>

                        <form onSubmit={handleSaveProfile} className="space-y-5">
                            {/* SECTION 1: VORNAME & NACHNAME */}
                            <div>
                                <h3 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase flex items-center gap-1.5 mb-3">
                                    <span>👤</span> {t("profile.personal_name_title", "Persönliche Daten")}
                                </h3>

                                <div className="grid grid-cols-2 gap-3">
                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-600 dark:text-gray-400 uppercase mb-1">
                                            {t("profile.first_name", "Vorname")}
                                        </label>
                                        <input
                                            type="text"
                                            value={formData.first_name}
                                            onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                            placeholder="Max"
                                            className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-600 dark:text-gray-400 uppercase mb-1">
                                            {t("profile.last_name", "Nachname")}
                                        </label>
                                        <input
                                            type="text"
                                            value={formData.last_name}
                                            onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                            placeholder="Mustermann"
                                            className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* SECTION 2: WOHNORT & RECHNUNGSADRESSE */}
                            <div className="border-t border-gray-100 dark:border-slate-800 pt-4">
                                <div className="flex items-center justify-between mb-3">
                                    <h3 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase flex items-center gap-1.5">
                                        <span>📍</span> {t("profile.address_title", "Wohnort & Rechnungsadresse")}
                                    </h3>
                                    <span className="text-[11px] text-gray-400">Optional / für Belege</span>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                                    <div className="md:col-span-3">
                                        <label className="block text-[11px] font-bold text-gray-600 dark:text-gray-400 uppercase mb-1">
                                            {t("profile.street", "Straße")}
                                        </label>
                                        <input
                                            type="text"
                                            value={formData.street}
                                            onChange={(e) => setFormData({ ...formData, street: e.target.value })}
                                            placeholder="Sonnenallee"
                                            className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-600 dark:text-gray-400 uppercase mb-1">
                                            {t("profile.house_number", "Hausnr.")}
                                        </label>
                                        <input
                                            type="text"
                                            value={formData.house_number}
                                            onChange={(e) => setFormData({ ...formData, house_number: e.target.value })}
                                            placeholder="42a"
                                            className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-600 dark:text-gray-400 uppercase mb-1">
                                            {t("profile.postal_code", "PLZ")}
                                        </label>
                                        <input
                                            type="text"
                                            value={formData.postal_code}
                                            onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                                            placeholder="10115"
                                            className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                        />
                                    </div>
                                    <div className="md:col-span-2">
                                        <label className="block text-[11px] font-bold text-gray-600 dark:text-gray-400 uppercase mb-1">
                                            {t("profile.city", "Ort")}
                                        </label>
                                        <input
                                            type="text"
                                            value={formData.city}
                                            onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                                            placeholder="Berlin"
                                            className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-600 dark:text-gray-400 uppercase mb-1">
                                            {t("profile.country", "Land")}
                                        </label>
                                        <div className="w-full border border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-800/60 rounded-xl px-3 py-2 text-sm text-gray-800 dark:text-gray-200 font-medium flex items-center gap-2">
                                            <span>🇩🇪</span>
                                            <span>Deutschland</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* SECTION 3: TELEFON & NOTFALL-KONTAKT */}
                            <div className="border-t border-gray-100 dark:border-slate-800 pt-4">
                                <h3 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase flex items-center gap-1.5 mb-3">
                                    <span>📞</span> {t("profile.contact_title", "Erreichbarkeit & Kontakt")}
                                </h3>

                                <div>
                                    <label className="block text-[11px] font-bold text-gray-600 dark:text-gray-400 uppercase mb-1">
                                        {t("profile.phone", "Telefon / Notfall-Kontakt")}
                                    </label>
                                    <input
                                        type="tel"
                                        value={formData.phone}
                                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                        placeholder="+49 170 1234567"
                                        className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                    />
                                    <p className="text-[11px] text-gray-500 dark:text-gray-400 mt-1">
                                        Wird für kritische Notfall-Benachrichtigungen, SMS-Alarme und Vor-Ort-Rückfragen verwendet.
                                    </p>
                                </div>
                            </div>

                            <div className="flex justify-end pt-3">
                                <button
                                    type="submit"
                                    disabled={savingProfile}
                                    className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-md transition cursor-pointer flex items-center gap-2"
                                >
                                    <span>💾</span>
                                    <span>{savingProfile ? t("common.saving", "Speichere...") : t("profile.save_personal", "Angaben speichern")}</span>
                                </button>
                            </div>
                        </form>
                    </Card>
                </div>
            )}

            {/* ========================================================= */}
            {/* TAB 2: FIRMENDATEN (2-SPALTEN-LAYOUT) */}
            {/* ========================================================= */}
            {activeTab === "company" && (
                <form onSubmit={handleSaveProfile} className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start animate-in fade-in duration-200">
                    {/* LINKE SPALTE: UNTERNEHMENSDATEN & UST-IDNR */}
                    <Card>
                        <div className="border-b border-gray-100 dark:border-slate-800 pb-4 mb-4 space-y-1.5">
                            <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                <span>🏢</span> {t("profile.company_details_title", "Unternehmensdaten & USt-IdNr.")}
                            </h2>
                            <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                                {t("profile.company_details_desc", "Hinterlege deinen offiziellen Firmennamen und deine USt-IdNr. für Vorsteuerabzug und korrekte Rechnungsbelege.")}
                            </p>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase mb-1">
                                    {t("profile.company_name", "Offizieller Firmenname")}
                                </label>
                                <input
                                    type="text"
                                    value={formData.company_name}
                                    onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                                    placeholder="Muster Energie GmbH"
                                    className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase mb-1">
                                    {t("profile.vat_id", "Umsatzsteuer-Identifikationsnummer (USt-IdNr.)")}
                                </label>
                                <input
                                    type="text"
                                    value={formData.vat_id}
                                    onChange={(e) => setFormData({ ...formData, vat_id: e.target.value })}
                                    placeholder="DE123456789"
                                    className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm font-mono text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase mb-1">
                                    {t("profile.billing_name", "Rechnungsempfänger / Abteilungszusatz")}
                                </label>
                                <input
                                    type="text"
                                    value={formData.billing_name}
                                    onChange={(e) => setFormData({ ...formData, billing_name: e.target.value })}
                                    placeholder="z.B. Buchhaltung / Kostenstelle 4020 / WEG Sonnenweg 12"
                                    className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                />
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-1">
                                    <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase">
                                        {t("profile.billing_email", "Rechnungs-E-Mail (Abweichend)")}
                                    </label>
                                    <span className="text-[10px] text-gray-400">Optional</span>
                                </div>
                                <input
                                    type="email"
                                    value={formData.billing_email}
                                    onChange={(e) => setFormData({ ...formData, billing_email: e.target.value })}
                                    placeholder="buchhaltung@firma.de"
                                    className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                />
                                <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-1">
                                    {t("profile.billing_email_hint", "Rechnungen & Belege werden an dieses Postfach gesendet. Wenn leer, wird deine Login-E-Mail genutzt.")}
                                </p>
                            </div>
                        </div>
                    </Card>

                    {/* RECHTE SPALTE: FIRMEN- & RECHNUNGSANSCHRIFT */}
                    <Card>
                        <div className="border-b border-gray-100 dark:border-slate-800 pb-4 mb-4 space-y-1.5">
                            <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                <span>📍</span> {t("profile.company_address_title", "Firmen- & Rechnungsanschrift")}
                            </h2>
                            <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                                {t("profile.company_address_desc", "Offizielle Anschrift des Unternehmens für die Belegausstellung.")}
                            </p>
                        </div>

                        <div className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                                <div className="md:col-span-3">
                                    <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase mb-1">
                                        {t("profile.street", "Straße")}
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.street}
                                        onChange={(e) => setFormData({ ...formData, street: e.target.value })}
                                        placeholder="Sonnenallee"
                                        className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase mb-1">
                                        {t("profile.house_number", "Hausnummer")}
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.house_number}
                                        onChange={(e) => setFormData({ ...formData, house_number: e.target.value })}
                                        placeholder="42a"
                                        className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase mb-1">
                                        {t("profile.postal_code", "Postleitzahl")}
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.postal_code}
                                        onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                                        placeholder="10115"
                                        className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                    />
                                </div>

                                <div className="md:col-span-2">
                                    <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase mb-1">
                                        {t("profile.city", "Stadt / Ort")}
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.city}
                                        onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                                        placeholder="Berlin"
                                        className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase mb-1">
                                        {t("profile.country", "Land")}
                                    </label>
                                    <div className="w-full border border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-800/60 rounded-xl px-3.5 py-2.5 text-sm text-gray-800 dark:text-gray-200 font-medium flex items-center gap-2">
                                        <span>🇩🇪</span>
                                        <span>Deutschland</span>
                                    </div>
                                </div>
                            </div>

                            <div className="flex justify-end pt-4 border-t border-gray-100 dark:border-slate-800">
                                <button
                                    type="submit"
                                    disabled={savingProfile}
                                    className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-md transition cursor-pointer flex items-center gap-2"
                                >
                                    <span>🏢</span>
                                    <span>{savingProfile ? t("common.saving", "Speichere...") : t("profile.save_company", "Firmendaten speichern")}</span>
                                </button>
                            </div>
                        </div>
                    </Card>
                </form>
            )}

            {/* ========================================================= */}
            {/* TAB 3: RECHNUNGEN & BELEGE (POSITION 3) */}
            {/* ========================================================= */}
            {activeTab === "invoices" && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start animate-in fade-in duration-200">
                    {/* LINKE SPALTE: AKTUELLER TARIF & ZAHLUNGSSTATUS */}
                    <Card>
                        <div className="border-b border-gray-100 dark:border-slate-800 pb-4 space-y-1.5">
                            <div className="flex items-center justify-between gap-3">
                                <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                    <span>💳</span> {t("billing.plan_details_title", "Tarif & Abrechnungsstatus")}
                                </h2>
                                <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${
                                    isLandlord
                                        ? "bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border-indigo-300 dark:border-indigo-800"
                                        : isPro
                                            ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800"
                                            : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700"
                                }`}>
                                    {isLandlord ? "🏢 Vermieter" : isPro ? "⚡ Pro" : "🌱 Free"}
                                </span>
                            </div>
                            <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                                {t("billing.plan_details_desc", "Übersicht zu deinem gebuchten Sharegy EMS-Tarif, Zahlungszyklus und Rechnungsdaten.")}
                            </p>
                        </div>

                        <div className="space-y-4 pt-4">
                            {/* Tarif-Detail Box */}
                            <div className="p-4.5 rounded-2xl bg-gradient-to-br from-indigo-50/70 via-slate-50 to-white dark:from-slate-800/90 dark:via-slate-800/60 dark:to-slate-850 border border-indigo-100 dark:border-indigo-900/40 space-y-3 shadow-xs">
                                <div className="flex items-center justify-between">
                                    <div className="text-xs font-bold uppercase text-indigo-700 dark:text-indigo-400">
                                        {t("billing.active_plan", "Aktiver Tarif")}
                                    </div>
                                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                                        🟢 {t("billing.active", "Aktiv")}
                                    </span>
                                </div>
                                <div className="text-xl font-black text-gray-900 dark:text-white">
                                    {planName}
                                </div>
                                <div className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
                                    {isLandlord
                                        ? t("billing.landlord_features", "Umfasst Mieterstrom-Unterverteilung, PDF-Monatsabrechnungen und Mehrparteien-EMS.")
                                        : isPro
                                            ? t("billing.pro_features", "Umfasst unbegrenzte Historie, Multi-Sensor-Prognosen, Börsenstrom-Optimierung und Push-Alarme.")
                                            : t("billing.free_features", "Kostenlose Basisfunktionen mit 7-Tage-Historie und lokaler EMS-Steuerung.")}
                                </div>

                                <div className="pt-2 border-t border-indigo-100/70 dark:border-slate-700/60 flex flex-wrap items-center gap-3">
                                    <Link
                                        to="/app/billing"
                                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl shadow-md transition flex items-center gap-1.5"
                                    >
                                        <span>⚙️</span>
                                        <span>{isPro || isLandlord ? t("billing.manage_plan", "Abonnement verwalten & Tarife") : t("billing.upgrade_pro", "Auf Pro upgraden")}</span>
                                    </Link>
                                </div>
                            </div>

                            {/* Hinterlegte Rechnungsadresse & Empfängertyp Kurzübersicht */}
                            {(() => {
                                const isBusinessCustomer = Boolean(formData.company_name?.trim() || formData.vat_id?.trim());
                                const hasAddress = Boolean(formData.street?.trim() || formData.city?.trim());
                                const personalName = `${formData.first_name || ""} ${formData.last_name || ""}`.trim();

                                return (
                                    <div className="p-4.5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/80 space-y-3 text-xs">
                                        <div className="flex flex-wrap items-center justify-between gap-2">
                                            <div className="font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                                                <span>📍</span>
                                                <span>{t("billing.invoice_recipient", "Rechnungsempfänger")}</span>
                                            </div>
                                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${
                                                isBusinessCustomer
                                                    ? "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800"
                                                    : "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800"
                                            }`}>
                                                {isBusinessCustomer ? "🏢 Geschäftskunde (B2B)" : "👤 Privatkunde (B2C)"}
                                            </span>
                                        </div>

                                        <div className="p-3 bg-white dark:bg-slate-800/80 rounded-xl border border-gray-200/70 dark:border-slate-700/70 space-y-1.5 text-[11px] leading-relaxed">
                                            {isBusinessCustomer ? (
                                                <>
                                                    <div className="font-bold text-sm text-gray-900 dark:text-white">
                                                        {formData.company_name}
                                                    </div>
                                                    {(formData.billing_name || personalName) && (
                                                        <div className="text-gray-600 dark:text-gray-300">
                                                            z. Hd.: <span className="font-medium">{formData.billing_name || personalName}</span>
                                                        </div>
                                                    )}
                                                    {formData.vat_id && (
                                                        <div className="text-gray-600 dark:text-gray-400 font-mono text-[10px]">
                                                            USt-IdNr.: {formData.vat_id}
                                                        </div>
                                                    )}
                                                </>
                                            ) : (
                                                <>
                                                    <div className="font-bold text-sm text-gray-900 dark:text-white">
                                                        {personalName || user?.email}
                                                    </div>
                                                </>
                                            )}

                                            {hasAddress ? (
                                                <div className="text-gray-600 dark:text-gray-300 pt-0.5">
                                                    {formData.street} {formData.house_number}, {formData.postal_code} {formData.city} ({formData.country || "DE"})
                                                </div>
                                            ) : (
                                                <div className="text-amber-600 dark:text-amber-400 font-medium pt-0.5 flex items-center gap-1">
                                                    <span>⚠️</span>
                                                    <span>Keine postalische Rechnungsadresse hinterlegt</span>
                                                </div>
                                            )}

                                            <div className="text-gray-500 dark:text-gray-400 pt-1 border-t border-gray-100 dark:border-slate-700/50">
                                                📧 Belegversand an: <span className="font-semibold text-gray-700 dark:text-gray-200">{formData.billing_email || user?.email}</span>
                                            </div>
                                        </div>

                                        {/* Kontextbezogene Aktionen / Links */}
                                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-1">
                                            {isBusinessCustomer ? (
                                                <>
                                                    <button
                                                        type="button"
                                                        onClick={() => handleTabChange("company")}
                                                        className="text-[11px] text-indigo-600 dark:text-indigo-400 hover:underline font-bold cursor-pointer flex items-center gap-1"
                                                    >
                                                        <span>🏢</span>
                                                        <span>Firmendaten & Rechnungsadresse anpassen ➔</span>
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => handleTabChange("profile")}
                                                        className="text-[10px] text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:underline cursor-pointer"
                                                    >
                                                        Privatadresse ansehen
                                                    </button>
                                                </>
                                            ) : (
                                                <>
                                                    <button
                                                        type="button"
                                                        onClick={() => handleTabChange("profile")}
                                                        className="text-[11px] text-indigo-600 dark:text-indigo-400 hover:underline font-bold cursor-pointer flex items-center gap-1"
                                                    >
                                                        <span>👤</span>
                                                        <span>Persönliche Rechnungsanschrift anpassen ➔</span>
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => handleTabChange("company")}
                                                        className="text-[10px] text-indigo-500 dark:text-indigo-400 hover:underline font-medium cursor-pointer"
                                                    >
                                                        🏢 Auf Firmenrechnung (B2B) umstellen ➔
                                                    </button>
                                                </>
                                            )}
                                        </div>
                                    </div>
                                );
                            })()}

                            {/* Rechtliche Hinweise & Vorsteuerabzug */}
                            <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-700/60 text-[11px] text-gray-500 dark:text-gray-400 leading-relaxed space-y-1">
                                <div className="font-bold text-gray-700 dark:text-gray-300 flex items-center gap-1.5">
                                    <span>⚖️</span>
                                    <span>Steuer- & Belegkonformität</span>
                                </div>
                                <p>
                                    Alle Rechnungen enthalten ordnungsgemäß ausgewiesene 19 % MwSt. und erfüllen die gesetzlichen Vorgaben für den geschäftlichen Vorsteuerabzug.
                                </p>
                            </div>
                        </div>
                    </Card>

                    {/* RECHTE SPALTE: RECHNUNGSARCHIV & PDF-DOWNLOADS */}
                    <InvoicesListCard invoices={invoices} onRefresh={refetchSubscription} />
                </div>
            )}

            {/* ========================================================= */}
            {/* TAB 3: BENACHRICHTIGUNGEN & ALARME */}
            {/* ========================================================= */}
            {activeTab === "notifications" && (
                <div className="animate-in fade-in duration-200">
                    <PushNotificationSettings
                        emailSlot={
                            <div className="space-y-2.5 text-xs">
                                <label className="flex items-start gap-3 p-3.5 rounded-xl border border-gray-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/40 cursor-pointer hover:bg-slate-100/70 dark:hover:bg-slate-800/70 transition">
                                    <input
                                        type="checkbox"
                                        checked={notifyWeekly}
                                        onChange={(e) => handleToggleNotification("notify_weekly_report", e.target.checked)}
                                        disabled={isSavingNotification}
                                        className="mt-0.5 rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                                    />
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between">
                                            <span className="font-bold text-gray-900 dark:text-white">{t("profile.notify_weekly", "Wöchentlicher Energie- & Autarkie-Report")}</span>
                                            {notifyWeekly && (
                                                <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-200 dark:border-emerald-800">
                                                    Aktiv (Mo 08:00)
                                                </span>
                                            )}
                                        </div>
                                        <div className="text-gray-500 dark:text-gray-400 text-[11px] mt-0.5">{t("profile.notify_weekly_sub", "Jeden Montag um 08:00 Uhr: PV-Erzeugung, Eigenverbrauch, Netzeinspeisung und Ersparnis in deiner Sprache.")}</div>
                                    </div>
                                </label>

                                <label className="flex items-start gap-3 p-3.5 rounded-xl border border-gray-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/40 cursor-pointer hover:bg-slate-100/70 dark:hover:bg-slate-800/70 transition">
                                    <input
                                        type="checkbox"
                                        checked={notifyCritical}
                                        onChange={(e) => handleToggleNotification("notify_critical_alerts", e.target.checked)}
                                        disabled={isSavingNotification}
                                        className="mt-0.5 rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                                    />
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between">
                                            <span className="font-bold text-gray-900 dark:text-white">{t("profile.notify_critical", "Kritische Hardware-Warnungen (Sofort)")}</span>
                                            {notifyCritical && (
                                                <span className="text-[10px] font-bold text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/60 px-2 py-0.5 rounded border border-rose-200 dark:border-rose-800">
                                                    Aktiv (Echtzeit)
                                                </span>
                                            )}
                                        </div>
                                        <div className="text-gray-500 dark:text-gray-400 text-[11px] mt-0.5">{t("profile.notify_critical_sub", "Sofortige E-Mail bei Wechselrichter-Offline, Batterie-Tiefentladung oder Kommunikationsausfall.")}</div>
                                    </div>
                                </label>
                            </div>
                        }
                    />
                </div>
            )}

            {/* ========================================================= */}
            {/* TAB 4: SICHERHEIT & PASSWORT */}
            {/* ========================================================= */}
            {activeTab === "security" && (
                <div className="grid gap-6 md:grid-cols-2 animate-in fade-in duration-200">
                    <Card>
                        <h2 className="text-base font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                            <span>🔐</span> {t("profile.security_title", "Sicherheit & Anmeldung")}
                        </h2>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
                            {t("profile.security_desc", "Verwalte deine Authentifizierungsmethode und Sitzungssicherheit.")}
                        </p>

                        <div className="space-y-4 text-xs">
                            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
                                <div className="font-bold text-gray-900 dark:text-white text-sm mb-1.5">
                                    {t("profile.magic_link_title", "Passwortlose Authentifizierung (Magic Link)")}
                                </div>
                                <p className="text-gray-500 dark:text-gray-400 text-[11px] leading-relaxed mb-3">
                                    {t("profile.magic_link_desc", "Du meldest dich sicher über kryptografisch signierte Einmal-Links per E-Mail an. Es ist kein klassisches Passwort erforderlich. Bei Sicherheitsbedenken kannst du alle offenen Links sofort entwerten und dich automatisch abmelden.")}
                                </p>
                                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pt-1 border-t border-slate-200/60 dark:border-slate-700/60">
                                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2.5 py-1 rounded-lg border border-emerald-200 dark:border-emerald-800 self-start sm:self-center">
                                        ✓ {t("profile.magic_link_active", "Magic Link Aktiv")}
                                    </span>
                                    <button
                                        type="button"
                                        onClick={() => setShowRevokeModal(true)}
                                        className="px-3 py-1.5 bg-rose-50 hover:bg-rose-100 dark:bg-rose-950/60 dark:hover:bg-rose-900/80 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800 rounded-xl text-xs font-bold transition cursor-pointer flex items-center justify-center gap-1.5 self-start sm:self-center shrink-0 shadow-2xs"
                                    >
                                        <span>🚨</span>
                                        <span>{t("profile.revoke_links_btn", "Alle Links löschen & abmelden")}</span>
                                    </button>
                                </div>
                            </div>

                            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <div className="font-bold text-gray-900 dark:text-white">Zwei-Faktor-Authentifizierung (2FA / TOTP)</div>
                                        <p className="text-gray-500 dark:text-gray-400 text-[11px]">Zusätzlicher Schutz über Authenticator-Apps.</p>
                                    </div>
                                    <span className="text-[10px] font-bold uppercase tracking-wider bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-300 px-2 py-0.5 rounded border border-amber-200 dark:border-amber-800">
                                        Demnächst
                                    </span>
                                </div>
                            </div>
                        </div>
                    </Card>

                    <Card>
                        <h2 className="text-base font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                            <span>💻</span> {t("profile.active_session", "Aktive Sitzung & Geräte")}
                        </h2>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
                            {t("profile.active_session_desc", "Informationen über deinen aktuellen Browser und die letzte Anmeldung.")}
                        </p>

                        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs space-y-2">
                            <div className="flex items-center justify-between">
                                <span className="text-gray-500">Angemeldeter Account:</span>
                                <span className="font-bold text-gray-800 dark:text-gray-200">{user?.email}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-gray-500">Browser / User-Agent:</span>
                                <span className="font-mono text-[10px] text-gray-700 dark:text-gray-300 truncate max-w-[200px]">
                                    {navigator.userAgent.slice(0, 35)}...
                                </span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-gray-500">Spracheinstellung:</span>
                                <span className="font-bold uppercase text-indigo-600">{currentLang}</span>
                            </div>
                        </div>
                    </Card>
                </div>
            )}

            {/* ========================================================= */}
            {/* TAB 6: DATENSCHUTZ & EXPORT (2-SPALTEN-LAYOUT) */}
            {/* ========================================================= */}
            {activeTab === "privacy" && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start animate-in fade-in duration-200">
                    {/* LINKE SPALTE: DATENEXPORT & TRANSPARENZ */}
                    <Card>
                        <div className="border-b border-gray-100 dark:border-slate-800 pb-4 mb-4 space-y-1.5">
                            <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                <span>📦</span> {t("gdpr.export_title", "Personenbezogener Datenexport (Art. 15 & 20 DSGVO)")}
                            </h2>
                            <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                                {t("gdpr.export_desc", "Transparenz über alle gespeicherten Datenkategorien und DSGVO-Auskunft als maschinenlesbare JSON-Datei.")}
                            </p>
                        </div>

                        {/* STORED DATA CATEGORIES */}
                        <div className="space-y-3">
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-xs space-y-1">
                                    <div className="font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                                        <span>👤</span>
                                        <span>{t("gdpr.cat_profile", "Benutzer- & Stammdaten")}</span>
                                    </div>
                                    <p className="text-gray-600 dark:text-gray-400 text-[11px] leading-relaxed">
                                        E-Mail (<code className="font-mono text-indigo-600 dark:text-indigo-400">{user?.email}</code>), Name, Sprache & Zeitzone.
                                    </p>
                                </div>

                                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-xs space-y-1">
                                    <div className="font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                                        <span>⚡</span>
                                        <span>{t("gdpr.cat_energy", "Energie & Telemetrie")}</span>
                                    </div>
                                    <p className="text-gray-600 dark:text-gray-400 text-[11px] leading-relaxed">
                                        Zähler, Wechselrichter, Speicher-SoC, OBIS-Messwerte und EMS-Aktorik.
                                    </p>
                                </div>

                                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-xs space-y-1">
                                    <div className="font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                                        <span>🏢</span>
                                        <span>{t("gdpr.cat_b2b", "Firmendaten & Belege")}</span>
                                    </div>
                                    <p className="text-gray-600 dark:text-gray-400 text-[11px] leading-relaxed">
                                        Firmenname, USt-IdNr., Mieterstrom-Clearing und Rechnungsnachbereitung.
                                    </p>
                                </div>

                                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-xs space-y-1">
                                    <div className="font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                                        <span>💳</span>
                                        <span>{t("gdpr.cat_billing", "Abrechnung & Stripe")}</span>
                                    </div>
                                    <p className="text-gray-600 dark:text-gray-400 text-[11px] leading-relaxed">
                                        Aktiver Tarif ({planName}), Rechnungs-PDFs und Kundennummern.
                                    </p>
                                </div>
                            </div>

                            <div className="pt-3 border-t border-gray-100 dark:border-slate-800 flex justify-end">
                                <button
                                    type="button"
                                    onClick={handleExportData}
                                    disabled={exporting}
                                    className="px-5 py-2.5 rounded-xl border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-200 text-xs font-bold shadow-xs hover:bg-gray-50 dark:hover:bg-slate-700 transition cursor-pointer flex items-center gap-2"
                                >
                                    <span>📥</span>
                                    <span>{exporting ? t("gdpr.exporting", "Exportiere...") : t("gdpr.export_button", "Daten exportieren (JSON)")}</span>
                                </button>
                            </div>
                        </div>
                    </Card>

                    {/* RECHTE SPALTE: BENUTZERKONTO LÖSCHEN */}
                    <Card>
                        <div className="border-b border-gray-100 dark:border-slate-800 pb-4 mb-4 space-y-1.5">
                            <h2 className="text-base font-bold text-rose-700 dark:text-rose-400 flex items-center gap-2">
                                <span>⚠️</span> {t("gdpr.delete_title", "Benutzerkonto löschen (Art. 17 DSGVO)")}
                            </h2>
                            <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                                {t("gdpr.delete_desc", "Recht auf Vergessenwerden und endgültige Kontoschließung.")}
                            </p>
                        </div>

                        <div className="p-4 rounded-2xl bg-rose-50/70 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/60 space-y-3 text-xs">
                            <div className="font-bold text-rose-900 dark:text-rose-200">
                                Unwiderrufliche Löschung aller Daten
                            </div>
                            <p className="text-rose-800/90 dark:text-rose-300/90 leading-relaxed text-[11px]">
                                Durch das Löschen deines Kontos werden alle deine Anmeldedaten, Geräteverknüpfungen, historischen Energiedaten und Benachrichtigungseinstellungen dauerhaft aus dem System entfernt.
                            </p>
                            <p className="text-[10px] text-rose-700/70 dark:text-rose-400/70">
                                Gesetzliche Aufbewahrungsfristen für bereits ausgestellte Rechnungsbelege (§ 147 AO) bleiben hiervon unberührt.
                            </p>

                            <div className="pt-2">
                                <button
                                    type="button"
                                    onClick={() => setShowDeleteModal(true)}
                                    className="w-full py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold shadow-md transition cursor-pointer flex items-center justify-center gap-2"
                                >
                                    <span>⚠️</span>
                                    <span>{t("gdpr.delete_button", "Konto unwiderruflich löschen")}</span>
                                </button>
                            </div>
                        </div>
                    </Card>
                </div>
            )}

            {/* ========================================================= */}
            {/* AVATAR PICKER MODAL */}
            {/* ========================================================= */}
            {showAvatarModal && (
                <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-150">
                    <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-gray-200 dark:border-slate-800 w-full max-w-xl overflow-hidden flex flex-col">
                        <div className="p-6 bg-slate-50 dark:bg-slate-800/80 border-b border-gray-100 dark:border-slate-800 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <span className="text-2xl p-2 bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 rounded-2xl">🎨</span>
                                <div>
                                    <h3 className="text-base font-bold text-gray-900 dark:text-white">
                                        Profil-Avatar auswählen
                                    </h3>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                        Wähle deinen persönlichen Avatar für TopNav, Menü und Dashboard.
                                    </p>
                                </div>
                            </div>
                            <button
                                type="button"
                                onClick={() => setShowAvatarModal(false)}
                                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-1.5 rounded-xl hover:bg-gray-100 dark:hover:bg-slate-800 transition cursor-pointer"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="p-6 space-y-5 max-h-[70vh] overflow-y-auto">
                            {/* RESET TO INITIALS OPTION */}
                            <button
                                type="button"
                                onClick={() => handleSelectAvatar("")}
                                className={`w-full p-3.5 rounded-2xl border text-left transition-all cursor-pointer flex items-center justify-between ${
                                    !formData.avatar
                                        ? "bg-indigo-50 dark:bg-indigo-950/60 border-indigo-500 text-indigo-900 dark:text-indigo-200 ring-2 ring-indigo-500/20"
                                        : "bg-white dark:bg-slate-800 border-gray-200 dark:border-slate-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700/50"
                                }`}
                            >
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-cyan-500 text-white font-black text-sm flex items-center justify-center shadow-xs">
                                        {initials}
                                    </div>
                                    <div>
                                        <div className="font-bold text-xs">Standard-Initialen verwenden ({initials})</div>
                                        <div className="text-[11px] text-gray-400">Klassischer Buchstaben-Avatar basierend auf Vor- und Nachname</div>
                                    </div>
                                </div>
                                {!formData.avatar && (
                                    <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">✓ Aktiv</span>
                                )}
                            </button>

                            {/* AVATAR GRID */}
                            <div>
                                <div className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-3">
                                    ⚡ Energie- & Smart-Home-Avatare
                                </div>
                                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                                    {AVATAR_PRESETS.map((av) => {
                                        const isSelected = formData.avatar === av.id;
                                        return (
                                            <button
                                                key={av.id}
                                                type="button"
                                                onClick={() => handleSelectAvatar(av.id)}
                                                className={`p-3 rounded-2xl border text-left transition-all cursor-pointer flex items-center gap-3 group ${
                                                    isSelected
                                                        ? "bg-indigo-50/80 dark:bg-indigo-950/60 border-indigo-500 text-indigo-900 dark:text-indigo-200 ring-2 ring-indigo-500/20 shadow-xs"
                                                        : "bg-white dark:bg-slate-800 border-gray-200 dark:border-slate-700 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                                                }`}
                                            >
                                                <div className={`w-11 h-11 rounded-xl bg-gradient-to-tr ${av.bg} flex items-center justify-center text-2xl shadow-xs shrink-0 transition-transform group-hover:scale-110`}>
                                                    <span>{av.emoji}</span>
                                                </div>
                                                <div className="min-w-0">
                                                    <div className="font-bold text-xs truncate">{av.label}</div>
                                                    <div className="text-[10px] text-gray-400 truncate">
                                                        {isSelected ? "✓ Gewählt" : "Wählen"}
                                                    </div>
                                                </div>
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                        </div>

                        <div className="p-4 bg-slate-50 dark:bg-slate-800/60 border-t border-gray-100 dark:border-slate-800 flex items-center justify-end">
                            <button
                                type="button"
                                onClick={() => setShowAvatarModal(false)}
                                className="px-5 py-2 rounded-xl text-xs font-semibold text-gray-700 dark:text-gray-300 bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 hover:bg-gray-100 transition cursor-pointer"
                            >
                                Schließen
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* CHANGE EMAIL MODAL */}
            {showEmailModal && (
                <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-150">
                    <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-gray-200 dark:border-slate-800 w-full max-w-md overflow-hidden flex flex-col">
                        <div className="p-6 bg-slate-50 dark:bg-slate-800/80 border-b border-gray-100 dark:border-slate-800 flex items-center gap-3">
                            <span className="text-2xl p-2 bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 rounded-2xl">✉️</span>
                            <div>
                                <h3 className="text-base font-bold text-gray-900 dark:text-white">
                                    E-Mail-Adresse ändern
                                </h3>
                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                    Sicherheitsbestätigung via E-Mail-Link
                                </p>
                            </div>
                        </div>

                        {emailChangeSuccess ? (
                            <div className="p-6 space-y-4 text-center">
                                <div className="w-12 h-12 bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 rounded-2xl flex items-center justify-center text-2xl mx-auto border border-emerald-200 dark:border-emerald-800">
                                    ✅
                                </div>
                                <h4 className="font-bold text-gray-900 dark:text-white text-sm">Bestätigungslink gesendet!</h4>
                                <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
                                    Wir haben eine Verifizierungs-E-Mail an <strong className="font-mono text-indigo-600 dark:text-indigo-400">{newEmailInput}</strong> gesendet. Bitte klicke auf den Link in der E-Mail (gültig für 30 Minuten), um die Änderung abzuschließen.
                                </p>
                                <div className="pt-2">
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setShowEmailModal(false);
                                            setEmailChangeSuccess(false);
                                            setNewEmailInput("");
                                        }}
                                        className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition shadow-xs cursor-pointer"
                                    >
                                        Verstanden & Schließen
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <form onSubmit={handleRequestEmailChange}>
                                <div className="p-6 space-y-4 text-xs sm:text-sm text-gray-700 dark:text-gray-300">
                                    <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                                        Aus Sicherheitsgründen senden wir einen Bestätigungslink an deine neue Adresse. Deine aktuelle Adresse bleibt aktiv, bis du den Link bestätigt hast.
                                    </p>

                                    <div className="space-y-1.5">
                                        <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase">
                                            Neue E-Mail-Adresse
                                        </label>
                                        <input
                                            type="email"
                                            required
                                            value={newEmailInput}
                                            onChange={(e) => setNewEmailInput(e.target.value)}
                                            placeholder="neue.adresse@beispiel.de"
                                            className="w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm font-medium focus:ring-2 focus:ring-indigo-500 focus:outline-none text-gray-900 dark:text-white"
                                        />
                                    </div>
                                </div>

                                <div className="p-4 bg-slate-50 dark:bg-slate-800/60 border-t border-gray-100 dark:border-slate-800 flex items-center justify-end gap-3">
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setShowEmailModal(false);
                                            setNewEmailInput("");
                                        }}
                                        className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 dark:text-gray-300 bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 hover:bg-gray-100 transition cursor-pointer"
                                    >
                                        Abbrechen
                                    </button>

                                    <button
                                        type="submit"
                                        disabled={requestingEmailChange || !newEmailInput.trim()}
                                        className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-bold shadow-xs transition cursor-pointer flex items-center gap-1.5"
                                    >
                                        <span>✉️</span>
                                        <span>{requestingEmailChange ? "Sende Link..." : "Bestätigungslink senden"}</span>
                                    </button>
                                </div>
                            </form>
                        )}
                    </div>
                </div>
            )}

            {/* REVOKE MAGIC LINKS & LOGOUT MODAL */}
            {showRevokeModal && (
                <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-150">
                    <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-rose-200 dark:border-rose-900 w-full max-w-lg overflow-hidden flex flex-col">
                        <div className="p-6 bg-rose-50 dark:bg-rose-950/50 border-b border-rose-100 dark:border-rose-900 flex items-center gap-3">
                            <span className="text-3xl p-2 bg-rose-100 dark:bg-rose-900/40 text-rose-600 rounded-2xl">🚨</span>
                            <div>
                                <h3 className="text-base font-bold text-rose-950 dark:text-rose-200">
                                    {t("profile.revoke_modal_title", "Alle Magic-Links löschen & Sitzung beenden?")}
                                </h3>
                                <p className="text-xs text-rose-700 dark:text-rose-400">
                                    {t("profile.revoke_modal_sub", "Sicherheitsaktion zur sofortigen Entwertung offener Login-Links")}
                                </p>
                            </div>
                        </div>

                        <div className="p-6 space-y-3.5 text-xs sm:text-sm text-gray-700 dark:text-gray-300">
                            <p className="leading-relaxed">
                                {t(
                                    "profile.revoke_modal_text",
                                    "Möchtest du wirklich alle für deinen Account ausgestellten Magic-Links unwiderruflich entwerten?"
                                )}
                            </p>

                            <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 space-y-2 text-xs">
                                <div className="flex items-start gap-2 text-rose-700 dark:text-rose-400 font-semibold">
                                    <span>•</span>
                                    <span>{t("profile.revoke_point_1", "Alle bisher per E-Mail versendeten Zugangslinks werden sofort ungültig.")}</span>
                                </div>
                                <div className="flex items-start gap-2 text-amber-700 dark:text-amber-400 font-semibold">
                                    <span>•</span>
                                    <span>{t("profile.revoke_point_2", "Deine aktive Sitzung wird zum Schutz deines Accounts sofort beendet (Auto-Logout).")}</span>
                                </div>
                                <div className="flex items-start gap-2 text-slate-600 dark:text-slate-400">
                                    <span>•</span>
                                    <span>{t("profile.revoke_point_3", "Du kannst jederzeit auf der Login-Seite einen neuen, frischen Magic-Link anfordern.")}</span>
                                </div>
                            </div>
                        </div>

                        <div className="p-4 bg-slate-50 dark:bg-slate-800/60 border-t border-gray-100 dark:border-slate-800 flex items-center justify-end gap-3">
                            <button
                                type="button"
                                onClick={() => setShowRevokeModal(false)}
                                disabled={revokingLinks}
                                className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 dark:text-gray-300 bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 hover:bg-gray-100 transition cursor-pointer"
                            >
                                {t("common.cancel", "Abbrechen")}
                            </button>

                            <button
                                type="button"
                                onClick={handleRevokeMagicLinks}
                                disabled={revokingLinks}
                                className="px-5 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 disabled:opacity-50 text-white text-xs font-bold shadow-xs transition cursor-pointer flex items-center gap-1.5"
                            >
                                <span>🚨</span>
                                <span>{revokingLinks ? t("profile.revoking", "Lösche & melde ab...") : t("profile.confirm_revoke", "Jetzt löschen & abmelden")}</span>
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* DELETE ACCOUNT CONFIRMATION MODAL */}
            {showDeleteModal && (
                <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-150">
                    <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-rose-200 dark:border-rose-900 w-full max-w-lg overflow-hidden flex flex-col">
                        <div className="p-6 bg-rose-50 dark:bg-rose-950/50 border-b border-rose-100 dark:border-rose-900 flex items-center gap-3">
                            <span className="text-3xl p-2 bg-rose-100 dark:bg-rose-900/40 text-rose-600 rounded-2xl">⚠️</span>
                            <div>
                                <h3 className="text-base font-bold text-rose-950 dark:text-rose-200">
                                    {t("gdpr.modal_delete_title", "Konto & Daten unwiderruflich löschen?")}
                                </h3>
                                <p className="text-xs text-rose-700 dark:text-rose-400">
                                    {t("gdpr.modal_delete_warning", "Diese Aktion kann nicht rückgängig gemacht werden!")}
                                </p>
                            </div>
                        </div>

                        <div className="p-6 space-y-4 text-xs sm:text-sm text-gray-700 dark:text-gray-300">
                            <p>
                                {t(
                                    "gdpr.modal_delete_text",
                                    "Wenn du fortfährst, werden dein Benutzerkonto, alle konfigurierten Zähler, Wechselrichter, historische Diagramme und Benachrichtigungen sofort gelöscht."
                                )}
                            </p>

                            <div className="bg-slate-50 dark:bg-slate-800 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 text-xs text-gray-600 dark:text-gray-400">
                                {t("gdpr.modal_delete_prompt", "Zur Bestätigung gib bitte deine E-Mail-Adresse")} (<strong>{user?.email}</strong>) {t("gdpr.modal_delete_or", "oder")} <strong>LÖSCHEN</strong> {t("gdpr.modal_delete_in_field", "ein:")}
                            </div>

                            <input
                                type="text"
                                value={deleteConfirmation}
                                onChange={(e) => setDeleteConfirmation(e.target.value)}
                                placeholder={user?.email || "LÖSCHEN"}
                                className="w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm font-medium focus:ring-2 focus:ring-rose-500 focus:outline-none text-gray-900 dark:text-white"
                            />

                            {deleteError && (
                                <p className="text-xs font-bold text-rose-600 bg-rose-50 dark:bg-rose-950/40 p-2.5 rounded-xl border border-rose-200 dark:border-rose-900">
                                    {deleteError}
                                </p>
                            )}
                        </div>

                        <div className="p-4 bg-slate-50 dark:bg-slate-800/60 border-t border-gray-100 dark:border-slate-800 flex items-center justify-end gap-3">
                            <button
                                type="button"
                                onClick={() => {
                                    setShowDeleteModal(false);
                                    setDeleteConfirmation("");
                                    setDeleteError(null);
                                }}
                                className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 dark:text-gray-300 bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 hover:bg-gray-100 transition cursor-pointer"
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
                                {deleting ? t("gdpr.deleting", "Lösche...") : t("gdpr.confirm_delete", "Endgültig löschen")}
                            </button>
                        </div>
                    </div>
                </div>
            )}

        </div>
    );
}
