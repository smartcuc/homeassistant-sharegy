/*
# src/pages/Settings.jsx
*/

import Card from "../components/ui/Card";
import { useUser } from "../hooks/useUser";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

export default function Settings() {
    const { user } = useUser();
    const { t } = useTranslation();

    return (
        <div className="p-6 max-w-3xl space-y-6">

            {/* HEADER */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                    <span>⚙️</span> {t("nav.app_settings", "App-Einstellungen")}
                </h1>
                <p className="text-sm text-gray-500 mt-1">
                    Allgemeine Einstellungen, Benachrichtigungen und System-Informationen.
                </p>
            </div>

            {/* ACCOUNT SHORTCUT */}
            <Card>
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="font-semibold text-gray-900 flex items-center gap-2">
                            <span>👤</span> {t("settings.account", "Benutzerkonto & Sprache")}
                        </h2>
                        <p className="text-xs text-gray-500 mt-0.5">
                            {user?.email} • Sprache & Zeitzone werden im Profil verwaltet.
                        </p>
                    </div>
                    <Link
                        to="/app/profile"
                        className="px-3.5 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-semibold rounded-xl transition"
                    >
                        Zum Profil →
                    </Link>
                </div>
            </Card>

            {/* INTERFACES SHORTCUT */}
            <Card>
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="font-semibold text-gray-900 flex items-center gap-2">
                            <span>📡</span> {t("nav.mqtt_interfaces", "MQTT & Schnittstellen")}
                        </h2>
                        <p className="text-xs text-gray-500 mt-0.5">
                            Zugangsdaten für ioBroker, Home Assistant, OpenTelemetry und Shelly.
                        </p>
                    </div>
                    <Link
                        to="/app/interfaces"
                        className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-gray-800 text-xs font-semibold rounded-xl transition"
                    >
                        Schnittstellen verwalten →
                    </Link>
                </div>
            </Card>

            {/* DISPLAY & THEME */}
            <Card>
                <h2 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <span>🎨</span> Anzeige & Theme
                </h2>
                <p className="text-xs text-gray-500 mb-4">
                    Passe das Erscheinungsbild und Farbschema deiner Sharegy-Oberfläche an.
                </p>
                <div className="flex gap-3">
                    <button className="px-4 py-2 text-xs font-semibold rounded-xl border border-indigo-600 bg-indigo-50 text-indigo-700 shadow-xs">
                        ☀️ Hell (Standard)
                    </button>
                    <button
                        disabled
                        className="px-4 py-2 text-xs font-semibold rounded-xl border border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed"
                        title="In Kürze verfügbar"
                    >
                        🌙 Dunkel (In Kürze)
                    </button>
                </div>
            </Card>

            {/* SYSTEM INFO */}
            <Card>
                <h2 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <span>ℹ️</span> System-Informationen
                </h2>
                <div className="text-xs text-gray-600 space-y-1.5 font-mono">
                    <div className="flex justify-between">
                        <span className="text-gray-400">Version:</span>
                        <span className="font-semibold text-gray-800">Sharegy EMS 2.4.0 (Free Edition)</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-400">Backend Engine:</span>
                        <span className="text-gray-800">Django 5.x / TimescaleDB</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-400">Telemetrie Broker:</span>
                        <span className="text-emerald-600 font-semibold">Online (MQTT & OTel)</span>
                    </div>
                </div>
            </Card>

        </div>
    );
}
