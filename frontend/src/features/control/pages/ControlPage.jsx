import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import { useSubscription } from "../../../hooks/useSubscription";
import ProBadge from "../../../components/common/ProBadge";
import ProUpgradeModal from "../../../components/common/ProUpgradeModal";
import BatteryArbitrageCard from "../../energy/components/BatteryArbitrageCard";
import EnergyOptimizerCard from "../../energy/components/EnergyOptimizerCard";

export default function ControlPage() {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const queryClient = useQueryClient();

    const [proModalOpen, setProModalOpen] = useState(false);
    const [submittingId, setSubmittingId] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);
    const [errorMessage, setErrorMessage] = useState(null);

    // Speichersysteme laden
    const storagesQuery = useQuery({
        queryKey: ["storages"],
        queryFn: () => apiFetch("/api/producer/storage/"),
        refetchInterval: 10000,
    });

    const storages = Array.isArray(storagesQuery.data) ? storagesQuery.data : [];

    const handleModeSwitch = async (storageId, newMode, extraParams = {}) => {
        if (!isPro) {
            setProModalOpen(true);
            return;
        }

        setSubmittingId(storageId);
        setSuccessMessage(null);
        setErrorMessage(null);

        try {
            const res = await apiFetch(`/api/producer/storage/${storageId}/control/`, {
                method: "POST",
                body: JSON.stringify({
                    control_mode: newMode,
                    ems_control_enabled: true,
                    ...extraParams,
                }),
            });
            setSuccessMessage(res.message || `Modus erfolgreich auf "${newMode}" gesetzt.`);
            queryClient.invalidateQueries({ queryKey: ["storages"] });
            queryClient.invalidateQueries({ queryKey: ["battery-arbitrage"] });
        } catch (err) {
            setErrorMessage(err.message || "Fehler beim Aktivieren der Steuerung.");
        } finally {
            setSubmittingId(null);
        }
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6 animate-fade-in text-gray-900">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-200 pb-5">
                <div>
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-2xl bg-indigo-600 text-white flex items-center justify-center text-xl shadow-xs">
                            🎛️
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
                                    {t("control.title", "Energiesteuerung & Smart-Charging")}
                                </h1>
                                <ProBadge size="sm" />
                            </div>
                            <p className="text-xs text-gray-500 mt-0.5">
                                {t("control.subtitle", "Intelligentes EMS-Management für Batteriespeicher, dynamische Stromtarife und Lastmanagement.")}
                            </p>
                        </div>
                    </div>
                </div>

                {!isPro && (
                    <button
                        onClick={() => setProModalOpen(true)}
                        className="px-4 py-2 bg-linear-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-bold text-xs rounded-xl shadow-xs transition flex items-center gap-2 cursor-pointer"
                    >
                        <span>👑</span>
                        <span>Pro-Funktion freischalten</span>
                    </button>
                )}
            </div>

            {/* Notifications */}
            {successMessage && (
                <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium flex items-center justify-between">
                    <span className="flex items-center gap-2">
                        <span>✅</span> {successMessage}
                    </span>
                    <button onClick={() => setSuccessMessage(null)} className="text-emerald-600 hover:text-emerald-900 cursor-pointer">✕</button>
                </div>
            )}

            {errorMessage && (
                <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium flex items-center justify-between">
                    <span className="flex items-center gap-2">
                        <span>⚠️</span> {errorMessage}
                    </span>
                    <button onClick={() => setErrorMessage(null)} className="text-rose-600 hover:text-rose-900 cursor-pointer">✕</button>
                </div>
            )}

            {/* =========================================================
                SEKTION 1: BATTERIESPEICHER STEUERUNG (PRO FEATURE)
            ========================================================= */}
            <div className="bg-white border border-gray-200 rounded-3xl p-6 shadow-xs space-y-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <span className="text-2xl">🔋</span>
                        <div>
                            <h2 className="text-base font-bold text-gray-900">
                                {t("control.storage_title", "Batteriespeicher-Betriebsmodi")}
                            </h2>
                            <p className="text-xs text-gray-500">
                                {t("control.storage_subtitle", "Wähle das Regelverhalten deines Heimspeichers (z. B. Sungrow SH-Serie oder Modbus-kompatible Systeme).")}
                            </p>
                        </div>
                    </div>
                </div>

                {storages.length === 0 ? (
                    <div className="p-8 text-center bg-gray-50 rounded-2xl border border-dashed border-gray-300 space-y-2">
                        <span className="text-2xl">🔋</span>
                        <div className="text-sm font-bold text-gray-700">Kein Batteriespeicher gefunden</div>
                        <p className="text-xs text-gray-500 max-w-md mx-auto">
                            Verbinde deinen Speicher unter <a href="/app/interfaces" className="text-indigo-600 underline">Schnittstellen</a> oder richte ihn unter <a href="/app/producers" className="text-indigo-600 underline">Erzeuger & Speicher</a> ein.
                        </p>
                    </div>
                ) : (
                    <div className="space-y-6">
                        {storages.map((storage) => {
                            const isPending = submittingId === storage.id;
                            return (
                                <div key={storage.id} className="p-5 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 text-white border border-slate-800 space-y-5">
                                    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-xl">
                                                🔋
                                            </div>
                                            <div>
                                                <div className="font-bold text-base text-white flex items-center gap-2">
                                                    <span>{storage.name}</span>
                                                    <span className="text-xs font-mono font-normal text-slate-400">
                                                        ({storage.capacity_kwh} kWh · SoC: {storage.live_soc_pct ?? "-"}%)
                                                    </span>
                                                </div>
                                                <p className="text-xs text-slate-400 font-mono">
                                                    Aktuell: {storage.status === "charging" ? "Lädt" : storage.status === "discharging" ? "Entlädt" : "Standby"}
                                                    {storage.live_power_w ? ` · ${(Math.abs(storage.live_power_w) / 1000).toFixed(2)} kW` : ""}
                                                </p>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-2">
                                            <span className="text-xs text-slate-400">EMS-Regelung:</span>
                                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                                                storage.ems_control_enabled 
                                                    ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" 
                                                    : "bg-slate-700 text-slate-400 border-slate-600"
                                            }`}>
                                                {storage.ems_control_enabled ? "Aktiviert" : "Standby"}
                                            </span>
                                        </div>
                                    </div>

                                    {/* MODI KARTEN */}
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                        {/* Modus 1: PV-Autarkie */}
                                        <div className={`p-4 rounded-xl border flex flex-col justify-between space-y-3 ${
                                            storage.control_mode === "self_consumption"
                                                ? "bg-emerald-950/50 border-emerald-500 ring-2 ring-emerald-400/40"
                                                : "bg-slate-900 border-slate-800"
                                        }`}>
                                            <div>
                                                <div className="flex items-center justify-between font-bold text-sm">
                                                    <span>☀️ PV-Autarkie (Autonom)</span>
                                                    {storage.control_mode === "self_consumption" && <span className="text-emerald-400 text-xs">✓ Aktiv</span>}
                                                </div>
                                                <p className="text-xs text-slate-400 mt-1">
                                                    Lädt ausschließlich mit eigenem Solar-Überschuss. Kein Zukauf von Netzstrom für den Speicher.
                                                </p>
                                            </div>

                                            <button
                                                disabled={isPending || storage.control_mode === "self_consumption"}
                                                onClick={() => handleModeSwitch(storage.id, "self_consumption")}
                                                className={`w-full py-2 px-3 rounded-lg text-xs font-bold transition cursor-pointer ${
                                                    storage.control_mode === "self_consumption"
                                                        ? "bg-emerald-600 text-white cursor-default"
                                                        : "bg-slate-800 hover:bg-slate-700 text-slate-200"
                                                }`}
                                            >
                                                {storage.control_mode === "self_consumption" ? "Aktiv geschaltet" : "Modus wählen"}
                                            </button>
                                        </div>

                                        {/* Modus 2: Preisgeführt (Dynamischer Tarif) */}
                                        <div className={`p-4 rounded-xl border flex flex-col justify-between space-y-3 ${
                                            storage.control_mode === "price_optimized"
                                                ? "bg-blue-950/60 border-blue-500 ring-2 ring-blue-400/40"
                                                : "bg-slate-900 border-slate-800"
                                        }`}>
                                            <div>
                                                <div className="flex items-center justify-between font-bold text-sm text-white">
                                                    <span className="flex items-center gap-1.5">
                                                        <span>💶 Preisgeführt (Tibber/EPEX)</span>
                                                        <ProBadge size="xs" />
                                                    </span>
                                                    {storage.control_mode === "price_optimized" && <span className="text-blue-400 text-xs">✓ Aktiv</span>}
                                                </div>
                                                <p className="text-xs text-slate-300 mt-1">
                                                    Lädt bei niedrigen oder negativen Börsenstrompreisen automatisch aus dem Netz voll (&le; {storage.price_threshold_ct || 15.0} ct/kWh).
                                                </p>
                                            </div>

                                            <button
                                                disabled={isPending || storage.control_mode === "price_optimized"}
                                                onClick={() => handleModeSwitch(storage.id, "price_optimized")}
                                                className={`w-full py-2 px-3 rounded-lg text-xs font-bold transition cursor-pointer ${
                                                    storage.control_mode === "price_optimized"
                                                        ? "bg-blue-600 text-white cursor-default"
                                                        : "bg-slate-800 hover:bg-slate-700 text-slate-200"
                                                }`}
                                            >
                                                {storage.control_mode === "price_optimized" ? "Aktiv geschaltet" : "Modus wählen"}
                                            </button>
                                        </div>

                                        {/* Modus 3: Sofortladen (Manuell) */}
                                        <div className={`p-4 rounded-xl border flex flex-col justify-between space-y-3 ${
                                            storage.control_mode === "forced_charge"
                                                ? "bg-amber-950/50 border-amber-500 ring-2 ring-amber-400/40"
                                                : "bg-slate-900 border-slate-800"
                                        }`}>
                                            <div>
                                                <div className="flex items-center justify-between font-bold text-sm text-white">
                                                    <span>⚡ Sofortladen (Boost)</span>
                                                    {storage.control_mode === "forced_charge" && <span className="text-amber-400 text-xs">✓ Aktiv</span>}
                                                </div>
                                                <p className="text-xs text-slate-400 mt-1">
                                                    Zwangsladung jetzt sofort mit {storage.target_charge_power_kw || 3.0} kW Ladeleistung (z. B. vor Netzausfall oder Sturm).
                                                </p>
                                            </div>

                                            <button
                                                disabled={isPending || storage.control_mode === "forced_charge"}
                                                onClick={() => handleModeSwitch(storage.id, "forced_charge")}
                                                className={`w-full py-2 px-3 rounded-lg text-xs font-bold transition cursor-pointer ${
                                                    storage.control_mode === "forced_charge"
                                                        ? "bg-amber-600 text-white cursor-default"
                                                        : "bg-slate-800 hover:bg-slate-700 text-slate-200"
                                                }`}
                                            >
                                                {storage.control_mode === "forced_charge" ? "Ladevorgang läuft" : "Jetzt vollmachen"}
                                            </button>
                                        </div>
                                    </div>

                                    {/* EINSTELLUNGEN REGLER */}
                                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-3 border-t border-slate-800 text-xs text-slate-300 font-mono">
                                        <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800">
                                            <span className="text-[11px] text-slate-400 block mb-1">🎯 Soll-Ladeleistung:</span>
                                            <span className="text-sm font-bold text-white">{storage.target_charge_power_kw || 3.0} kW</span>
                                        </div>

                                        <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800">
                                            <span className="text-[11px] text-slate-400 block mb-1">📉 Börsenpreis-Schwelle:</span>
                                            <span className="text-sm font-bold text-emerald-400">&le; {storage.price_threshold_ct || 15.0} ct/kWh</span>
                                        </div>

                                        <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800">
                                            <span className="text-[11px] text-slate-400 block mb-1">🛡️ Notstromreserve (Min SoC):</span>
                                            <span className="text-sm font-bold text-amber-400">{storage.min_soc_reserve_pct || 10.0}%</span>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* =========================================================
                SEKTION 2: DYNAMISCHE TARIF-ARBITRAGE & ZEITFENSTER-PLANER
            ========================================================= */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <BatteryArbitrageCard />
                <EnergyOptimizerCard />
            </div>

            {/* Pro Upgrade Modal */}
            <ProUpgradeModal
                open={proModalOpen}
                onClose={() => setProModalOpen(false)}
                featureName="Energiesteuerung & Smart-Charging"
                featureDesc="Nutze die automatische Preis-Arbitrage mit dynamischen Tarifen (Tibber/EPEX), automatische Zwangsladung bei Tiefstpreisen und aktive Steuerung deiner Hausspeicher."
            />
        </div>
    );
}
