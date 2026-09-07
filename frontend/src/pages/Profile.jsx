/*
# src/pages/Profile.jsx
*/

import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import Card from "../components/ui/Card";
import PushNotificationSettings from "../features/alerts/components/PushNotificationSettings";
import { apiFetch } from "../api/client";
import { useSettings } from "../hooks/useSettings";
import { useUser } from "../hooks/useUser";
import { useSubscription } from "../hooks/useSubscription";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import i18n from "../i18n";
import { AVATAR_PRESETS, getAvatarConfig } from "../utils/avatars";

export default function Profile() {
    const { user } = useUser();
    const queryClient = useQueryClient();
    const { settings } = useSettings();
    const { t } = useTranslation();
    const { isPro, isLandlord, planName } = useSubscription();
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

    // 5 Clean Tabs Definition (API tab removed)
    const tabs = [
        { id: "profile", label: t("profile.tab_personal", "Persönliche Angaben"), icon: "👤", badge: null },
        { id: "company", label: t("profile.tab_company", "Unternehmensdaten & B2B"), icon: "🏢", badge: formData.company_name?.trim() ? "B2B" : null },
        { id: "notifications", label: t("profile.tab_notifications", "Benachrichtigungen"), icon: "🔔", badge: null },
        { id: "security", label: t("profile.tab_security", "Sicherheit & Sitzung"), icon: "🔐", badge: null },
        { id: "privacy", label: t("profile.tab_privacy", "Datenschutz & DSGVO"), icon: "🛡️", badge: null },
    ];

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6">

            {/* ENTERPRISE USER HERO HEADER */}
            <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-3xl p-6 text-white shadow-xl border border-slate-800/80 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
                <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div className="flex items-center gap-4">
                        {/* AVATAR HERO CONTAINER WITH QUICK-EDIT BUTTON */}
                        <div className="relative group cursor-pointer" onClick={() => setShowAvatarModal(true)}>
                            {currentAvatarConfig ? (
                                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-tr ${currentAvatarConfig.bg} text-white font-black text-3xl flex items-center justify-center shadow-lg ring-4 ring-white/10 shrink-0 transition-transform group-hover:scale-105`}>
                                    <span>{currentAvatarConfig.emoji}</span>
                                </div>
                            ) : (
                                <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-500 to-cyan-400 text-white font-black text-2xl flex items-center justify-center shadow-lg ring-4 ring-white/10 shrink-0 transition-transform group-hover:scale-105">
                                    {initials}
                                </div>
                            )}
                            <div className="absolute inset-0 bg-black/40 rounded-2xl opacity-0 group-hover:opacity-100 flex items-center justify-center text-xs font-bold text-white transition-opacity backdrop-blur-2xs">
                                ✏️ Ändern
                            </div>
                        </div>

                        <div>
                            <div className="flex flex-wrap items-center gap-2 mb-1">
                                <h1 className="text-2xl font-bold tracking-tight text-white">
                                    {displayName}
                                </h1>
                                <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${
                                    isLandlord
                                        ? "bg-indigo-500/20 text-indigo-300 border-indigo-400/40"
                                        : isPro
                                            ? "bg-emerald-500/20 text-emerald-300 border-emerald-400/40"
                                            : "bg-slate-700/50 text-slate-300 border-slate-600"
                                }`}>
                                    {isLandlord ? "🏢 Vermieter & Quartiere" : isPro ? "⚡ Sharegy Pro" : "🌱 Sharegy Free"}
                                </span>
                                {user?.is_staff && (
                                    <span className="text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-400/40 px-2 py-0.5 rounded-full">
                                        Admin
                                    </span>
                                )}
                            </div>
                            <p className="text-xs text-slate-400 flex items-center gap-2">
                                <span>📧 {user?.email}</span>
                                <span className="inline-flex items-center gap-1 text-emerald-400 font-medium">
                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                                    {t("profile.verified_email", "Verifiziert")}
                                </span>
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            type="button"
                            onClick={() => setShowAvatarModal(true)}
                            className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold transition border border-white/10 flex items-center gap-2 backdrop-blur-xs shadow-xs cursor-pointer"
                        >
                            <span>🎨</span>
                            <span>{t("profile.choose_avatar", "Avatar wählen")}</span>
                        </button>
                        <Link
                            to="/app/billing"
                            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition shadow-md flex items-center gap-2"
                        >
                            <span>💳</span>
                            <span>{t("profile.manage_subscription", "Abonnement verwalten")}</span>
                        </Link>
                    </div>
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

            {/* ENTERPRISE TAB NAVIGATION (5 CLEAN TABS) */}
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
                                <span className="text-[10px] px-1.5 py-0.2 rounded-md bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-mono">
                                    {tab.badge}
                                </span>
                            )}
                        </button>
                    );
                })}
            </div>

            {/* ========================================================= */}
            {/* TAB 1: PERSÖNLICHE ANGABEN & AVATAR */}
            {/* ========================================================= */}
            {activeTab === "profile" && (
                <div className="grid gap-6 md:grid-cols-2 animate-in fade-in duration-200">
                    {/* PERSONAL INFORMATION FORM */}
                    <Card>
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                <span>👤</span> {t("profile.personal_info", "Persönliche Angaben & Kontakt")}
                            </h2>
                            <span className="text-xs text-gray-400">ID: #{user?.id || "–"}</span>
                        </div>

                        <form onSubmit={handleSaveProfile} className="space-y-4">
                            {/* AVATAR PREVIEW IN FORM */}
                            <div className="p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200 dark:border-slate-700 flex items-center justify-between gap-3">
                                <div className="flex items-center gap-3 min-w-0">
                                    {currentAvatarConfig ? (
                                        <div className={`w-12 h-12 rounded-xl bg-gradient-to-tr ${currentAvatarConfig.bg} flex items-center justify-center text-2xl shadow-xs shrink-0`}>
                                            <span>{currentAvatarConfig.emoji}</span>
                                        </div>
                                    ) : (
                                        <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-indigo-500 to-cyan-500 flex items-center justify-center text-base font-black text-white shadow-xs shrink-0">
                                            {initials}
                                        </div>
                                    )}
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
                                    className="px-3.5 py-1.5 bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 hover:bg-gray-100 dark:hover:bg-slate-600 rounded-xl text-xs font-bold text-gray-800 dark:text-gray-200 transition cursor-pointer shrink-0 shadow-2xs"
                                >
                                    🎨 Ändern
                                </button>
                            </div>

                            {/* EMAIL WITH CHANGE WORKFLOW */}
                            <div>
                                <div className="flex items-center justify-between mb-1">
                                    <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase">
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

                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase mb-1">
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
                                    <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase mb-1">
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

                            <div>
                                <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase mb-1">
                                    {t("profile.phone", "Telefon / Notfall-Kontakt")}
                                </label>
                                <input
                                    type="tel"
                                    value={formData.phone}
                                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                    placeholder="+49 170 1234567"
                                    className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                />
                            </div>

                            {/* WOHNANSCHRIFT / ADRESSE */}
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
                                        <select
                                            value={formData.country || "DE"}
                                            onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                                            className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3 py-2 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                        >
                                            <option value="DE">🇩🇪 DE</option>
                                            <option value="AT">🇦🇹 AT</option>
                                            <option value="CH">🇨🇭 CH</option>
                                            <option value="PL">🇵🇱 PL</option>
                                            <option value="NL">🇳🇱 NL</option>
                                            <option value="FR">🇫🇷 FR</option>
                                        </select>
                                    </div>
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

                    {/* REGIONAL PREFERENCES (LANGUAGE & TIMEZONE) */}
                    <div className="space-y-6">
                        <Card>
                            <h2 className="text-base font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                                <span>🌐</span> {t("profile.language_title", "Sprache & Lokalisierung")}
                            </h2>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
                                {t("profile.language_desc", "Wähle deine bevorzugte Sprache für Benutzeroberfläche, Berichte und E-Mails.")}
                            </p>

                            <div className="grid grid-cols-3 gap-2.5">
                                {[
                                    { id: "de", label: "Deutsch", flag: "🇩🇪", sub: "Standard" },
                                    { id: "en", label: "English", flag: "🇬🇧", sub: "Global" },
                                    { id: "pl", label: "Polski", flag: "🇵🇱", sub: "Regional" },
                                    { id: "fr", label: "Français", flag: "🇫🇷", sub: "BETA" },
                                    { id: "nl", label: "Nederlands", flag: "🇳🇱", sub: "BETA" },
                                    { id: "es", label: "Español", flag: "🇪🇸", sub: "BETA" },
                                ].map((lang) => {
                                    const isSelected = currentLang === lang.id;
                                    return (
                                        <button
                                            key={lang.id}
                                            type="button"
                                            onClick={() => handleLanguageChange(lang.id)}
                                            className={`p-3 rounded-2xl border text-left transition-all cursor-pointer flex items-center gap-2.5 ${
                                                isSelected
                                                    ? "bg-indigo-50/80 dark:bg-indigo-950/60 border-indigo-500 text-indigo-900 dark:text-indigo-200 ring-2 ring-indigo-500/20 shadow-xs"
                                                    : "bg-white dark:bg-slate-800/80 border-gray-200 dark:border-slate-700 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-slate-600"
                                            }`}
                                        >
                                            <span className="text-2xl shrink-0">{lang.flag}</span>
                                            <div className="min-w-0">
                                                <div className="font-bold text-xs truncate">{lang.label}</div>
                                                <div className="text-[10px] text-gray-400 dark:text-gray-500 truncate">{lang.sub}</div>
                                            </div>
                                        </button>
                                    );
                                })}
                            </div>
                        </Card>

                        <Card>
                            <h2 className="text-base font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                                <span>🕒</span> {t("profile.timezone_title", "Zeitzone")}
                            </h2>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
                                {t("profile.timezone_desc", "Rechtssichere Zeitstempel für 15-Minuten Lastgänge und Energie-Abrechnungen.")}
                            </p>

                            <div className="space-y-4">
                                <select
                                    value={activeTimezone}
                                    onChange={(e) => setSelectedTimezone(e.target.value)}
                                    className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-gray-900 dark:text-white font-medium focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                >
                                    <option value="">{t("profile.timezone_default", "Standard (Europe/Berlin)")}</option>
                                    {commonTimezones.map((tz) => (
                                        <option key={tz} value={tz}>
                                            {tz}
                                        </option>
                                    ))}
                                </select>

                                <div className="flex justify-end">
                                    <button
                                        type="button"
                                        onClick={saveTimezone}
                                        disabled={savingTimezone}
                                        className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-xs transition cursor-pointer flex items-center gap-1.5"
                                    >
                                        <span>💾</span>
                                        <span>{savingTimezone ? t("common.saving", "Speichere...") : t("profile.save_timezone", "Zeitzone speichern")}</span>
                                    </button>
                                </div>
                            </div>
                        </Card>
                    </div>
                </div>
            )}

            {/* ========================================================= */}
            {/* TAB 2: UNTERNEHMEN & B2B FIRMENDATEN */}
            {/* ========================================================= */}
            {activeTab === "company" && (
                <div className="space-y-6 animate-in fade-in duration-200">
                    <Card>
                        <div className="border-b border-gray-100 dark:border-slate-800 pb-4 mb-5">
                            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 text-xs font-bold mb-1.5">
                                <span>🏢</span>
                                <span>{t("profile.b2b_badge", "Gewerbe & B2B")}</span>
                            </div>
                            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                                {t("profile.company_details_title", "Unternehmensdaten & USt-IdNr.")}
                            </h2>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                                {t("profile.company_details_desc", "Optional für Firmenkunden: Hinterlege deinen offiziellen Firmennamen und deine USt-IdNr. für Vorsteuerabzug und korrekte B2B-Rechnungsbelege.")}
                            </p>
                        </div>

                        <form onSubmit={handleSaveProfile} className="space-y-5">
                            {/* FIRMENDATEN FELDER */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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

                            {/* RECHNUNGS- / FIRMENADRESSE */}
                            <div className="border-t border-gray-100 dark:border-slate-800 pt-5">
                                <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                                    <span>📍</span> {t("profile.company_address_title", "Firmen- & Rechnungsanschrift")}
                                </h3>

                                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
                                        <select
                                            value={formData.country || "DE"}
                                            onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                                            className="w-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-gray-900 dark:text-white font-medium focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                        >
                                            <option value="DE">🇩🇪 Deutschland</option>
                                            <option value="AT">🇦🇹 Österreich</option>
                                            <option value="CH">🇨🇭 Schweiz</option>
                                            <option value="PL">🇵🇱 Polen</option>
                                            <option value="NL">🇳🇱 Niederlande</option>
                                            <option value="FR">🇫🇷 Frankreich</option>
                                        </select>
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
                        </form>
                    </Card>
                </div>
            )}

            {/* ========================================================= */}
            {/* TAB 3: BENACHRICHTIGUNGEN & ALARME */}
            {/* ========================================================= */}
            {activeTab === "notifications" && (
                <div className="space-y-6 animate-in fade-in duration-200">
                    <PushNotificationSettings />

                    <Card>
                        <h2 className="text-base font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                            <span>📧</span> {t("profile.email_notifications", "E-Mail-Zusammenfassungen & Systemberichte")}
                        </h2>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
                            {t("profile.email_notifications_desc", "Erhalte automatisierte Wochenberichte und monatliche Mieterstrom-Abrechnungs-Bilanzen direkt per E-Mail.")}
                        </p>

                        <div className="space-y-3 text-xs">
                            <label className="flex items-start gap-3 p-3.5 rounded-xl border border-gray-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/40 cursor-pointer">
                                <input type="checkbox" defaultChecked className="mt-0.5 rounded text-indigo-600 focus:ring-indigo-500" />
                                <div>
                                    <div className="font-bold text-gray-900 dark:text-white">{t("profile.notify_weekly", "Wöchentlicher Energie- & Autarkie-Report")}</div>
                                    <div className="text-gray-500 dark:text-gray-400 text-[11px]">{t("profile.notify_weekly_sub", "Jeden Montag um 08:00 Uhr: PV-Erzeugung, Eigenverbrauch, Netzeinspeisung und Ersparnis.")}</div>
                                </div>
                            </label>

                            <label className="flex items-start gap-3 p-3.5 rounded-xl border border-gray-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/40 cursor-pointer">
                                <input type="checkbox" defaultChecked className="mt-0.5 rounded text-indigo-600 focus:ring-indigo-500" />
                                <div>
                                    <div className="font-bold text-gray-900 dark:text-white">{t("profile.notify_critical", "Kritische Hardware-Warnungen (Sofort)")}</div>
                                    <div className="text-gray-500 dark:text-gray-400 text-[11px]">{t("profile.notify_critical_sub", "Sofortige E-Mail bei Wechselrichter-Offline, Batterie-Tiefentladung oder Kommunikationsausfall.")}</div>
                                </div>
                            </label>
                        </div>
                    </Card>
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
                                <div className="font-bold text-gray-900 dark:text-white mb-1">Passwortlose Authentifizierung (Magic Link)</div>
                                <p className="text-gray-500 dark:text-gray-400 mb-3 text-[11px]">
                                    Du meldest dich sicher über kryptografisch signierte Einmal-Links per E-Mail an. Es ist kein klassisches Passwort erforderlich.
                                </p>
                                <span className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 px-2.5 py-1 rounded-md border border-indigo-200 dark:border-indigo-800">
                                    ✓ Magic Link Aktiv
                                </span>
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
            {/* TAB 5: DATENSCHUTZ, COMPLIANCE & DSGVO */}
            {/* ========================================================= */}
            {activeTab === "privacy" && (
                <div className="space-y-6 animate-in fade-in duration-200">
                    <Card>
                        <div className="border-b border-gray-100 dark:border-slate-800 pb-4 mb-5">
                            <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 text-xs font-bold mb-2">
                                <span>🛡️</span>
                                <span>{t("gdpr.badge", "Datenschutz & Betroffenenrechte (DSGVO)")}</span>
                            </div>
                            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                                {t("gdpr.title", "Deine Daten & Privatsphäre")}
                            </h2>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                {t("gdpr.subtitle", "Transparenz über alle gespeicherten Datenkategorien, Datenexport und Kontolöschung gem. Art. 15, 17 und 20 DSGVO.")}
                            </p>
                        </div>

                        {/* STORED DATA CATEGORIES */}
                        <div className="space-y-3 mb-6">
                            <h3 className="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                <span>📋</span>
                                <span>{t("gdpr.stored_data_title", "Übersicht gespeicherter Datenkategorien (Art. 15 DSGVO)")}</span>
                            </h3>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-xs space-y-1.5">
                                    <div className="font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                                        <span>👤</span>
                                        <span>{t("gdpr.cat_profile", "Benutzer- & Stammdaten")}</span>
                                    </div>
                                    <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                                        E-Mail-Adresse (<code className="font-mono text-indigo-600 dark:text-indigo-400">{user?.email}</code>), Name, hinterlegte Sprache & Zeitzone.
                                    </p>
                                    <span className="inline-block text-[10px] text-gray-400 font-semibold">Rechtsgrundlage: Art. 6 (1) lit. b DSGVO</span>
                                </div>

                                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-xs space-y-1.5">
                                    <div className="font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                                        <span>⚡</span>
                                        <span>{t("gdpr.cat_energy", "Energie- & Telemetriedaten")}</span>
                                    </div>
                                    <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                                        Verknüpfte Zähler, Wechselrichter, Speicher-SoC, OBIS-Messzeitreihen (1.8.0/2.8.0) und WSS-Aktorik.
                                    </p>
                                    <span className="inline-block text-[10px] text-gray-400 font-semibold">Rechtsgrundlage: Art. 6 (1) lit. b DSGVO</span>
                                </div>

                                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-xs space-y-1.5">
                                    <div className="font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                                        <span>🏢</span>
                                        <span>{t("gdpr.cat_b2b", "B2B & Vermieter-Daten")}</span>
                                    </div>
                                    <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                                        Firmenname, USt-IdNr., Mieterstrom-Clearing-Protokolle und steuerliche Nachweisbelege.
                                    </p>
                                    <span className="inline-block text-[10px] text-gray-400 font-semibold">Rechtsgrundlage: Art. 6 (1) lit. c DSGVO (§ 147 AO)</span>
                                </div>

                                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-xs space-y-1.5">
                                    <div className="font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                                        <span>💳</span>
                                        <span>{t("gdpr.cat_billing", "Abrechnung & Stripe")}</span>
                                    </div>
                                    <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                                        Aktiver Tarif ({planName}), Rechnungs-PDFs und Stripe Customer Identifikatoren.
                                    </p>
                                    <span className="inline-block text-[10px] text-gray-400 font-semibold">Rechtsgrundlage: Art. 6 (1) lit. b & c DSGVO</span>
                                </div>
                            </div>
                        </div>

                        {/* DATA EXPORT */}
                        <div className="border-t border-gray-100 dark:border-slate-800 pt-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                            <div>
                                <h3 className="text-sm font-bold text-gray-900 dark:text-white">
                                    {t("gdpr.export_title", "Datenübertragbarkeit (Art. 20 DSGVO)")}
                                </h3>
                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                    {t("gdpr.export_desc", "Lade alle über dich gespeicherten Daten in einem maschinenlesbaren JSON-Format herunter.")}
                                </p>
                            </div>

                            <button
                                type="button"
                                onClick={handleExportData}
                                disabled={exporting}
                                className="px-4 py-2.5 rounded-xl border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-200 text-xs font-bold shadow-xs hover:bg-gray-50 dark:hover:bg-slate-700 transition cursor-pointer flex items-center gap-2 shrink-0"
                            >
                                <span>📥</span>
                                <span>{exporting ? t("gdpr.exporting", "Exportiere...") : t("gdpr.export_button", "Daten exportieren (JSON)")}</span>
                            </button>
                        </div>

                        {/* DANGER ZONE: ACCOUNT DELETION */}
                        <div className="border-t border-rose-100 dark:border-rose-950 bg-rose-50/50 dark:bg-rose-950/20 -mx-6 -mb-6 p-6 mt-6 rounded-b-3xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                            <div>
                                <h3 className="text-sm font-bold text-rose-900 dark:text-rose-300 flex items-center gap-1.5">
                                    <span>⚠️</span>
                                    <span>{t("gdpr.delete_title", "Konto & alle Daten löschen (Art. 17 DSGVO)")}</span>
                                </h3>
                                <p className="text-xs text-rose-700/80 dark:text-rose-400/80 mt-0.5">
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
