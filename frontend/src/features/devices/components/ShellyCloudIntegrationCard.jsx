/*
# frontend/src/features/devices/components/ShellyCloudIntegrationCard.jsx
*/

import { useState } from "react";
import { apiFetch } from "../../../api/client";
import { useTranslation } from "react-i18next";

export default function ShellyCloudIntegrationCard({ primaryHome, onImportComplete }) {
    const { t } = useTranslation();
    const [authKey, setAuthKey] = useState("");
    const [serverUrl, setServerUrl] = useState("https://shelly-45-eu.shelly.cloud");
    const [isLoading, setIsLoading] = useState(false);
    const [isImporting, setIsImporting] = useState(false);
    const [discoveryResult, setDiscoveryResult] = useState(null);
    const [importResult, setImportResult] = useState(null);
    const [errorMsg, setErrorMsg] = useState(null);
    const [showKeyHelp, setShowKeyHelp] = useState(false);
    const [showAuthKey, setShowAuthKey] = useState(false);

    async function handleTestDiscovery() {
        if (!authKey.trim()) {
            setErrorMsg("Bitte gib deinen Shelly Cloud Auth-Key / Token ein.");
            return;
        }

        setIsLoading(true);
        setErrorMsg(null);
        setDiscoveryResult(null);
        setImportResult(null);

        try {
            const data = await apiFetch("/api/devices/shelly-cloud/test/", {
                method: "POST",
                body: JSON.stringify({
                    auth_key: authKey.trim(),
                    server_url: serverUrl.trim(),
                }),
            });
            setDiscoveryResult(data);
        } catch (err) {
            setErrorMsg(err.message || "Verbindung zur Shelly Cloud fehlgeschlagen. Bitte prüfe deinen Auth-Key.");
        } finally {
            setIsLoading(false);
        }
    }

    async function handleImportAll() {
        if (!authKey.trim()) return;

        setIsImporting(true);
        setErrorMsg(null);
        setImportResult(null);

        try {
            const data = await apiFetch("/api/devices/shelly-cloud/import/", {
                method: "POST",
                body: JSON.stringify({
                    auth_key: authKey.trim(),
                    server_url: serverUrl.trim(),
                    home_id: primaryHome?.id,
                }),
            });
            setImportResult(data);
            if (onImportComplete) {
                onImportComplete(data);
            }
        } catch (err) {
            setErrorMsg(err.message || "Fehler beim Importieren der Shelly-Geräte.");
        } finally {
            setIsImporting(false);
        }
    }

    return (
        <div className="bg-white border border-sky-200/80 rounded-2xl shadow-xs overflow-hidden ring-1 ring-sky-100">
            {/* CARD HEADER */}
            <div className="p-5 bg-gradient-to-r from-sky-50/80 via-blue-50/30 to-white border-b border-sky-200/80 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-sky-500 text-white flex items-center justify-center text-xl shadow-xs font-bold">
                        ☁️
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h2 className="text-base font-bold text-gray-900">
                                Shelly Cloud 1-Klick Auto-Discovery
                            </h2>
                            <span className="text-[10px] font-bold px-2 py-0.5 bg-sky-100 text-sky-800 rounded-full border border-sky-200">
                                Neu & Automatisch
                            </span>
                        </div>
                        <p className="text-xs text-gray-500">
                            Importiert alle Geräte aus deinem Shelly-Cloud-Konto auf Knopfdruck als Hauptzähler, Balkonkraftwerk oder Steckdose.
                        </p>
                    </div>
                </div>

                <button
                    type="button"
                    onClick={() => setShowKeyHelp(!showKeyHelp)}
                    className="text-xs text-sky-700 hover:text-sky-900 font-medium underline flex items-center gap-1 cursor-pointer"
                >
                    ℹ️ Wo finde ich den Auth-Key?
                </button>
            </div>

            {/* EXPANDABLE TOKEN INSTRUCTIONS */}
            {showKeyHelp && (
                <div className="p-4 bg-sky-50/60 border-b border-sky-200/60 text-xs text-slate-700 space-y-2">
                    <div className="font-semibold text-sky-900">So findest du deinen Shelly Cloud Auth-Key:</div>
                    <ol className="list-decimal list-inside space-y-1 text-slate-600 pl-1">
                        <li>Öffne die <strong>Shelly Smart Control App</strong> oder <a href="https://control.shelly.cloud" target="_blank" rel="noreferrer" className="text-sky-700 underline font-medium">control.shelly.cloud</a>.</li>
                        <li>Gehe unten rechts auf <strong>Benutzer-Einstellungen</strong> (Profil / Zahnrad).</li>
                        <li>Klicke auf <strong>Autorisierungs-Cloud-Schlüssel</strong> &gt; <em>Schlüssel anfordern / anzeigen</em>.</li>
                        <li>Kopiere den angezeigten langen Token und füge ihn unten ein.</li>
                    </ol>
                    <div className="text-[11px] text-emerald-800 bg-emerald-50 p-2 rounded-lg border border-emerald-200 mt-2">
                        💡 <strong>Tipp:</strong> Wenn du gar keine Cloud nutzen möchtest (kostenlos & datensparsam), nutze einfach die oben beschriebene <strong>Outbound-WebSocket (WSS)</strong> Methode direkt auf dem Gerät!
                    </div>
                </div>
            )}

            {/* FORM BODY */}
            <div className="p-6 space-y-5">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="md:col-span-2 space-y-1.5">
                        <div className="flex items-center justify-between">
                            <label className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                                Shelly Cloud Auth-Key (API-Token) *
                            </label>
                            <button
                                type="button"
                                onClick={() => setShowAuthKey(!showAuthKey)}
                                className="text-xs text-sky-700 hover:text-sky-900 font-medium flex items-center gap-1 cursor-pointer"
                                title={showAuthKey ? "Schlüssel verbergen" : "Schlüssel anzeigen"}
                            >
                                <span>{showAuthKey ? "🙈" : "👁️"}</span>
                                <span>{showAuthKey ? "Verbergen" : "Anzeigen"}</span>
                            </button>
                        </div>
                        <div className="relative">
                            <input
                                type={showAuthKey ? "text" : "password"}
                                value={authKey}
                                onChange={(e) => setAuthKey(e.target.value)}
                                placeholder="z. B. MjM0NTY3YXV0aF8xMjM0NTY3ODkwYWJjZGU..."
                                className="w-full text-xs font-mono px-3.5 py-2.5 pr-10 rounded-xl border border-gray-300 focus:outline-hidden focus:ring-2 focus:ring-sky-500 bg-white"
                            />
                            <button
                                type="button"
                                onClick={() => setShowAuthKey(!showAuthKey)}
                                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-700 p-1 text-sm cursor-pointer"
                                title={showAuthKey ? "Schlüssel verbergen" : "Schlüssel anzeigen"}
                            >
                                {showAuthKey ? "🙈" : "👁️"}
                            </button>
                        </div>
                    </div>

                    <div className="space-y-1.5">
                        <label className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                            Shelly Cloud Server URL
                        </label>
                        <input
                            type="text"
                            value={serverUrl}
                            onChange={(e) => setServerUrl(e.target.value)}
                            placeholder="https://shelly-45-eu.shelly.cloud"
                            className="w-full text-xs font-mono px-3.5 py-2.5 rounded-xl border border-gray-300 focus:outline-hidden focus:ring-2 focus:ring-sky-500 bg-white"
                        />
                    </div>
                </div>

                {/* BUTTONS */}
                <div className="flex flex-wrap items-center gap-3 pt-1">
                    <button
                        type="button"
                        onClick={handleTestDiscovery}
                        disabled={isLoading || isImporting || !authKey.trim()}
                        className="px-4 py-2.5 bg-sky-600 hover:bg-sky-700 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-xs transition flex items-center gap-2 cursor-pointer"
                    >
                        {isLoading ? (
                            <>
                                <span className="animate-spin text-sm">⏳</span>
                                Suche Shelly Geräte...
                            </>
                        ) : (
                            <>
                                <span>🔍</span>
                                Shelly-Geräte suchen (Discovery)
                            </>
                        )}
                    </button>

                    {discoveryResult?.success && (
                        <button
                            type="button"
                            onClick={handleImportAll}
                            disabled={isImporting}
                            className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-xs transition flex items-center gap-2 cursor-pointer"
                        >
                            {isImporting ? (
                                <>
                                    <span className="animate-spin text-sm">⏳</span>
                                    Importiere Geräte...
                                </>
                            ) : (
                                <>
                                    <span>📥</span>
                                    Alle {discoveryResult.device_count} Geräte in Sharegy importieren
                                </>
                            )}
                        </button>
                    )}
                </div>

                {/* ERROR NOTIFICATION */}
                {errorMsg && (
                    <div className="p-3.5 bg-red-50 border border-red-200 rounded-xl text-xs text-red-800 flex items-start gap-2.5">
                        <span className="text-base">⚠️</span>
                        <div>{errorMsg}</div>
                    </div>
                )}

                {/* DISCOVERY RESULT LIST */}
                {discoveryResult?.success && !importResult && (
                    <div className="mt-4 p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-slate-800">
                                🟢 {discoveryResult.message}
                            </span>
                            <span className="text-[11px] text-slate-500 font-mono">
                                Server: {discoveryResult.server_url}
                            </span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 max-h-56 overflow-y-auto">
                            {discoveryResult.devices?.map((dev) => (
                                <div
                                    key={dev.id}
                                    className="p-2.5 bg-white border border-slate-200 rounded-lg flex items-center justify-between text-xs"
                                >
                                    <div className="space-y-0.5">
                                        <div className="font-semibold text-slate-800">{dev.name}</div>
                                        <div className="text-[10px] text-slate-400 font-mono">{dev.id} · {dev.model}</div>
                                    </div>
                                    <div className="text-right">
                                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-sm ${dev.online ? "bg-emerald-100 text-emerald-800" : "bg-slate-100 text-slate-600"}`}>
                                            {dev.online ? "Online" : "Offline"}
                                        </span>
                                        {dev.power_w !== undefined && (
                                            <div className="text-[10px] font-mono font-medium text-slate-600 mt-0.5">
                                                {Math.round(dev.power_w)} W
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* IMPORT SUCCESS RESULT */}
                {importResult?.success && (
                    <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-2 text-xs text-emerald-900">
                        <div className="font-bold flex items-center gap-1.5 text-emerald-800 text-sm">
                            <span>✅</span> {importResult.message}
                        </div>
                        <p className="text-emerald-700">
                            Die Geräte sind jetzt im System registriert und können im Dashboard und im Energiemanagement genutzt werden.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
