import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

const BRAND_PRESETS = [
    {
        id: "go-e",
        name: "go-eCharger",
        models: ["Gemini", "Gemini flex", "HOMEfix", "HOME+"],
        icon: "🔌",
        hint: "In der go-e App unter 'Einstellungen' > 'OCPP' die Server-URL eintragen und aktivieren.",
    },
    {
        id: "easee",
        name: "Easee",
        models: ["Charge Lite", "Equalizer", "Charge Max", "One"],
        icon: "⚡",
        hint: "Im Easee Cloud Portal oder Installer-App den Betreiber auf OCPP 1.6-J (Sharegy) setzen.",
    },
    {
        id: "keba",
        name: "Keba KeContact",
        models: ["P30 x-series", "P30 c-series", "P40"],
        icon: "🏢",
        hint: "Im Keba Webinterface unter 'OCPP Communication' die WebSocket-URL und ChargePoint-ID eintragen.",
    },
    {
        id: "alfen",
        name: "Alfen",
        models: ["Eve Single Pro-line", "Eve Single S-line", "Eve Double Pro-line"],
        icon: "🇳🇱",
        hint: "Mit dem Alfen Service Installer Tool das Backend-Profil auf Sharegy WSS konfigurieren.",
    },
    {
        id: "mennekes",
        name: "Mennekes",
        models: ["AMTRON Professional", "AMTRON Charge Control", "AMEDIO"],
        icon: "🇩🇪",
        hint: "Im Mennekes Web-Manager unter 'Backend / OCPP' die WebSocket-Verbindung hinterlegen.",
    },
    {
        id: "zaptec",
        name: "Zaptec",
        models: ["Zaptec Go", "Zaptec Pro"],
        icon: "🇳🇴",
        hint: "Im Zaptec Portal unter 'Installationen' > 'Authentifizierung' die OCPP 1.6-J Cloud anbinden.",
    },
    {
        id: "heidelberg",
        name: "Heidelberg / Amperfied",
        models: ["Energy Control", "Wallbox connect.solar"],
        icon: "🔋",
        hint: "Im Konfigurations-Interface unter OCPP Backend die generierte WSS-Adresse einfügen.",
    },
    {
        id: "openwb",
        name: "openWB",
        models: ["series2 standard+", "series2 custom", "pro"],
        icon: "🐧",
        hint: "In den openWB Einstellungen unter 'Lademodus / OCPP Client' die Verbindung aktivieren.",
    },
    {
        id: "custom",
        name: "Andere Wallbox (OCPP 1.6-J)",
        models: ["Standard OCPP 1.6-J / JSON"],
        icon: "🌐",
        hint: "Jede Wallbox mit OCPP 1.6-JSON Unterstützung kann direkt verbunden werden.",
    },
];

export default function AddWallboxModal({ isOpen, onClose, onCreated }) {
    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const [selectedBrand, setSelectedBrand] = useState(BRAND_PRESETS[0]);
    const [name, setName] = useState("Meine Wallbox");
    const [chargePointId, setChargePointId] = useState(
        `WB-${Math.random().toString(36).substring(2, 7).toUpperCase()}`
    );
    const [maxCurrentA, setMaxCurrentA] = useState(16);
    const [phases, setPhases] = useState(3);
    const [smartMode, setSmartMode] = useState("pv_surplus");
    const [copied, setCopied] = useState(false);
    const [error, setError] = useState(null);

    // Generierte WebSocket OCPP URL
    const host = window.location.hostname || "sharegy.de";
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ocppWsUrl = `${wsProtocol}//${host}/ocpp/${chargePointId}`;

    const createMutation = useMutation({
        mutationFn: async (payload) => {
            return apiFetch("/api/energy/wallboxes/", {
                method: "POST",
                body: JSON.stringify(payload),
            });
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["wallboxes"] });
            if (onCreated) onCreated(data);
            onClose();
        },
        onError: (err) => {
            setError(err.message || "Fehler beim Registrieren der Wallbox.");
        },
    });

    const handleCopyUrl = async () => {
        try {
            await navigator.clipboard.writeText(ocppWsUrl);
            setCopied(true);
            setTimeout(() => setCopied(false), 3000);
        } catch (e) {
            // Fallback
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setError(null);

        createMutation.mutate({
            name: name || `${selectedBrand.name} Wallbox`,
            charge_point_id: chargePointId.trim(),
            vendor: selectedBrand.name,
            model: selectedBrand.models[0] || "OCPP 1.6-J",
            max_current_a: Number(maxCurrentA),
            phases: Number(phases),
            smart_charging_mode: smartMode,
        });
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
                {/* Modal Header */}
                <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
                    <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                            <span className="text-xl">🔌</span>
                        </div>
                        <div>
                            <h3 className="text-base font-bold text-white flex items-center gap-2">
                                Wallbox verbinden (OCPP 1.6-J)
                                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                                    Zero-Hardware
                                </span>
                            </h3>
                            <p className="text-xs text-slate-400">
                                Direkte Cloud-Anbindung ohne Raspberry Pi oder Zusatzmodule.
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800 transition-colors"
                    >
                        ✕
                    </button>
                </div>

                {/* Form Body */}
                <form onSubmit={handleSubmit} className="p-6 overflow-y-auto space-y-5">
                    {error && (
                        <div className="p-3 bg-red-950/50 border border-red-500/40 rounded-xl text-xs text-red-300">
                            ⚠️ {error}
                        </div>
                    )}

                    {/* 1. Hersteller / Marke auswählen */}
                    <div>
                        <label className="block text-xs font-semibold text-slate-300 mb-2">
                            1. Hersteller / Modell wählen
                        </label>
                        <div className="grid grid-cols-3 sm:grid-cols-3 gap-2">
                            {BRAND_PRESETS.map((brand) => (
                                <button
                                    key={brand.id}
                                    type="button"
                                    onClick={() => {
                                        setSelectedBrand(brand);
                                        if (name === "Meine Wallbox" || BRAND_PRESETS.some((b) => name.startsWith(b.name))) {
                                            setName(`${brand.name} Wallbox`);
                                        }
                                    }}
                                    className={`p-2.5 rounded-xl border text-left transition-all flex items-center gap-2 ${
                                        selectedBrand.id === brand.id
                                            ? "bg-emerald-500/10 border-emerald-500/60 text-emerald-300 shadow-md ring-1 ring-emerald-500/30"
                                            : "bg-slate-950/40 border-slate-800 text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
                                    }`}
                                >
                                    <span className="text-lg">{brand.icon}</span>
                                    <span className="text-xs font-semibold truncate">{brand.name}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* 2. OCPP Verbindungs-URL & ID */}
                    <div className="bg-slate-950/80 border border-emerald-500/30 rounded-xl p-4 relative overflow-hidden">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                                2. Deine persönliche OCPP WebSocket URL
                            </span>
                            <span className="text-[10px] text-slate-400 font-mono">Port 443 (SSL/WSS)</span>
                        </div>

                        <div className="flex items-center gap-2 bg-slate-900 border border-slate-700/80 rounded-lg p-2.5 mb-2">
                            <input
                                readOnly
                                value={ocppWsUrl}
                                className="bg-transparent text-xs font-mono text-emerald-300 w-full focus:outline-none select-all"
                            />
                            <button
                                type="button"
                                onClick={handleCopyUrl}
                                className="px-3 py-1 rounded-md text-xs font-semibold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition-all flex items-center gap-1 shrink-0 font-bold"
                            >
                                {copied ? "✓ Kopiert!" : "📋 Kopieren"}
                            </button>
                        </div>

                        <p className="text-[11px] text-slate-300 leading-relaxed flex items-start gap-1.5 mt-2">
                            <span>💡</span>
                            <span>{selectedBrand.hint}</span>
                        </p>
                    </div>

                    {/* 3. Parameter-Konfiguration */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-xs font-medium text-slate-300 mb-1">
                                Anzeigename
                            </label>
                            <input
                                type="text"
                                required
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                                placeholder="z. B. Garage Easee"
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-slate-300 mb-1">
                                Charge Point ID (Kennung)
                            </label>
                            <input
                                type="text"
                                required
                                value={chargePointId}
                                onChange={(e) => setChargePointId(e.target.value.toUpperCase())}
                                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-emerald-500"
                                placeholder="z. B. WB-01"
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-slate-300 mb-1">
                                Max. Stromstärke (Absicherung)
                            </label>
                            <select
                                value={maxCurrentA}
                                onChange={(e) => setMaxCurrentA(e.target.value)}
                                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                            >
                                <option value="16">16 A (11 kW bei 3 Phasen)</option>
                                <option value="32">32 A (22 kW bei 3 Phasen)</option>
                                <option value="10">10 A (Schuko / Reduziert)</option>
                                <option value="13">13 A</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-slate-300 mb-1">
                                Standard-Lademodus
                            </label>
                            <select
                                value={smartMode}
                                onChange={(e) => setSmartMode(e.target.value)}
                                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                            >
                                <option value="pv_surplus">☀️ Nur PV-Überschuss (100% Solar)</option>
                                <option value="min_pv">⛅ Min + PV-Überschuss (Basis 6A)</option>
                                <option value="spot_price">💶 Börsenpreisgeführt</option>
                                <option value="instant">⚡ Sofortladen (Volle Leistung)</option>
                            </select>
                        </div>
                    </div>

                    {/* Modal Footer */}
                    <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white transition-colors"
                        >
                            Abbrechen
                        </button>
                        <button
                            type="submit"
                            disabled={createMutation.isPending}
                            className="px-5 py-2.5 rounded-xl text-xs font-bold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition-all shadow-lg shadow-emerald-500/20 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
                        >
                            {createMutation.isPending ? "Registriere..." : "Wallbox anlegen & verbinden 🚀"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
