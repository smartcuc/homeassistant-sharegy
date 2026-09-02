import { useState, useEffect } from "react";
import { apiFetch } from "../../../api/client";

export default function CloudInverterIntegrationCard({ primaryHome }) {
    const [profiles, setProfiles] = useState([]);
    const [selectedProfileId, setSelectedProfileId] = useState("sungrow_isolarcloud");
    const [credentials, setCredentials] = useState({
        appkey: "demo",
        user_account: "tester@sharegy.de",
        user_password: "••••••••",
        ps_id: "123456",
    });
    const [deviceName, setDeviceName] = useState("Mein Sungrow Wechselrichter");
    const [isTesting, setIsTesting] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [testResult, setTestResult] = useState(null);
    const [saveSuccess, setSaveSuccess] = useState(null);
    const [errorMsg, setErrorMsg] = useState(null);

    useEffect(() => {
        loadProfiles();
    }, []);

    async function loadProfiles() {
        try {
            const data = await apiFetch("/api/devices/cloud-profiles/");
            if (data?.profiles) {
                setProfiles(data.profiles);
                if (data.profiles.length > 0) {
                    setSelectedProfileId(data.profiles[0].id);
                }
            }
        } catch (err) {
            console.warn("Could not load cloud profiles:", err);
        }
    }


    const currentProfile = profiles.find((p) => p.id === selectedProfileId) || {
        id: "sungrow_isolarcloud",
        name: "Sungrow iSolarCloud",
        vendor: "Sungrow",
        description: "Cloud-Schnittstelle für alle Sungrow Hybrid-Wechselrichter (SH-Serie) und SBR-Batteriespeicher.",
        fields: [
            { key: "appkey", label: "Sungrow AppKey", placeholder: "z. B. B4A5F7... oder 'demo'", required: true },
            { key: "user_account", label: "iSolarCloud Benutzername / E-Mail", placeholder: "nutzer@example.de", required: true },
            { key: "user_password", label: "iSolarCloud Passwort", type: "password", required: true },
            { key: "ps_id", label: "Anlagen-ID (Power Station ID)", placeholder: "z. B. 123456", required: true },
        ],
    };

    function handleFieldChange(key, value) {
        setCredentials((prev) => ({ ...prev, [key]: value }));
        setTestResult(null);
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
            setErrorMsg(err.message || "Verbindungstest fehlgeschlagen.");
        } finally {
            setIsTesting(false);
        }
    }

    async function handleIntegrate() {
        setIsSaving(true);
        setSaveSuccess(null);
        setErrorMsg(null);
        try {
            const data = await apiFetch("/api/devices/cloud-profiles/integrate/", {
                method: "POST",
                body: JSON.stringify({
                    home_id: primaryHome?.id,
                    name: deviceName,
                    profile_id: selectedProfileId,
                    credentials: credentials,
                    polling_interval: 60,
                }),
            });
            setSaveSuccess(data);
        } catch (err) {
            setErrorMsg(err.message || "Kopplung fehlgeschlagen.");
        } finally {
            setIsSaving(false);
        }
    }


    return (
        <div className="bg-white border border-blue-200/80 rounded-2xl shadow-xs overflow-hidden ring-1 ring-blue-100">
            {/* Header */}
            <div className="p-5 bg-gradient-to-r from-blue-50/80 via-indigo-50/30 to-white border-b border-blue-200/80 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center text-xl shadow-xs">
                        ☁️
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h2 className="text-base font-bold text-gray-900">
                                Hersteller Cloud-Kopplung (Sungrow iSolarCloud, SolarEdge, Fronius)
                            </h2>
                            <span className="text-[10px] font-bold px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full border border-blue-200">
                                Task 5.7 YAML Profile
                            </span>
                        </div>
                        <p className="text-xs text-gray-500">
                            Direkte Server-zu-Server Anbindung für Wechselrichter und Batteriespeicher ohne lokale Hardware vor Ort.
                        </p>
                    </div>
                </div>
            </div>

            <div className="p-6 space-y-6">
                {/* 1. Hersteller-Auswahl */}
                <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-2">
                        1. Wähle deinen Wechselrichter-Hersteller / Cloud-Dienst
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
                                        setDeviceName(`Mein ${p.name}`);
                                        setTestResult(null);
                                        setSaveSuccess(null);
                                        setErrorMsg(null);
                                    }}
                                    className={`p-3 rounded-xl border text-left transition cursor-pointer flex flex-col justify-between ${
                                        isSelected
                                            ? "border-blue-500 bg-blue-50/50 ring-2 ring-blue-200 shadow-2xs"
                                            : "border-gray-200 bg-gray-50/50 hover:bg-gray-100/80"
                                    }`}
                                >
                                    <div className="flex items-center justify-between">
                                        <span className="font-bold text-sm text-gray-900">{p.vendor}</span>
                                        {isSelected && <span className="text-blue-600 text-xs">✓ Aktiv</span>}
                                    </div>
                                    <span className="text-xs text-gray-500 mt-1">{p.name}</span>
                                </button>
                            );
                        })}
                    </div>
                    <p className="text-xs text-gray-500 mt-2">{currentProfile.description}</p>

                    {/* Detaillierte Schritt-für-Schritt Anleitung */}
                    {currentProfile.help && (
                        <div className="mt-3 p-4 rounded-xl bg-blue-50/70 border border-blue-200/70 text-xs text-blue-900 space-y-2">
                            <div className="flex items-center justify-between font-bold text-blue-950">
                                <span className="flex items-center gap-1.5">
                                    <span>💡</span>
                                    <span>Anleitung zur Einrichtung ({currentProfile.name})</span>
                                </span>
                                <span className="text-[10px] text-blue-600 bg-blue-100 px-2 py-0.5 rounded-md font-mono">
                                    {currentProfile.vendor} API
                                </span>
                            </div>
                            <div className="text-[12px] leading-relaxed text-blue-800 whitespace-pre-line bg-white/70 p-3 rounded-lg border border-blue-100/80">
                                {currentProfile.help.de || currentProfile.help.en}
                            </div>
                        </div>
                    )}
                </div>


                {/* 2. Gerätename & Zugangsdaten */}
                <div className="space-y-4 pt-2 border-t border-gray-100">
                    <label className="block text-xs font-bold uppercase tracking-wider text-gray-600">
                        2. Zugangsdaten & Konfiguration
                    </label>

                    <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                            Anzeigename in Sharegy
                        </label>
                        <input
                            type="text"
                            value={deviceName}
                            onChange={(e) => setDeviceName(e.target.value)}
                            placeholder="z. B. Sungrow SH10RT PV-Anlage"
                            className="w-full text-sm px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-hidden"
                        />
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {(currentProfile.fields || []).map((field) => (
                            <div key={field.key}>
                                <label className="block text-xs font-medium text-gray-700 mb-1">
                                    {field.label} {field.required && <span className="text-red-500">*</span>}
                                </label>
                                <input
                                    type={field.type || "text"}
                                    value={credentials[field.key] || ""}
                                    onChange={(e) => handleFieldChange(field.key, e.target.value)}
                                    placeholder={field.placeholder || ""}
                                    className="w-full text-sm px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-hidden font-mono"
                                />
                                {field.description && (
                                    <p className="text-[11px] text-gray-400 mt-0.5">{field.description}</p>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Live Feedback / Test-Ergebnis */}
                {testResult && (
                    <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 space-y-2 text-xs">
                        <div className="flex items-center gap-2 text-emerald-800 font-bold">
                            <span>✅</span> {testResult.message}
                            {testResult.simulated && (
                                <span className="px-2 py-0.5 bg-emerald-200 text-emerald-900 rounded-md text-[10px]">
                                    Sandbox / Simulator
                                </span>
                            )}
                        </div>
                        {testResult.live_metrics && (
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-emerald-200/60">
                                <div className="bg-white/80 p-2 rounded-lg border border-emerald-100">
                                    <div className="text-gray-500 text-[10px]">PV-Leistung</div>
                                    <div className="text-sm font-bold text-emerald-700">
                                        {testResult.live_metrics.pv_power_w ?? 0} W
                                    </div>
                                </div>
                                <div className="bg-white/80 p-2 rounded-lg border border-emerald-100">
                                    <div className="text-gray-500 text-[10px]">Netzbezug/Einspeisung</div>
                                    <div className="text-sm font-bold text-emerald-700">
                                        {testResult.live_metrics.grid_power_w ?? 0} W
                                    </div>
                                </div>
                                <div className="bg-white/80 p-2 rounded-lg border border-emerald-100">
                                    <div className="text-gray-500 text-[10px]">Hausverbrauch</div>
                                    <div className="text-sm font-bold text-emerald-700">
                                        {testResult.live_metrics.load_power_w ?? 0} W
                                    </div>
                                </div>
                                <div className="bg-white/80 p-2 rounded-lg border border-emerald-100">
                                    <div className="text-gray-500 text-[10px]">Batterie-SoC</div>
                                    <div className="text-sm font-bold text-emerald-700">
                                        {testResult.live_metrics.battery_soc ?? "-"} %
                                    </div>
                                </div>
                            </div>
                        )}
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

                {/* Buttons */}
                <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
                    <button
                        type="button"
                        onClick={handleTestConnection}
                        disabled={isTesting}
                        className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 text-xs font-bold rounded-xl transition cursor-pointer flex items-center gap-1.5"
                    >
                        {isTesting ? "⏳ Teste Verbindung..." : "🔌 Verbindung testen"}
                    </button>

                    <button
                        type="button"
                        onClick={handleIntegrate}
                        disabled={isSaving}
                        className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-xs transition cursor-pointer flex items-center gap-1.5"
                    >
                        {isSaving ? "⏳ Speichere..." : "🚀 Jetzt mit Sharegy verbinden"}
                    </button>
                </div>
            </div>
        </div>
    );
}
