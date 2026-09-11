import { useState, useEffect } from "react";
import { apiFetch } from "../../../api/client";
import { useTranslation } from "react-i18next";
import DeviceSelfTestModal from "./DeviceSelfTestModal";

export default function CloudInverterIntegrationCard({
    primaryHome,
    filterVendor = null,
    sectionNumber = 3,
    cardTitle = null,
}) {
    const { t } = useTranslation();

    // Available manifest profiles
    const [profiles, setProfiles] = useState([]);
    const [activeIntegrations, setActiveIntegrations] = useState([]);
    const [isLoadingIntegrations, setIsLoadingIntegrations] = useState(false);

    // Form / Editing State
    const [editingIntegrationId, setEditingIntegrationId] = useState(null);
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [selectedProfileId, setSelectedProfileId] = useState(filterVendor === "sungrow" ? "sungrow_isolarcloud" : null);
    const [credentials, setCredentials] = useState({});
    const [deviceName, setDeviceName] = useState("");
    const [pollingInterval, setPollingInterval] = useState(60);

    // Operation States
    const [isTesting, setIsTesting] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [pollingId, setPollingId] = useState(null);
    const [testResult, setTestResult] = useState(null);
    const [saveSuccess, setSaveSuccess] = useState(null);
    const [errorMsg, setErrorMsg] = useState(null);
    const [selfTestOpen, setSelfTestOpen] = useState(false);
    const [showFieldValues, setShowFieldValues] = useState({});

    const toggleFieldVisibility = (key) => {
        setShowFieldValues((prev) => ({ ...prev, [key]: !prev[key] }));
    };

    useEffect(() => {
        loadProfiles();
        loadActiveIntegrations();
    }, [filterVendor, primaryHome?.id]);

    async function loadProfiles() {
        try {
            const data = await apiFetch("/api/devices/cloud-profiles/");
            if (data?.profiles) {
                let list = data.profiles;
                if (filterVendor === "sungrow") {
                    list = list.filter((p) => p.vendor?.toLowerCase() === "sungrow" || p.id === "sungrow_isolarcloud");
                    setSelectedProfileId("sungrow_isolarcloud");
                } else if (filterVendor === "others") {
                    list = list.filter((p) => p.vendor?.toLowerCase() !== "sungrow" && p.id !== "sungrow_isolarcloud");
                    setSelectedProfileId(null);
                }
                setProfiles(list);
            }
        } catch (err) {
            console.warn("Could not load cloud profiles:", err);
        }
    }

    const isSungrowIntegration = (item) => {
        if (!item) return false;
        const pId = (item.profile_id || "").toLowerCase();
        const vendor = (item.vendor || "").toLowerCase();
        const name = (item.device_name || item.profile_name || "").toLowerCase();
        return pId.includes("sungrow") || vendor.includes("sungrow") || name.includes("sungrow") || pId === "sungrow_isolarcloud";
    };

    async function loadActiveIntegrations() {
        if (!primaryHome?.id) return;
        setIsLoadingIntegrations(true);
        try {
            const data = await apiFetch(`/api/devices/cloud-integrations/?home_id=${primaryHome.id}`);
            if (data?.integrations) {
                let list = data.integrations;
                if (filterVendor === "sungrow") {
                    list = list.filter((item) => isSungrowIntegration(item));
                } else if (filterVendor === "others") {
                    list = list.filter((item) => !isSungrowIntegration(item));
                }
                setActiveIntegrations(list);
            }
        } catch (err) {
            console.warn("Could not load user cloud integrations:", err);
        } finally {
            setIsLoadingIntegrations(false);
        }
    }

    const currentProfile = profiles.find((p) => p.id === selectedProfileId) || null;

    function handleFieldChange(key, value) {
        setCredentials((prev) => ({ ...prev, [key]: value }));
        setTestResult(null);
        setErrorMsg(null);
    }

    function handleStartAdd() {
        if (filterVendor === "sungrow") return;
        setEditingIntegrationId(null);
        setDeviceName("");
        setCredentials({});
        setPollingInterval(60);
        setSelectedProfileId(null);
        setTestResult(null);
        setSaveSuccess(null);
        setErrorMsg(null);
        setIsFormOpen(true);
    }

    function handleStartEdit(integration) {
        if (isSungrowIntegration(integration) || filterVendor === "sungrow") return;
        setEditingIntegrationId(integration.id);
        setDeviceName(integration.device_name || "");
        setSelectedProfileId(integration.profile_id);
        setCredentials(integration.credentials || {});
        setPollingInterval(integration.polling_interval_seconds || 60);
        setTestResult(null);
        setSaveSuccess(null);
        setErrorMsg(null);
        setIsFormOpen(true);
    }

    function handleCancelForm() {
        setEditingIntegrationId(null);
        setIsFormOpen(false);
        setTestResult(null);
        setSaveSuccess(null);
        setErrorMsg(null);
    }

    async function handleTestConnection() {
        setIsTesting(true);
        setTestResult(null);
        setErrorMsg(null);
        try {
            const data = await apiFetch("/api/devices/cloud-profiles/test/", {
                method: "POST",
                body: JSON.stringify({
                    profile_id: selectedProfileId,
                    credentials: credentials,
                }),
            });
            setTestResult(data);
        } catch (err) {
            setErrorMsg(err.message || t("cloud_inverter.error_test_failed", "Verbindungstest fehlgeschlagen."));
        } finally {
            setIsTesting(false);
        }
    }

    async function handleSungrowOAuth() {
        const directSungrowUrl = `https://web3.isolarcloud.eu/#/authorized-app?cloudId=3&applicationId=4830&redirectUrl=${encodeURIComponent("https://sharegy.de/api/v1/integrations/sungrow/callback")}`;
        try {
            const data = await apiFetch(`/api/devices/sungrow/auth-url/?home_id=${primaryHome?.id || ""}`);
            if (data?.auth_url) {
                window.location.href = data.auth_url;
                return;
            }
        } catch (err) {
            console.warn("API URL fetch failed, using direct Sungrow OAuth redirect:", err);
        }
        window.location.href = directSungrowUrl;
    }

    async function handleIntegrateOrUpdate() {
        setIsSaving(true);
        setSaveSuccess(null);
        setErrorMsg(null);
        try {
            const payload = {
                integration_id: editingIntegrationId,
                home_id: primaryHome?.id,
                name: deviceName,
                profile_id: selectedProfileId,
                credentials: credentials,
                polling_interval: pollingInterval,
            };
            const data = await apiFetch("/api/devices/cloud-profiles/integrate/", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            setSaveSuccess(data);
            await loadActiveIntegrations();
            setTimeout(() => {
                setIsFormOpen(false);
                setEditingIntegrationId(null);
            }, 1200);
        } catch (err) {
            setErrorMsg(err.message || t("cloud_inverter.error_integration_failed", "Kopplung fehlgeschlagen."));
        } finally {
            setIsSaving(false);
        }
    }

    async function handlePollNow(integration) {
        setPollingId(integration.id);
        setErrorMsg(null);
        try {
            await apiFetch(`/api/devices/${integration.device_id}/cloud/poll-now/`, {
                method: "POST",
            });
            await loadActiveIntegrations();
        } catch (err) {
            setErrorMsg(err.message || t("cloud_inverter.error_poll_failed", "Sofort-Abfrage fehlgeschlagen."));
        } finally {
            setPollingId(null);
        }
    }

    async function handleDeleteIntegration(integration) {
        const confirmMsg = t("cloud_inverter.disconnect_confirm", {
            name: integration.device_name,
            defaultValue: `Möchtest du die Verbindung zu '${integration.device_name}' wirklich trennen?`,
        });
        if (!window.confirm(confirmMsg)) return;

        try {
            await apiFetch(`/api/devices/cloud-integrations/${integration.id}/`, {
                method: "DELETE",
            });
            await loadActiveIntegrations();
            if (editingIntegrationId === integration.id) {
                handleCancelForm();
            }
        } catch (err) {
            setErrorMsg(err.message || t("cloud_inverter.error_delete_failed", "Fehler beim Trennen der Verbindung."));
        }
    }

    const formatRelativeTime = (isoString) => {
        if (!isoString) return t("cloud_inverter.never_polled", "Noch nie synchronisiert");
        try {
            const date = new Date(isoString);
            const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
            if (seconds < 60) return t("cloud_inverter.time_seconds_ago", { seconds, defaultValue: `vor ${seconds}s` });
            const minutes = Math.floor(seconds / 60);
            if (minutes < 60) return t("cloud_inverter.time_minutes_ago", { minutes, defaultValue: `vor ${minutes} Min.` });
            const hours = Math.floor(minutes / 60);
            return t("cloud_inverter.time_hours_ago", { hours, defaultValue: `vor ${hours} Std.` });
        } catch {
            return isoString;
        }
    };

    return (
        <div className="bg-white border border-blue-200/80 rounded-2xl shadow-xs overflow-hidden ring-1 ring-blue-100">
            {/* Header */}
            <div className={`p-5 bg-gradient-to-r ${filterVendor === "sungrow" ? "from-orange-50/90 via-amber-50/40" : "from-blue-50/80 via-indigo-50/30"} to-white border-b ${filterVendor === "sungrow" ? "border-orange-200/80" : "border-blue-200/80"} flex flex-wrap items-center justify-between gap-3`}>
                <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl ${filterVendor === "sungrow" ? "bg-amber-600" : "bg-blue-600"} text-white flex items-center justify-center text-xl shadow-xs`}>
                        {filterVendor === "sungrow" ? "☀️" : "☁️"}
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h2 className="text-base font-bold text-gray-900">
                                {cardTitle || `${sectionNumber}. ${t("cloud_inverter.default_card_title", "Hersteller Cloud-Kopplung (Sungrow, SolarEdge, Fronius)")}`}
                            </h2>
                            <span className={`text-[10px] font-bold px-2 py-0.5 ${filterVendor === "sungrow" ? "bg-amber-100 text-amber-900 border border-amber-200" : "bg-blue-100 text-blue-800 border border-blue-200"} rounded-full`}>
                                {filterVendor === "sungrow" ? "Zero-Hardware Direct" : t("cloud_inverter.badge_cloud_openapi", "Cloud & OpenAPI")}
                            </span>
                        </div>
                        <p className="text-xs text-gray-500">
                            {filterVendor === "sungrow"
                                ? t("cloud_inverter.sungrow_desc", "Direkte 1-Klick Schnittstelle für alle Sungrow Hybrid-Wechselrichter (SH-Serie) und SBR-Speicher.")
                                : t("cloud_inverter.others_desc", "Server-zu-Server Anbindung für SolarEdge, Fronius, Kostal, Growatt und weitere Wechselrichter.")}
                        </p>
                    </div>
                </div>

                {/* Top Action Button */}
                {filterVendor === "sungrow" ? (
                    activeIntegrations.length > 0 && (
                        <button
                            type="button"
                            onClick={handleSungrowOAuth}
                            className="px-3.5 py-1.5 bg-white hover:bg-amber-50 text-amber-900 border border-amber-300 text-xs font-bold rounded-xl shadow-2xs transition flex items-center gap-1.5 cursor-pointer"
                        >
                            <span>🔑</span>
                            <span>{t("cloud_inverter.sungrow_reauth_btn", "iSolarCloud Autorisierung erneuern")}</span>
                        </button>
                    )
                ) : (
                    !isFormOpen && (
                        <button
                            type="button"
                            onClick={handleStartAdd}
                            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-2xs transition flex items-center gap-1.5 cursor-pointer"
                        >
                            <span>+</span>
                            <span>{t("cloud_inverter.add_inverter_btn", "Wechselrichter koppeln")}</span>
                        </button>
                    )
                )}
            </div>

            <div className="p-6 space-y-6">
                {/* 1. SUNGROW STATUS BANNER (WENN BEREITS AUTORISIERT) */}
                {filterVendor === "sungrow" && activeIntegrations.length > 0 && (
                    <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-50 via-teal-50/40 to-white border border-emerald-200 flex flex-wrap items-center justify-between gap-3 text-xs">
                        <div className="flex items-center gap-3">
                            <span className="w-8 h-8 rounded-lg bg-emerald-500 text-white flex items-center justify-center text-base shadow-2xs">✓</span>
                            <div>
                                <div className="font-bold text-emerald-950 flex items-center gap-2">
                                    <span>{t("cloud_inverter.sungrow_api_active", "Sungrow iSolarCloud API ist autorisiert & aktiv")}</span>
                                    <span className="text-[10px] bg-emerald-200/80 text-emerald-900 font-mono px-2 py-0.5 rounded-full font-bold">OAuth 2.0</span>
                                </div>
                                <div className="text-emerald-800 text-[11px] mt-0.5">
                                    {t("cloud_inverter.sungrow_api_desc", "Alle erkannten Sungrow Wechselrichter und Speicher deines iSolarCloud Kontos sind angebunden und synchronisieren automatisch.")}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* 2. LISTE AKTIVER / BEREITS VERBUNDENER WECHSELRICHTER */}
                {activeIntegrations.length > 0 && (
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <div className="text-xs font-bold uppercase tracking-wider text-gray-700 flex items-center gap-2">
                                <span>⚡</span>
                                <span>{t("cloud_inverter.active_title", "Bereits verbundene Wechselrichter & Schnittstellen")} ({activeIntegrations.length})</span>
                            </div>
                            <span className="text-[11px] text-gray-400">
                                {t("cloud_inverter.auto_sync_badge", "Automatische Cloud-Synchronisation aktiv")}
                            </span>
                        </div>

                        <div className="grid grid-cols-1 gap-3">
                            {activeIntegrations.map((item) => {
                                const isOk = item.last_status === "ok";
                                const isErr = item.last_status === "error";
                                const isCurrentlyPolling = pollingId === item.id;
                                const isBeingEdited = editingIntegrationId === item.id && isFormOpen;

                                return (
                                    <div
                                        key={item.id}
                                        className={`p-4 rounded-xl border transition flex flex-wrap items-center justify-between gap-3 ${
                                            isBeingEdited
                                                ? "border-blue-500 bg-blue-50/50 ring-2 ring-blue-200"
                                                : isErr
                                                ? "border-rose-200 bg-rose-50/40"
                                                : "border-slate-200 bg-slate-50/70 hover:border-slate-300 hover:bg-slate-50"
                                        }`}
                                    >
                                        <div className="flex items-center gap-3 min-w-0">
                                            <div className="w-9 h-9 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-lg shadow-2xs shrink-0">
                                                {item.vendor === "sungrow" ? "☀️" : "🔌"}
                                            </div>
                                            <div className="min-w-0">
                                                <div className="flex items-center gap-2 flex-wrap">
                                                    <span className="font-bold text-gray-900 text-sm truncate">
                                                        {item.device_name}
                                                    </span>
                                                    <span className="text-[10px] font-semibold px-2 py-0.5 bg-slate-200 text-slate-800 rounded-md">
                                                        {item.profile_name}
                                                    </span>
                                                    <span
                                                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 ${
                                                            isOk
                                                                ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                                                                : isErr
                                                                ? "bg-rose-100 text-rose-800 border border-rose-200"
                                                                : "bg-amber-100 text-amber-800 border border-amber-200"
                                                        }`}
                                                    >
                                                        <span>{isOk ? "●" : isErr ? "▲" : "○"}</span>
                                                        <span>
                                                            {isOk
                                                                ? t("cloud_inverter.status_ok", "Aktiv ● Verbunden")
                                                                : isErr
                                                                ? t("cloud_inverter.status_error", "Fehler bei Abfrage")
                                                                : t("cloud_inverter.status_pending", "Ausstehend")}
                                                        </span>
                                                    </span>
                                                </div>

                                                <div className="flex items-center gap-3 text-[11px] text-gray-500 mt-1 flex-wrap">
                                                    <span>
                                                        ⏱️ {t("cloud_inverter.last_polled", "Zuletzt synchronisiert")}:{" "}
                                                        <strong className="text-gray-700">{formatRelativeTime(item.last_polled_at)}</strong>
                                                    </span>
                                                    {!isSungrow && (
                                                        <>
                                                            <span>•</span>
                                                            <span>
                                                                Intervall: <strong className="text-gray-700">{item.polling_interval_seconds}s</strong>
                                                            </span>
                                                        </>
                                                    )}
                                                    {item.last_error_message && (
                                                        <span className="text-rose-600 truncate max-w-xs" title={item.last_error_message}>
                                                            ⚠️ {item.last_error_message}
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>

                                        {/* Action Toolbar */}
                                        <div className="flex items-center gap-1.5 shrink-0">
                                            <button
                                                type="button"
                                                onClick={() => handlePollNow(item)}
                                                disabled={isCurrentlyPolling}
                                                className="px-2.5 py-1.5 bg-white hover:bg-slate-100 border border-slate-300 text-slate-700 text-xs font-semibold rounded-lg shadow-2xs transition flex items-center gap-1 cursor-pointer"
                                                title={t("cloud_inverter.poll_now", "Jetzt abrufen")}
                                            >
                                                <span>{isCurrentlyPolling ? "⏳" : "🔄"}</span>
                                                <span className="hidden sm:inline">
                                                    {isCurrentlyPolling ? t("cloud_inverter.polling_now", "Lade...") : t("cloud_inverter.poll_now", "Jetzt abrufen")}
                                                </span>
                                            </button>

                                            {/* Sungrow: Kein manuelles Bearbeiten, bei Fehler Re-Auth Button */}
                                            {isSungrow ? (
                                                isErr && (
                                                    <button
                                                        type="button"
                                                        onClick={handleSungrowOAuth}
                                                        className="px-2.5 py-1.5 bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold rounded-lg shadow-2xs transition flex items-center gap-1 cursor-pointer"
                                                        title={t("cloud_inverter.sungrow_reauth_btn", "iSolarCloud Autorisierung erneuern")}
                                                    >
                                                        <span>🔑</span>
                                                        <span className="hidden sm:inline">{t("cloud_inverter.sungrow_reauth_short", "Neu autorisieren")}</span>
                                                    </button>
                                                )
                                            ) : (
                                                <button
                                                    type="button"
                                                    onClick={() => handleStartEdit(item)}
                                                    className="px-2.5 py-1.5 bg-white hover:bg-slate-100 border border-slate-300 text-slate-700 text-xs font-semibold rounded-lg shadow-2xs transition flex items-center gap-1 cursor-pointer"
                                                    title={t("cloud_inverter.edit_btn", "Bearbeiten")}
                                                >
                                                    <span>⚙️</span>
                                                    <span className="hidden sm:inline">{t("cloud_inverter.edit_btn", "Bearbeiten")}</span>
                                                </button>
                                            )}

                                            <button
                                                type="button"
                                                onClick={() => handleDeleteIntegration(item)}
                                                className="px-2.5 py-1.5 bg-white hover:bg-rose-50 border border-slate-300 hover:border-rose-300 text-rose-600 text-xs font-semibold rounded-lg shadow-2xs transition flex items-center gap-1 cursor-pointer"
                                                title={t("cloud_inverter.disconnect_btn", "Trennen")}
                                            >
                                                <span>🗑️</span>
                                            </button>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* 3. SUNGROW ERST-ANMELDUNG (NUR WENN NOCH KEINE AKTIVE KOPPLUNG VORHANDEN) */}
                {filterVendor === "sungrow" && activeIntegrations.length === 0 && (
                    <div className="space-y-4">
                        <div className="p-5 rounded-2xl bg-gradient-to-r from-amber-600 via-orange-600 to-amber-700 text-white shadow-md flex flex-wrap items-center justify-between gap-4">
                            <div className="space-y-1.5 max-w-xl">
                                <div className="flex items-center gap-2">
                                    <span className="text-xl">⚡</span>
                                    <span className="font-bold text-base text-white">
                                        {t("cloud_inverter.sungrow_oauth_title", "Offizielle 1-Klick Sungrow Autorisierung (OAuth 2.0)")}
                                    </span>
                                </div>
                                <p className="text-xs text-amber-100 leading-relaxed">
                                    {t("cloud_inverter.sungrow_oauth_sub", "Verbinde deinen Sungrow Hybrid-Wechselrichter (SH-Serie) und SBR-Speicher direkt und sicher über die offizielle iSolarCloud Schnittstelle — ganz ohne manuelle Passworteingabe oder AppKey-Konfiguration.")}
                                </p>
                            </div>
                            <button
                                type="button"
                                onClick={handleSungrowOAuth}
                                className="px-5 py-3 bg-white text-amber-800 hover:bg-amber-50 font-bold text-xs rounded-xl shadow-md transition cursor-pointer flex items-center gap-2"
                            >
                                <span>🔑</span>
                                <span>{t("cloud_inverter.sungrow_login_btn", "Jetzt bei Sungrow anmelden & freigeben")}</span>
                            </button>
                        </div>

                        <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200/70 text-xs text-amber-950 space-y-2">
                            <div className="flex items-center justify-between font-bold text-amber-950">
                                <span className="flex items-center gap-1.5">
                                    <span>💡</span>
                                    <span>{t("cloud_inverter.sungrow_how_it_works", "So funktioniert die automatische Anbindung")}</span>
                                </span>
                                <span className="text-[10px] text-amber-800 bg-amber-200/60 px-2 py-0.5 rounded-md font-mono">
                                    Sungrow OpenAPI & OAuth 2.0
                                </span>
                            </div>
                            <ol className="list-decimal list-inside space-y-1 text-[12px] leading-relaxed text-amber-900 bg-white/70 p-3 rounded-lg border border-amber-200/60">
                                <li>{t("cloud_inverter.sungrow_step_1", "Klicke auf Jetzt bei Sungrow anmelden & freigeben.")}</li>
                                <li>{t("cloud_inverter.sungrow_step_2", "Du wirst sicher zu Sungrow iSolarCloud weitergeleitet, um Sharegy für deine Anlage freizuschalten.")}</li>
                                <li>{t("cloud_inverter.sungrow_step_3", "Nach der Freigabe erfolgt die Rückleitung zu Sharegy — dein Wechselrichter und Batteriespeicher werden vollautomatisch angelegt und synchronisiert.")}</li>
                            </ol>
                        </div>
                    </div>
                )}

                {/* 4. FORMULAR: BEARBEITEN / NEU ANLEGEN (NUR FÜR WEITERE WRs ODER DETAILS) */}
                {isFormOpen && filterVendor !== "sungrow" && (
                    <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200/80 space-y-6 animate-in fade-in duration-200">
                        <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                            <div className="flex items-center gap-2">
                                <span className="text-lg">{editingIntegrationId ? "⚙️" : "➕"}</span>
                                <h3 className="font-bold text-gray-900 text-sm">
                                    {editingIntegrationId
                                        ? t("cloud_inverter.editing_title", "Wechselrichter-Verbindung bearbeiten")
                                        : t("cloud_inverter.adding_title", "Neuen Wechselrichter koppeln")}
                                </h3>
                            </div>
                            <button
                                type="button"
                                onClick={handleCancelForm}
                                className="text-xs text-gray-500 hover:text-gray-800 font-semibold px-2.5 py-1 rounded-lg hover:bg-white border border-transparent hover:border-gray-200 cursor-pointer"
                            >
                                ✕ {t("cloud_inverter.cancel_edit", "Abbrechen")}
                            </button>
                        </div>

                        {filterVendor !== "sungrow" && (
                            <div>
                                <label className="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-2">
                                    {t("cloud_inverter.choose_vendor_title", "1. Wähle deinen Wechselrichter-Hersteller / Cloud-Dienst")}
                                </label>
                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                    {profiles.map((p) => {
                                        const isSelected = p.id === selectedProfileId;
                                        return (
                                            <button
                                                key={p.id}
                                                type="button"
                                                onClick={() => {
                                                    setSelectedProfileId(p.id);
                                                    if (!deviceName || !editingIntegrationId) {
                                                        setDeviceName(`Mein ${p.name}`);
                                                    }
                                                    setTestResult(null);
                                                    setSaveSuccess(null);
                                                    setErrorMsg(null);
                                                }}
                                                className={`p-3 rounded-xl border text-left transition cursor-pointer flex flex-col justify-between ${
                                                    isSelected
                                                        ? "border-blue-500 bg-blue-50/50 ring-2 ring-blue-200 shadow-2xs"
                                                        : "border-gray-200 bg-white hover:bg-gray-50"
                                                }`}
                                            >
                                                <div className="flex items-center justify-between">
                                                    <span className="font-bold text-sm text-gray-900">{p.vendor}</span>
                                                    {isSelected && <span className="text-blue-600 text-xs">✓ {t("common.selected", "Ausgewählt")}</span>}
                                                </div>
                                                <span className="text-xs text-gray-500 mt-1">{p.name}</span>
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {currentProfile && (
                            <div className="space-y-4 pt-2 border-t border-gray-200">
                                <label className="block text-xs font-bold uppercase tracking-wider text-gray-600">
                                    {t("cloud_inverter.credentials_title", "2. Zugangsdaten & Konfiguration")}
                                </label>

                                <div>
                                    <label className="block text-xs font-medium text-gray-700 mb-1">
                                        {t("cloud_inverter.display_name_label", "Anzeigename in Sharegy")}
                                    </label>
                                    <input
                                        type="text"
                                        value={deviceName}
                                        onChange={(e) => setDeviceName(e.target.value)}
                                        placeholder={`z. B. ${currentProfile.vendor} PV-Anlage`}
                                        className="w-full text-sm px-3 py-2 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-hidden"
                                    />
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                    {(currentProfile.fields || []).map((field) => {
                                        const isSecret =
                                            field.type === "password" ||
                                            field.key.toLowerCase().includes("pass") ||
                                            field.key.toLowerCase().includes("secret") ||
                                            field.key.toLowerCase().includes("token") ||
                                            field.key.toLowerCase().includes("key");
                                        const isVisible = Boolean(showFieldValues[field.key]);

                                        return (
                                            <div key={field.key} className="space-y-1">
                                                <div className="flex items-center justify-between">
                                                    <label className="block text-xs font-medium text-gray-700">
                                                        {field.label} {field.required && <span className="text-red-500">*</span>}
                                                    </label>
                                                    {isSecret && (
                                                        <button
                                                            type="button"
                                                            onClick={() => toggleFieldVisibility(field.key)}
                                                            className="text-[11px] text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1 cursor-pointer"
                                                        >
                                                            <span>{isVisible ? "🙈" : "👁️"}</span>
                                                            <span>{isVisible ? t("common.hide", "Verbergen") : t("common.show", "Anzeigen")}</span>
                                                        </button>
                                                    )}
                                                </div>

                                                <div className="relative">
                                                    <input
                                                        type={isSecret ? (isVisible ? "text" : "password") : (field.type || "text")}
                                                        value={credentials[field.key] || ""}
                                                        onChange={(e) => handleFieldChange(field.key, e.target.value)}
                                                        placeholder={field.placeholder || ""}
                                                        className={`w-full text-sm px-3 py-2 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-hidden font-mono ${
                                                            isSecret ? "pr-10" : ""
                                                        }`}
                                                    />
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>

                                {/* Polling Interval */}
                                <div className="pt-2 border-t border-gray-200 space-y-1.5">
                                    <div className="flex items-center justify-between">
                                        <label className="block text-xs font-medium text-gray-700">
                                            ⏱️ {t("cloud_inverter.polling_interval_label", "Abfrage-Intervall (Cloud Polling)")}
                                        </label>
                                        <span className="text-[11px] font-mono text-gray-500">
                                            {pollingInterval >= 60 ? `${pollingInterval / 60} Min.` : `${pollingInterval} Sek.`}
                                        </span>
                                    </div>
                                    <div className="grid grid-cols-4 gap-2">
                                        {[
                                            { label: "30s (Ultra-Live)", value: 30 },
                                            { label: "60s (Standard)", value: 60 },
                                            { label: "2 Min.", value: 120 },
                                            { label: "5 Min. (Schonend)", value: 300 },
                                        ].map((opt) => (
                                            <button
                                                key={opt.value}
                                                type="button"
                                                onClick={() => setPollingInterval(opt.value)}
                                                className={`py-1.5 px-2 rounded-lg text-xs font-semibold border transition text-center cursor-pointer ${
                                                    pollingInterval === opt.value
                                                        ? "bg-blue-600 text-white border-blue-600 shadow-xs"
                                                        : "bg-white text-gray-700 border-gray-200 hover:bg-gray-100"
                                                }`}
                                            >
                                                {opt.label}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Status / Test Results */}
                        {testResult && (
                            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 space-y-2 text-xs">
                                <div className="flex items-center gap-2 text-emerald-800 font-bold">
                                    <span>✅</span> {testResult.message}
                                </div>
                            </div>
                        )}

                        {saveSuccess && (
                            <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-blue-800 text-xs font-medium flex items-center gap-2">
                                <span>🎉</span> {saveSuccess.message}
                            </div>
                        )}

                        {errorMsg && (
                            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium flex items-center gap-2">
                                <span>⚠️</span> {errorMsg}
                            </div>
                        )}

                        {/* Action Buttons */}
                        <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
                            <button
                                type="button"
                                onClick={() => setSelfTestOpen(true)}
                                className="px-4 py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 text-xs font-bold rounded-xl transition cursor-pointer flex items-center gap-1.5"
                            >
                                ⚡ {t("cloud_inverter.self_test_btn", "1-Klick Selbsttest")}
                            </button>

                            <button
                                type="button"
                                onClick={handleTestConnection}
                                disabled={isTesting}
                                className="px-4 py-2 bg-white hover:bg-gray-100 text-gray-800 border border-gray-300 text-xs font-bold rounded-xl transition cursor-pointer flex items-center gap-1.5"
                            >
                                {isTesting ? `⏳ ${t("cloud_inverter.testing", "Teste Verbindung...")}` : `🔌 ${t("cloud_inverter.test_btn", "Verbindung testen")}`}
                            </button>

                            <button
                                type="button"
                                onClick={handleIntegrateOrUpdate}
                                disabled={isSaving}
                                className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-xs transition cursor-pointer flex items-center gap-1.5"
                            >
                                {isSaving
                                    ? `⏳ ${t("common.saving", "Speichere...")}`
                                    : editingIntegrationId
                                    ? `💾 ${t("cloud_inverter.update_btn", "Änderungen speichern")}`
                                    : `🚀 ${t("cloud_inverter.connect_btn", "Jetzt mit Sharegy verbinden")}`}
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* 1-Klick Hardware-Selbsttest Modal */}
            <DeviceSelfTestModal
                open={selfTestOpen}
                onClose={() => setSelfTestOpen(false)}
                profileId={selectedProfileId}
                deviceName={currentProfile?.name || deviceName || t("devices.inverter", "Wechselrichter")}
                credentials={credentials}
            />
        </div>
    );
}
