import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import { useSubscription } from "../../../hooks/useSubscription";
import ProBadge from "../../../components/common/ProBadge";
import ProUpgradeModal from "../../../components/common/ProUpgradeModal";

import LivePowerBudgetHeader from "../components/LivePowerBudgetHeader";
import PriorityCascadeBar from "../components/PriorityCascadeBar";
import LiveSurplusWaterfallCard from "../components/LiveSurplusWaterfallCard";
import DispatchTimelineCard from "../components/DispatchTimelineCard";
import BWWPLoadManagementCard from "../../energy/components/BWWPLoadManagementCard";
import FloorHeatingLoadCard from "../components/FloorHeatingLoadCard";
import BatteryStorageControlCard from "../components/BatteryStorageControlCard";
import WallboxCard from "../../energy/components/WallboxCard";
import FuelRadarCard from "../components/FuelRadarCard";
import PoolPumpCard from "../components/PoolPumpCard";
import AirConditioningCard from "../components/AirConditioningCard";
import SmartApplianceCard from "../components/SmartApplianceCard";
import HeatingRodCard from "../components/HeatingRodCard";
import AddWallboxModal from "../../devices/components/AddWallboxModal";
import CommunityInviteCard from "../../community/components/CommunityInviteCard";
import CommunityShareModal from "../../community/components/CommunityShareModal";

export default function ControlPage() {
    const { t } = useTranslation();
    const { isPro, proYearlyMonthlyEquiv } = useSubscription();
    const queryClient = useQueryClient();

    const [activeTab, setActiveTab] = useState("all");
    const [proModalOpen, setProModalOpen] = useState(false);
    const [shareModalOpen, setShareModalOpen] = useState(false);
    const [addWallboxOpen, setAddWallboxOpen] = useState(false);
    const [actionFeedback, setActionFeedback] = useState(null);

    // 1. Hub Live-Daten laden (Budget, Verbraucher, Fahrplan, Prioritäten)
    const hubQuery = useQuery({
        queryKey: ["load-management-hub"],
        queryFn: () => apiFetch("/api/energy/load-management/hub/"),
        refetchInterval: isPro ? 10000 : 30000,
    });

    // 2. Prioritäten Mutation
    const priorityMutation = useMutation({
        mutationFn: (payload) =>
            apiFetch("/api/energy/load-management/hub/priorities/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["load-management-hub"] });
            showFeedback("Prioritäten-Kaskade erfolgreich aktualisiert.");
        },
    });

    // 3. Quick-Action Mutation
    const actionMutation = useMutation({
        mutationFn: (payload) =>
            apiFetch("/api/energy/load-management/hub/action/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            }),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["load-management-hub"] });
            queryClient.invalidateQueries({ queryKey: ["bwwp-load-mgmt"] });
            queryClient.invalidateQueries({ queryKey: ["floor-heating"] });
            queryClient.invalidateQueries({ queryKey: ["storages"] });
            queryClient.invalidateQueries({ queryKey: ["wallboxes"] });
            showFeedback(data.message || "Aktion erfolgreich ausgeführt.");
        },
    });

    const showFeedback = (msg) => {
        setActionFeedback(msg);
        setTimeout(() => setActionFeedback(null), 4000);
    };

    const hubData = hubQuery.data || {};
    const liveBudget = hubData.live_budget || {};
    const consumers = hubData.consumers || [];
    const dispatchSchedule = hubData.dispatch_schedule || [];
    const priorityOrder = hubData.priority_order || ["battery", "floor_heating", "bwwp", "wallbox", "heatpump", "pool", "ac", "appliances", "heating_rod"];
    const masterMode = hubData.master_mode || "autopilot";

    const handlePriorityOrderChange = (newOrder) => {
        if (!isPro) {
            setProModalOpen(true);
            return;
        }
        priorityMutation.mutate({
            priority_order: newOrder,
            master_mode: masterMode,
        });
    };

    const handleMasterModeChange = (newMode) => {
        if (!isPro) {
            setProModalOpen(true);
            return;
        }
        priorityMutation.mutate({
            priority_order: priorityOrder,
            master_mode: newMode,
        });
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

    // Filter consumers by category tab
    const filteredConsumers = consumers.filter((c) => {
        if (activeTab === "all") return true;
        if (activeTab === "floor_heating") return c.category === "floor_heating";
        if (activeTab === "heat") return ["bwwp", "heatpump", "heating_rod", "floor_heating"].includes(c.category);
        if (activeTab === "mobility") return c.category === "wallbox";
        if (activeTab === "storage") return c.category === "battery";
        if (activeTab === "pool") return c.category === "pool";
        if (activeTab === "ac") return c.category === "ac";
        if (activeTab === "appliances") return c.category === "appliances";
        return true;
    });

    const poolConsumers = consumers.filter((c) => c.category === "pool");
    const acConsumers = consumers.filter((c) => c.category === "ac");
    const applianceConsumers = consumers.filter((c) => c.category === "appliances");
    const heatingRodConsumers = consumers.filter((c) => c.category === "heating_rod");

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* Action Feedback Banner (Floating Toast) */}
            {actionFeedback && (
                <div className="fixed bottom-6 right-6 z-50 px-4 py-3 bg-slate-900/95 text-white text-xs font-bold rounded-2xl shadow-2xl border border-emerald-500/50 flex items-center gap-2.5 backdrop-blur-md animate-in fade-in slide-in-from-bottom-4 duration-300">
                    <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center text-xs">✓</span>
                    <span>{actionFeedback}</span>
                    <button 
                        onClick={() => setActionFeedback(null)}
                        className="ml-2 text-slate-400 hover:text-white transition cursor-pointer text-xs"
                    >
                        ✕
                    </button>
                </div>
            )}

            {/* PAGE HEADER */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                        <span>🎛️</span> {t("control.title", "Energiesteuerung & Lastmanagement")}
                        {!isPro && <ProBadge size="sm" />}
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
                        {t("control.subtitle", "Intelligente PV-Überschusssteuerung, Prioritäten-Kaskade und automatisierte Verbraucher-Fahrpläne.")}
                    </p>
                </div>
                {!isPro && (
                    <button
                        type="button"
                        onClick={() => setProModalOpen(true)}
                        className="self-start sm:self-auto px-4 py-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 text-xs font-black rounded-xl shadow-md shadow-amber-500/20 transition cursor-pointer flex items-center gap-1.5"
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
                    <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/15 rounded-full blur-3xl pointer-events-none" />
                    <div className="absolute bottom-0 left-0 w-72 h-72 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

                    <div className="relative z-10 max-w-3xl space-y-4">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-400/30 text-xs font-bold uppercase tracking-wider">
                            <span>⭐</span>
                            <span>Sharegy Pro Exklusiv</span>
                        </div>
                        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-white leading-tight">
                            Automatisiere dein Zuhause mit intelligenter Laststeuerung & PV-Überschuss-Kaskade
                        </h2>
                        <p className="text-indigo-200/80 text-sm sm:text-base leading-relaxed">
                            Verteile deinen Solarstrom in Echtzeit auf Heimspeicher, Wärmepumpe, Wallbox und Klimaanlage. Schütze dein Netz mit gesetzeskonformer § 14a EnWG Drosselung und profitiere von dynamischen Börsenpreisen.
                        </p>
                    </div>

                    {/* Features Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 relative z-10">
                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">⚡</div>
                            <h3 className="text-sm font-bold text-white">Merit-Order Kaskade</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Bestimme per Drag & Drop, welcher Verbraucher bei Solarüberschuss priorisiert versorgt wird.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">🤖</div>
                            <h3 className="text-sm font-bold text-white">Autopilot & 4 Betriebsmodi</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Autopilot, reiner PV-Überschuss, Börsenpreis-Sparer oder manueller Direktmodus.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">🚗</div>
                            <h3 className="text-sm font-bold text-white">Dynamisches PV-Laden (OCPP)</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Automatische Ampere-Regelung und Phasenumschaltung für deine Wallbox.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">♨️</div>
                            <h3 className="text-sm font-bold text-white">SG-Ready Wärmepumpen & BWWP</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Schalte Warmwasser-Sollwertanhebungen vollautomatisch bei Solar-Spitzen.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">🔋</div>
                            <h3 className="text-sm font-bold text-white">Batterie-Arbitrage & Grid-Boost</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Lade deinen Speicher gezielt bei negativen oder ultragünstigen Börsenstrompreisen nach.
                            </p>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xs space-y-2">
                            <div className="text-2xl">🛡️</div>
                            <h3 className="text-sm font-bold text-white">§ 14a EnWG Netzdrosselung</h3>
                            <p className="text-xs text-indigo-200/70 leading-relaxed">
                                Automatische Abarbeitung von Drosselsignalen des Netzbetreibers ohne Komfortverlust.
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
                                <span>Energiesteuerung mit Sharegy Pro freischalten</span>
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* 🎛️ DASHBOARD CONTENT: ECHTE DATEN BZW. GELOCKTE DEMO-VORSCHAU */}
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
                                    Klicke hier, um alle Steuerungsoptionen mit Sharegy Pro freizuschalten
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* 1. Live Power Budget & Master Autopilot Header */}
                <LivePowerBudgetHeader
                    budget={liveBudget}
                    masterMode={masterMode}
                    onMasterModeChange={handleMasterModeChange}
                    onQuickBoost={(type, durationHours) => {
                        if (type === "wallbox_boost") {
                            handleQuickAction("wallbox", "boost", null, { power_kw: 11, duration_hours: durationHours });
                        } else if (type === "battery_reserve") {
                            handleQuickAction("battery", "reserve_100", null, { duration_hours: durationHours });
                        } else if (type === "max_pv") {
                            handleMasterModeChange("pv_only");
                        }
                    }}
                    isSaving={priorityMutation.isPending}
                />

                {/* 2. Priority Cascade Bar (Merit-Order) */}
                <PriorityCascadeBar
                    priorityOrder={priorityOrder}
                    onOrderChange={handlePriorityOrderChange}
                    isSaving={priorityMutation.isPending}
                />

                {/* 3. Live Surplus Waterfall Flow Card */}
                <LiveSurplusWaterfallCard budget={liveBudget} />

                {/* 4. 24h Dispatch Timeline & Schedule */}
                <DispatchTimelineCard schedule={dispatchSchedule} />

                {/* 4. SECTION: STEUERBARE GROSSVERBRAUCHER & AKTOREN */}
                <div className="space-y-4 pt-2">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 dark:border-slate-800 pb-3">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-xl shadow-2xs">
                                ⚡
                            </div>
                            <div>
                                <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                    <span>Steuerbare Großverbraucher & Aktoren</span>
                                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                                        {consumers.length} Verbraucher
                                    </span>
                                </h2>
                                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                    Direktsteuerung, Betriebsmodi und Sollwerte für alle angebundenen Relais, Wallboxen und Wärmepumpen.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Filter Tabs - Grouped into 5 streamlined domains */}
                    <div className="flex flex-wrap items-center gap-2 pb-1">
                        {[
                            { key: "all", label: t("control.tab_all", "Alle Verbraucher"), icon: "🎛️" },
                            { key: "mobility", label: t("control.tab_mobility", "Mobilität & Wallbox"), icon: "🚗" },
                            { key: "heat", label: t("control.tab_heat", "Wärme & Klima"), icon: "🔥" },
                            { key: "battery", label: t("control.tab_battery", "Heimspeicher"), icon: "🔋" },
                            { key: "comfort", label: t("control.tab_comfort", "Komfort & Haushalt"), icon: "🧺" },
                        ].map((tab) => (
                            <button
                                key={tab.key}
                                type="button"
                                onClick={() => setActiveTab(tab.key)}
                                className={`px-4 py-2 rounded-2xl text-xs sm:text-sm font-bold transition flex items-center gap-2 cursor-pointer ${
                                    activeTab === tab.key
                                        ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                                        : "bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
                                }`}
                            >
                                <span>{tab.icon}</span>
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </div>

                    {/* Dedicated Sub-Hub Banners for Mobility & Heating in All View */}
                    {activeTab === "all" && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Link
                                to="/app/mobility"
                                className="p-5 rounded-3xl bg-gradient-to-br from-sky-500/10 via-indigo-500/5 to-transparent border border-sky-500/20 hover:border-sky-500/40 transition group flex items-center justify-between shadow-sm cursor-pointer"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-2xl bg-sky-500/20 text-sky-600 dark:text-sky-400 flex items-center justify-center text-2xl group-hover:scale-110 transition shrink-0">
                                        🚗
                                    </div>
                                    <div>
                                        <div className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                            <span>{t("mobility.title", "E-Mobilität & Spritpreis-Radar")}</span>
                                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-600 dark:text-sky-400 font-mono">
                                                {t("common.open_hub", "Hub öffnen →")}
                                            </span>
                                        </div>
                                        <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                            {t("mobility.banner_desc", "Wallbox-Steuerung (1,4–11 kW) & MTS-K Live-Spritpreisvergleich.")}
                                        </div>
                                    </div>
                                </div>
                                <div className="text-slate-400 group-hover:translate-x-1 transition text-lg font-bold pr-2">
                                    ➔
                                </div>
                            </Link>

                            <Link
                                to="/app/heating"
                                className="p-5 rounded-3xl bg-gradient-to-br from-rose-500/10 via-amber-500/5 to-transparent border border-rose-500/20 hover:border-rose-500/40 transition group flex items-center justify-between shadow-sm cursor-pointer"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-2xl bg-rose-500/20 text-rose-600 dark:text-rose-400 flex items-center justify-center text-2xl group-hover:scale-110 transition shrink-0">
                                        🌡️
                                    </div>
                                    <div>
                                        <div className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                            <span>{t("heating.title", "Wärme & Thermische Speicher")}</span>
                                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-600 dark:text-rose-400 font-mono">
                                                {t("common.open_hub", "Hub öffnen →")}
                                            </span>
                                        </div>
                                        <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                            {t("heating.banner_desc", "Wettergeführte FBH (MPC Estrich-Vorladung) & BWWP Wärmepumpe.")}
                                        </div>
                                    </div>
                                </div>
                                <div className="text-slate-400 group-hover:translate-x-1 transition text-lg font-bold pr-2">
                                    ➔
                                </div>
                            </Link>
                        </div>
                    )}

                    {/* Consumer Cards Grid */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* 🔋 Heimspeicher / Battery Storage Control */}
                        {(activeTab === "all" || activeTab === "battery") && (
                            <BatteryStorageControlCard />
                        )}

                        {/* 🚗 Wallbox / OCPP E-Auto Ladekarte */}
                        {(activeTab === "all" || activeTab === "mobility") && (
                            <WallboxCard onOpenAddModal={() => setAddWallboxOpen(true)} />
                        )}

                        {/* ♨️ BWWP & Wärmepumpen SG-Ready Lastmanagement */}
                        {(activeTab === "all" || activeTab === "heat") && (
                            <BWWPLoadManagementCard />
                        )}

                        {/* 🌡️ Fußbodenheizung & Thermische Estrich-Vorladung */}
                        {(activeTab === "all" || activeTab === "heat") && (
                            <FloorHeatingLoadCard />
                        )}

                        {/* ⛽ Mobilitäts- & Spritpreis-Radar (MTS-K / Tankerkönig) */}
                        {(activeTab === "mobility") && (
                            <FuelRadarCard />
                        )}

                        {/* 🏊 Poolpumpen & Filteranlagen */}
                        {(activeTab === "all" || activeTab === "comfort") &&
                            (poolConsumers.length > 0 ? (
                                poolConsumers.map((c) => (
                                    <PoolPumpCard
                                        key={c.id}
                                        consumer={c}
                                        onAction={handleQuickAction}
                                        isPending={actionMutation.isPending}
                                    />
                                ))
                            ) : activeTab === "comfort" ? (
                                <div className="col-span-full bg-white dark:bg-slate-900 rounded-3xl p-8 border border-slate-200 dark:border-slate-800 text-center space-y-3">
                                    <div className="text-3xl">🏊</div>
                                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">Keine Poolpumpe verknüpft</h3>
                                    <p className="text-xs text-slate-500 max-w-md mx-auto">
                                        Weise einem Shelly- oder MQTT-Relais die Rolle »Poolpumpe« zu, um die Filterzeiten automatisch über PV-Überschuss zu steuern.
                                    </p>
                                </div>
                            ) : null)}

                        {/* ❄️ Klimaanlagen (Pre-Cooling) */}
                        {(activeTab === "all" || activeTab === "heat") &&
                            (acConsumers.length > 0 ? (
                                acConsumers.map((c) => (
                                    <AirConditioningCard
                                        key={c.id}
                                        consumer={c}
                                        onAction={handleQuickAction}
                                        isPending={actionMutation.isPending}
                                    />
                                ))
                            ) : activeTab === "heat" && heatingRodConsumers.length === 0 ? (
                                <div className="col-span-full bg-white dark:bg-slate-900 rounded-3xl p-8 border border-slate-200 dark:border-slate-800 text-center space-y-3">
                                    <div className="text-3xl">❄️</div>
                                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">Keine Klimaanlage verknüpft</h3>
                                    <p className="text-xs text-slate-500 max-w-md mx-auto">
                                        Nutze smartere Vor-Kühlung (Pre-Cooling) bei Solar-Peaks oder extrem günstigen Börsenpreisen.
                                    </p>
                                </div>
                            ) : null)}

                        {/* 🧺 Haushaltsgeräte / Ready-to-Start Smart Plugs */}
                        {(activeTab === "all" || activeTab === "comfort") &&
                            (applianceConsumers.length > 0 ? (
                                applianceConsumers.map((c) => (
                                    <SmartApplianceCard
                                        key={c.id}
                                        consumer={c}
                                        onAction={handleQuickAction}
                                        isPending={actionMutation.isPending}
                                    />
                                ))
                            ) : activeTab === "comfort" && poolConsumers.length === 0 ? (
                                <div className="col-span-full bg-white dark:bg-slate-900 rounded-3xl p-8 border border-slate-200 dark:border-slate-800 text-center space-y-3">
                                    <div className="text-3xl">🧺</div>
                                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">Keine smarten Zwischenstecker verknüpft</h3>
                                    <p className="text-xs text-slate-500 max-w-md mx-auto">
                                        Verbinde Zwischenstecker für Waschmaschine, Trockner oder Spülmaschine für automatischen Solar-Start.
                                    </p>
                                </div>
                            ) : null)}

                        {/* ⚡ Heizstab / Power-to-Heat Puffer */}
                        {(activeTab === "all" || activeTab === "heat") &&
                            (heatingRodConsumers.length > 0 ? (
                                heatingRodConsumers.map((c) => (
                                    <HeatingRodCard
                                        key={c.id}
                                        consumer={c}
                                        onAction={handleQuickAction}
                                        isPending={actionMutation.isPending}
                                    />
                                ))
                            ) : null)}
                    </div>
                </div>

                {/* Quartiers-Energy Sharing (§ 42b EnWG) Banner at bottom */}
                <CommunityInviteCard
                    onOpenShareModal={() => setShareModalOpen(true)}
                    kpis={{
                        autarky_pct: liveBudget.battery_soc_pct || 86,
                        self_consumption_pct: 92,
                        community_shared_kwh: 148,
                    }}
                />
            </div>

            {/* Community Social Share Modal */}
            <CommunityShareModal
                isOpen={shareModalOpen}
                onClose={() => setShareModalOpen(false)}
                kpis={{
                    autarky_pct: liveBudget.battery_soc_pct || 86,
                    self_consumption_pct: 92,
                    community_shared_kwh: 148,
                }}
            />

            {/* Add Wallbox Modal */}
            <AddWallboxModal
                isOpen={addWallboxOpen}
                open={addWallboxOpen}
                onClose={() => setAddWallboxOpen(false)}
            />

            {/* Pro Upgrade Modal */}
            <ProUpgradeModal
                open={proModalOpen}
                onClose={() => setProModalOpen(false)}
                featureName="Smart Load Management & Autopilot Hub"
                featureDesc="Automatisiere die Verteilung von Solarüberschuss und Börsenstrompreisen auf all deine flexiblen Großverbraucher."
            />
        </div>
    );
}
