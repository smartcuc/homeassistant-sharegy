import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Sun, BatteryCharging, Car, Flame, Home, Network, Users, ArrowRight, ShieldCheck, Zap, Sparkles } from "lucide-react";

export default function LiveEnergyFlowSimulator({ className = "" }) {
    const { t } = useTranslation();

    const SCENARIOS = {
        solar_surplus: {
            id: "solar_surplus",
            title: "☀️ Hoher PV-Überschuss (Mittag)",
            desc: "PV erzeugt maximal. EMS lädt Auto und Speicher, der Rest wird im Quartier mit Nachbarn geteilt.",
            badge: "Autarkie 100% · Sharing aktiv",
            badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
            pvKw: 8.8,
            pvStatus: "Erzeugung",
            batteryKw: -2.4, // charging
            batterySoc: 74,
            homeKw: 1.2,
            wallboxKw: 4.2,
            wallboxMode: "PV-Überschuss",
            heatpumpKw: 0.0,
            gridKw: 0.0,
            communityKw: 1.0, // sharing to neighbors
            priceCt: 28.4,
            enwgStatus: "Autark",
        },
        dynamic_tariff: {
            id: "dynamic_tariff",
            title: "🌙 Günstiger Nachtstrom (Arbitrage)",
            desc: "Börsenpreis bei 12 ct/kWh. EMS lädt den Speicher & das E-Auto automatisch im Preistief.",
            badge: "Arbitrage aktiv · Netzkauf",
            badgeColor: "bg-indigo-500/20 text-indigo-300 border-indigo-500/30",
            pvKw: 0.0,
            pvStatus: "Nacht",
            batteryKw: -3.0, // charging from grid
            batterySoc: 38,
            homeKw: 0.8,
            wallboxKw: 7.4,
            wallboxMode: "Nacht-Günstig",
            heatpumpKw: 1.8,
            gridKw: 13.0, // importing cheap
            communityKw: 0.0,
            priceCt: 12.8,
            enwgStatus: "Smart Charge",
        },
        evening_peak: {
            id: "evening_peak",
            title: "⚡ Abend-Peak (Hohe Börsenpreise)",
            desc: "Strompreis bei 44 ct/kWh. Heimspeicher puffert den Haushalt und speist Nachbarhäuser.",
            badge: "0 € Netzkosten · Peak Shaving",
            badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/30",
            pvKw: 0.4,
            pvStatus: "Dämmerung",
            batteryKw: 3.2, // discharging
            batterySoc: 88,
            homeKw: 2.1,
            wallboxKw: 0.0,
            wallboxMode: "Standby",
            heatpumpKw: 1.2,
            gridKw: 0.0,
            communityKw: 0.3, // sharing to neighbor
            priceCt: 44.2,
            enwgStatus: "Puffer aktiv",
        },
        enwg_dimming: {
            id: "enwg_dimming",
            title: "🛡️ § 14a EnWG Dimmung (Netzschutz)",
            desc: "Netzbetreiber fordert Dimmung. EMS regelt Wallbox & WP präzise auf 4,2 kW und sichert 160 € Prämie.",
            badge: "§ 14a Modul 1 aktiv",
            badgeColor: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30",
            pvKw: 2.5,
            pvStatus: "Bewölkt",
            batteryKw: 1.2,
            batterySoc: 65,
            homeKw: 1.5,
            wallboxKw: 2.2, // dimmed
            wallboxMode: "§ 14a Gedimmt (2.2 kW)",
            heatpumpKw: 2.0, // dimmed
            gridKw: 2.0,
            communityKw: 0.0,
            priceCt: 31.5,
            enwgStatus: "Konform (4.2 kW Limit)",
        },
    };

    const [activeScenarioKey, setActiveScenarioKey] = useState("solar_surplus");
    const [animationTick, setAnimationTick] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setAnimationTick(prev => (prev + 1) % 100);
        }, 1500);
        return () => clearInterval(interval);
    }, []);

    const s = SCENARIOS[activeScenarioKey];

    return (
        <div className={`bg-gradient-to-br from-slate-900 via-slate-950 to-indigo-950/80 rounded-3xl border border-indigo-500/30 p-6 md:p-8 text-white shadow-2xl relative overflow-hidden ${className}`}>
            {/* Background Glows */}
            <div className="absolute top-0 right-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

            {/* Header / Scenario Selection */}
            <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-indigo-900/50 pb-6">
                <div>
                    <div className="flex items-center gap-2">
                        <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-black uppercase tracking-wider">
                            Interactive Live Canvas
                        </span>
                        <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${s.badgeColor}`}>
                            {s.badge}
                        </span>
                    </div>
                    <h3 className="text-xl md:text-2xl font-black text-white mt-1.5 flex items-center gap-2">
                        <span>Echtzeit-Energiefluss & Quartiers-Sharing</span>
                    </h3>
                    <p className="text-xs md:text-sm text-indigo-200/70 mt-1 max-w-xl">
                        {s.desc}
                    </p>
                </div>

                {/* Scenario Toggle Tabs */}
                <div className="grid grid-cols-2 sm:grid-cols-4 lg:flex lg:flex-wrap gap-1.5 bg-slate-950/60 p-1.5 rounded-2xl border border-indigo-900/40">
                    {Object.values(SCENARIOS).map(item => {
                        const isActive = item.id === activeScenarioKey;
                        return (
                            <button
                                key={item.id}
                                type="button"
                                onClick={() => setActiveScenarioKey(item.id)}
                                className={`px-3 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer text-left sm:text-center ${
                                    isActive
                                        ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30 border border-indigo-400/40"
                                        : "text-slate-400 hover:text-white hover:bg-white/5 border border-transparent"
                                }`}
                            >
                                <span className="block truncate">{item.title.split(" ")[0]} {item.title.split(" ")[1]}</span>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Center Grid: Energy OS Hub */}
            <div className="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-6 my-8 items-center">
                {/* Left Column: Generation & Grid */}
                <div className="space-y-4">
                    {/* PV Inverter */}
                    <div className="p-4 rounded-2xl bg-slate-900/80 border border-amber-500/30 hover:border-amber-400/60 transition shadow-sm relative overflow-hidden group">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2.5">
                                <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
                                    <Sun className="w-5 h-5" />
                                </div>
                                <div>
                                    <div className="text-xs text-slate-400 font-semibold uppercase">PV-Anlage</div>
                                    <div className="text-sm font-bold text-white">{s.pvStatus}</div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-xl font-black font-mono text-amber-400">
                                    {s.pvKw > 0 ? `+${s.pvKw.toFixed(1)}` : "0.0"} <span className="text-xs font-normal">kW</span>
                                </div>
                                <div className="text-[10px] text-amber-300/80 font-medium">10 kWp Anlage</div>
                            </div>
                        </div>
                    </div>

                    {/* Grid Node */}
                    <div className="p-4 rounded-2xl bg-slate-900/80 border border-indigo-500/30 hover:border-indigo-400/60 transition shadow-sm relative overflow-hidden group">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2.5">
                                <div className="p-2.5 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                                    <Network className="w-5 h-5" />
                                </div>
                                <div>
                                    <div className="text-xs text-slate-400 font-semibold uppercase">Öffentliches Netz</div>
                                    <div className="text-xs font-bold text-indigo-300">EPEX {s.priceCt.toFixed(1)} ct/kWh</div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className={`text-xl font-black font-mono ${s.gridKw > 0 ? "text-indigo-300" : "text-slate-400"}`}>
                                    {s.gridKw > 0 ? `${s.gridKw.toFixed(1)}` : "0.0"} <span className="text-xs font-normal">kW</span>
                                </div>
                                <div className="text-[10px] text-indigo-300/80 font-medium">{s.enwgStatus}</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Center: Sharegy Cloud Energy Brain (Core Hub) */}
                <div className="flex flex-col items-center justify-center p-6 rounded-3xl bg-gradient-to-b from-indigo-950/80 to-slate-900/90 border-2 border-indigo-500/50 shadow-2xl shadow-indigo-500/20 text-center relative group">
                    <div className="absolute -top-3 px-3 py-0.5 rounded-full bg-indigo-500 text-white font-mono text-[10px] font-black uppercase tracking-widest shadow-md">
                        Sharegy Cloud EMS
                    </div>

                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 to-emerald-400 p-0.5 shadow-lg shadow-indigo-500/30 my-3 animate-pulse">
                        <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center text-3xl">
                            ⚡
                        </div>
                    </div>

                    <h4 className="text-base font-black text-white tracking-tight">Sub-Sekunden Regelung</h4>
                    <p className="text-xs text-indigo-200/80 mt-1 max-w-xs">
                        Optimiert PV, Speicher, Wallbox & § 14a EnWG ohne teure Hardware-Box.
                    </p>

                    <div className="grid grid-cols-2 gap-2 w-full mt-4 text-left">
                        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-2.5">
                            <div className="text-[10px] text-slate-400 font-semibold uppercase">Reaktionszeit</div>
                            <div className="text-sm font-black font-mono text-emerald-400">&lt; 850 ms</div>
                        </div>
                        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-2.5">
                            <div className="text-[10px] text-slate-400 font-semibold uppercase">§ 14a Status</div>
                            <div className="text-sm font-black font-mono text-cyan-400">Modul 1 (+160€)</div>
                        </div>
                    </div>
                </div>

                {/* Right Column: Consumers & Storage */}
                <div className="space-y-4">
                    {/* Battery Storage */}
                    <div className="p-4 rounded-2xl bg-slate-900/80 border border-emerald-500/30 hover:border-emerald-400/60 transition shadow-sm relative overflow-hidden group">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2.5">
                                <div className="p-2.5 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                                    <BatteryCharging className="w-5 h-5" />
                                </div>
                                <div>
                                    <div className="text-xs text-slate-400 font-semibold uppercase">Batteriespeicher</div>
                                    <div className="text-xs font-bold text-emerald-300">SOC {s.batterySoc}%</div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-xl font-black font-mono text-emerald-400">
                                    {s.batteryKw < 0 ? `Laden ${Math.abs(s.batteryKw).toFixed(1)}` : s.batteryKw > 0 ? `Entladen ${s.batteryKw.toFixed(1)}` : "0.0"} <span className="text-xs font-normal">kW</span>
                                </div>
                                <div className="text-[10px] text-slate-400 font-medium">10 kWh Kapazität</div>
                            </div>
                        </div>
                    </div>

                    {/* Wallbox / Heatpump / House Consumers */}
                    <div className="p-4 rounded-2xl bg-slate-900/80 border border-cyan-500/30 hover:border-cyan-400/60 transition shadow-sm relative overflow-hidden group">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2.5">
                                <div className="p-2.5 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                                    <Car className="w-5 h-5" />
                                </div>
                                <div>
                                    <div className="text-xs text-slate-400 font-semibold uppercase">Wallbox & Haus</div>
                                    <div className="text-xs font-bold text-cyan-300">{s.wallboxMode}</div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-xl font-black font-mono text-cyan-300">
                                    {(s.homeKw + s.wallboxKw + s.heatpumpKw).toFixed(1)} <span className="text-xs font-normal">kW</span>
                                </div>
                                <div className="text-[10px] text-slate-400 font-medium">Haus: {s.homeKw} kW · Auto: {s.wallboxKw} kW</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Bottom: Pillar 2 Community Energy Sharing Live Stream */}
            <div className="relative z-10 bg-gradient-to-r from-emerald-950/60 via-slate-900/90 to-indigo-950/60 border border-emerald-500/30 rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-xl">
                        🏘️
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-white uppercase tracking-wider">Säule 2: P2P Energy Sharing</span>
                            <span className="text-[10px] font-bold px-2 py-0.2 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                                Quartier vernetzt
                            </span>
                        </div>
                        <p className="text-xs text-slate-300 mt-0.5">
                            {s.communityKw > 0 
                                ? `🔥 Du teilst gerade ${s.communityKw.toFixed(1)} kW Solarstrom mit Haus #3 & #7 im Quartier.`
                                : "Gemeinschafts-Pool im Standby – bereit für den nächsten Solar-Überschuss."}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-4 text-right">
                    <div className="bg-slate-950/80 px-3.5 py-1.5 rounded-xl border border-emerald-500/30">
                        <div className="text-[10px] text-slate-400 uppercase font-semibold">Community-Vergütung</div>
                        <div className="text-sm font-black text-emerald-400 font-mono">18,5 ct/kWh <span className="text-[10px] font-normal text-slate-400">(statt 8,2 ct EEG)</span></div>
                    </div>
                </div>
            </div>
        </div>
    );
}
