/*
# src/pages/Profile.jsx
*/

import { useEffect, useState } from "react";
import Card from "../components/ui/Card";
import { apiFetch } from "../api/client";
import { useSettings } from "../hooks/useSettings";
import { useUser } from "../hooks/useUser";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

export default function Profile() {
    const { user } = useUser();
    const queryClient = useQueryClient();
    const { settings } = useSettings();
    const { t, i18n } = useTranslation();

    const [timezone, setTimezone] = useState("");
    const [saved, setSaved] = useState(false);
    const [savingTimezone, setSavingTimezone] = useState(false);

    const timezoneQuery = useQuery({
        queryKey: ["timezones"],
        queryFn: () => apiFetch("/api/timezones/"),
        staleTime: Infinity,
    });

    const commonTimezones =
        timezoneQuery.data?.filter((tz) =>
            tz.startsWith("Europe/") || tz === "UTC"
        ) || [];

    useEffect(() => {
        if (settings?.timezone) {
            setTimezone(settings.timezone);
        }
    }, [settings]);

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
                body: JSON.stringify({ timezone }),
            });
            await queryClient.invalidateQueries({ queryKey: ["settings"] });
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
                    <span>👤</span> {t("settings.account", "Benutzerprofil")}
                </h1>
                <p className="text-gray-500 mt-1">
                    Persönliche Daten, Sprache und regionale Einstellungen.
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
                        <span>📧</span> Kontoinformationen
                    </h2>
                    <div className="space-y-3 text-sm">
                        <div>
                            <span className="text-xs text-gray-400 block uppercase font-bold">E-Mail-Adresse</span>
                            <span className="font-medium text-gray-800">{user?.email}</span>
                        </div>
                        <div>
                            <span className="text-xs text-gray-400 block uppercase font-bold">Name</span>
                            <span className="font-medium text-gray-800">
                                {user?.first_name ? `${user.first_name} ${user.last_name || ""}` : "Nicht angegeben"}
                            </span>
                        </div>
                        <div>
                            <span className="text-xs text-gray-400 block uppercase font-bold">Haushalte</span>
                            <span className="font-medium text-gray-800">
                                {user?.homes?.length || 1} {user?.homes?.length === 1 ? "Haushalt" : "Haushalte"}
                            </span>
                        </div>
                    </div>
                </Card>

                {/* LANGUAGE SELECTION */}
                <Card>
                    <h2 className="text-base font-bold text-gray-900 mb-1 flex items-center gap-2">
                        <span>🌐</span> {t("settings.language", "Sprache der Benutzeroberfläche")}
                    </h2>
                    <p className="text-xs text-gray-500 mb-4">
                        Wähle deine bevorzugte Sprache. Die Änderung wird sofort aktiv.
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
                                    className={`p-3 rounded-xl border text-left transition flex items-center justify-between ${
                                        isActive
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
                                            Aktiv
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
                    <span>🕒</span> Zeitzone & Region
                </h2>
                <p className="text-xs text-gray-500 mb-4">
                    Wichtig für korrekte Zeitachsen in Diagrammen und stundengenaue Strompreis-Analysen.
                </p>

                <div className="max-w-md space-y-3">
                    <select
                        value={timezone}
                        onChange={(e) => setTimezone(e.target.value)}
                        className="w-full border rounded-xl px-3.5 py-2.5 bg-white text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                        <option value="">Bitte auswählen</option>
                        {commonTimezones.map((tz) => (
                            <option key={tz} value={tz}>{tz}</option>
                        ))}
                    </select>

                    <div className="flex gap-2 pt-1">
                        <button
                            type="button"
                            onClick={() => setTimezone(Intl.DateTimeFormat().resolvedOptions().timeZone)}
                            className="px-3.5 py-2 border rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-50 transition"
                        >
                            Automatisch erkennen
                        </button>

                        <button
                            type="button"
                            onClick={saveTimezone}
                            disabled={savingTimezone}
                            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs transition"
                        >
                            {savingTimezone ? "Speichere..." : "Zeitzone speichern"}
                        </button>
                    </div>
                </div>
            </Card>

        </div>
    );
}
