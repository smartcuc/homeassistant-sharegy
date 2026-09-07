/*
# src/features/alerts/components/PushNotificationSettings.jsx
*/

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import Card from "../../../components/ui/Card";
import { apiFetch } from "../../../api/client";
import {
    isPushSupported,
    getCurrentPushSubscription,
    subscribeToPushNotifications,
    unsubscribeFromPushNotifications,
} from "../../../utils/pushManager";
import { useSubscription } from "../../../hooks/useSubscription";
import ProUpgradeModal from "../../../components/common/ProUpgradeModal";

export default function PushNotificationSettings({ emailSlot = null }) {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const queryClient = useQueryClient();

    const [isSubscribedOnDevice, setIsSubscribedOnDevice] = useState(false);
    const [isDeviceChecking, setIsDeviceChecking] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [feedbackMessage, setFeedbackMessage] = useState(null);
    const [showDevicesModal, setShowDevicesModal] = useState(false);
    const [proModalOpen, setProModalOpen] = useState(false);
    const [deletingDeviceId, setDeletingDeviceId] = useState(null);

    // 1. Preferences vom Server laden
    const prefQuery = useQuery({
        queryKey: ["notification-preferences"],
        queryFn: () => apiFetch("/api/notifications/preferences/"),
    });

    const pref = prefQuery.data || {
        push_enabled: true,
        quiet_hours_enabled: false,
        quiet_hours_start: "22:00",
        quiet_hours_end: "07:00",
        allow_critical_in_quiet_hours: true,
        notify_battery: true,
        notify_leakage: true,
        notify_pv: true,
        notify_prices: true,
        notify_device_status: true,
        active_devices_count: 0,
        devices: [],
    };

    // 2. Lokalen Browser-Abonnement-Status ermitteln
    useEffect(() => {
        let mounted = true;
        async function checkSubscription() {
            if (!isPushSupported()) {
                if (mounted) {
                    setIsSubscribedOnDevice(false);
                    setIsDeviceChecking(false);
                }
                return;
            }
            try {
                const sub = await getCurrentPushSubscription();
                if (mounted) {
                    setIsSubscribedOnDevice(!!sub);
                    setIsDeviceChecking(false);
                }
            } catch {
                if (mounted) setIsDeviceChecking(false);
            }
        }
        checkSubscription();
        return () => { mounted = false; };
    }, []);

    // 3. Mutationen
    const updatePrefMutation = useMutation({
        mutationFn: (newPrefs) =>
            apiFetch("/api/notifications/preferences/", {
                method: "POST",
                body: JSON.stringify(newPrefs),
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["notification-preferences"] });
        },
    });

    const deleteDeviceMutation = useMutation({
        mutationFn: (deviceId) =>
            apiFetch(`/api/notifications/devices/${deviceId}/delete/`, { method: "POST" }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["notification-preferences"] });
            setFeedbackMessage({
                type: "info",
                text: t("notifications.device_removed", "Gerät erfolgreich abgemeldet."),
            });
            setTimeout(() => setFeedbackMessage(null), 4000);
        },
        onError: (err) => {
            alert(err.message || "Fehler beim Abmelden des Geräts.");
        },
    });

    const testPushMutation = useMutation({
        mutationFn: () =>
            apiFetch("/api/notifications/test-push/", { method: "POST" }),
        onSuccess: (data) => {
            setFeedbackMessage({
                type: data.success ? "success" : "error",
                text: data.message,
            });
            setTimeout(() => setFeedbackMessage(null), 5000);
        },
        onError: (err) => {
            setFeedbackMessage({
                type: "error",
                text: err.message || "Test-Push fehlgeschlagen.",
            });
            setTimeout(() => setFeedbackMessage(null), 5000);
        },
    });

    // 4. Push auf aktuellem Gerät ein-/ausschalten
    const handleToggleDeviceSubscription = async () => {
        if (!isSubscribedOnDevice && !isPro) {
            setProModalOpen(true);
            return;
        }
        setActionLoading(true);
        setFeedbackMessage(null);
        try {
            if (isSubscribedOnDevice) {
                await unsubscribeFromPushNotifications();
                setIsSubscribedOnDevice(false);
                setFeedbackMessage({
                    type: "info",
                    text: t("notifications.unsubscribed", "Push-Benachrichtigungen auf diesem Gerät erfolgreich abgemeldet."),
                });
            } else {
                await subscribeToPushNotifications();
                setIsSubscribedOnDevice(true);
                setFeedbackMessage({
                    type: "success",
                    text: t("notifications.subscribed", "🎉 Großartig! Dieses Gerät ist jetzt für Push-Alarme registriert."),
                });
            }
            queryClient.invalidateQueries({ queryKey: ["notification-preferences"] });
        } catch (err) {
            setFeedbackMessage({
                type: "error",
                text: err.message || "Fehler beim Aktualisieren der Benachrichtigungen.",
            });
        } finally {
            setActionLoading(false);
            setTimeout(() => setFeedbackMessage(null), 6000);
        }
    };

    const handlePrefChange = (key, value) => {
        updatePrefMutation.mutate({
            ...pref,
            [key]: value,
        });
    };

    const supported = isPushSupported();
    const isPermissionBlocked = typeof window !== "undefined" && "Notification" in window && Notification.permission === "denied";

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
            {/* ========================================================================= */}
            {/* LINKER CONTAINER: PUSH-STATUS & GERÄTE-VERWALTUNG */}
            {/* ========================================================================= */}
            <Card>
                {/* Header */}
                <div className="border-b border-gray-100 dark:border-slate-800 pb-4 space-y-1.5">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                        <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
                            <span>📲</span> {t("notifications.title", "Mobile Push & Echtzeit-Alarme")}
                        </h2>

                        {/* Klickbare Geräteanzahl */}
                        {pref.active_devices_count > 0 ? (
                            <button
                                type="button"
                                onClick={() => setShowDevicesModal(true)}
                                className="text-xs font-semibold px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-950/60 text-slate-800 dark:text-slate-200 hover:text-indigo-600 dark:hover:text-indigo-400 border border-slate-300/80 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-700 transition flex items-center gap-1.5 cursor-pointer shadow-2xs group"
                                title={t("notifications.view_devices_tooltip", "Klicken, um registrierte Geräte anzuzeigen")}
                            >
                                <span>📱</span>
                                <span>
                                    {pref.active_devices_count}{" "}
                                    {pref.active_devices_count === 1
                                        ? t("notifications.device_registered_single", "Gerät registriert")
                                        : t("notifications.registered_devices", "Geräte registriert")}
                                </span>
                                <span className="text-gray-400 group-hover:text-indigo-600 text-[10px]">▼</span>
                            </button>
                        ) : (
                            <span className="text-xs font-semibold px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-200/60 dark:border-slate-700">
                                0 {t("notifications.registered_devices", "Geräte registriert")}
                            </span>
                        )}
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                        {t("notifications.desc", "Erhalte kritische Alarme, Speicherwarnungen und Negativpreis-Chancen direkt auf den Sperrbildschirm deines Smartphones oder Desktops.")}
                    </p>
                </div>

                <div className="space-y-4 pt-4">
                    {/* Permission Denied in Firefox/Browser Warning */}
                    {isPermissionBlocked && (
                        <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200 text-xs space-y-1.5 shadow-2xs">
                            <div className="font-bold flex items-center gap-2">
                                <span>🔒</span>
                                <span>Benachrichtigungen sind in deinem Browser blockiert</span>
                            </div>
                            <p className="leading-relaxed">
                                Klicke oben links in der Adressleiste auf das <strong>durchgestrichene Symbol / Schloss</strong> neben <code>sharegy.de</code> und stelle Benachrichtigungen auf <strong>„Erlauben“</strong>.
                            </p>
                        </div>
                    )}

                    {/* Feedback Message */}
                    {feedbackMessage && (
                        <div className={`p-3.5 rounded-xl text-xs font-medium flex items-center gap-2 transition ${
                            feedbackMessage.type === "success"
                                ? "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"
                                : feedbackMessage.type === "error"
                                ? "bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-300 border border-rose-200 dark:border-rose-800"
                                : "bg-blue-50 dark:bg-blue-950/40 text-blue-800 dark:text-blue-300 border border-blue-200 dark:border-blue-800"
                        }`}>
                            <span>{feedbackMessage.type === "success" ? "✅" : feedbackMessage.type === "error" ? "⚠️" : "ℹ️"}</span>
                            <span>{feedbackMessage.text}</span>
                        </div>
                    )}

                    {/* Device Activation Card */}
                    <div className="bg-gradient-to-br from-indigo-50/70 via-slate-50 to-white dark:from-slate-800/90 dark:via-slate-800/60 dark:to-slate-850 border border-indigo-100 dark:border-indigo-900/40 rounded-2xl p-4.5 space-y-3 shadow-xs">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                            <div className="flex items-center gap-2">
                                <span className="text-base">📱</span>
                                <span className="font-bold text-sm text-gray-900 dark:text-white">
                                    {t("notifications.this_device", "Dieses Gerät (Browser / Smartphone)")}
                                </span>
                            </div>
                            {!isDeviceChecking && (
                                <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                                    isSubscribedOnDevice
                                        ? "bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"
                                        : "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                                }`}>
                                    {isSubscribedOnDevice ? t("notifications.status_active", "🟢 Aktiv angemeldet") : t("notifications.status_inactive", "⚪ Nicht angemeldet")}
                                </span>
                            )}
                        </div>

                        <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
                            {supported
                                ? isSubscribedOnDevice
                                    ? t("notifications.device_ready", "Dieses Gerät empfängt Push-Nachrichten zuverlässig im Hintergrund.")
                                    : t("notifications.device_not_registered", "Klicke auf Aktivieren, um Alarme auch bei geschlossener App auf dieses Gerät zu erhalten.")
                                : t("notifications.not_supported", "Web-Push wird von diesem Browser nicht nativ unterstützt.")}
                        </p>

                        {/* Buttons unter dem Text */}
                        <div className="pt-2 flex flex-wrap items-center gap-2.5">
                            {isSubscribedOnDevice ? (
                                <>
                                    <button
                                        type="button"
                                        onClick={() => testPushMutation.mutate()}
                                        disabled={testPushMutation.isPending}
                                        className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition shadow-xs flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                                        title="Sendet sofort eine Test-Push-Nachricht an deine registrierten Geräte"
                                    >
                                        <span>⚡</span>
                                        <span>{testPushMutation.isPending ? t("common.sending", "Sendet...") : t("notifications.test_push", "Test-Push senden")}</span>
                                    </button>

                                    {/* Abmelde-Button */}
                                    <button
                                        type="button"
                                        onClick={handleToggleDeviceSubscription}
                                        disabled={!supported || actionLoading}
                                        className="px-4 py-2 rounded-xl text-xs font-semibold bg-white dark:bg-slate-800 hover:bg-rose-50 dark:hover:bg-rose-950/60 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-800 transition shadow-2xs flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                                    >
                                        <span>🔕</span>
                                        <span>{actionLoading ? t("common.loading", "Lädt...") : t("notifications.disable_device", "Auf diesem Gerät abmelden")}</span>
                                    </button>
                                </>
                            ) : (
                                /* Aktivieren-Button */
                                <button
                                    type="button"
                                    onClick={handleToggleDeviceSubscription}
                                    disabled={!supported || actionLoading}
                                    className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-500/20 transition flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                                >
                                    <span>🔔</span>
                                    <span>{actionLoading ? t("common.loading", "Lädt...") : t("notifications.enable_device", "Push auf diesem Gerät aktivieren")}</span>
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Feature Highlights / Security Info */}
                    <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/80 space-y-2.5 text-xs text-slate-600 dark:text-slate-400">
                        <div className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                            <span>🛡️</span>
                            <span>Web-Push & Datensicherheit</span>
                        </div>
                        <ul className="space-y-1.5 text-[11px] leading-relaxed">
                            <li className="flex items-center gap-2">
                                <span className="text-emerald-500 font-bold">✓</span>
                                <span>Ende-zu-Ende verschlüsselte Zustellung (VAPID / RFC 8291 Standard)</span>
                            </li>
                            <li className="flex items-center gap-2">
                                <span className="text-emerald-500 font-bold">✓</span>
                                <span>Keine App-Store-Installation nötig (PWA & moderner Web-Standard)</span>
                            </li>
                            <li className="flex items-center gap-2">
                                <span className="text-emerald-500 font-bold">✓</span>
                                <span>Jederzeit pro Endgerät mit einem Klick abmeldbar</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </Card>

            {/* ========================================================================= */}
            {/* RECHTER CONTAINER: ALARM-REGELN, RUHEZEITEN & BERICHTE */}
            {/* ========================================================================= */}
            <Card>
                {/* Header */}
                <div className="border-b border-gray-100 dark:border-slate-800 pb-4 space-y-1.5">
                    <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
                        <span>⚙️</span> {t("notifications.rules_title", "Alarm-Regeln & Benachrichtigungskanäle")}
                    </h2>
                    <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                        {t("notifications.rules_desc", "Passe Ruhezeiten an, filtere Warnstufen und konfiguriere automatisierte E-Mail-Berichte.")}
                    </p>
                </div>

                <div className="space-y-5 pt-4">
                    {/* SEKTION 1: RUHEZEITEN & NACHTMODUS */}
                    <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/80 space-y-3.5">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="font-bold text-xs text-gray-900 dark:text-white flex items-center gap-2">
                                    <span>🌙</span> {t("notifications.quiet_hours", "Ruhezeiten (Nachtmodus)")}
                                </div>
                                <p className="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5">
                                    {t("notifications.quiet_hours_desc", "Stummschaltung von nicht-kritischen Hinweisen zu bestimmten Uhrzeiten.")}
                                </p>
                            </div>

                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={pref.quiet_hours_enabled}
                                    onChange={(e) => handlePrefChange("quiet_hours_enabled", e.target.checked)}
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-slate-200 dark:bg-slate-700 peer-focus:outline-hidden rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                            </label>
                        </div>

                        {pref.quiet_hours_enabled && (
                            <div className="pt-3 border-t border-gray-200/60 dark:border-slate-700/60 grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                                <div className="space-y-1">
                                    <label className="text-[11px] font-bold text-gray-700 dark:text-gray-300 uppercase">
                                        {t("notifications.start_time", "Beginn der Ruhezeit")}
                                    </label>
                                    <input
                                        type="time"
                                        value={pref.quiet_hours_start}
                                        onChange={(e) => handlePrefChange("quiet_hours_start", e.target.value)}
                                        className="w-full text-xs font-semibold border border-gray-200 dark:border-slate-700 rounded-xl px-3 py-2 bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                    />
                                </div>

                                <div className="space-y-1">
                                    <label className="text-[11px] font-bold text-gray-700 dark:text-gray-300 uppercase">
                                        {t("notifications.end_time", "Ende der Ruhezeit")}
                                    </label>
                                    <input
                                        type="time"
                                        value={pref.quiet_hours_end}
                                        onChange={(e) => handlePrefChange("quiet_hours_end", e.target.value)}
                                        className="w-full text-xs font-semibold border border-gray-200 dark:border-slate-700 rounded-xl px-3 py-2 bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                    />
                                </div>

                                <div className="sm:col-span-2 pt-1">
                                    <label className="inline-flex items-center gap-2.5 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={pref.allow_critical_in_quiet_hours}
                                            onChange={(e) => handlePrefChange("allow_critical_in_quiet_hours", e.target.checked)}
                                            className="rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                                        />
                                        <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                                            🚨 {t("notifications.allow_critical", "Kritische Notfall-Alarme trotz Ruhezeit zustellen")}
                                        </span>
                                    </label>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* SEKTION 2: AKTIVE ALARM-KATEGORIEN */}
                    <div className="space-y-2.5">
                        <div className="text-[11px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            {t("notifications.categories", "Aktive Push-Kategorien")}
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {[
                                { key: "notify_battery", label: t("notifications.cat_battery", "Batterie-Notreserve & Entladung"), icon: "🔋" },
                                { key: "notify_leakage", label: t("notifications.cat_leakage", "Nachtverbrauch & Leckagen"), icon: "💧" },
                                { key: "notify_pv", label: t("notifications.cat_pv", "PV-Ertragsausfall & Anomalien"), icon: "☀️" },
                                { key: "notify_prices", label: t("notifications.cat_prices", "Börsenstrom-Negativpreise"), icon: "💶" },
                                { key: "notify_device_status", label: t("notifications.cat_device", "Geräte-Offline & Signalverlust"), icon: "📡" },
                            ].map((cat) => {
                                const isChecked = pref[cat.key] ?? true;
                                return (
                                    <label
                                        key={cat.key}
                                        className={`flex items-center justify-between p-3 rounded-xl border transition cursor-pointer ${
                                            isChecked
                                                ? "bg-indigo-50/50 dark:bg-indigo-950/30 border-indigo-200 dark:border-indigo-800/60"
                                                : "bg-slate-50 dark:bg-slate-800/40 border-gray-200 dark:border-slate-700 opacity-70"
                                        }`}
                                    >
                                        <span className="text-xs font-medium text-gray-800 dark:text-gray-200 flex items-center gap-2">
                                            <span className="text-sm">{cat.icon}</span>
                                            <span className="truncate">{cat.label}</span>
                                        </span>
                                        <input
                                            type="checkbox"
                                            checked={isChecked}
                                            onChange={(e) => handlePrefChange(cat.key, e.target.checked)}
                                            className="rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer shrink-0 ml-2"
                                        />
                                    </label>
                                );
                            })}
                        </div>
                    </div>

                    {/* SEKTION 3: E-MAIL-BERICHTE (SLOT) */}
                    {emailSlot && (
                        <div className="border-t border-gray-100 dark:border-slate-800 pt-5 space-y-3">
                            <div className="text-[11px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                {t("profile.email_notifications", "E-Mail-Zusammenfassungen & Systemberichte")}
                            </div>
                            {emailSlot}
                        </div>
                    )}
                </div>
            </Card>

            {/* ========================================================================= */}
            {/* MODAL: REGISTRIERTE GERÄTE MIT DATUM/UHRZEIT & AUDIT-INFOS */}
            {/* ========================================================================= */}
            {showDevicesModal && (
                <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-fade-in">
                    <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-gray-200 dark:border-slate-700 w-full max-w-xl overflow-hidden flex flex-col max-h-[85vh]">
                        {/* Modal Header */}
                        <div className="p-5 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white flex items-center justify-between">
                            <div className="flex items-center gap-2.5">
                                <span className="text-2xl">📱</span>
                                <div>
                                    <h3 className="text-base font-bold">
                                        {t("notifications.modal_devices_title", "Registrierte Push-Geräte")}
                                    </h3>
                                    <p className="text-xs text-indigo-200">
                                        {t("notifications.modal_devices_subtitle", "Übersicht aller Geräte, die Push-Nachrichten für dieses Konto empfangen.")}
                                    </p>
                                </div>
                            </div>
                            <button
                                onClick={() => setShowDevicesModal(false)}
                                className="text-white/70 hover:text-white p-1.5 rounded-xl hover:bg-white/10 transition cursor-pointer text-sm"
                            >
                                ✕
                            </button>
                        </div>

                        {/* Modal Content / Devices List */}
                        <div className="p-5 overflow-y-auto space-y-3 divide-y divide-gray-100 dark:divide-slate-800">
                            {(!pref.devices || pref.devices.length === 0) ? (
                                <div className="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
                                    {t("notifications.no_devices_found", "Keine aktiven Geräte registriert.")}
                                </div>
                            ) : (
                                pref.devices.map((device) => {
                                    const regDate = device.created_at
                                        ? new Date(device.created_at).toLocaleString("de-DE", {
                                            day: "2-digit",
                                            month: "2-digit",
                                            year: "numeric",
                                            hour: "2-digit",
                                            minute: "2-digit",
                                        })
                                        : "-";

                                    const lastUsed = device.last_used_at
                                        ? new Date(device.last_used_at).toLocaleString("de-DE", {
                                            day: "2-digit",
                                            month: "2-digit",
                                            year: "numeric",
                                            hour: "2-digit",
                                            minute: "2-digit",
                                        })
                                        : null;

                                    return (
                                        <div key={device.id} className="pt-3 first:pt-0 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                                            <div className="space-y-1">
                                                <div className="flex items-center gap-2">
                                                    <span className="font-bold text-sm text-gray-900 dark:text-white">
                                                        {device.device_name}
                                                    </span>
                                                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                                                        🟢 {t("common.active", "Aktiv")}
                                                    </span>
                                                </div>
                                                <div className="text-xs text-gray-600 dark:text-gray-400 flex flex-wrap gap-x-4 gap-y-1 font-medium">
                                                    <span>
                                                        📅 {t("notifications.registered_at", "Registriert:")} <strong>{regDate} Uhr</strong>
                                                    </span>
                                                    {device.registered_ip && device.registered_ip !== "-" && (
                                                        <span className="text-gray-500 dark:text-gray-400">
                                                            🌐 IP: <code className="font-mono text-indigo-600 dark:text-indigo-400">{device.registered_ip}</code>
                                                        </span>
                                                    )}
                                                </div>
                                                {lastUsed && (
                                                    <div className="text-[11px] text-gray-400 dark:text-gray-500">
                                                        {t("notifications.last_active", "Letzte Aktivität:")} {lastUsed} Uhr
                                                    </div>
                                                )}
                                            </div>

                                            <button
                                                onClick={async () => {
                                                    if (window.confirm(t("notifications.confirm_remove_device", "Möchtest du dieses Gerät wirklich abmelden?"))) {
                                                        setDeletingDeviceId(device.id);
                                                        try {
                                                            await deleteDeviceMutation.mutateAsync(device.id);
                                                        } finally {
                                                            setDeletingDeviceId(null);
                                                        }
                                                    }
                                                }}
                                                disabled={deletingDeviceId === device.id}
                                                className="px-3 py-1.5 rounded-xl border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/50 text-xs font-semibold transition flex items-center gap-1 shrink-0 self-start sm:self-center cursor-pointer disabled:opacity-50"
                                            >
                                                <span>🔕</span>
                                                <span>{deletingDeviceId === device.id ? t("common.loading", "Wird abgemeldet...") : t("notifications.remove_device", "Gerät abmelden")}</span>
                                            </button>
                                        </div>
                                    );
                                })
                            )}
                        </div>

                        {/* Modal Footer */}
                        <div className="p-4 bg-slate-50 dark:bg-slate-800/80 border-t border-gray-100 dark:border-slate-800 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                            <span>{pref.devices?.length || 0} {t("notifications.devices_total", "Geräte insgesamt")}</span>
                            <button
                                type="button"
                                onClick={() => setShowDevicesModal(false)}
                                className="px-4 py-2 rounded-xl bg-gray-900 dark:bg-slate-700 hover:bg-black dark:hover:bg-slate-600 text-white font-bold transition shadow-xs cursor-pointer"
                            >
                                {t("common.close", "Schließen")}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Pro Upgrade Dialog */}
            <ProUpgradeModal
                open={proModalOpen}
                onClose={() => setProModalOpen(false)}
                featureName="Mobile Push-Benachrichtigungen"
                featureDesc="Erhalte sofortige Push-Alarme bei Ausfällen, Netztrennungen und Speicher-Tiefentladungen direkt auf dein Smartphone mit Sharegy Pro."
            />
        </div>
    );
}
