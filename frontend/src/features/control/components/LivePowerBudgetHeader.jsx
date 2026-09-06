import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Zap, ShieldCheck, Sun, RotateCcw, Clock } from "lucide-react";

export default function LivePowerBudgetHeader({
    budget = {},
    masterMode,
    onMasterModeChange,
    onQuickBoost,
    isSaving,
}) {
    const { t } = useTranslation();
    const [activeBoost, setActiveBoost] = useState(null);

    const surplusW = budget.available_surplus_w ?? 0;
    const pvW = budget.pv_production_w ?? 0;
    const loadW = budget.house_load_w ?? 0;
    const soc = budget.battery_soc_pct ?? 65;
    const priceCt = budget.current_price_ct ?? 24.5;
    const activeCount = budget.active_devices_count ?? 0;
    const totalCount = budget.total_devices_count ?? 0;

    const handleTriggerBoost = (type, label, durationHours = 2) => {
        const boostObj = { type, label, until: new Date(Date.now() + durationHours * 3600 * 1000) };
        setActiveBoost(boostObj);
        if (onQuickBoost) {
            onQuickBoost(type, durationHours);
        }
    };

    const handleCancelBoost = () => {
        setActiveBoost(null);
        if (onMasterModeChange) {
            onMasterModeChange("autopilot");
        }
    };

    return (
        <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 rounded-3xl p-6 text-white border border-indigo-500/30 shadow-xl relative overflow-hidden">
            {/* Ambient Background Glow */}
            <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute -bottom-10 -left-10 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

            <div className="relative z-10 space-y-5">
                {/* Top Row: Title & Master Mode Selector */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-indigo-800/40 pb-5">
                    <div className="flex items-center gap-3.5">
                        <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-2xl shadow-inner">
                            🎛️
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-xl font-black tracking-tight text-white">
                                    {t("control.hub_title", "Smart Load Management & Dispatch Hub")}
                                </h2>
                                <span className="px-2.5 py-0.5 text-[11px] font-bold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                                    ● Live Regelung
                                </span>
                            </div>
                            <p className="text-xs text-indigo-200/70 mt-0.5">
                                Intelligente Verteilung von Solarüberschuss & Börsentarifen auf BWWP, Wallbox, Speicher, Pool & Großverbraucher.
                            </p>
                        </div>
                    </div>

                    {/* Master Mode Selector */}
                    <div className="flex items-center gap-2.5 bg-white/5 border border-white/10 rounded-2xl p-1.5 backdrop-blur-xs">
                        <span className="text-xs font-semibold text-indigo-200 px-2 hidden sm:inline">
                            Master-Modus:
                        </span>
                        <select
                            value={masterMode}
                            onChange={(e) => onMasterModeChange(e.target.value)}
                            disabled={isSaving}
                            className="bg-indigo-900/80 hover:bg-indigo-800/90 text-white font-bold text-xs rounded-xl px-3 py-2 border border-indigo-400/40 cursor-pointer transition outline-none"
                        >
                            <option value="autopilot">🟢 Autopilot (PV + Spotmarkt)</option>
                            <option value="pv_only">☀️ Nur PV-Überschuss</option>
                            <option value="price_saver">⚡ Sparfuchs (Börsen-Tiefstpreise)</option>
                            <option value="manual">✋ Manuell (Urlaub)</option>
                        </select>
                    </div>
                </div>

                {/* ⚡ 1-CLICK QUICK BOOST / OVERRIDE BAR */}
                <div className="bg-indigo-950/60 border border-indigo-500/25 rounded-2xl p-3 backdrop-blur-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center gap-1 shrink-0">
                            <Zap className="w-3.5 h-3.5 text-amber-400" />
                            1-Klick Aktionen:
                        </span>
                        {activeBoost ? (
                            <div className="flex items-center gap-2 bg-amber-500/20 border border-amber-400/40 px-2.5 py-1 rounded-xl text-xs font-bold text-amber-200 animate-pulse">
                                <Clock className="w-3.5 h-3.5 text-amber-300" />
                                <span>{activeBoost.label} aktiv</span>
                                <button
                                    type="button"
                                    onClick={handleCancelBoost}
                                    className="ml-1.5 text-xs bg-white/20 hover:bg-white/30 px-1.5 py-0.5 rounded text-white cursor-pointer"
                                    title="Sofort beenden & Autopilot aktivieren"
                                >
                                    ✕ Beenden
                                </button>
                            </div>
                        ) : (
                            <span className="text-xs text-indigo-200/60 hidden md:inline">
                                Schnellschaltung für Sofort-Laden oder Notstrom-Reserve
                            </span>
                        )}
                    </div>

                    <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
                        <button
                            type="button"
                            onClick={() => handleTriggerBoost("wallbox_boost", "⚡ Wallbox Boost 11kW (2h)")}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 hover:text-amber-100 border border-amber-400/30 text-xs font-bold transition cursor-pointer shadow-xs active:scale-95"
                            title="Startet Wallbox mit maximaler Ladeleistung (11 kW) für 2 Stunden"
                        >
                            <Zap className="w-3.5 h-3.5 text-amber-400" />
                            <span>Wallbox Boost (11 kW)</span>
                        </button>

                        <button
                            type="button"
                            onClick={() => handleTriggerBoost("battery_reserve", "🔋 Speicher-Schutz (100% Reserve)")}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-200 hover:text-indigo-100 border border-indigo-400/30 text-xs font-bold transition cursor-pointer shadow-xs active:scale-95"
                            title="Hält den Heimspeicher als Notstromreserve und sperrt Entladung"
                        >
                            <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                            <span>Speicher-Schutz</span>
                        </button>

                        <button
                            type="button"
                            onClick={() => handleTriggerBoost("max_pv", "☀️ Max. PV-Eigenverbrauch")}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-200 hover:text-emerald-100 border border-emerald-400/30 text-xs font-bold transition cursor-pointer shadow-xs active:scale-95"
                            title="Gibt alle flexiblen Verbraucher für maximalen Eigenverbrauch frei"
                        >
                            <Sun className="w-3.5 h-3.5 text-emerald-400" />
                            <span>Max. Eigenverbrauch</span>
                        </button>

                        {activeBoost && (
                            <button
                                type="button"
                                onClick={handleCancelBoost}
                                className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-slate-200 border border-white/20 text-xs font-semibold transition cursor-pointer"
                                title="Zurück zum Autopilot"
                            >
                                <RotateCcw className="w-3 h-3" />
                                <span>Reset</span>
                            </button>
                        )}
                    </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
                    {/* Solarüberschuss */}
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-xs">
                        <div className="text-xs font-medium text-indigo-200/80 flex items-center justify-between">
                            <span>Verfügbarer Überschuss</span>
                            <span>☀️</span>
                        </div>
                        <div className="text-2xl font-black font-mono text-emerald-400 mt-1 flex items-baseline gap-1">
                            <span>{surplusW > 0 ? surplusW.toLocaleString("de-DE") : "0"}</span>
                            <span className="text-xs font-normal text-indigo-200/70">W</span>
                        </div>
                        <div className="text-[11px] text-indigo-200/60 mt-0.5">
                            PV: {pvW.toLocaleString("de-DE")} W · Last: {loadW.toLocaleString("de-DE")} W
                        </div>
                    </div>

                    {/* Heimspeicher SoC */}
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-xs">
                        <div className="text-xs font-medium text-indigo-200/80 flex items-center justify-between">
                            <span>Heimspeicher Stand</span>
                            <span>🔋</span>
                        </div>
                        <div className="text-2xl font-black font-mono text-indigo-300 mt-1 flex items-baseline gap-1">
                            <span>{soc}</span>
                            <span className="text-xs font-normal text-indigo-200/70">%</span>
                        </div>
                        <div className="text-[11px] text-indigo-200/60 mt-0.5">
                            {soc >= 80 ? "Prio 1 gedeckt ➔ Überschuss frei" : "Prio 1 lädt mit Vorrang"}
                        </div>
                    </div>

                    {/* Börsenstrompreis */}
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-xs">
                        <div className="text-xs font-medium text-indigo-200/80 flex items-center justify-between">
                            <span>Börsenpreis (Effektiv)</span>
                            <span>⚡</span>
                        </div>
                        <div className="text-2xl font-black font-mono text-amber-300 mt-1 flex items-baseline gap-1">
                            <span>{priceCt.toFixed(1)}</span>
                            <span className="text-xs font-normal text-indigo-200/70">ct/kWh</span>
                        </div>
                        <div className="text-[11px] text-indigo-200/60 mt-0.5">
                            Spotmarkt Day-Ahead aktiv
                        </div>
                    </div>

                    {/* Gesteuerte Lasten */}
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-xs">
                        <div className="text-xs font-medium text-indigo-200/80 flex items-center justify-between">
                            <span>Aktive Regelung</span>
                            <span>🤖</span>
                        </div>
                        <div className="text-2xl font-black font-mono text-white mt-1 flex items-baseline gap-1">
                            <span>{activeCount}</span>
                            <span className="text-xs font-normal text-indigo-200/70">/ {totalCount} Lasten</span>
                        </div>
                        <div className="text-[11px] text-indigo-200/60 mt-0.5">
                            Gesteuert: {((budget.total_controlled_w || 0) / 1000).toFixed(1)} kW
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
