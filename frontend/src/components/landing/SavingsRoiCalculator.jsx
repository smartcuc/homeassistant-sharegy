import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Calculator, TrendingUp, ShieldCheck, Zap, ArrowRight, CheckCircle2 } from "lucide-react";
import { Link } from "react-router-dom";

export default function SavingsRoiCalculator({ className = "" }) {
    const { t } = useTranslation();

    const [pvKwp, setPvKwp] = useState(10);
    const [batteryKwh, setBatteryKwh] = useState(10);
    const [hasWallbox, setHasWallbox] = useState(true);
    const [hasHeatPump, setHasHeatPump] = useState(true);
    const [participatesSharing, setParticipatesSharing] = useState(true);

    // Calculations
    // 1. PV Generation ~ 950 kWh / kWp
    const annualSolarGen = pvKwp * 950;
    
    // Baseline self-consumption without smart EMS ~ 30%, with battery ~ 65%, with smart EMS & EV/HeatPump ~ 85%
    const baseAutarky = pvKwp === 0 ? 0 : batteryKwh > 0 ? (hasWallbox && hasHeatPump ? 0.85 : 0.70) : 0.35;
    
    // Self consumed kWh
    const selfConsumedKwh = Math.round(annualSolarGen * baseAutarky);
    const gridPriceEur = 0.365;
    const feedInTariffEur = 0.082;
    
    // Direct Self-Consumption Savings
    const directSavings = Math.round(selfConsumedKwh * (gridPriceEur - feedInTariffEur));
    
    // § 14a Netzentgelt Modul 1 Pauschale
    const enwgBonus = (hasWallbox || hasHeatPump) ? 160 : 0;
    
    // Energy Sharing P2P Surplus Revenue (~ 1.500 kWh shared with neighbors @ 18.5 ct instead of 8.2 ct EEG = +155 €)
    const surplusKwh = Math.max(0, annualSolarGen - selfConsumedKwh);
    const sharingBonus = participatesSharing && surplusKwh > 500 
        ? Math.round(Math.min(surplusKwh * 0.5, 2000) * (0.185 - 0.082))
        : 0;

    // Dynamic Tariffs Arbitrage (Charging battery/car in low price hours)
    const arbitrageSavings = (batteryKwh > 0 || hasWallbox) ? Math.round(batteryKwh * 18 + (hasWallbox ? 140 : 0)) : 0;

    const totalAnnualBenefit = directSavings + enwgBonus + sharingBonus + arbitrageSavings;

    return (
        <div className={`bg-slate-900 border border-slate-800 rounded-3xl p-6 md:p-8 text-white shadow-2xl relative overflow-hidden ${className}`}>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6 mb-8">
                <div>
                    <div className="flex items-center gap-2">
                        <span className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-xs font-black uppercase tracking-wider">
                            Transparenz-Rechner
                        </span>
                        <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                            § 14a EnWG + P2P Sharing
                        </span>
                    </div>
                    <h3 className="text-xl md:text-2xl font-black text-white mt-1.5">
                        Dein jährlicher Sharegy-Vorteil
                    </h3>
                    <p className="text-xs md:text-sm text-slate-400 mt-1">
                        Passe deine Haushaltsausstattung an und sieh deinen exakten Kostenvorteil im Vergleich zum Standard-Grundversorger.
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
                {/* Left: Interactive Controls (7 cols) */}
                <div className="lg:col-span-7 space-y-6">
                    {/* PV Slider */}
                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                                <span>☀️</span> PV-Leistung
                            </label>
                            <span className="font-mono text-base font-black text-amber-400 bg-slate-950 px-3 py-1 rounded-xl border border-slate-800">
                                {pvKwp} kWp
                            </span>
                        </div>
                        <input
                            type="range"
                            min="0"
                            max="25"
                            step="1"
                            value={pvKwp}
                            onChange={(e) => setPvKwp(Number(e.target.value))}
                            className="w-full accent-amber-400 h-2 bg-slate-950 rounded-lg cursor-pointer"
                        />
                        <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
                            <span>0 kWp (Mieter)</span>
                            <span>10 kWp (Standard EFH)</span>
                            <span>25 kWp (Großanlage)</span>
                        </div>
                    </div>

                    {/* Battery Slider */}
                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                                <span>🔋</span> Heimspeicher-Kapazität
                            </label>
                            <span className="font-mono text-base font-black text-emerald-400 bg-slate-950 px-3 py-1 rounded-xl border border-slate-800">
                                {batteryKwh} kWh
                            </span>
                        </div>
                        <input
                            type="range"
                            min="0"
                            max="20"
                            step="1"
                            value={batteryKwh}
                            onChange={(e) => setBatteryKwh(Number(e.target.value))}
                            className="w-full accent-emerald-400 h-2 bg-slate-950 rounded-lg cursor-pointer"
                        />
                        <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
                            <span>Ohne Speicher</span>
                            <span>10 kWh</span>
                            <span>20 kWh</span>
                        </div>
                    </div>

                    {/* Toggle Badges */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                        <button
                            type="button"
                            onClick={() => setHasWallbox(!hasWallbox)}
                            className={`p-3 rounded-2xl border text-left transition-all cursor-pointer ${
                                hasWallbox
                                    ? "bg-cyan-950/40 border-cyan-500/50 text-white"
                                    : "bg-slate-950/50 border-slate-800 text-slate-500 hover:border-slate-700"
                            }`}
                        >
                            <div className="flex items-center justify-between">
                                <span className="text-lg">🚗</span>
                                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${hasWallbox ? "bg-cyan-500/20 text-cyan-300" : "bg-slate-800 text-slate-400"}`}>
                                    {hasWallbox ? "Aktiv" : "Aus"}
                                </span>
                            </div>
                            <div className="text-xs font-bold mt-2">Wallbox (E-Auto)</div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Überschussladung</div>
                        </button>

                        <button
                            type="button"
                            onClick={() => setHasHeatPump(!hasHeatPump)}
                            className={`p-3 rounded-2xl border text-left transition-all cursor-pointer ${
                                hasHeatPump
                                    ? "bg-indigo-950/40 border-indigo-500/50 text-white"
                                    : "bg-slate-950/50 border-slate-800 text-slate-500 hover:border-slate-700"
                            }`}
                        >
                            <div className="flex items-center justify-between">
                                <span className="text-lg">♨️</span>
                                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${hasHeatPump ? "bg-indigo-500/20 text-indigo-300" : "bg-slate-800 text-slate-400"}`}>
                                    {hasHeatPump ? "Aktiv" : "Aus"}
                                </span>
                            </div>
                            <div className="text-xs font-bold mt-2">Wärmepumpe</div>
                            <div className="text-[10px] text-slate-400 mt-0.5">SG-Ready & § 14a</div>
                        </button>

                        <button
                            type="button"
                            onClick={() => setParticipatesSharing(!participatesSharing)}
                            className={`p-3 rounded-2xl border text-left transition-all cursor-pointer ${
                                participatesSharing
                                    ? "bg-emerald-950/40 border-emerald-500/50 text-white"
                                    : "bg-slate-950/50 border-slate-800 text-slate-500 hover:border-slate-700"
                            }`}
                        >
                            <div className="flex items-center justify-between">
                                <span className="text-lg">🏘️</span>
                                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${participatesSharing ? "bg-emerald-500/20 text-emerald-300" : "bg-slate-800 text-slate-400"}`}>
                                    {participatesSharing ? "Aktiv" : "Aus"}
                                </span>
                            </div>
                            <div className="text-xs font-bold mt-2">Energy Sharing</div>
                            <div className="text-[10px] text-slate-400 mt-0.5">Quartiers-Community</div>
                        </button>
                    </div>
                </div>

                {/* Right: Calculated Live Breakdown (5 cols) */}
                <div className="lg:col-span-5 bg-gradient-to-b from-slate-950 via-slate-900 to-indigo-950/70 border-2 border-emerald-500/40 rounded-3xl p-6 shadow-2xl relative">
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                        Berechneter Gesamtvorteil
                    </div>
                    <div className="text-4xl font-black font-mono text-emerald-400 mt-2 flex items-baseline gap-1.5">
                        <span>+{totalAnnualBenefit.toLocaleString("de-DE")}</span>
                        <span className="text-base font-normal text-indigo-200">€ / Jahr</span>
                    </div>

                    <div className="space-y-3 mt-6 border-t border-slate-800 pt-5 text-xs">
                        <div className="flex justify-between items-center">
                            <span className="text-slate-300 flex items-center gap-1.5">
                                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                                Eigenverbrauchs-Optimierung
                            </span>
                            <span className="font-mono font-bold text-white">+{directSavings} €</span>
                        </div>

                        {enwgBonus > 0 && (
                            <div className="flex justify-between items-center">
                                <span className="text-slate-300 flex items-center gap-1.5">
                                    <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                                    § 14a EnWG Netzentgelt-Bonus
                                </span>
                                <span className="font-mono font-bold text-cyan-300">+{enwgBonus} €</span>
                            </div>
                        )}

                        {sharingBonus > 0 && (
                            <div className="flex justify-between items-center">
                                <span className="text-slate-300 flex items-center gap-1.5">
                                    <CheckCircle2 className="w-4 h-4 text-teal-400" />
                                    P2P Community-Mehrerlös
                                </span>
                                <span className="font-mono font-bold text-teal-300">+{sharingBonus} €</span>
                            </div>
                        )}

                        {arbitrageSavings > 0 && (
                            <div className="flex justify-between items-center">
                                <span className="text-slate-300 flex items-center gap-1.5">
                                    <CheckCircle2 className="w-4 h-4 text-indigo-400" />
                                    Dynamischer Tarif & Arbitrage
                                </span>
                                <span className="font-mono font-bold text-indigo-300">+{arbitrageSavings} €</span>
                            </div>
                        )}
                    </div>

                    <div className="mt-6 pt-5 border-t border-slate-800">
                        <Link
                            to="/login"
                            className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-black text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20 transition cursor-pointer"
                        >
                            <span>Jetzt mit Sharegy starten</span>
                            <ArrowRight className="w-4 h-4" />
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
