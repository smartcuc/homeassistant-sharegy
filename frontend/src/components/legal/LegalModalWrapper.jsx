/*
# src/components/legal/LegalModalWrapper.jsx
*/

import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function LegalModalWrapper({ title, children, onClose }) {
    const { t } = useTranslation();
    const navigate = useNavigate();

    // Modal Mode (opened from Footer popup)
    if (onClose) {
        return (
            <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-fade-in">
                <div className="bg-white border border-gray-200 rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
                    {/* Header */}
                    <div className="p-6 border-b border-gray-100 flex items-center justify-between bg-slate-50/80">
                        <div className="flex items-center gap-3">
                            <span className="text-2xl p-2 bg-indigo-50 text-indigo-600 rounded-xl border border-indigo-100">⚖️</span>
                            <div>
                                <h2 className="text-lg font-bold text-gray-900">
                                    {title}
                                </h2>
                                <span className="text-xs text-gray-400">Sharegy Legal & Compliance</span>
                            </div>
                        </div>

                        <button
                            onClick={onClose}
                            className="w-8 h-8 rounded-full bg-white border border-gray-200 text-gray-400 hover:text-gray-700 flex items-center justify-center text-sm font-bold transition cursor-pointer"
                        >
                            ✕
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-6 sm:p-8 overflow-y-auto text-gray-700 text-sm leading-relaxed space-y-6">
                        {children}
                    </div>

                    {/* Footer */}
                    <div className="p-4 border-t border-gray-100 bg-gray-50/50 flex justify-end">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-5 py-2 text-xs font-semibold text-gray-700 bg-white border border-gray-200 hover:bg-gray-100 rounded-xl transition cursor-pointer shadow-2xs"
                        >
                            {t("common.close", "Schließen")}
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // Standalone Page Mode (e.g. navigated to /impressum, /datenschutz, /agb, /widerruf)
    return (
        <div className="min-h-screen bg-slate-50 text-gray-800 flex flex-col">
            {/* Top Navigation Bar */}
            <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-2xs">
                <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-2 text-indigo-600 font-black text-xl hover:opacity-90 transition">
                        <span>⚡</span>
                        <span>Sharegy</span>
                    </Link>

                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => navigate(-1)}
                            className="px-3.5 py-1.5 rounded-xl border border-gray-200 text-xs font-semibold text-gray-600 hover:bg-gray-50 transition cursor-pointer flex items-center gap-1.5"
                        >
                            <span>←</span>
                            <span>{t("common.back", "Zurück")}</span>
                        </button>
                        <Link
                            to="/login"
                            className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition shadow-xs"
                        >
                            {t("auth.login", "Anmelden")}
                        </Link>
                    </div>
                </div>
            </header>

            {/* Main Content Area */}
            <main className="flex-1 max-w-4xl w-full mx-auto p-6 sm:p-10">
                <div className="bg-white rounded-3xl border border-gray-200 shadow-xs p-6 sm:p-12 space-y-6">
                    <div className="border-b border-gray-100 pb-6 mb-6">
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-lg text-xs font-bold mb-3">
                            <span>⚖️</span>
                            <span>Rechtliche Angaben & Verbraucherinformationen</span>
                        </div>
                        <h1 className="text-3xl font-black text-gray-900 tracking-tight">
                            {title}
                        </h1>
                        <p className="text-xs text-gray-400 mt-1">
                            Stand: {new Date().toLocaleDateString("de-DE", { month: "long", year: "numeric" })} · Gültig für alle Dienste der Sharegy Plattform
                        </p>
                    </div>

                    <div className="prose prose-slate max-w-none text-gray-700 text-sm leading-relaxed space-y-6">
                        {children}
                    </div>
                </div>
            </main>

            {/* Minimal Footer */}
            <footer className="bg-white border-t border-gray-200 py-6 text-center text-xs text-gray-400">
                <div className="flex justify-center flex-wrap gap-6 mb-2">
                    <Link to="/impressum" className="hover:text-indigo-600">Impressum</Link>
                    <Link to="/datenschutz" className="hover:text-indigo-600">Datenschutz</Link>
                    <Link to="/agb" className="hover:text-indigo-600">AGB</Link>
                    <Link to="/widerruf" className="hover:text-indigo-600">Widerrufsbelehrung</Link>
                </div>
                <p>© {new Date().getFullYear()} smartEvo GmbH · Alle Rechte vorbehalten.</p>
            </footer>
        </div>
    );
}

