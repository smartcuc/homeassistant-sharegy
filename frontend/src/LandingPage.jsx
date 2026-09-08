import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useUser } from "./hooks/useUser";
import { 
    Zap, 
    Sun, 
    BatteryCharging, 
    Car, 
    Flame, 
    ShieldCheck, 
    Users, 
    TrendingUp, 
    ArrowRight, 
    CheckCircle2, 
    Sparkles, 
    Sliders, 
    Cpu, 
    Layers, 
    HelpCircle, 
    ChevronRight,
    Eye,
    Globe
} from "lucide-react";

import Header from "./components/Header";
import Footer from "./components/Footer";
import LiveEnergyFlowSimulator from "./components/landing/LiveEnergyFlowSimulator";
import SavingsRoiCalculator from "./components/landing/SavingsRoiCalculator";
import { trackEvent } from "./lib/track";

export default function LandingPage() {
    const { t } = useTranslation();
    const { user, loading } = useUser();
    const navigate = useNavigate();

    const [activePillarTab, setActivePillarTab] = useState("pillar1"); // 'pillar1' or 'pillar2'
    const [openFaq, setOpenFaq] = useState(null);

    useEffect(() => {
        document.title = "Sharegy – Dein Energy OS | Smart EMS & P2P Energy Sharing";
        trackEvent("landing_view", { version: "v2_dual_pillar" });
    }, []);

    const scrollToSection = (id) => {
        const elem = document.getElementById(id);
        if (elem) {
            elem.scrollIntoView({ behavior: "smooth" });
        }
    };

    const HARDWARE_LOGOS = [
        { name: "SMA", type: "Wechselrichter" },
        { name: "Fronius", type: "Wechselrichter & Speicher" },
        { name: "Sungrow", type: "Hybrid-Systeme" },
        { name: "Huawei", type: "FusionSolar" },
        { name: "BYD", type: "Batteriespeicher" },
        { name: "Tesla", type: "Powerwall & EV" },
        { name: "easee", type: "Wallbox (OCPP)" },
        { name: "go-e", type: "Wallbox" },
        { name: "openWB", type: "Wallbox & Steuerung" },
        { name: "Daikin", type: "Wärmepumpe (SG-Ready)" },
        { name: "Viessmann", type: "Wärmepumpe" },
        { name: "Vaillant", type: "Wärmepumpe" },
        { name: "Shelly", type: "Relais & Messung" },
    ];

    const FAQS = [
        {
            q: "Brauche ich eine zusätzliche teure Hardware-Box im Zählerschrank?",
            a: "Nein! Sharegy ist 100% Cloud- & Protokoll-basiert. Wir verbinden uns direkt über die Standard-Schnittstellen deiner vorhandenen Geräte (Modbus TCP, OCPP 1.6-J, SunSpec, Cloud-APIs). Du sparst dir Anschaffungs- und Installationskosten von 800 € bis 1.500 € für proprietäre Hardware."
        },
        {
            q: "Wie funktioniert die § 14a EnWG Netzentgelt-Reduzierung?",
            a: "Sharegy erfüllt alle Vorgaben nach § 14a EnWG für steuerbare Verbrauchseinrichtungen (Wallboxen, Wärmepumpen, Batteriespeicher). Durch die netzdienliche Dimmungsfähigkeit sicherst du dir die jährliche Pauschale (Modul 1: ca. 160 € bis 190 €/Jahr) oder signifikant reduzierte Netzentgelte (Modul 2)."
        },
        {
            q: "Was ist der Unterschied zwischen Säule 1 (Smart EMS) und Säule 2 (Energy Sharing)?",
            a: "Säule 1 optimiert deine eigene Anlage im Haus (PV-Überschuss ins Auto und den Speicher, dynamische Strompreise, § 14a Netzentgelte). Säule 2 verbindet dich mit deinen Nachbarn, Mietern oder deiner Familie: Wenn dein Speicher voll ist, teilst du deinen Solarstrom im Quartier zu fairen Preisen (z.B. 18,5 ct/kWh), statt ihn für geringe Cent-Beträge ins Netz einzuspeisen."
        },
        {
            q: "Wie kann ich die Live-Demo testen?",
            a: "Klicke einfach oben auf 'Live-Demo ansehen' oder nutze den interaktiven Simulator direkt auf dieser Seite. Du kannst sofort alle Steuerungsmodi und Szenarien interaktiv ausprobieren – ganz ohne Registrierung."
        }
    ];

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-emerald-500 selection:text-slate-950 font-sans">
            {/* 🔝 HEADER */}
            <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80 transition-all">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
                    {/* Brand */}
                    <Link to="/" className="flex items-center gap-2 group cursor-pointer">
                        <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-amber-400 via-orange-500 to-indigo-600 p-0.5 shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
                            <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center text-xl">
                                ⚡
                            </div>
                        </div>
                        <div className="flex flex-col">
                            <span className="font-mono text-xl font-black tracking-tight text-white flex items-center gap-1">
                                sharegy
                                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                                    OS
                                </span>
                            </span>
                            <span className="text-[10px] text-slate-400 font-medium -mt-0.5">Energy Operating System</span>
                        </div>
                    </Link>

                    {/* Navigation Links */}
                    <nav className="hidden md:flex items-center gap-6 text-xs font-semibold text-slate-300">
                        <button onClick={() => scrollToSection("pillars")} className="hover:text-white transition cursor-pointer">
                            Die 2 Säulen
                        </button>
                        <button onClick={() => scrollToSection("simulator")} className="hover:text-white transition cursor-pointer flex items-center gap-1.5">
                            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                            Live-Simulator
                        </button>
                        <button onClick={() => scrollToSection("calculator")} className="hover:text-white transition cursor-pointer">
                            Ersparnis-Rechner
                        </button>
                        <button onClick={() => scrollToSection("hardware")} className="hover:text-white transition cursor-pointer">
                            Kompatibilität
                        </button>
                        <button onClick={() => scrollToSection("faq")} className="hover:text-white transition cursor-pointer">
                            FAQ
                        </button>
                    </nav>

                    {/* Action CTAs */}
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => scrollToSection("simulator")}
                            className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-indigo-200 hover:text-white border border-indigo-500/30 text-xs font-bold transition cursor-pointer"
                        >
                            <Eye className="w-3.5 h-3.5 text-indigo-400" />
                            <span>Live-Demo</span>
                        </button>

                        {user ? (
                            <Link
                                to="/app/dashboard"
                                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition flex items-center gap-1.5 shadow-lg shadow-indigo-600/30"
                            >
                                <span>Zum Dashboard</span>
                                <ArrowRight className="w-3.5 h-3.5" />
                            </Link>
                        ) : (
                            <Link
                                to="/login"
                                className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 text-xs font-black uppercase tracking-wider transition flex items-center gap-1.5 shadow-lg shadow-emerald-500/20"
                            >
                                <span>Login / Starten</span>
                                <ArrowRight className="w-3.5 h-3.5" />
                            </Link>
                        )}
                    </div>
                </div>
            </header>

            {/* 🔥 HERO SECTION */}
            <section className="relative pt-16 pb-24 px-4 sm:px-6 lg:px-8 overflow-hidden">
                {/* Background Ambient Lights */}
                <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-gradient-to-tr from-indigo-600/20 via-emerald-600/15 to-transparent rounded-full blur-3xl pointer-events-none" />

                <div className="max-w-5xl mx-auto text-center relative z-10 space-y-6">
                    {/* Top Pill */}
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-900/90 border border-indigo-500/40 text-xs font-bold text-indigo-200 shadow-xl">
                        <Sparkles className="w-4 h-4 text-amber-400 animate-spin-slow" />
                        <span>Säule 1 (Smart EMS & § 14a) & Säule 2 (P2P Energy Sharing)</span>
                        <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] uppercase font-mono">100% Cloud</span>
                    </div>

                    {/* Main Headline */}
                    <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-white leading-[1.1]">
                        Das <span className="bg-gradient-to-r from-amber-300 via-emerald-400 to-teal-300 bg-clip-text text-transparent">Energy OS</span> für dein Zuhause & dein Quartier.
                    </h1>

                    {/* Subtitle */}
                    <p className="max-w-3xl mx-auto text-base sm:text-lg text-slate-300 leading-relaxed font-normal">
                        Keine teure 1.500 € Zusatzbox. Sharegy steuert deine <strong>PV-Anlage, Heimspeicher, Wallbox & Wärmepumpe</strong> vollautomatisch nach dynamischen Strompreisen & § 14a EnWG – und ermöglicht <strong>echtes P2P Energy Sharing</strong> mit deinen Nachbarn.
                    </p>

                    {/* Hero Buttons */}
                    <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
                        <button
                            onClick={() => scrollToSection("simulator")}
                            className="w-full sm:w-auto px-7 py-4 rounded-2xl bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 font-black text-sm uppercase tracking-wider flex items-center justify-center gap-2.5 shadow-xl shadow-emerald-500/25 hover:scale-[1.02] transition-all cursor-pointer"
                        >
                            <span>🚀 Live-Demo ohne Registrierung</span>
                            <ArrowRight className="w-4 h-4" />
                        </button>

                        <Link
                            to="/login"
                            className="w-full sm:w-auto px-7 py-4 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm border border-slate-700 hover:border-indigo-400/50 flex items-center justify-center gap-2 transition-all cursor-pointer shadow-lg"
                        >
                            <span>Kostenlos starten</span>
                            <ChevronRight className="w-4 h-4 text-slate-400" />
                        </Link>
                    </div>

                    {/* Feature Highlights Badges */}
                    <div className="pt-8 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-xs text-slate-400 font-medium">
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                            <span>100% Cloud-basiert (Kein Raspberry Pi / keine Box)</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                            <span>§ 14a EnWG Netzentgelt-Prämie (+160 €/a)</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                            <span>Sub-Sekunden PV-Überschussregelung</span>
                        </div>
                    </div>
                </div>
            </section>

            {/* 🛠️ HARDWARE & ECOSYSTEM TRUST BAR */}
            <section id="hardware" className="py-12 border-y border-slate-800/80 bg-slate-950/60">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <p className="text-center text-xs font-bold uppercase tracking-widest text-slate-400 mb-6">
                        Nahtlos kompatibel mit führenden Herstellern & offenen Standards
                    </p>

                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
                        {HARDWARE_LOGOS.map((hw, idx) => (
                            <div
                                key={idx}
                                className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3 text-center hover:border-indigo-500/40 transition group"
                            >
                                <div className="font-mono font-bold text-slate-200 group-hover:text-emerald-400 transition-colors">
                                    {hw.name}
                                </div>
                                <div className="text-[10px] text-slate-400 mt-0.5">
                                    {hw.type}
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="mt-6 flex flex-wrap items-center justify-center gap-4 text-xs font-mono text-slate-400">
                        <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800">Modbus TCP</span>
                        <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800">OCPP 1.6-J</span>
                        <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800">SunSpec</span>
                        <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800">SG-Ready</span>
                        <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800">REST API</span>
                        <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800">Home Assistant Bridge</span>
                    </div>
                </div>
            </section>

            {/* 🏛️ THE 2 PILLARS OF SHAREGY (EQUITABLE DUAL-PILLAR SHOWCASE) */}
            <section id="pillars" className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
                <div className="text-center max-w-3xl mx-auto mb-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs font-black uppercase tracking-wider mb-3">
                        Das Fundament
                    </div>
                    <h2 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
                        Zwei gleichberechtigte Säulen für deine Energiezukunft
                    </h2>
                    <p className="text-slate-400 text-sm sm:text-base mt-4">
                        Sharegy vereint dezentrales High-Tech Smart-Home Energiemanagement mit dezentralem P2P Energy Sharing im Quartier.
                    </p>
                </div>

                {/* Pillar Selector Tabs */}
                <div className="flex justify-center mb-10">
                    <div className="bg-slate-900 p-1.5 rounded-2xl border border-slate-800 flex gap-2">
                        <button
                            type="button"
                            onClick={() => setActivePillarTab("pillar1")}
                            className={`px-5 py-3 rounded-xl text-xs sm:text-sm font-black transition-all cursor-pointer flex items-center gap-2 ${
                                activePillarTab === "pillar1"
                                    ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
                                    : "text-slate-400 hover:text-white"
                            }`}
                        >
                            <Zap className="w-4 h-4 text-amber-400" />
                            <span>Säule 1: Smart EMS & § 14a EnWG</span>
                        </button>

                        <button
                            type="button"
                            onClick={() => setActivePillarTab("pillar2")}
                            className={`px-5 py-3 rounded-xl text-xs sm:text-sm font-black transition-all cursor-pointer flex items-center gap-2 ${
                                activePillarTab === "pillar2"
                                    ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30 border border-emerald-400/30"
                                    : "text-slate-400 hover:text-white"
                            }`}
                        >
                            <Users className="w-4 h-4 text-teal-300" />
                            <span>Säule 2: P2P Energy Sharing</span>
                        </button>
                    </div>
                </div>

                {/* Pillar 1 Content */}
                {activePillarTab === "pillar1" && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in">
                        {/* Feature 1 */}
                        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 hover:border-indigo-500/40 transition">
                            <div className="w-12 h-12 rounded-2xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-2xl mb-5">
                                ☀️
                            </div>
                            <h3 className="text-lg font-bold text-white">Sub-Sekunden PV-Überschussregelung</h3>
                            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                                Dynamische Anpassung von Wallbox und Heizstab in Echtzeit. Dein Auto lädt genau mit der Sonnenenergie, die vom Dach kommt – ohne teuren Netzstrom.
                            </p>
                            <div className="mt-4 pt-4 border-t border-slate-800/80 text-xs text-amber-400 font-semibold">
                                ✓ Automatische Phasen-Umschaltung (1p/3p)
                            </div>
                        </div>

                        {/* Feature 2 */}
                        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 hover:border-indigo-500/40 transition">
                            <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-2xl mb-5">
                                📈
                            </div>
                            <h3 className="text-lg font-bold text-white">Dynamischer Strompreis-Radar</h3>
                            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                                Integration von Börsenstrompreisen (EPEX Spot / Awattar / Tibber). Der Heimspeicher lädt vollautomatisch in Niedrigpreisphasen und puffert Spitzenpreise ab.
                            </p>
                            <div className="mt-4 pt-4 border-t border-slate-800/80 text-xs text-indigo-300 font-semibold">
                                ✓ Bis zu 35% geringere Netzstromkosten
                            </div>
                        </div>

                        {/* Feature 3 */}
                        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 hover:border-indigo-500/40 transition">
                            <div className="w-12 h-12 rounded-2xl bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-2xl mb-5">
                                🛡️
                            </div>
                            <h3 className="text-lg font-bold text-white">§ 14a EnWG Netzentgelt-Bonus</h3>
                            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                                Gesetzliche Steuerung für Wallboxen und Wärmepumpen (SteuVE). Sharegy garantiert netzdienliche Dimmung auf 4,2 kW und sichert dir die volle Jahrespauschale.
                            </p>
                            <div className="mt-4 pt-4 border-t border-slate-800/80 text-xs text-cyan-300 font-semibold">
                                ✓ Modul 1 Pauschale (+160 € / Jahr)
                            </div>
                        </div>
                    </div>
                )}

                {/* Pillar 2 Content */}
                {activePillarTab === "pillar2" && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in">
                        {/* Feature 1 */}
                        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 hover:border-emerald-500/40 transition">
                            <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-2xl mb-5">
                                🏘️
                            </div>
                            <h3 className="text-lg font-bold text-white">Quartiers-Strompool (§ 42b EnWG)</h3>
                            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                                Überschussstrom nicht für 8 Cent verschenken: Teile deinen Solarstrom direkt mit Nachbarn, Mietern oder Familienmitgliedern im selben Quartier.
                            </p>
                            <div className="mt-4 pt-4 border-t border-slate-800/80 text-xs text-emerald-400 font-semibold">
                                ✓ Mehr Ertrag für Erzeuger, günstiger für Nachbarn
                            </div>
                        </div>

                        {/* Feature 2 */}
                        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 hover:border-emerald-500/40 transition">
                            <div className="w-12 h-12 rounded-2xl bg-teal-500/20 border border-teal-500/30 flex items-center justify-center text-2xl mb-5">
                                📊
                            </div>
                            <h3 className="text-lg font-bold text-white">100% Automatisierte Abrechnung</h3>
                            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                                Keine manuellen Excel-Tabellen oder Zählerablesungen. Sharegy saldiert alle kWh sub-sekundengenau und generiert automatische monatliche Abrechnungsbelege.
                            </p>
                            <div className="mt-4 pt-4 border-t border-slate-800/80 text-xs text-teal-300 font-semibold">
                                ✓ Rechtssicher & Mieterstrom-konform
                            </div>
                        </div>

                        {/* Feature 3 */}
                        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 hover:border-emerald-500/40 transition">
                            <div className="w-12 h-12 rounded-2xl bg-teal-500/20 border border-teal-500/30 flex items-center justify-center text-2xl mb-5">
                                🏆
                            </div>
                            <h3 className="text-lg font-bold text-white">Community Autarkie & Social Proof</h3>
                            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                                Verfolge den gemeinsamen Autarkiegrad deines Quartiers, teile Erfolge auf LinkedIn & WhatsApp und mache dein Viertel gemeinsam CO₂-neutral.
                            </p>
                            <div className="mt-4 pt-4 border-t border-slate-800/80 text-xs text-teal-300 font-semibold">
                                ✓ Gamification & Quartiers-Rangliste
                            </div>
                        </div>
                    </div>
                )}
            </section>

            {/* ⚡ INTERACTIVE LIVE ENERGY FLOW SIMULATOR (REPLACING THE OLD SVG) */}
            <section id="simulator" className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
                <div className="text-center max-w-3xl mx-auto mb-10">
                    <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-black uppercase tracking-wider">
                        Live Simulation
                    </span>
                    <h2 className="text-3xl sm:text-4xl font-black text-white mt-2 tracking-tight">
                        So steuert Sharegy dein Energie-Ökosystem
                    </h2>
                    <p className="text-slate-400 text-xs sm:text-sm mt-2">
                        Wähle verschiedene Wetterszenarien & Strompreise und beobachte die sub-sekundengenaue Verteilung in Echtzeit.
                    </p>
                </div>

                {/* Embedded High-End Simulator Component */}
                <LiveEnergyFlowSimulator />
            </section>

            {/* 💡 HARDWARE VERGLEICH: CLOUD EMS VS. TEURE ZUSATZBOX */}
            <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto">
                <div className="bg-slate-900/70 border border-slate-800 rounded-3xl p-6 md:p-10 shadow-xl">
                    <h3 className="text-2xl font-black text-white text-center mb-8">
                        Warum Sharegy? Der direkte Vergleich
                    </h3>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs sm:text-sm">
                            <thead>
                                <tr className="border-b border-slate-800 text-slate-400">
                                    <th className="pb-4 font-bold">Merkmal</th>
                                    <th className="pb-4 font-black text-emerald-400">⚡ Sharegy Cloud Energy OS</th>
                                    <th className="pb-4 font-medium text-slate-500">Klassische Hardware-Boxen</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/60">
                                <tr>
                                    <td className="py-4 font-semibold text-white">Anschaffungskosten</td>
                                    <td className="py-4 font-bold text-emerald-400">0 € (100% Cloud-basiert)</td>
                                    <td className="py-4 text-slate-400">800 € – 1.500 € Hardware-Kauf</td>
                                </tr>
                                <tr>
                                    <td className="py-4 font-semibold text-white">Elektriker-Installation</td>
                                    <td className="py-4 font-bold text-emerald-400">Nicht erforderlich (Plug & Connect)</td>
                                    <td className="py-4 text-slate-400">300 € – 600 € Einbau im Schaltschrank</td>
                                </tr>
                                <tr>
                                    <td className="py-4 font-semibold text-white">P2P Energy Sharing</td>
                                    <td className="py-4 font-bold text-emerald-400">Nativ integriert (Quartiers-Pool)</td>
                                    <td className="py-4 text-slate-500">❌ Nicht unterstützt (Insel-System)</td>
                                </tr>
                                <tr>
                                    <td className="py-4 font-semibold text-white">§ 14a EnWG Steuerung</td>
                                    <td className="py-4 font-bold text-emerald-400">Automatisiert (Modul 1 + 2)</td>
                                    <td className="py-4 text-slate-400">Oft nur mit teuren Zusatz-Relais</td>
                                </tr>
                                <tr>
                                    <td className="py-4 font-semibold text-white">Hersteller-Freiheit</td>
                                    <td className="py-4 font-bold text-emerald-400">Offen (Modbus, OCPP, SunSpec)</td>
                                    <td className="py-4 text-slate-500">Oft proprietärer Vendor Lock-in</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            {/* 💰 INTERACTIVE ROI & § 14a SAVINGS CALCULATOR */}
            <section id="calculator" className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
                <SavingsRoiCalculator />
            </section>

            {/* ❓ FAQ SECTION */}
            <section id="faq" className="py-20 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h2 className="text-2xl sm:text-4xl font-black text-white">Häufig gestellte Fragen</h2>
                    <p className="text-slate-400 text-xs sm:text-sm mt-2">Alles, was du über Sharegy, die Cloud-Steuerung und Energy Sharing wissen musst.</p>
                </div>

                <div className="space-y-4">
                    {FAQS.map((faq, idx) => {
                        const isOpen = openFaq === idx;
                        return (
                            <div key={idx} className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden transition">
                                <button
                                    type="button"
                                    onClick={() => setOpenFaq(isOpen ? null : idx)}
                                    className="w-full p-5 text-left flex items-center justify-between gap-4 cursor-pointer hover:bg-slate-800/40"
                                >
                                    <span className="font-bold text-sm text-white">{faq.q}</span>
                                    <span className="text-indigo-400 text-lg font-bold">{isOpen ? "−" : "+"}</span>
                                </button>
                                {isOpen && (
                                    <div className="px-5 pb-5 text-xs sm:text-sm text-slate-300 leading-relaxed border-t border-slate-800/60 pt-4">
                                        {faq.a}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </section>

            {/* 🚀 FINAL CTA BANNER */}
            <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto">
                <div className="bg-gradient-to-r from-indigo-950 via-slate-900 to-emerald-950 border-2 border-indigo-500/40 rounded-3xl p-8 sm:p-12 text-center shadow-2xl relative overflow-hidden">
                    <div className="relative z-10 space-y-6">
                        <h2 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
                            Bereit für dein smartes Energy OS?
                        </h2>
                        <p className="text-sm sm:text-base text-indigo-200/80 max-w-2xl mx-auto">
                            Verbinde deine PV-Anlage, Wallbox & Speicher in wenigen Klicks – oder teste sofort die interaktive Live-Demo.
                        </p>
                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
                            <button
                                onClick={() => scrollToSection("simulator")}
                                className="w-full sm:w-auto px-8 py-4 rounded-xl bg-slate-950 hover:bg-slate-900 text-indigo-300 border border-indigo-400/40 font-bold text-sm transition cursor-pointer"
                            >
                                <span>Live-Demo im Simulator testen</span>
                            </button>
                            <Link
                                to="/login"
                                className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-black text-sm uppercase tracking-wider transition cursor-pointer shadow-lg shadow-emerald-500/25"
                            >
                                <span>Jetzt kostenlos starten →</span>
                            </Link>
                        </div>
                    </div>
                </div>
            </section>

            {/* 🦶 FOOTER */}
            <Footer />
        </div>
    );
}