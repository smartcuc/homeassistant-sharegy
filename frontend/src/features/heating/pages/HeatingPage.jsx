import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../../../api/client";
import { useSubscription } from "../../../hooks/useSubscription";
import ProBadge from "../../../components/common/ProBadge";
import ProUpgradeModal from "../../../components/common/ProUpgradeModal";
import FloorHeatingLoadCard from "../../control/components/FloorHeatingLoadCard";
import BWWPLoadManagementCard from "../../energy/components/BWWPLoadManagementCard";
import HeatingRodCard from "../../control/components/HeatingRodCard";
import AirConditioningCard from "../../control/components/AirConditioningCard";

export default function HeatingPage() {
    const { t } = useTranslation();
    const { isPro, proYearlyMonthlyEquiv } = useSubscription();
    const queryClient = useQueryClient();
    const [activeTab, setActiveTab] = useState("all");
    const [actionFeedback, setActionFeedback] = useState(null);
    const [proModalOpen, setProModalOpen] = useState(false);

    // 1. Live Floor Heating Status abfragen für Quick-KPIs
    const fbhQuery = useQuery({
        queryKey: ["floor-heating"],
        queryFn: () => apiFetch("/api/energy/floor-heating/"),
        refetchInterval: 5000,
    });

    // 2. Hub Live-Daten für Verbraucher & Klimaanlagen
    const hubQuery = useQuery({
        queryKey: ["load-management-hub"],
        queryFn: () => apiFetch("/api/energy/load-management/hub/"),
        refetchInterval: 15000,
    });

    // 3. Quick-Action Mutation für Klimaanlage & Aktoren
    const actionMutation = useMutation({
        mutationFn: (payload) =>
            apiFetch("/api/energy/load-management/hub/action/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            }),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["load-management-hub"] });
            queryClient.invalidateQueries({ queryKey: ["floor-heating"] });
            queryClient.invalidateQueries({ queryKey: ["bwwp-load-mgmt"] });
            showFeedback(data.message || "Aktion erfolgreich ausgeführt.");
        },
    });

    const showFeedback = (msg) => {
        setActionFeedback(msg);
        setTimeout(() => setActionFeedback(null), 4000);
    };

    const handleQuickAction = (category, action, deviceId = null, params = {}) => {
        if (!isPro) {
            setProModalOpen(true);
            return;
        }
        actionMutation.mutate({
            category,
            action,
            device_id: deviceId,
            params,
        });
    };

    const fbhData = fbhQuery.data || {};
    const storage = fbhData.storage || {};
    const flow = fbhData.flow_temperature || {};
    const temp = fbhData.temperature || {};
    const isLive = !fbhQuery.isLoading && !fbhQuery.isError && fbhData.config_id;

    const hubData = hubQuery.data || {};
    const consumers = hubData.consumers || [];
    const acConsumers = consumers.filter((c) => c.category === "ac");

    return (
        <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
            {/* Feedback Toast */}
            {actionFeedback && (
                <div className="fixed bottom-6 right-6 z-50 bg-slate-900 text-white text-xs font-bold px-4 py-3 rounded-2xl shadow-2xl border border-indigo-500/40 flex items-center gap-2 animate-slide-up">
                    <span>⚡</span>
                    <span>{actionFeedback}</span>
                </div>
            )}

            {/* 1. Header: Titel & Beschreibung */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
                <div className="flex items-start sm:items-center gap-3.5">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-rose-500 to-amber-500 text-white flex items-center justify-center text-2xl shadow-lg shadow-rose-500/20 shrink-0">
                        🌡️
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h1 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
                                Wärme, Heizung & Raumklima
                            </h1>
                            {!isPro && <ProBadge size="sm" />}
                        </div>
                        <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
                            Wettergeführte Fußbodenheizung (DIN EN 12831 / MPC), thermische Estrich-Speicherbatterie & Wärmepumpen-Lastmanagement.
                        </p>
                    </div>
                </div>

                {!isPro && (
                    <button
                        type="button"
                        onClick={() => setProModalOpen(true)}
                        className="self-start sm:self-auto px-4 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 text-xs font-black rounded-2xl shadow-md shadow-amber-500/20 transition cursor-pointer flex items-center gap-1.5 shrink-0"
                    >
                        <span>⭐</span>
                        <span>Auf Pro upgraden (ab {proYearlyMonthlyEquiv} €/M)</span>
                    </button>
                )}
            </div>

            {/* 👑 PRO PAYWALL HERO BANNER FOR FREE USERS */}
            {!isPro && (
                <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-950 border border-indigo-500/40 rounded-3xl p-8 sm:p-10 shadow-2xl text-white relative overflow-hidden space-y-8 animate-in fade-in duration-300">
                    {/* Background glow */}
                    <div className="absolute top-0 right-0 w-96 h-96 bg-rose-500/15 rounded-full blur-3xl pointer-events-none" />
                    <div className="absolute bottom-0 left-0 w-72 h-72 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

                    <div className="relative z-10 max-w-3xl space-y-4">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-400/30 text-xs font-bold uppercase tracking-wider">
                            <span>⭐</span>
                            <span>Sharegy Pro Exklusiv</span>
                        </div>
                        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-white leading-tight">
                            Nutze deinen Estrich als thermische Batterie & spare bis zu 45% Heizkosten
                        </h2>
                        <p className="text-indigo-200/80 text-sm sm:text-base leading-relaxed">
                            Vorausschauende KI-Wetter-Vorladung (MPC), SG-Ready Warmwasser-Überhitzung bei Solar-Peaks und intelligente Heizstab-Modulation für maximale Autarkie.
                        </p>
                    </div>

                    {/* Features Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 relative z-10">
                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">🧠</div>
                            <h3 className="text-sm font-bold text-white">Predictive MPC Estrich-Vorladung</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Erkennt Kältefronten & Preissprünge 24h im Voraus und lädt deinen Fußboden mit Solarstrom vor.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">🧱</div>
                            <h3 className="text-sm font-bold text-white">Thermische Bauteilaktivierung</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Speichert 10–25 kWh thermische Energie im Betonestrich – ganz ohne teure Zusatzspeicher.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">♨️</div>
                            <h3 className="text-sm font-bold text-white">BWWP SG-Ready Solar-Boost</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Hebt die Warmwasser-Solltemperatur bei Solar-Peaks auf 60–65°C an (inkl. Legionellenschutz).
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">⚡</div>
                            <h3 className="text-sm font-bold text-white">Heizstab Power-to-Heat</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Stufenlose Modulation für Thyristor- und Relais-Heizstäbe für 100% Eigenverbrauchsquote.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">❄️</div>
                            <h3 className="text-sm font-bold text-white">Solares Pre-Cooling (Klimaanlage)</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Kühlt Wohnräume während maximaler Sonnenstunden vor und verhindert teuren Abend-Netzbezug.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">📉</div>
                            <h3 className="text-sm font-bold text-white">Heizkurven-Feinabstimmung</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Automatische Anpassung der Steilheit nach DIN EN 12831 und lokalen Wetterprognosen.
                            </p>
                        </div>
                    </div>

                    {/* CTA Actions */}
                    <div className="pt-4 border-t border-indigo-800/40 relative z-10 flex flex-col sm:flex-row items-center justify-between gap-4">
                        <div className="text-xs text-indigo-200/70 text-center sm:text-left">
                            Bereits ab <strong className="text-white font-mono">{proYearlyMonthlyEquiv} €</strong> / Monat (jährliche Zahlweise) · 14 Tage kostenlos testen · Jederzeit kündbar
                        </div>
                        <div className="flex items-center gap-3 w-full sm:w-auto">
                            <button
                                type="button"
                                onClick={() => setProModalOpen(true)}
                                className="w-full sm:w-auto px-6 py-3.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 text-sm font-black rounded-2xl shadow-xl shadow-amber-500/20 transition cursor-pointer flex items-center justify-center gap-2"
                            >
                                <span>⭐</span>
                                <span>Wärmemanagement mit Sharegy Pro freischalten</span>
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* 🌡️ DASHBOARD CONTENT: ECHTE DATEN BZW. GELOCKTE DEMO-VORSCHAU */}
            <div className={`space-y-6 ${!isPro ? "relative" : ""}`}>
                {!isPro && (
                    <div 
                        onClick={() => setProModalOpen(true)}
                        className="absolute inset-0 z-20 bg-slate-950/20 backdrop-blur-[1.5px] rounded-3xl cursor-pointer flex flex-col items-center justify-start pt-24 p-6 text-center hover:bg-slate-950/30 transition group"
                    >
                        <div className="px-5 py-3 rounded-2xl bg-slate-900/95 border border-indigo-500/40 shadow-2xl text-white flex items-center gap-3 transform group-hover:scale-105 transition">
                            <span className="text-xl">🔒</span>
                            <div className="text-left">
                                <div className="text-xs font-bold text-white flex items-center gap-1.5">
                                    <span>Interaktive Demo-Vorschau</span>
                                    <ProBadge size="xs" />
                                </div>
                                <div className="text-[11px] text-indigo-200/80">
                                    Klicke hier, um alle Wärme- und Estrich-Optionen mit Sharegy Pro freizuschalten
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* 2. Badges & Filter-Tabs unter dem Titel */}
                <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
                    {/* Status Badges */}
                    <div className="flex flex-wrap items-center gap-2">
                        <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800 flex items-center gap-1.5">
                            <span>🔥</span>
                            <span>Thermische Speicher & MPC</span>
                        </span>

                        {isLive ? (
                            <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 flex items-center gap-1.5">
                                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                <span>Live-Steuerung aktiv ({fbhData.control_mode_display || "Autopilot"})</span>
                            </span>
                        ) : fbhQuery.isLoading ? (
                            <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800 flex items-center gap-1.5">
                                <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping" />
                                <span>Verbinde mit Heizkreis...</span>
                            </span>
                        ) : (
                            <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 flex items-center gap-1.5">
                                <span>⚙️</span>
                                <span>Bereit</span>
                            </span>
                        )}

                        {fbhData.is_preheating_active && (
                            <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30 flex items-center gap-1.5">
                                <span>⚡</span>
                                <span>Estrich-Vorladeboost aktiv</span>
                            </span>
                        )}
                    </div>

                    {/* Filter Tabs */}
                    <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
                        {[
                            { key: "all", label: "Alle Heizsysteme", icon: "♨️" },
                            { key: "fbh", label: "Fußbodenheizung", icon: "🌡️" },
                            { key: "bwwp", label: "Brauchwasser & WP", icon: "🔥" },
                            { key: "ac_rod", label: "Klima & Heizstab", icon: "❄️" },
                        ].map((tab) => (
                            <button
                                key={tab.key}
                                type="button"
                                onClick={() => setActiveTab(tab.key)}
                                className={`px-3.5 py-1.5 rounded-2xl text-xs font-bold transition flex items-center gap-1.5 shrink-0 cursor-pointer ${
                                    activeTab === tab.key
                                        ? "bg-rose-600 text-white shadow-md shadow-rose-600/20"
                                        : "bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
                                }`}
                            >
                                <span>{tab.icon}</span>
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </div>
                </div>

            {/* 3. Quick Thermal Metrics Overview */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
                    <div className="w-11 h-11 rounded-2xl bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 flex items-center justify-center text-xl shrink-0">
                        🧱
                    </div>
                    <div>
                        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Estrich-Speichermasse</div>
                        <div className="text-base font-black text-slate-900 dark:text-white font-mono">
                            {storage.estrich_mass_kg ? (storage.estrich_mass_kg / 1000).toFixed(1) : "—"} <span className="text-xs font-normal text-slate-500">t Beton</span>
                        </div>
                        <div className="text-[11px] text-slate-500">
                            {storage.thermal_capacity_kwh_k ? `${storage.thermal_capacity_kwh_k} kWh/K Kapazität` : "Berechne..."}
                        </div>
                    </div>
                </div>

                <div className="p-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
                    <div className="w-11 h-11 rounded-2xl bg-rose-50 dark:bg-rose-950/50 text-rose-600 dark:text-rose-400 flex items-center justify-center text-xl shrink-0">
                        🔥
                    </div>
                    <div>
                        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Thermischer Ladezustand</div>
                        <div className="text-base font-black text-slate-900 dark:text-white font-mono">
                            {storage.thermal_soc_pct !== undefined ? `${storage.thermal_soc_pct}%` : "—"} <span className="text-xs font-normal text-slate-500">SoC</span>
                        </div>
                        <div className="text-[11px] text-rose-600 dark:text-rose-400 font-bold">
                            {storage.stored_energy_kwh_th !== undefined ? `${storage.stored_energy_kwh_th} kWh th. geladen` : "Berechne..."}
                        </div>
                    </div>
                </div>

                <div className="p-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
                    <div className="w-11 h-11 rounded-2xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-xl shrink-0">
                        📉
                    </div>
                    <div>
                        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">MPC Vorlauftemperatur</div>
                        <div className="text-base font-black text-slate-900 dark:text-white font-mono">
                            {flow.opt_flow_temp_c !== undefined ? `${flow.opt_flow_temp_c}°C` : "—"} <span className="text-xs font-normal text-slate-500">Soll</span>
                        </div>
                        <div className="text-[11px] text-indigo-600 dark:text-indigo-400 font-medium">
                            {flow.solar_offset_k > 0 
                                ? `☀️ -${flow.solar_offset_k} K Sonnengewinn` 
                                : `Heizkurve ${flow.heating_curve_slope || "0.60"}`}
                        </div>
                    </div>
                </div>

                <div className="p-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
                    <div className="w-11 h-11 rounded-2xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-xl shrink-0">
                        🛋️
                    </div>
                    <div>
                        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Raumtemperatur</div>
                        <div className="text-base font-black text-slate-900 dark:text-white font-mono">
                            {temp.current_c !== undefined ? `${temp.current_c}°C` : "—"} <span className="text-xs font-normal text-slate-500">Ist</span>
                        </div>
                        <div className="text-[11px] text-slate-500">
                            {temp.target_c !== undefined ? `Sollwert: ${temp.target_c}°C` : "Soll: 21.0°C"}
                        </div>
                    </div>
                </div>
            </div>

            {/* 4. Main Cards Layout: FBH oben, Brauchwasser & Klimaanlage NEBENEINANDER */}
            <div className="space-y-6">
                {/* 🌡️ Fußbodenheizung & Thermische Estrich-Vorladung (Volle Breite) */}
                {(activeTab === "all" || activeTab === "fbh") && (
                    <div>
                        <FloorHeatingLoadCard />
                    </div>
                )}

                {/* ♨️ Brauchwasser-Wärmepumpe & ❄️ Klimaanlage / Heizstab NEBENEINANDER (2-Spalten-Raster) */}
                {(activeTab === "all" || activeTab === "bwwp" || activeTab === "ac_rod") && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
                        {/* Spalte 1: Brauchwasser & SG-Ready Wärmepumpe */}
                        {(activeTab === "all" || activeTab === "bwwp") && (
                            <div className="space-y-4">
                                <BWWPLoadManagementCard />
                            </div>
                        )}

                        {/* Spalte 2: Klimaanlage (Pre-Cooling) & Heizstab */}
                        {(activeTab === "all" || activeTab === "ac_rod") && (
                            <div className="space-y-6">
                                {acConsumers.length > 0 ? (
                                    acConsumers.map((c) => (
                                        <AirConditioningCard
                                            key={c.id}
                                            consumer={c}
                                            onAction={handleQuickAction}
                                            isPending={actionMutation.isPending}
                                        />
                                    ))
                                ) : (
                                    <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200 dark:border-slate-800 space-y-4 shadow-sm">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <div className="w-12 h-12 rounded-2xl bg-sky-500/10 text-sky-600 dark:text-sky-400 flex items-center justify-center text-2xl">
                                                    ❄️
                                                </div>
                                                <div>
                                                    <h3 className="text-base font-bold text-slate-900 dark:text-white">
                                                        Klimaanlage & Raumkühlung
                                                    </h3>
                                                    <p className="text-xs text-slate-400">
                                                        Smarte Vor-Kühlung (Pre-Cooling)
                                                    </p>
                                                </div>
                                            </div>
                                            <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-sky-50 dark:bg-sky-950/50 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-800">
                                                Autopilot
                                            </span>
                                        </div>

                                        <div className="grid grid-cols-2 gap-3">
                                            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200/60 dark:border-slate-700/60">
                                                <div className="text-[11px] text-slate-500">Ziel-Kühltemperatur</div>
                                                <div className="text-lg font-bold font-mono text-slate-900 dark:text-white mt-0.5">22.0 °C</div>
                                            </div>
                                            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200/60 dark:border-slate-700/60">
                                                <div className="text-[11px] text-slate-500">Solar-Precooling</div>
                                                <div className="text-lg font-bold font-mono text-sky-600 dark:text-sky-400 mt-0.5">Aktiv</div>
                                            </div>
                                        </div>

                                        <div className="p-3.5 rounded-2xl bg-sky-50/50 dark:bg-sky-950/20 border border-sky-200/60 dark:border-sky-800/40 text-xs text-slate-600 dark:text-slate-300">
                                            ☀️ <strong>Solares Pre-Cooling:</strong> Kühlt Räume bei mittäglichen Solar-Peaks automatisch um 1,5 K vor, um teuren Netzbezug in der Abend-Spitze zu vermeiden.
                                        </div>
                                    </div>
                                )}

                {/* Heizstab Laststufen-Karte */}
                                <HeatingRodCard />
                            </div>
                        )}
                    </div>
                )}
            </div>
            </div>

            {/* Pro Upgrade Modal */}
            <ProUpgradeModal
                open={proModalOpen}
                onClose={() => setProModalOpen(false)}
                featureName="Smart Wärme- & Thermischer Speicher-Autopilot"
                featureDesc="Nutze die Estrich-Vorladung (MPC), SG-Ready Warmwasser-Boost und PV-Heizstab-Modulation für bis zu 45% Heizkostenersparnis."
            />
        </div>
    );
}
