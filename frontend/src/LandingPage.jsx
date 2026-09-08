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
    Globe,
    Info
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
        trackEvent("landing_view", { version: "v2_dual_pillar_light" });
    }, []);

    const scrollToSection = (id) => {
        const elem = document.getElementById(id);
        if (elem) {
            elem.scrollIntoView({ behavior: "smooth" });
        }
    };

    const HARDWARE_LOGOS = [
        { name: "SMA", type: "Wechselrichter & Sunny" },
        { name: "Fronius", type: "Symo / Gen24 / Speicher" },
        { name: "Sungrow", type: "Hybrid-Inverter & Battery" },
        { name: "Huawei", type: "FusionSolar & LUNA" },
        { name: "BYD", type: "HVS / HVM Speicher" },
        { name: "Tesla", type: "Powerwall & Wall Connector" },
        { name: "easee", type: "Home / Charge (OCPP)" },
        { name: "go-e", type: "Charger Gemini / Home" },
        { name: "openWB", type: "Wallbox & Steuerung" },
        { name: "Daikin", type: "Altherma (SG-Ready)" },
        { name: "Viessmann & Vaillant", type: "Wärmepumpen (SG-Ready)" },
        { name: "Shelly", type: "Pro / Plus Smart Relais" },
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
            q: "Sind alle genannten Herstellernamen und Marken geschützt?",
            a: "Ja. Alle auf dieser Website genannten Marken, Markenzeichen und Produktnamen sind Eigentum der jeweiligen Rechteinhaber. Ihre Nennung dient ausschließlich der sachlichen und informativen Beschreibung der technischen Kompatibilität und Schnittstellen gem. § 23 MarkenG."
        },
        {
            q: "Wie kann ich die Live-Demo testen?",
            a: "Klicke einfach oben auf 'Live-Demo ansehen' oder nutze den interaktiven Simulator direkt auf dieser Seite. Du kannst sofort alle Steuerungsmodi und Szenarien interaktiv ausprobieren – ganz ohne Registrierung."
        }
    ];

    return (
        <div className="min-h-screen bg-slate-50 text-slate-900 selection:bg-emerald-500 selection:text-white font-sans">
            {/* 🔝 HEADER */}
            <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200/80 transition-all">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
                    {/* Brand */}
                    <Link to="/" className="flex items-center gap-2.5 group cursor-pointer">
                        <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-amber-400 via-orange-500 to-indigo-600 p-0.5 shadow-md shadow-orange-500/20 group-hover:scale-105 transition-transform">
                            <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center text-xl text-white">
                                ⚡
                            </div>
                        </div>
                        <div className="flex flex-col">
                            <span className="font-mono text-xl font-black tracking-tight text-slate-900 flex items-center gap-1">
                                sharegy
                                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
                                    OS
                                </span>
                            </span>
                            <span className="text-[10px] text-slate-500 font-medium -mt-0.5">Energy Operating System</span>
                        </div>
                    </Link>

                    {/* Navigation Links */}
                    <nav className="hidden md:flex items-center gap-7 text-xs font-bold text-slate-600">
                        <button onClick={() => scrollToSection("pillars")} className="hover:text-indigo-600 transition cursor-pointer">
                            Die 2 Säulen
                        </button>
                        <button onClick={() => scrollToSection("simulator")} className="hover:text-indigo-600 transition cursor-pointer flex items-center gap-1.5">
                            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            Live-Simulator
                        </button>
                        <button onClick={() => scrollToSection("calculator")} className="hover:text-indigo-600 transition cursor-pointer">
                            Ersparnis-Rechner
                        </button>
                        <button onClick={() => scrollToSection("hardware")} className="hover:text-indigo-600 transition cursor-pointer">
                            Kompatibilität
                        </button>
                        <button onClick={() => scrollToSection("faq")} className="hover:text-indigo-600 transition cursor-pointer">
                            FAQ
                        </button>
                    </nav>

                    {/* Action CTAs */}
                    <div className="flex items-center gap-3">
                        <a
                            href="/api/demo/"
                            className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-900 border border-indigo-200 text-xs font-bold transition cursor-pointer shadow-2xs"
                        >
                            <Eye className="w-3.5 h-3.5 text-indigo-600" />
                            <span>Echte Live-Demo</span>
                        </a>

                        {user ? (
                            <Link
                                to="/app/dashboard"
                                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition flex items-center gap-1.5 shadow-md shadow-indigo-600/20"
                            >
                                <span>Zum Dashboard</span>
                                <ArrowRight className="w-3.5 h-3.5" />
                            </Link>
                        ) : (
                            <Link
                                to="/login"
                                className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white text-xs font-black uppercase tracking-wider transition flex items-center gap-1.5 shadow-md shadow-emerald-500/20"
                            >
                                <span>Login / Starten</span>
                                <ArrowRight className="w-3.5 h-3.5" />
                            </Link>
                        )}
                    </div>
                </div>
            </header>

            {/* 🔥 HERO SECTION (BRIGHT & CRISP) */}
            <section className="relative pt-16 pb-24 px-4 sm:px-6 lg:px-8 overflow-hidden bg-gradient-to-b from-indigo-50/60 via-white to-slate-50">
                {/* Background Ambient Glows */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[350px] bg-gradient-to-tr from-amber-200/30 via-emerald-200/25 to-indigo-200/30 rounded-full blur-3xl pointer-events-none" />

                <div className="max-w-5xl mx-auto text-center relative z-10 space-y-6">
                    {/* Top Pill */}
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-indigo-200/80 text-xs font-bold text-indigo-900 shadow-sm">
                        <Sparkles className="w-4 h-4 text-amber-500" />
                        <span>Säule 1 (Smart EMS & § 14a) & Säule 2 (P2P Energy Sharing)</span>
                        <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] uppercase font-mono font-bold">100% Cloud</span>
                    </div>

                    {/* Main Headline */}
                    <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-slate-900 leading-[1.1]">
                        Das <span className="bg-gradient-to-r from-amber-500 via-emerald-600 to-teal-600 bg-clip-text text-transparent">Energy OS</span> für dein Zuhause & dein Quartier.
                    </h1>

                    {/* Subtitle */}
                    <p className="max-w-3xl mx-auto text-base sm:text-lg text-slate-600 leading-relaxed font-normal">
                        Keine teure 1.500 € Zusatzbox. Sharegy steuert deine <strong>PV-Anlage, Heimspeicher, Wallbox & Wärmepumpe</strong> vollautomatisch nach dynamischen Strompreisen & § 14a EnWG – und ermöglicht <strong>echtes P2P Energy Sharing</strong> mit deinen Nachbarn.
                    </p>

                    {/* Hero Buttons */}
                    <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
                        <a
                            href="/api/demo/"
                            className="w-full sm:w-auto px-7 py-4 rounded-2xl bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 hover:from-emerald-600 hover:to-teal-600 text-white font-black text-sm uppercase tracking-wider flex items-center justify-center gap-2.5 shadow-xl shadow-emerald-500/25 hover:scale-[1.02] transition-all cursor-pointer"
                        >
                            <span>🚀 Echte Live-Demo starten (1-Klick)</span>
                            <ArrowRight className="w-4 h-4" />
                        </a>

                        <button
                            type="button"
                            onClick={() => scrollToSection("simulator")}
                            className="w-full sm:w-auto px-6 py-4 rounded-2xl bg-white hover:bg-slate-50 text-slate-700 hover:text-indigo-600 font-bold text-sm border border-slate-300 hover:border-indigo-400 flex items-center justify-center gap-2 transition-all cursor-pointer shadow-md"
                        >
                            <span>Simulator ansehen ↓</span>
                        </button>

                        <Link
                            to="/login"
                            className="w-full sm:w-auto px-6 py-4 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm border border-slate-800 flex items-center justify-center gap-2 transition-all cursor-pointer shadow-md"
                        >
                            <span>Kostenlos starten</span>
                            <ChevronRight className="w-4 h-4 text-slate-400" />
                        </Link>
                    </div>

                    {/* Feature Highlights Badges */}
                    <div className="pt-8 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-xs text-slate-600 font-medium">
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                            <span>100% Cloud-basiert (Kein Raspberry Pi / keine Box)</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                            <span>§ 14a EnWG Netzentgelt-Prämie (+160 €/a)</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                            <span>Sub-Sekunden PV-Überschussregelung</span>
                        </div>
                    </div>
                </div>
            </section>

            {/* 🛠️ HARDWARE & ECOSYSTEM TRUST BAR + LEGAL DISCLAIMER */}
            <section id="hardware" className="py-14 border-y border-slate-200/80 bg-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <p className="text-center text-xs font-bold uppercase tracking-widest text-slate-500 mb-6">
                        Nahtlos kompatibel mit führenden Herstellern & offenen Industriestandards
                    </p>

                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3.5">
                        {HARDWARE_LOGOS.map((hw, idx) => (
                            <div
                                key={idx}
                                className="bg-slate-50 border border-slate-200/80 rounded-2xl p-3.5 text-center hover:border-indigo-400 hover:bg-indigo-50/30 transition group shadow-2xs"
                            >
                                <div className="font-mono font-bold text-slate-800 group-hover:text-indigo-600 transition-colors">
                                    {hw.name}
                                </div>
                                <div className="text-[10px] text-slate-500 mt-0.5">
                                    {hw.type}
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="mt-6 flex flex-wrap items-center justify-center gap-3 text-xs font-mono text-slate-600">
                        <span className="px-3 py-1 rounded-lg bg-slate-100 border border-slate-200 font-semibold">Modbus TCP</span>
                        <span className="px-3 py-1 rounded-lg bg-slate-100 border border-slate-200 font-semibold">OCPP 1.6-J</span>
                        <span className="px-3 py-1 rounded-lg bg-slate-100 border border-slate-200 font-semibold">SunSpec</span>
                        <span className="px-3 py-1 rounded-lg bg-slate-100 border border-slate-200 font-semibold">SG-Ready</span>
                        <span className="px-3 py-1 rounded-lg bg-slate-100 border border-slate-200 font-semibold">REST API & MQTT</span>
                        <span className="px-3 py-1 rounded-lg bg-slate-100 border border-slate-200 font-semibold">Home Assistant Bridge</span>
                        <span className="px-3 py-1 rounded-lg bg-slate-100 border border-slate-200 font-semibold">ioBroker Adapter</span>
                    </div>

                    {/* ⚖️ RECHTLICHER MARKENHINWEIS GEM. § 23 MARKENG */}
                    <div className="mt-8 text-center max-w-4xl mx-auto flex items-center justify-center gap-2 text-[11px] text-slate-400 leading-relaxed border-t border-slate-100 pt-4">
                        <Info className="w-3.5 h-3.5 flex-shrink-0 text-slate-400" />
                        <span>
                            <strong>Rechtlicher Hinweis:</strong> Alle genannten Marken-, Firmen- und Produktnamen sind eingetragene Warenzeichen ihrer jeweiligen Rechteinhaber. Ihre Nennung erfolgt ausschließlich zur sachlichen Information über die Schnittstellen- und Protokollkompatibilität gem. § 23 MarkenG.
                        </span>
                    </div>
                </div>
            </section>

            {/* 🏛️ THE 2 PILLARS OF SHAREGY (EQUITABLE DUAL-PILLAR SHOWCASE) */}
            <section id="pillars" className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
                <div className="text-center max-w-3xl mx-auto mb-14">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 text-indigo-800 border border-indigo-200 text-xs font-black uppercase tracking-wider mb-3">
                        Das Fundament
                    </div>
                    <h2 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight">
                        Zwei gleichberechtigte Säulen für deine Energiezukunft
                    </h2>
                    <p className="text-slate-600 text-sm sm:text-base mt-4">
                        Sharegy vereint dezentrales High-Tech Smart-Home Energiemanagement mit dezentralem P2P Energy Sharing im Quartier.
                    </p>
                </div>

                {/* Pillar Selector Tabs */}
                <div className="flex justify-center mb-10">
                    <div className="bg-white p-1.5 rounded-2xl border border-slate-200 shadow-sm flex gap-2">
                        <button
                            type="button"
                            onClick={() => setActivePillarTab("pillar1")}
                            className={`px-5 py-3 rounded-xl text-xs sm:text-sm font-black transition-all cursor-pointer flex items-center gap-2 ${
                                activePillarTab === "pillar1"
                                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                            }`}
                        >
                            <Zap className="w-4 h-4 text-amber-300" />
                            <span>Säule 1: Smart EMS & § 14a EnWG</span>
                        </button>

                        <button
                            type="button"
                            onClick={() => setActivePillarTab("pillar2")}
                            className={`px-5 py-3 rounded-xl text-xs sm:text-sm font-black transition-all cursor-pointer flex items-center gap-2 ${
                                activePillarTab === "pillar2"
                                    ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/30"
                                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                            }`}
                        >
                            <Users className="w-4 h-4 text-teal-200" />
                            <span>Säule 2: P2P Energy Sharing</span>
                        </button>
                    </div>
                </div>

                {/* Pillar 1 Content */}
                {activePillarTab === "pillar1" && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in">
                        {/* Feature 1 */}
                        <div className="bg-white border border-slate-200 rounded-3xl p-7 hover:border-indigo-400 hover:shadow-lg transition">
                            <div className="w-12 h-12 rounded-2xl bg-amber-100 border border-amber-200 flex items-center justify-center text-2xl mb-5">
                                ☀️
                            </div>
                            <h3 className="text-lg font-bold text-slate-900">Sub-Sekunden PV-Überschussregelung</h3>
                            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                                Dynamische Anpassung von Wallbox und Heizstab in Echtzeit. Dein Auto lädt genau mit der Sonnenenergie, die vom Dach kommt – ohne teuren Netzstrom.
                            </p>
                            <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-amber-700 font-bold">
                                ✓ Automatische Phasen-Umschaltung (1p/3p)
                            </div>
                        </div>

                        {/* Feature 2 */}
                        <div className="bg-white border border-slate-200 rounded-3xl p-7 hover:border-indigo-400 hover:shadow-lg transition">
                            <div className="w-12 h-12 rounded-2xl bg-indigo-100 border border-indigo-200 flex items-center justify-center text-2xl mb-5">
                                📈
                            </div>
                            <h3 className="text-lg font-bold text-slate-900">Dynamischer Strompreis-Radar</h3>
                            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                                Integration von Börsenstrompreisen (EPEX Spot / Awattar / Tibber). Der Heimspeicher lädt vollautomatisch in Niedrigpreisphasen und puffert Spitzenpreise ab.
                            </p>
                            <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-indigo-700 font-bold">
                                ✓ Bis zu 35% geringere Netzstromkosten
                            </div>
                        </div>

                        {/* Feature 3 */}
                        <div className="bg-white border border-slate-200 rounded-3xl p-7 hover:border-indigo-400 hover:shadow-lg transition">
                            <div className="w-12 h-12 rounded-2xl bg-cyan-100 border border-cyan-200 flex items-center justify-center text-2xl mb-5">
                                🛡️
                            </div>
                            <h3 className="text-lg font-bold text-slate-900">§ 14a EnWG Netzentgelt-Bonus</h3>
                            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                                Gesetzliche Steuerung für Wallboxen und Wärmepumpen (SteuVE). Sharegy garantiert netzdienliche Dimmung auf 4,2 kW und sichert dir die volle Jahrespauschale.
                            </p>
                            <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-cyan-700 font-bold">
                                ✓ Modul 1 Pauschale (+160 € / Jahr)
                            </div>
                        </div>
                    </div>
                )}

                {/* Pillar 2 Content */}
                {activePillarTab === "pillar2" && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in">
                        {/* Feature 1 */}
                        <div className="bg-white border border-slate-200 rounded-3xl p-7 hover:border-emerald-400 hover:shadow-lg transition">
                            <div className="w-12 h-12 rounded-2xl bg-emerald-100 border border-emerald-200 flex items-center justify-center text-2xl mb-5">
                                🏘️
                            </div>
                            <h3 className="text-lg font-bold text-slate-900">Quartiers-Strompool (§ 42b EnWG)</h3>
                            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                                Überschussstrom nicht für 8 Cent verschenken: Teile deinen Solarstrom direkt mit Nachbarn, Mietern oder Familienmitgliedern im selben Quartier.
                            </p>
                            <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-emerald-700 font-bold">
                                ✓ Mehr Ertrag für Erzeuger, günstiger für Nachbarn
                            </div>
                        </div>

                        {/* Feature 2 */}
                        <div className="bg-white border border-slate-200 rounded-3xl p-7 hover:border-emerald-400 hover:shadow-lg transition">
                            <div className="w-12 h-12 rounded-2xl bg-teal-100 border border-teal-200 flex items-center justify-center text-2xl mb-5">
                                📊
                            </div>
                            <h3 className="text-lg font-bold text-slate-900">100% Automatisierte Abrechnung</h3>
                            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                                Keine manuellen Excel-Tabellen oder Zählerablesungen. Sharegy saldiert alle kWh sub-sekundengenau und generiert automatische monatliche Abrechnungsbelege.
                            </p>
                            <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-teal-700 font-bold">
                                ✓ Rechtssicher & Mieterstrom-konform
                            </div>
                        </div>

                        {/* Feature 3 */}
                        <div className="bg-white border border-slate-200 rounded-3xl p-7 hover:border-emerald-400 hover:shadow-lg transition">
                            <div className="w-12 h-12 rounded-2xl bg-teal-100 border border-teal-200 flex items-center justify-center text-2xl mb-5">
                                🏆
                            </div>
                            <h3 className="text-lg font-bold text-slate-900">Community Autarkie & Social Proof</h3>
                            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                                Verfolge den gemeinsamen Autarkiegrad deines Quartiers, teile Erfolge auf LinkedIn & WhatsApp und mache dein Viertel gemeinsam CO₂-neutral.
                            </p>
                            <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-teal-700 font-bold">
                                ✓ Gamification & Quartiers-Rangliste
                            </div>
                        </div>
                    </div>
                )}
            </section>

            {/* ⚡ INTERACTIVE LIVE ENERGY FLOW SIMULATOR (HIGH-TECH CONSOLE IN CONTRAST) */}
            <section id="simulator" className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
                <div className="text-center max-w-3xl mx-auto mb-10">
                    <span className="p-1.5 rounded-lg bg-emerald-100 text-emerald-800 border border-emerald-200 text-xs font-black uppercase tracking-wider">
                        Live Simulation
                    </span>
                    <h2 className="text-3xl sm:text-4xl font-black text-slate-900 mt-2 tracking-tight">
                        So steuert Sharegy dein Energie-Ökosystem
                    </h2>
                    <p className="text-slate-600 text-xs sm:text-sm mt-2">
                        Wähle verschiedene Wetterszenarien & Strompreise und beobachte die sub-sekundengenaue Verteilung in Echtzeit.
                    </p>
                </div>

                {/* Embedded High-End Simulator Component */}
                <LiveEnergyFlowSimulator />
            </section>

            {/* 💡 HARDWARE VERGLEICH: CLOUD EMS VS. TEURE ZUSATZBOX */}
            <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto">
                <div className="bg-white border border-slate-200/90 rounded-3xl p-6 md:p-10 shadow-lg">
                    <h3 className="text-2xl sm:text-3xl font-black text-slate-900 text-center mb-8">
                        Warum Sharegy? Der direkte Vergleich
                    </h3>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs sm:text-sm">
                            <thead>
                                <tr className="border-b border-slate-200 text-slate-500">
                                    <th className="pb-4 font-bold">Merkmal</th>
                                    <th className="pb-4 font-black text-emerald-600">⚡ Sharegy Cloud Energy OS</th>
                                    <th className="pb-4 font-medium text-slate-500">Klassische Hardware-Boxen</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                <tr>
                                    <td className="py-4 font-semibold text-slate-800">Anschaffungskosten</td>
                                    <td className="py-4 font-bold text-emerald-600">0 € (100% Cloud-basiert)</td>
                                    <td className="py-4 text-slate-500">800 € – 1.500 € Hardware-Kauf</td>
                                </tr>
                                <tr>
                                    <td className="py-4 font-semibold text-slate-800">Elektriker-Installation</td>
                                    <td className="py-4 font-bold text-emerald-600">Nicht erforderlich (Plug & Connect)</td>
                                    <td className="py-4 text-slate-500">300 € – 600 € Einbau im Schaltschrank</td>
                                </tr>
                                <tr>
                                    <td className="py-4 font-semibold text-slate-800">P2P Energy Sharing</td>
                                    <td className="py-4 font-bold text-emerald-600">Nativ integriert (Quartiers-Pool)</td>
                                    <td className="py-4 text-slate-400">❌ Nicht unterstützt (Insel-System)</td>
                                </tr>
                                <tr>
                                    <td className="py-4 font-semibold text-slate-800">§ 14a EnWG Steuerung</td>
                                    <td className="py-4 font-bold text-emerald-600">Automatisiert (Modul 1 + 2)</td>
                                    <td className="py-4 text-slate-500">Oft nur mit teuren Zusatz-Relais</td>
                                </tr>
                                <tr>
                                    <td className="py-4 font-semibold text-slate-800">Hersteller-Freiheit</td>
                                    <td className="py-4 font-bold text-emerald-600">Offen (Modbus, OCPP, SunSpec)</td>
                                    <td className="py-4 text-slate-400">Oft proprietärer Vendor Lock-in</td>
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
                    <h2 className="text-2xl sm:text-4xl font-black text-slate-900">Häufig gestellte Fragen</h2>
                    <p className="text-slate-600 text-xs sm:text-sm mt-2">Alles, was du über Sharegy, die Cloud-Steuerung und Energy Sharing wissen musst.</p>
                </div>

                <div className="space-y-4">
                    {FAQS.map((faq, idx) => {
                        const isOpen = openFaq === idx;
                        return (
                            <div key={idx} className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-2xs transition">
                                <button
                                    type="button"
                                    onClick={() => setOpenFaq(isOpen ? null : idx)}
                                    className="w-full p-5 text-left flex items-center justify-between gap-4 cursor-pointer hover:bg-slate-50"
                                >
                                    <span className="font-bold text-sm text-slate-900">{faq.q}</span>
                                    <span className="text-indigo-600 text-lg font-bold">{isOpen ? "−" : "+"}</span>
                                </button>
                                {isOpen && (
                                    <div className="px-5 pb-5 text-xs sm:text-sm text-slate-600 leading-relaxed border-t border-slate-100 pt-4">
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
                <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-indigo-500/30 rounded-3xl p-8 sm:p-12 text-center text-white shadow-2xl relative overflow-hidden">
                    <div className="relative z-10 space-y-6">
                        <h2 className="text-3xl sm:text-5xl font-black tracking-tight">
                            Bereit für dein smartes Energy OS?
                        </h2>
                        <p className="text-sm sm:text-base text-indigo-200/90 max-w-2xl mx-auto">
                            Verbinde deine PV-Anlage, Wallbox & Speicher in wenigen Klicks – oder teste sofort die interaktive Live-Demo.
                        </p>
                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
                            <a
                                href="/api/demo/"
                                className="w-full sm:w-auto px-8 py-4 rounded-xl bg-slate-950 hover:bg-slate-800 text-indigo-300 border border-indigo-400/40 font-bold text-sm transition cursor-pointer flex items-center justify-center gap-2"
                            >
                                <span>🚀 Echte Live-Demo starten (1-Klick)</span>
                            </a>
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