import { useTranslation } from "react-i18next";
import { ArrowDown, Zap, Battery, Home, Car, Droplets, Sun, ShieldCheck } from "lucide-react";

export default function LiveSurplusWaterfallCard({ budget = {} }) {
    const { t } = useTranslation();

    const pvW = budget.pv_production_w ?? 0;
    const loadW = budget.house_load_w ?? 0;
    const soc = budget.battery_soc_pct ?? 65;
    const surplusW = Math.max(0, pvW - loadW);

    // Dynamic waterfall calculation
    const batteryPrioW = Math.min(surplusW, soc < 95 ? Math.min(2500, surplusW) : 0);
    const afterBatteryW = Math.max(0, surplusW - batteryPrioW);

    const bwwpPrioW = Math.min(afterBatteryW, afterBatteryW >= 800 ? 800 : 0);
    const afterBwwpW = Math.max(0, afterBatteryW - bwwpPrioW);

    const wallboxPrioW = Math.min(afterBwwpW, afterBwwpW >= 1400 ? afterBwwpW : 0);
    const gridExportW = Math.max(0, afterBwwpW - wallboxPrioW);

    const formatW = (val) => {
        if (val >= 1000) return `${(val / 1000).toFixed(1)} kW`;
        return `${Math.round(val)} W`;
    };

    return (
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-5 sm:p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm relative overflow-hidden space-y-4">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 flex items-center justify-center text-xl shadow-2xs">
                        🌊
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <span>Live-Leistungsverteiler (Überschuss-Wasserfall)</span>
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                                ● Echtzeit
                            </span>
                        </h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                            Dynamische Merit-Order Aufteilung des Solarstroms auf alle Verbraucherstufen.
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 px-2.5 py-1 rounded-xl">
                        PV: {formatW(pvW)}
                    </span>
                </div>
            </div>

            {/* Waterfall Flow Items */}
            <div className="space-y-2.5">
                {/* 1. Solar Input */}
                <div className="p-3 bg-amber-50/80 dark:bg-amber-950/30 border border-amber-200/80 dark:border-amber-800/60 rounded-2xl flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-xl bg-amber-500 text-white flex items-center justify-center font-bold text-sm shadow-xs">
                            <Sun className="w-4 h-4" />
                        </div>
                        <div>
                            <div className="text-xs font-bold text-slate-900 dark:text-white">1. Solare Gesamterzeugung</div>
                            <div className="text-[11px] text-slate-500 dark:text-slate-400">Verfügbare Bruttoleistung vom Dach</div>
                        </div>
                    </div>
                    <div className="text-sm font-black font-mono text-amber-600 dark:text-amber-400">
                        {formatW(pvW)}
                    </div>
                </div>

                {/* Arrow */}
                <div className="flex justify-center text-slate-300 dark:text-slate-600 -my-1">
                    <ArrowDown className="w-4 h-4 animate-bounce" />
                </div>

                {/* 2. Direct House Load */}
                <div className="p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60 rounded-2xl flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-xl bg-blue-500 text-white flex items-center justify-center font-bold text-sm shadow-xs">
                            <Home className="w-4 h-4" />
                        </div>
                        <div>
                            <div className="text-xs font-bold text-slate-900 dark:text-white">2. Haus-Grundlast (Priorität 0)</div>
                            <div className="text-[11px] text-slate-500 dark:text-slate-400">Direktdeckung aller Haushaltsverbraucher</div>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-sm font-black font-mono text-blue-600 dark:text-blue-400">
                            -{formatW(loadW)}
                        </div>
                        <div className="text-[10px] text-slate-400">Rest: {formatW(surplusW)}</div>
                    </div>
                </div>

                {/* Arrow */}
                <div className="flex justify-center text-slate-300 dark:text-slate-600 -my-1">
                    <ArrowDown className="w-4 h-4" />
                </div>

                {/* 3. Battery Storage (Prio 1) */}
                <div className="p-3 bg-indigo-50/80 dark:bg-indigo-950/30 border border-indigo-200/80 dark:border-indigo-800/60 rounded-2xl flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-sm shadow-xs">
                            <Battery className="w-4 h-4" />
                        </div>
                        <div>
                            <div className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                <span>3. Heimspeicher (Priorität 1)</span>
                                <span className="text-[10px] font-mono px-1.5 py-0.2 bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 rounded font-bold">{soc}% SoC</span>
                            </div>
                            <div className="text-[11px] text-slate-500 dark:text-slate-400">Batterieladung zur Nachtabdeckung</div>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-sm font-black font-mono text-indigo-600 dark:text-indigo-400">
                            -{formatW(batteryPrioW)}
                        </div>
                        <div className="text-[10px] text-slate-400">Rest: {formatW(afterBatteryW)}</div>
                    </div>
                </div>

                {/* Arrow */}
                <div className="flex justify-center text-slate-300 dark:text-slate-600 -my-1">
                    <ArrowDown className="w-4 h-4" />
                </div>

                {/* 4. BWWP / Hot Water (Prio 2) */}
                <div className="p-3 bg-orange-50/80 dark:bg-orange-950/30 border border-orange-200/80 dark:border-orange-800/60 rounded-2xl flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-xl bg-orange-500 text-white flex items-center justify-center font-bold text-sm shadow-xs">
                            <Droplets className="w-4 h-4" />
                        </div>
                        <div>
                            <div className="text-xs font-bold text-slate-900 dark:text-white">4. Warmwasser / BWWP (Priorität 2)</div>
                            <div className="text-[11px] text-slate-500 dark:text-slate-400">SG-Ready thermischer Solar-Boost bis 60°C</div>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-sm font-black font-mono text-orange-600 dark:text-orange-400">
                            {bwwpPrioW > 0 ? `-${formatW(bwwpPrioW)}` : "Bereit (0 W)"}
                        </div>
                        <div className="text-[10px] text-slate-400">Rest: {formatW(afterBwwpW)}</div>
                    </div>
                </div>

                {/* Arrow */}
                <div className="flex justify-center text-slate-300 dark:text-slate-600 -my-1">
                    <ArrowDown className="w-4 h-4" />
                </div>

                {/* 5. Wallbox / EV (Prio 3) */}
                <div className="p-3 bg-emerald-50/80 dark:bg-emerald-950/30 border border-emerald-200/80 dark:border-emerald-800/60 rounded-2xl flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-sm shadow-xs">
                            <Car className="w-4 h-4" />
                        </div>
                        <div>
                            <div className="text-xs font-bold text-slate-900 dark:text-white">5. Wallbox / E-Auto (Priorität 3)</div>
                            <div className="text-[11px] text-slate-500 dark:text-slate-400">OCPP 1.6-J dynamisches PV-Überschussladen</div>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-sm font-black font-mono text-emerald-600 dark:text-emerald-400">
                            {wallboxPrioW > 0 ? `-${formatW(wallboxPrioW)}` : "Warte auf Solarstrom"}
                        </div>
                        <div className="text-[10px] text-slate-400">Netzexport: {formatW(gridExportW)}</div>
                    </div>
                </div>
            </div>
        </div>
    );
}
