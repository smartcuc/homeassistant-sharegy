import { useTranslation } from "react-i18next";

export default function LivePowerBudgetHeader({ budget = {}, masterMode, onMasterModeChange, isSaving }) {
    const { t } = useTranslation();

    const surplusW = budget.available_surplus_w ?? 0;
    const pvW = budget.pv_production_w ?? 0;
    const loadW = budget.house_load_w ?? 0;
    const soc = budget.battery_soc_pct ?? 65;
    const priceCt = budget.current_price_ct ?? 24.5;
    const activeCount = budget.active_devices_count ?? 0;
    const totalCount = budget.total_devices_count ?? 0;

    return (
        <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 rounded-3xl p-6 text-white border border-indigo-500/30 shadow-xl relative overflow-hidden">
            {/* Ambient Background Glow */}
            <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute -bottom-10 -left-10 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

            <div className="relative z-10 space-y-6">
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
