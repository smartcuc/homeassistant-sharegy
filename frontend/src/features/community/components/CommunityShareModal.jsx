import { useState } from "react";
import { useTranslation } from "react-i18next";

export default function CommunityShareModal({ isOpen, onClose, kpis = {}, userProfile = {} }) {
    const { t } = useTranslation();
    const [copied, setCopied] = useState(false);
    const [activeTab, setActiveTab] = useState("whatsapp");

    if (!isOpen) return null;

    // Kennzahlen extrahieren
    const autarkyPct = Math.round(Number(kpis.autarky_pct || kpis.autarky || 86));
    const selfConsumptionPct = Math.round(Number(kpis.self_consumption_pct || 92));
    const sharedKwh = Number(kpis.community_shared_kwh || kpis.shared_kwh || 148).toFixed(0);
    const co2SavedKg = Number(kpis.co2_saved_kg || (sharedKwh * 0.42)).toFixed(0);
    const treesEquivalent = Math.max(1, Math.round(co2SavedKg / 12.5));

    const inviteToken = userProfile.invite_token || "solarpower";
    const appUrl = window.location.origin || "https://sharegy.de";
    const shareUrl = `${appUrl}/join?ref=${inviteToken}`;

    // Vorbereitete Share-Texte
    const shareTexts = {
        whatsapp: `☀️⚡ Ich habe diesen Monat ${autarkyPct}% Strom-Autarkie erreicht und ${sharedKwh} kWh sauberen Sonnenstrom mit meinen Nachbarn geteilt! (${co2SavedKg} kg CO₂ gespart 🌳)\n\nMach dein Haus auch zum Kraftwerk mit Sharegy: ${shareUrl}`,
        linkedin: `🚀 Die dezentrale Energiewende in der Praxis: Mit @Sharegy habe ich diesen Monat eine Autarkiequote von ${autarkyPct}% und ${sharedKwh} kWh Energy Sharing im Quartier erzielt.\n\nKeine teuren Hardware-Boxen, sondern 100% smarte Cloud-Steuerung für PV, Speicher & Wallbox.\n\n👉 Mehr erfahren: ${shareUrl} #EnergySharing #Photovoltaik #SmartGrid #Cleantech`,
        twitter: `☀️ ${autarkyPct}% Autarkie & ${sharedKwh} kWh Solarstrom mit Nachbarn geteilt! Danke an @sharegy_de für das sub-sekunden EMS & intelligentes Wallbox-Laden 🚗⚡\n\n${shareUrl}`,
    };

    const currentText = shareTexts[activeTab] || shareTexts.whatsapp;

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(currentText);
            setCopied(true);
            setTimeout(() => setCopied(false), 3000);
        } catch (e) {
            // fallback
        }
    };

    const handleWhatsAppClick = () => {
        const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(shareTexts.whatsapp)}`;
        window.open(url, "_blank");
    };

    const handleLinkedInClick = () => {
        const url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`;
        window.open(url, "_blank");
    };

    const handleTwitterClick = () => {
        const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareTexts.twitter)}`;
        window.open(url, "_blank");
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-fade-in">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
                {/* Modal Header */}
                <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/70">
                    <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
                            <span className="text-xl">📢</span>
                        </div>
                        <div>
                            <h3 className="text-base font-bold text-white flex items-center gap-2">
                                Erfolge teilen & Nachbarn einladen
                                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                                    Community
                                </span>
                            </h3>
                            <p className="text-xs text-slate-400">
                                Zeige deine Solar-Bilanz und baue deine lokale Energiegemeinschaft auf.
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800 transition-colors"
                    >
                        ✕
                    </button>
                </div>

                {/* Modal Body */}
                <div className="p-6 overflow-y-auto space-y-6">
                    {/* Live Preview der Visual Social Card */}
                    <div className="bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950/40 border border-emerald-500/40 rounded-2xl p-5 shadow-xl relative overflow-hidden group">
                        {/* Background Glow */}
                        <div className="absolute top-0 right-0 w-48 h-48 bg-emerald-500/15 rounded-full blur-3xl pointer-events-none"></div>

                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2">
                                <span className="text-lg">⚡</span>
                                <span className="font-bold text-sm tracking-tight text-white">
                                    Sharegy <span className="text-emerald-400 font-mono text-xs">Energy Impact</span>
                                </span>
                            </div>
                            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                                🏆 Solar-Champion
                            </span>
                        </div>

                        {/* KPI Grid der Karte */}
                        <div className="grid grid-cols-3 gap-2.5 mb-4 text-center">
                            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3">
                                <div className="text-[10px] text-slate-400 uppercase font-semibold">Autarkie</div>
                                <div className="text-2xl font-black text-emerald-400 font-mono mt-0.5">
                                    {autarkyPct}%
                                </div>
                            </div>

                            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3">
                                <div className="text-[10px] text-slate-400 uppercase font-semibold">Geteilt</div>
                                <div className="text-2xl font-black text-amber-400 font-mono mt-0.5">
                                    {sharedKwh} <span className="text-xs font-normal">kWh</span>
                                </div>
                            </div>

                            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3">
                                <div className="text-[10px] text-slate-400 uppercase font-semibold">CO₂ Ersparnis</div>
                                <div className="text-2xl font-black text-cyan-400 font-mono mt-0.5">
                                    {co2SavedKg} <span className="text-xs font-normal">kg</span>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800/80 pt-2.5">
                            <span className="flex items-center gap-1">
                                <span>🌳</span>
                                <span>Entspricht <strong>{treesEquivalent} gepflanzten Bäumen</strong></span>
                            </span>
                            <span className="text-slate-400 font-mono text-[10px]">sharegy.de</span>
                        </div>
                    </div>

                    {/* Plattform Tabs */}
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <label className="text-xs font-semibold text-slate-300">
                                Wähle deine Plattform:
                            </label>
                            <span className="text-[11px] text-slate-400 font-medium">Text wird automatisch angepasst</span>
                        </div>

                        <div className="grid grid-cols-3 gap-2 mb-3">
                            <button
                                type="button"
                                onClick={() => setActiveTab("whatsapp")}
                                className={`py-2 px-3 rounded-xl border text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                                    activeTab === "whatsapp"
                                        ? "bg-emerald-600/20 border-emerald-500 text-emerald-300 ring-1 ring-emerald-500/40"
                                        : "bg-slate-950/50 border-slate-800 text-slate-400 hover:text-slate-200"
                                }`}
                            >
                                <span>💬</span>
                                <span>WhatsApp</span>
                            </button>

                            <button
                                type="button"
                                onClick={() => setActiveTab("linkedin")}
                                className={`py-2 px-3 rounded-xl border text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                                    activeTab === "linkedin"
                                        ? "bg-blue-600/20 border-blue-500 text-blue-300 ring-1 ring-blue-500/40"
                                        : "bg-slate-950/50 border-slate-800 text-slate-400 hover:text-slate-200"
                                }`}
                            >
                                <span>💼</span>
                                <span>LinkedIn</span>
                            </button>

                            <button
                                type="button"
                                onClick={() => setActiveTab("twitter")}
                                className={`py-2 px-3 rounded-xl border text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                                    activeTab === "twitter"
                                        ? "bg-cyan-600/20 border-cyan-500 text-cyan-300 ring-1 ring-cyan-500/40"
                                        : "bg-slate-950/50 border-slate-800 text-slate-400 hover:text-slate-200"
                                }`}
                            >
                                <span>🐦</span>
                                <span>X / Twitter</span>
                            </button>
                        </div>

                        {/* Vorschau des Share-Textes */}
                        <div className="relative">
                            <textarea
                                readOnly
                                rows={4}
                                value={currentText}
                                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 font-sans leading-relaxed focus:outline-none focus:border-emerald-500 select-all"
                            />
                            <button
                                type="button"
                                onClick={handleCopy}
                                className="absolute top-2.5 right-2.5 px-2.5 py-1 rounded-lg text-[11px] font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all flex items-center gap-1"
                            >
                                {copied ? "✓ Kopiert!" : "📋 Kopieren"}
                            </button>
                        </div>
                    </div>

                    {/* Quick Direct Buttons */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                        <button
                            type="button"
                            onClick={handleWhatsAppClick}
                            className="py-2.5 px-4 rounded-xl text-xs font-bold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition-all flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20"
                        >
                            <span>💬</span>
                            <span>Auf WhatsApp teilen</span>
                        </button>

                        <button
                            type="button"
                            onClick={handleLinkedInClick}
                            className="py-2.5 px-4 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-600/20"
                        >
                            <span>💼</span>
                            <span>Auf LinkedIn teilen</span>
                        </button>

                        <button
                            type="button"
                            onClick={handleTwitterClick}
                            className="py-2.5 px-4 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 transition-all flex items-center justify-center gap-2"
                        >
                            <span>🐦</span>
                            <span>Auf X teilen</span>
                        </button>
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex items-center justify-between text-xs text-slate-400">
                    <span className="truncate">Referral Link: <span className="font-mono text-emerald-400">{shareUrl}</span></span>
                    <button
                        type="button"
                        onClick={onClose}
                        className="px-4 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white transition-colors"
                    >
                        Schließen
                    </button>
                </div>
            </div>
        </div>
    );
}
