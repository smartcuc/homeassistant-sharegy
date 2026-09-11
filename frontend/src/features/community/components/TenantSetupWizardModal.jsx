/*
# src/features/community/components/TenantSetupWizardModal.jsx
# Geführter 3-Schritte Gebäude-Einrichtungs-Assistent für Vermieter & WEGs (Laien-verständlich)
*/

import { useState } from "react";
import { apiFetch } from "../../../api/client";

export default function TenantSetupWizardModal({ isOpen, onClose, onComplete, existingTenant }) {
    const [step, setStep] = useState(1);
    const [saving, setSaving] = useState(false);

    // Schritt 1: Gebäude & Photovoltaik
    const [buildingData, setBuildingData] = useState({
        name: existingTenant?.name || "Sonnengarten Quartier 1",
        address: existingTenant?.address || "Sonnenallee 42, 10115 Berlin",
        pv_capacity_kwp: existingTenant?.pv_capacity_kwp || 25,
        battery_capacity_kwh: existingTenant?.battery_capacity_kwh || 15,
        allocation_model: existingTenant?.allocation_model || "dynamic",
    });

    // Schritt 2: Wohnungen & Zähler (Schnellerfassung)
    const [apartments, setApartments] = useState([
        { id: 1, name: "Top 1 (EG links)", email: "schmidt@beispiel.de", mea_share: 25.0, meter_id: "1EMH0011223344" },
        { id: 2, name: "Top 2 (EG rechts)", email: "weber@beispiel.de", mea_share: 25.0, meter_id: "1EMH0011223345" },
        { id: 3, name: "Top 3 (1. OG links)", email: "mueller@beispiel.de", mea_share: 25.0, meter_id: "1EMH0011223346" },
        { id: 4, name: "Top 4 (1. OG rechts)", email: "meier@beispiel.de", mea_share: 25.0, meter_id: "1EMH0011223347" },
    ]);

    // Schritt 3: Einfache Stromtarife
    const [tariffs, setTariffs] = useState({
        solar_rate_ct: 16.0,      // Cent je kWh Solarstrom vom Dach
        grid_rate_ct: 32.0,       // Cent je kWh Zukauf Reststrom vom Netz
        base_fee_monthly_eur: 8.50, // Monatliche Grundgebühr je Partei
    });

    if (!isOpen) return null;

    // Wohnung hinzufügen
    function addApartment() {
        const nextId = apartments.length + 1;
        const equalShare = Number((100 / nextId).toFixed(2));
        setApartments([
            ...apartments.map(a => ({ ...a, mea_share: equalShare })),
            {
                id: Date.now(),
                name: `Top ${nextId} (Wohnung ${nextId})`,
                email: "",
                mea_share: equalShare,
                meter_id: `1EMH001122${nextId + 50}`,
            }
        ]);
    }

    // Wohnung entfernen
    function removeApartment(id) {
        if (apartments.length <= 1) return;
        const remaining = apartments.filter(a => a.id !== id);
        const equalShare = Number((100 / remaining.length).toFixed(2));
        setApartments(remaining.map(a => ({ ...a, mea_share: equalShare })));
    }

    // Wohnung aktualisieren
    function updateApartment(id, field, val) {
        setApartments(apartments.map(a => a.id === id ? { ...a, [field]: val } : a));
    }

    // Gesamtersparnis grob berechnen
    const estimatedYearlySolarKwh = buildingData.pv_capacity_kwp * 950;
    const estimatedSharedKwh = estimatedYearlySolarKwh * 0.75;
    const priceDiffCt = Math.max(0, tariffs.grid_rate_ct - tariffs.solar_rate_ct);
    const estimatedYearlyCommunitySavingsEur = Math.round((estimatedSharedKwh * priceDiffCt) / 100);

    // Speichern
    async function handleFinish() {
        setSaving(true);
        try {
            // Speichern via API
            await apiFetch("/api/billing/community/tariffs/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    tenant_id: existingTenant?.id,
                    solar_rate_ct: tariffs.solar_rate_ct,
                    grid_rate_ct: tariffs.grid_rate_ct,
                    base_fee_monthly_eur: tariffs.base_fee_monthly_eur,
                })
            }).catch(() => null);

            if (onComplete) onComplete({ buildingData, apartments, tariffs });
            onClose();
        } catch (err) {
            console.error("Wizard error:", err);
            onClose();
        } finally {
            setSaving(false);
        }
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-xs animate-fade-in">
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-3xl w-full shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
                
                {/* MODAL HEADER */}
                <div className="p-6 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex items-center justify-between">
                    <div>
                        <div className="flex items-center gap-2">
                            <span className="text-2xl">✨</span>
                            <h2 className="text-lg font-black text-slate-900 dark:text-white">
                                Gebäude-Einrichtungs-Assistent (in 3 einfachen Schritten)
                            </h2>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            Richte dein Mehrfamilienhaus, die Parteien und den Solartarif in unter 3 Minuten ein.
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-lg font-bold p-1 rounded-lg cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                {/* PROGRESS STEPPER */}
                <div className="grid grid-cols-3 border-b border-slate-100 dark:border-slate-800 text-xs font-bold">
                    <button
                        onClick={() => setStep(1)}
                        className={`p-3.5 flex items-center justify-center gap-2 border-b-2 transition cursor-pointer ${
                            step === 1
                                ? "border-indigo-600 text-indigo-600 dark:text-indigo-400 bg-indigo-50/30 dark:bg-indigo-950/20"
                                : "border-transparent text-slate-400 hover:text-slate-600"
                        }`}
                    >
                        <span className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-[10px]">1</span>
                        <span>Gebäude & Solaranlage</span>
                    </button>
                    <button
                        onClick={() => setStep(2)}
                        className={`p-3.5 flex items-center justify-center gap-2 border-b-2 transition cursor-pointer ${
                            step === 2
                                ? "border-indigo-600 text-indigo-600 dark:text-indigo-400 bg-indigo-50/30 dark:bg-indigo-950/20"
                                : "border-transparent text-slate-400 hover:text-slate-600"
                        }`}
                    >
                        <span className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-[10px]">2</span>
                        <span>Wohnungen & Zähler ({apartments.length})</span>
                    </button>
                    <button
                        onClick={() => setStep(3)}
                        className={`p-3.5 flex items-center justify-center gap-2 border-b-2 transition cursor-pointer ${
                            step === 3
                                ? "border-indigo-600 text-indigo-600 dark:text-indigo-400 bg-indigo-50/30 dark:bg-indigo-950/20"
                                : "border-transparent text-slate-400 hover:text-slate-600"
                        }`}
                    >
                        <span className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-[10px]">3</span>
                        <span>Stromtarife & Sparrechnung</span>
                    </button>
                </div>

                {/* BODY CONTENT */}
                <div className="p-6 overflow-y-auto space-y-6 flex-1">
                    
                    {/* ======================================================== */}
                    {/* SCHRITT 1: GEBÄUDE & PV-ANLAGE */}
                    {/* ======================================================== */}
                    {step === 1 && (
                        <div className="space-y-4 animate-fade-in">
                            <div className="bg-indigo-500/10 border border-indigo-500/20 p-4 rounded-2xl">
                                <h3 className="text-sm font-bold text-indigo-900 dark:text-indigo-200 flex items-center gap-1.5">
                                    <span>💡</span> Wie funktioniert das?
                                </h3>
                                <p className="text-xs text-indigo-700/90 dark:text-indigo-300/90 mt-1 leading-relaxed">
                                    Trage hier den Namen deines Gebäudes und die Größe der Solaranlage ein. Sharegy übernimmt automatisch die gesetzliche Aufteilung der Solarenergie nach § 42b EnWG (Gemeinschaftliche Gebäudeversorgung).
                                </p>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        Name der Liegenschaft / WEG
                                    </label>
                                    <input
                                        type="text"
                                        value={buildingData.name}
                                        onChange={(e) => setBuildingData({ ...buildingData, name: e.target.value })}
                                        placeholder="z.B. Mehrfamilienhaus Sonnenweg 8"
                                        className="w-full text-sm font-semibold p-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-indigo-500 dark:text-white"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        Adresse (Straße, PLZ, Ort)
                                    </label>
                                    <input
                                        type="text"
                                        value={buildingData.address}
                                        onChange={(e) => setBuildingData({ ...buildingData, address: e.target.value })}
                                        placeholder="Sonnenallee 42, 10115 Berlin"
                                        className="w-full text-sm font-semibold p-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-indigo-500 dark:text-white"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                                <div>
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        ☀️ PV-Leistung auf dem Dach
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            value={buildingData.pv_capacity_kwp}
                                            onChange={(e) => setBuildingData({ ...buildingData, pv_capacity_kwp: Number(e.target.value) })}
                                            className="w-full text-sm font-bold p-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-xl dark:text-white"
                                        />
                                        <span className="absolute right-3 top-3.5 text-xs text-slate-400 font-bold">kWp</span>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        🔋 Batteriespeicher im Keller
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            value={buildingData.battery_capacity_kwh}
                                            onChange={(e) => setBuildingData({ ...buildingData, battery_capacity_kwh: Number(e.target.value) })}
                                            className="w-full text-sm font-bold p-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-xl dark:text-white"
                                        />
                                        <span className="absolute right-3 top-3.5 text-xs text-slate-400 font-bold">kWh</span>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        ⚖️ Aufteilungs-Logik
                                    </label>
                                    <select
                                        value={buildingData.allocation_model}
                                        onChange={(e) => setBuildingData({ ...buildingData, allocation_model: e.target.value })}
                                        className="w-full text-sm font-semibold p-3 border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-xl dark:text-white cursor-pointer"
                                    >
                                        <option value="dynamic">⚡ Dynamisch (Wer gerade Strom braucht)</option>
                                        <option value="static">📐 Statisch (Nach Wohnungsgröße MEA)</option>
                                        <option value="hybrid">🤝 Hybrid (Feste Quote + Rest teilen)</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* ======================================================== */}
                    {/* SCHRITT 2: WOHNUNGEN & ZÄHLER */}
                    {/* ======================================================== */}
                    {step === 2 && (
                        <div className="space-y-4 animate-fade-in">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                                        Wohnungen & Bewohner ({apartments.length} Einheiten)
                                    </h3>
                                    <p className="text-xs text-slate-500">
                                        Trage hier die Wohnungen und die jeweiligen Stromzähler-Nummern ein.
                                    </p>
                                </div>
                                <button
                                    onClick={addApartment}
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-3 py-2 rounded-xl transition cursor-pointer flex items-center gap-1.5"
                                >
                                    <span>+</span> Wohnung hinzufügen
                                </button>
                            </div>

                            <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
                                {apartments.map((apt) => (
                                    <div
                                        key={apt.id}
                                        className="grid grid-cols-12 gap-2 p-3 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-2xl items-center"
                                    >
                                        <div className="col-span-3">
                                            <input
                                                type="text"
                                                value={apt.name}
                                                onChange={(e) => updateApartment(apt.id, "name", e.target.value)}
                                                placeholder="Wohnungsname"
                                                className="w-full text-xs font-bold p-2 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-lg dark:text-white"
                                            />
                                        </div>
                                        <div className="col-span-3">
                                            <input
                                                type="email"
                                                value={apt.email}
                                                onChange={(e) => updateApartment(apt.id, "email", e.target.value)}
                                                placeholder="mieter@beispiel.de"
                                                className="w-full text-xs p-2 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-lg dark:text-white"
                                            />
                                        </div>
                                        <div className="col-span-3">
                                            <input
                                                type="text"
                                                value={apt.meter_id}
                                                onChange={(e) => updateApartment(apt.id, "meter_id", e.target.value)}
                                                placeholder="Zählernummer"
                                                className="w-full text-xs font-mono p-2 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-lg dark:text-white"
                                            />
                                        </div>
                                        <div className="col-span-2">
                                            <div className="relative">
                                                <input
                                                    type="number"
                                                    value={apt.mea_share}
                                                    onChange={(e) => updateApartment(apt.id, "mea_share", Number(e.target.value))}
                                                    className="w-full text-xs font-bold p-2 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-lg dark:text-white"
                                                />
                                                <span className="absolute right-2 top-2 text-[10px] text-slate-400 font-bold">%</span>
                                            </div>
                                        </div>
                                        <div className="col-span-1 text-right">
                                            <button
                                                onClick={() => removeApartment(apt.id)}
                                                disabled={apartments.length <= 1}
                                                className="text-red-500 hover:text-red-700 text-xs font-bold p-1 rounded hover:bg-red-50 dark:hover:bg-red-950/20 disabled:opacity-30 cursor-pointer"
                                            >
                                                ✕
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* ======================================================== */}
                    {/* SCHRITT 3: STROMTARIFE & SPARSIMULATION */}
                    {/* ======================================================== */}
                    {step === 3 && (
                        <div className="space-y-4 animate-fade-in">
                            <div className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-2xl flex items-center justify-between">
                                <div>
                                    <div className="text-xs font-bold text-emerald-800 dark:text-emerald-300">
                                        🎉 Prognostizierter Gemeinschaftsvorteil
                                    </div>
                                    <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-0.5">
                                        ~{estimatedYearlyCommunitySavingsEur.toLocaleString("de-DE")} € <span className="text-xs font-normal text-slate-500">Ersparnis pro Jahr</span>
                                    </div>
                                </div>
                                <div className="text-3xl">💰</div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                <div className="p-4 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 rounded-2xl">
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        ☀️ Solarstrom-Preis
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            step="0.1"
                                            value={tariffs.solar_rate_ct}
                                            onChange={(e) => setTariffs({ ...tariffs, solar_rate_ct: Number(e.target.value) })}
                                            className="w-full text-base font-black p-3 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl dark:text-white"
                                        />
                                        <span className="absolute right-3 top-3.5 text-xs text-slate-400 font-bold">ct/kWh</span>
                                    </div>
                                    <p className="text-[10px] text-slate-400 mt-1">Was Mieter für den Sonnenstrom zahlen.</p>
                                </div>

                                <div className="p-4 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 rounded-2xl">
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        🔌 Reststrom-Preis
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            step="0.1"
                                            value={tariffs.grid_rate_ct}
                                            onChange={(e) => setTariffs({ ...tariffs, grid_rate_ct: Number(e.target.value) })}
                                            className="w-full text-base font-black p-3 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl dark:text-white"
                                        />
                                        <span className="absolute right-3 top-3.5 text-xs text-slate-400 font-bold">ct/kWh</span>
                                    </div>
                                    <p className="text-[10px] text-slate-400 mt-1">Preis für Netzstrom bei Bewölkung.</p>
                                </div>

                                <div className="p-4 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 rounded-2xl">
                                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                        🏢 Grundgebühr je Partei
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            step="0.5"
                                            value={tariffs.base_fee_monthly_eur}
                                            onChange={(e) => setTariffs({ ...tariffs, base_fee_monthly_eur: Number(e.target.value) })}
                                            className="w-full text-base font-black p-3 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl dark:text-white"
                                        />
                                        <span className="absolute right-3 top-3.5 text-xs text-slate-400 font-bold">€/Monat</span>
                                    </div>
                                    <p className="text-[10px] text-slate-400 mt-1">Für Messstellenbetrieb & Zähler.</p>
                                </div>
                            </div>
                        </div>
                    )}

                </div>

                {/* MODAL FOOTER */}
                <div className="p-5 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex items-center justify-between">
                    <div>
                        {step > 1 && (
                            <button
                                onClick={() => setStep(step - 1)}
                                className="px-4 py-2 text-xs font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition cursor-pointer"
                            >
                                ← Zurück
                            </button>
                        )}
                    </div>

                    <div className="flex gap-2">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 text-xs font-bold text-slate-500 hover:text-slate-700 dark:hover:text-slate-200 cursor-pointer"
                        >
                            Abbrechen
                        </button>

                        {step < 3 ? (
                            <button
                                onClick={() => setStep(step + 1)}
                                className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-5 py-2.5 rounded-xl transition cursor-pointer flex items-center gap-1.5"
                            >
                                Weiter zu Schritt {step + 1} →
                            </button>
                        ) : (
                            <button
                                onClick={handleFinish}
                                disabled={saving}
                                className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-black px-6 py-2.5 rounded-xl transition shadow-md hover:shadow-lg cursor-pointer flex items-center gap-2"
                            >
                                {saving ? "Speichere..." : "🚀 Gebäude jetzt fertigstellen & aktivieren"}
                            </button>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}
