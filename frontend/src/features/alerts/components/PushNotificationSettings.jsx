/*
# src/features/alerts/components/PushNotificationSettings.jsx
*/

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import {
    isPushSupported,
    getCurrentPushSubscription,
    subscribeToPushNotifications,
    unsubscribeFromPushNotifications,
} from "../../../utils/pushManager";

export default function PushNotificationSettings() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const [isSubscribedOnDevice, setIsSubscribedOnDevice] = useState(false);
    const [isDeviceChecking, setIsDeviceChecking] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [feedbackMessage, setFeedbackMessage] = useState(null);

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
        setActionLoading(true);
        setFeedbackMessage(null);
        try {
            if (isSubscribedOnDevice) {
                await unsubscribeFromPushNotifications();
                setIsSubscribedOnDevice(false);
                setFeedbackMessage({
                    type: "info",
                    text: t("notifications.unsubscribed", "Push-Benachrichtigungen auf diesem Gerät deaktiviert."),
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
                text: err.message || "Fehler beim Aktivieren der Benachrichtigungen.",
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
        <div className="bg-white border border-gray-200/80 rounded-2xl p-6 shadow-xs space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-100 pb-5">
                <div>
                    <h2 className="font-bold text-gray-900 text-base flex items-center gap-2">
                        <span>📲</span> {t("notifications.title", "Mobile Push & Echtzeit-Alarme")}
                    </h2>
                    <p className="text-xs text-gray-500 mt-1">
                        {t("notifications.desc", "Erhalte kritische Alarme, Speicherwarnungen und Negativpreis-Chancen direkt auf den Sperrbildschirm deines Smartphones oder Desktops.")}
                    </p>
                </div>

                <div className="flex items-center gap-2">
                    <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-slate-100 text-slate-700">
                        {pref.active_devices_count || 0} {t("notifications.registered_devices", "Geräte registriert")}
                    </span>
                </div>
            </div>

            {/* Permission Denied in Firefox/Browser Warning */}
            {isPermissionBlocked && (
                <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 text-xs space-y-1.5 shadow-2xs">
                    <div className="font-bold flex items-center gap-2">
                        <span>🔒</span>
                        <span>Benachrichtigungen sind in deinem Browser für diese Seite blockiert</span>
                    </div>
                    <p className="leading-relaxed">
                        Klicke oben links in der Adressleiste auf das <strong>durchgestrichene Symbol / Schloss</strong> neben <code>sharegy.de</code> und hebe die Blockierung für <em>Benachrichtigungen senden</em> auf (auf <strong>„Erlauben“</strong> stellen oder das Kreuzchen entfernen). Lade die Seite danach neu.
                    </p>
                </div>
            )}

            {/* Feedback Message */}
            {feedbackMessage && (
                <div className={`p-3.5 rounded-xl text-xs font-medium flex items-center gap-2 transition ${
                    feedbackMessage.type === "success"
                        ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                        : feedbackMessage.type === "error"
                        ? "bg-rose-50 text-rose-800 border border-rose-200"
                        : "bg-blue-50 text-blue-800 border border-blue-200"
                }`}>
                    <span>{feedbackMessage.type === "success" ? "✅" : feedbackMessage.type === "error" ? "⚠️" : "ℹ️"}</span>
                    <span>{feedbackMessage.text}</span>
                </div>
            )}

            {/* Device Activation Card */}
            <div className="bg-gradient-to-br from-indigo-50/70 to-slate-50 border border-indigo-100 rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1">
                    <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm text-gray-900">
                            {t("notifications.this_device", "Dieses Gerät (Browser / Smartphone)")}
                        </span>
                        {!isDeviceChecking && (
                            <span className={`px-2 py-0.5 rounded-full text-[11px] font-bold ${
                                isSubscribedOnDevice
                                    ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                                    : "bg-gray-200/80 text-gray-700"
                            }`}>
                                {isSubscribedOnDevice ? t("notifications.status_active", "🟢 Aktiv") : t("notifications.status_inactive", "⚪ Nicht abonniert")}
                            </span>
                        )}
                    </div>
                    <p className="text-xs text-gray-600">
                        {supported
                            ? isSubscribedOnDevice
                                ? t("notifications.device_ready", "Dieses Gerät empfängt Push-Nachrichten zuverlässig im Hintergrund.")
                                : t("notifications.device_not_registered", "Klicke auf Aktivieren, um Alarme auch bei geschlossener App auf dieses Gerät zu erhalten.")
                            : t("notifications.not_supported", "Web-Push wird von diesem Browser nicht nativ unterstützt.")}
                    </p>
                </div>

                <div className="flex items-center gap-2.5 shrink-0">
                    <button
                        onClick={handleToggleDeviceSubscription}
                        disabled={!supported || actionLoading || isDeviceChecking}
                        className={`px-4 py-2 rounded-xl text-xs font-bold transition shadow-xs flex items-center gap-1.5 ${
                            isSubscribedOnDevice
                                ? "bg-white hover:bg-rose-50 text-rose-700 border border-rose-200"
                                : "bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-200"
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                        <span>{isSubscribedOnDevice ? "🔕" : "🔔"}</span>
                        <span>{isSubscribedOnDevice ? t("notifications.disable_device", "Auf diesem Gerät deaktivieren") : t("notifications.enable_device", "Push auf diesem Gerät aktivieren")}</span>
                    </button>

                    {isSubscribedOnDevice && (
                        <button
                            onClick={() => testPushMutation.mutate()}
                            disabled={testPushMutation.isPending}
                            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 transition shadow-2xs flex items-center gap-1"
                            title="Sendet sofort eine Test-Push-Nachricht an deine registrierten Geräte"
                        >
                            <span>⚡</span>
                            <span>{testPushMutation.isPending ? t("common.sending", "Sendet...") : t("notifications.test_push", "Test-Push")}</span>
                        </button>
                    )}
                </div>
            </div>

            {/* Quiet Hours Configuration */}
            <div className="border border-gray-100 rounded-2xl p-4 sm:p-5 space-y-4">
                <div className="flex items-center justify-between">
                    <div>
                        <div className="font-semibold text-sm text-gray-900 flex items-center gap-2">
                            <span>🌙</span> {t("notifications.quiet_hours", "Ruhezeiten (Nachtmodus)")}
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">
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
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-hidden rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                    </label>
                </div>

                {pref.quiet_hours_enabled && (
                    <div className="pt-3 border-t border-gray-100 grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-700">
                                {t("notifications.start_time", "Beginn der Ruhezeit")}
                            </label>
                            <input
                                type="time"
                                value={pref.quiet_hours_start}
                                onChange={(e) => handlePrefChange("quiet_hours_start", e.target.value)}
                                className="w-full text-xs font-medium border border-gray-200 rounded-xl px-3 py-2 bg-gray-50 focus:bg-white focus:outline-indigo-600"
                            />
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-700">
                                {t("notifications.end_time", "Ende der Ruhezeit")}
                            </label>
                            <input
                                type="time"
                                value={pref.quiet_hours_end}
                                onChange={(e) => handlePrefChange("quiet_hours_end", e.target.value)}
                                className="w-full text-xs font-medium border border-gray-200 rounded-xl px-3 py-2 bg-gray-50 focus:bg-white focus:outline-indigo-600"
                            />
                        </div>

                        <div className="sm:col-span-2 pt-2">
                            <label className="inline-flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={pref.allow_critical_in_quiet_hours}
                                    onChange={(e) => handlePrefChange("allow_critical_in_quiet_hours", e.target.checked)}
                                    className="rounded-md border-gray-300 text-indigo-600 focus:ring-indigo-500"
                                />
                                <span className="text-xs font-medium text-gray-800">
                                    🚨 {t("notifications.allow_critical", "Kritische Notfall-Alarme (z. B. Batterie leer, Frostschutz) trotz Ruhezeit zustellen")}
                                </span>
                            </label>
                        </div>
                    </div>
                )}
            </div>

            {/* Category Filter Toggles */}
            <div className="space-y-3">
                <div className="font-semibold text-xs text-gray-500 uppercase tracking-wider">
                    {t("notifications.categories", "Aktive Alarm-Kategorien")}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {[
                        { key: "notify_battery", label: t("notifications.cat_battery", "Batterie-Notreserve & Entladung"), icon: "🔋" },
                        { key: "notify_leakage", label: t("notifications.cat_leakage", "Nachtverbrauch & Dauerlast-Leckagen"), icon: "💧" },
                        { key: "notify_pv", label: t("notifications.cat_pv", "PV-Ertragsausfall & Anomalien"), icon: "☀️" },
                        { key: "notify_prices", label: t("notifications.cat_prices", "Börsenstrom-Negativpreise & Peaks"), icon: "💶" },
                        { key: "notify_device_status", label: t("notifications.cat_device", "Geräte-Offline & Signalverlust"), icon: "📡" },
                    ].map((cat) => (
                        <label
                            key={cat.key}
                            className="flex items-center justify-between p-3 rounded-xl border border-gray-100 hover:bg-gray-50/80 transition cursor-pointer"
                        >
                            <span className="text-xs font-medium text-gray-800 flex items-center gap-2">
                                <span>{cat.icon}</span>
                                <span>{cat.label}</span>
                            </span>
                            <input
                                type="checkbox"
                                checked={pref[cat.key] ?? true}
                                onChange={(e) => handlePrefChange(cat.key, e.target.checked)}
                                className="rounded-md border-gray-300 text-indigo-600 focus:ring-indigo-500"
                            />
                        </label>
                    ))}
                </div>
            </div>
        </div>
    );
}
