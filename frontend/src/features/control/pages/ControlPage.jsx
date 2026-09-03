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

    const [editStorage, setEditStorage] = useState(null);
    const [editParams, setEditParams] = useState({
        target_charge_power_kw: 3.0,
        price_threshold_ct: 15.0,
        min_soc_reserve_pct: 10.0,
    });

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

    const handleSaveParams = async () => {
        if (!editStorage) return;
        if (!isPro) {
            setProModalOpen(true);
            return;
        }

        setSubmittingId(editStorage.id);
        setSuccessMessage(null);
        setErrorMessage(null);

        try {
            const res = await apiFetch(`/api/producer/storage/${editStorage.id}/control/`, {
                method: "POST",
                body: JSON.stringify({
                    target_charge_power_kw: parseFloat(editParams.target_charge_power_kw),
                    price_threshold_ct: parseFloat(editParams.price_threshold_ct),
                    min_soc_reserve_pct: parseFloat(editParams.min_soc_reserve_pct),
                    ems_control_enabled: true,
                }),
            });
            setSuccessMessage(res.message || "EMS-Regelparameter erfolgreich gespeichert.");
            setEditStorage(null);
            queryClient.invalidateQueries({ queryKey: ["storages"] });
        } catch (err) {
            setErrorMessage(err.message || "Fehler beim Speichern der Regelparameter.");
        } finally {
            setSubmittingId(null);
        }
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6 animate-fade-in text-gray-900">
            {/* =========================================================
                PAGE HEADER
            ========================================================= */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-200 pb-5">
                <div>
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-2xl bg-indigo-600 text-white flex items-center justify-center text-xl shadow-xs shrink-0">
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
                                {t("control.subtitle", "Intelligentes EMS-Management für Batteriespeicher, dynamische Börsenstromtarife und Lastmanagement.")}
                            </p>
                        </div>
                    </div>
                </div>

                {!isPro && (
                    <button
                        type="button"
                        onClick={() => setProModalOpen(true)}
                        className="px-4 py-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-black text-xs rounded-xl shadow-xs transition flex items-center gap-2 cursor-pointer self-start sm:self-auto"
                    >
                        <span>⭐</span>
                        <span>{t("control.unlock_pro", "Pro-Steuerung freischalten")}</span>
                    </button>
                )}
            </div>

            {/* Notifications */}
            {successMessage && (
                <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium flex items-center justify-between shadow-2xs">
                    <span className="flex items-center gap-2">
                        <span className="text-base">✅</span> {successMessage}
                    </span>
                    <button type="button" onClick={() => setSuccessMessage(null)} className="text-emerald-600 hover:text-emerald-900 cursor-pointer p-1">✕</button>
                </div>
            )}

            {errorMessage && (
                <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium flex items-center justify-between shadow-2xs">
                    <span className="flex items-center gap-2">
                        <span className="text-base">⚠️</span> {errorMessage}
                    </span>
                    <button type="button" onClick={() => setErrorMessage(null)} className="text-rose-600 hover:text-rose-900 cursor-pointer p-1">✕</button>
                </div>
            )}

            {/* =========================================================
                SEKTION 1: BATTERIESPEICHER STEUERUNG (PRO FEATURE)
            ========================================================= */}
            <div className="bg-white border border-gray-200/80 rounded-3xl p-6 shadow-xs space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-100 pb-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-xl shadow-2xs shrink-0">
                            🔋
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-base font-bold text-gray-900">
                                    {t("control.storage_title", "Hausspeicher-Betriebsmodi & Live-Regelung")}
                                </h2>
                                <ProBadge size="xs" />
                            </div>
                            <p className="text-xs text-gray-500 mt-0.5">
                                {t("control.storage_subtitle", "Wähle das Regelverhalten deines Heimspeichers (z. B. Sungrow SH-Serie, SBR-Speicher oder Modbus-Geräte).")}
                            </p>
                        </div>
                    </div>

                    <a
                        href="/app/producers"
                        className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition flex items-center gap-1 self-start sm:self-auto"
                    >
                        <span>Speicher-Parameter verwalten</span>
                        <span>→</span>
                    </a>
                </div>

                {storagesQuery.isLoading ? (
                    <div className="p-8 bg-slate-50 rounded-2xl border border-slate-100 animate-pulse space-y-3">
                        <div className="h-5 bg-slate-200 rounded w-1/4" />
                        <div className="h-20 bg-slate-100 rounded-xl" />
                    </div>
                ) : storages.length === 0 ? (
                    <div className="p-8 text-center bg-gray-50/80 rounded-2xl border border-dashed border-gray-300 space-y-3">
                        <span className="text-3xl">🔋</span>
                        <div className="text-sm font-bold text-gray-800">Kein Batteriespeicher konfiguriert</div>
                        <p className="text-xs text-gray-500 max-w-md mx-auto">
                            Verbinde deinen Wechselrichter & Speicher unter <a href="/app/interfaces" className="text-indigo-600 font-semibold underline">Schnittstellen</a> (z. B. 1-Klick Sungrow) oder erstelle das System unter <a href="/app/producers" className="text-indigo-600 font-semibold underline">Erzeuger & Speicher</a>.
                        </p>
                    </div>
                ) : (
                    <div className="space-y-6">
                        {storages.map((storage) => {
                            const isPending = submittingId === storage.id;
                            const liveSoc = storage.live_soc_pct;
                            const livePower = storage.live_power_w;

                            return (
                                <div key={storage.id} className="p-5 sm:p-6 rounded-3xl bg-linear-to-br from-slate-900 via-slate-950 to-slate-900 text-white border border-slate-800 shadow-xl space-y-6">
                                    {/* Storage Header Bar */}
                                    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
                                        <div className="flex items-center gap-3.5">
                                            <div className="w-11 h-11 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-2xl shadow-inner">
                                                🔋
                                            </div>
                                            <div>
                                                <div className="font-bold text-base sm:text-lg text-white flex items-center gap-2">
                                                    <span>{storage.name}</span>
                                                    <span className="text-xs font-mono font-normal text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-800/60">
                                                        {storage.capacity_kwh} kWh
                                                    </span>
                                                </div>
                                                <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400 font-mono mt-0.5">
                                                    <span>Ladestand: <strong className="text-white">{liveSoc !== null && liveSoc !== undefined ? `${liveSoc}%` : "-"}</strong></span>
                                                    <span>·</span>
                                                    <span>Fluss: <strong className={livePower < -30 ? "text-emerald-400" : livePower > 30 ? "text-blue-400" : "text-slate-300"}>
                                                        {livePower ? `${(Math.abs(livePower) / 1000).toFixed(2)} kW (${livePower < -30 ? "Laden" : "Entladen"})` : "Standby"}
                                                    </strong></span>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-2.5">
                                            <div className="text-right">
                                                <div className="text-[10px] uppercase font-bold tracking-wider text-slate-400">EMS-Status</div>
                                                <span className={`inline-flex items-center gap-1.5 text-[11px] font-bold px-2.5 py-0.5 rounded-full border mt-0.5 ${
                                                    storage.ems_control_enabled 
                                                        ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30 shadow-xs" 
                                                        : "bg-slate-800 text-slate-400 border-slate-700"
                                                }`}>
                                                    <span className={`w-1.5 h-1.5 rounded-full ${storage.ems_control_enabled ? "bg-emerald-400 animate-pulse" : "bg-slate-500"}`} />
                                                    {storage.ems_control_enabled ? "Aktiv geregelt" : "Standby"}
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* 3 BETRIEBSMODI KARTEN */}
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
                                        {/* Modus 1: PV-Autarkie */}
                                        <div className={`p-4 sm:p-5 rounded-2xl border flex flex-col justify-between space-y-4 transition ${
                                            storage.control_mode === "self_consumption"
                                                ? "bg-emerald-950/40 border-emerald-500 ring-2 ring-emerald-400/40 shadow-lg shadow-emerald-950/50"
                                                : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                                        }`}>
                                            <div className="space-y-2">
                                                <div className="flex items-center justify-between font-bold text-sm">
                                                    <span className="flex items-center gap-1.5 text-white">
                                                        <span>☀️</span>
                                                        <span>PV-Autarkie</span>
                                                    </span>
                                                    {storage.control_mode === "self_consumption" && (
                                                        <span className="text-[10px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500 text-slate-950">
                                                            Aktiv
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="text-xs text-slate-400 leading-relaxed">
                                                    Lädt ausschließlich mit eigenem Solar-Überschuss. Kein kostenpflichtiger Netzstrombezug für die Batterie.
                                                </p>
                                            </div>

                                            <button
                                                type="button"
                                                disabled={isPending || storage.control_mode === "self_consumption"}
                                                onClick={() => handleModeSwitch(storage.id, "self_consumption")}
                                                className={`w-full py-2.5 px-3 rounded-xl text-xs font-bold transition cursor-pointer flex items-center justify-center gap-1.5 ${
                                                    storage.control_mode === "self_consumption"
                                                        ? "bg-emerald-600 text-white cursor-default shadow-xs"
                                                        : "bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/60"
                                                }`}
                                            >
                                                {storage.control_mode === "self_consumption" ? "✓ Modus ist aktiv" : "Autarkie-Modus wählen"}
                                            </button>
                                        </div>

                                        {/* Modus 2: Preisgeführt (Dynamischer Tarif) */}
                                        <div className={`p-4 sm:p-5 rounded-2xl border flex flex-col justify-between space-y-4 transition ${
                                            storage.control_mode === "price_optimized"
                                                ? "bg-blue-950/50 border-blue-500 ring-2 ring-blue-400/40 shadow-lg shadow-blue-950/50"
                                                : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                                        }`}>
                                            <div className="space-y-2">
                                                <div className="flex items-center justify-between font-bold text-sm">
                                                    <span className="flex items-center gap-1.5 text-white">
                                                        <span>💶</span>
                                                        <span>Preisgeführt (Tibber/EPEX)</span>
                                                    </span>
                                                    {storage.control_mode === "price_optimized" ? (
                                                        <span className="text-[10px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-blue-500 text-white">
                                                            Aktiv
                                                        </span>
                                                    ) : (
                                                        <ProBadge size="xs" />
                                                    )}
                                                </div>
                                                <p className="text-xs text-slate-300 leading-relaxed">
                                                    Lädt bei niedrigen oder negativen Börsenstrompreisen automatisch voll (&le; {storage.price_threshold_ct || 15.0} ct/kWh).
                                                </p>
                                            </div>

                                            <button
                                                type="button"
                                                disabled={isPending || storage.control_mode === "price_optimized"}
                                                onClick={() => handleModeSwitch(storage.id, "price_optimized")}
                                                className={`w-full py-2.5 px-3 rounded-xl text-xs font-bold transition cursor-pointer flex items-center justify-center gap-1.5 ${
                                                    storage.control_mode === "price_optimized"
                                                        ? "bg-blue-600 text-white cursor-default shadow-xs"
                                                        : "bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/60"
                                                }`}
                                            >
                                                {storage.control_mode === "price_optimized" ? "✓ Modus ist aktiv" : "Preisgeführt wählen"}
                                            </button>
                                        </div>

                                        {/* Modus 3: Sofortladen (Manuell) */}
                                        <div className={`p-4 sm:p-5 rounded-2xl border flex flex-col justify-between space-y-4 transition ${
                                            storage.control_mode === "forced_charge"
                                                ? "bg-amber-950/40 border-amber-500 ring-2 ring-amber-400/40 shadow-lg shadow-amber-950/50"
                                                : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                                        }`}>
                                            <div className="space-y-2">
                                                <div className="flex items-center justify-between font-bold text-sm">
                                                    <span className="flex items-center gap-1.5 text-white">
                                                        <span>⚡</span>
                                                        <span>Sofortladen (Boost)</span>
                                                    </span>
                                                    {storage.control_mode === "forced_charge" && (
                                                        <span className="text-[10px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-500 text-slate-950">
                                                            Lädt
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="text-xs text-slate-400 leading-relaxed">
                                                    Zwangsladung jetzt sofort mit {storage.target_charge_power_kw || 3.0} kW Ladeleistung (z. B. vor Netzausfall oder Sturm).
                                                </p>
                                            </div>

                                            <button
                                                type="button"
                                                disabled={isPending || storage.control_mode === "forced_charge"}
                                                onClick={() => handleModeSwitch(storage.id, "forced_charge")}
                                                className={`w-full py-2.5 px-3 rounded-xl text-xs font-bold transition cursor-pointer flex items-center justify-center gap-1.5 ${
                                                    storage.control_mode === "forced_charge"
                                                        ? "bg-amber-600 text-white cursor-default shadow-xs"
                                                        : "bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/60"
                                                }`}
                                            >
                                                {storage.control_mode === "forced_charge" ? "⚡ Ladevorgang läuft..." : "Jetzt vollmachen"}
                                            </button>
                                        </div>
                                    </div>

                                    {/* EINSTELLUNGEN PARAMETER LEISTE MIT SCHNELL-BEARBEITUNG */}
                                    <div className="pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 flex-1 font-mono">
                                            <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
                                                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">🎯 Soll-Ladeleistung:</span>
                                                <span className="text-sm font-bold text-white">{storage.target_charge_power_kw || 3.0} kW</span>
                                            </div>

                                            <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
                                                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">📉 Börsenpreis-Schwelle:</span>
                                                <span className="text-sm font-bold text-emerald-400">&le; {storage.price_threshold_ct || 15.0} ct/kWh</span>
                                            </div>

                                            <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
                                                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">🛡️ Notstromreserve:</span>
                                                <span className="text-sm font-bold text-amber-400">{storage.min_soc_reserve_pct || 10.0}%</span>
                                            </div>
                                        </div>

                                        <button
                                            type="button"
                                            onClick={() => {
                                                setEditStorage(storage);
                                                setEditParams({
                                                    target_charge_power_kw: storage.target_charge_power_kw || 3.0,
                                                    price_threshold_ct: storage.price_threshold_ct || 15.0,
                                                    min_soc_reserve_pct: storage.min_soc_reserve_pct || 10.0,
                                                });
                                            }}
                                            className="px-4 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-bold rounded-xl transition cursor-pointer flex items-center justify-center gap-1.5 shrink-0"
                                        >
                                            <span>⚙️</span>
                                            <span>Werte anpassen</span>
                                        </button>
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

            {/* =========================================================
                PARAMETER BEARBEITEN MODAL
            ========================================================= */}
            {editStorage && (
                <div className="fixed inset-0 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fade-in">
                    <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-5 border border-slate-200">
                        <div className="flex items-center justify-between border-b border-gray-100 pb-3">
                            <div className="flex items-center gap-2.5">
                                <span className="text-xl">⚙️</span>
                                <h3 className="font-bold text-base text-gray-900">
                                    EMS-Regelparameter: {editStorage.name}
                                </h3>
                            </div>
                            <button
                                type="button"
                                onClick={() => setEditStorage(null)}
                                className="text-gray-400 hover:text-gray-600 p-1 cursor-pointer"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="space-y-4 text-xs">
                            {/* 1. Soll-Ladeleistung */}
                            <div className="space-y-1.5">
                                <div className="flex justify-between font-semibold text-gray-700">
                                    <span>🎯 Soll-Ladeleistung (kW):</span>
                                    <span className="font-mono font-bold text-indigo-600">{editParams.target_charge_power_kw} kW</span>
                                </div>
                                <input
                                    type="number"
                                    step="0.5"
                                    min="0.5"
                                    max="25.0"
                                    value={editParams.target_charge_power_kw}
                                    onChange={(e) => setEditParams({ ...editParams, target_charge_power_kw: e.target.value })}
                                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm font-bold text-gray-900 focus:bg-white focus:ring-2 focus:ring-indigo-500 transition"
                                />
                                <span className="text-[10px] text-gray-400">Leistung, mit der der Speicher bei Netzladung/Sofortladung geladen wird.</span>
                            </div>

                            {/* 2. Börsenpreis-Schwelle */}
                            <div className="space-y-1.5">
                                <div className="flex justify-between font-semibold text-gray-700">
                                    <span>📉 Preisschwelle für Zwangsladung (ct/kWh):</span>
                                    <span className="font-mono font-bold text-emerald-600">&le; {editParams.price_threshold_ct} ct/kWh</span>
                                </div>
                                <input
                                    type="number"
                                    step="0.5"
                                    value={editParams.price_threshold_ct}
                                    onChange={(e) => setEditParams({ ...editParams, price_threshold_ct: e.target.value })}
                                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm font-bold text-gray-900 focus:bg-white focus:ring-2 focus:ring-emerald-500 transition"
                                />
                                <span className="text-[10px] text-gray-400">Liegt der dynamische Strompreis unter dieser Schwelle, lädt der Speicher automatisch aus dem Netz.</span>
                            </div>

                            {/* 3. Notstromreserve SoC */}
                            <div className="space-y-1.5">
                                <div className="flex justify-between font-semibold text-gray-700">
                                    <span>🛡️ Notstrom-Mindestreserve (%):</span>
                                    <span className="font-mono font-bold text-amber-600">{editParams.min_soc_reserve_pct}%</span>
                                </div>
                                <input
                                    type="number"
                                    step="1"
                                    min="5"
                                    max="50"
                                    value={editParams.min_soc_reserve_pct}
                                    onChange={(e) => setEditParams({ ...editParams, min_soc_reserve_pct: e.target.value })}
                                    className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm font-bold text-gray-900 focus:bg-white focus:ring-2 focus:ring-amber-500 transition"
                                />
                                <span className="text-[10px] text-gray-400">Wird der Speicher entladen, stoppt die Entladung bei diesem Ladestand für Stromausfälle.</span>
                            </div>
                        </div>

                        <div className="flex items-center justify-end gap-2 pt-3 border-t border-gray-100">
                            <button
                                type="button"
                                onClick={() => setEditStorage(null)}
                                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold text-xs rounded-xl transition cursor-pointer"
                            >
                                Abbrechen
                            </button>
                            <button
                                type="button"
                                onClick={handleSaveParams}
                                className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl transition cursor-pointer flex items-center gap-1.5 shadow-xs"
                            >
                                <span>Speichern</span>
                            </button>
                        </div>
                    </div>
                </div>
            )}

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
