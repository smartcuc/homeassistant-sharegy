/*
# src/components/Footer.jsx
*/

import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function Footer({ onOpenImpressum, onOpenDatenschutz, onOpenAgb, onOpenWiderruf, onOpenCookies }) {
    const { t } = useTranslation();

    const handleOpenCookies = () => {
        if (onOpenCookies) {
            onOpenCookies();
        } else {
            window.dispatchEvent(new Event("open-cookie-settings"));
        }
    };

    return (
        <footer className="bg-gray-900 text-gray-300 mt-16 px-6 py-12">

            <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-8">

                {/* BRAND */}
                <div>
                    <h3 className="text-white font-semibold mb-2 text-lg flex items-center gap-1.5">
                        <span>⚡</span>
                        <span>Sharegy</span>
                    </h3>

                    <p className="text-sm text-gray-400 leading-relaxed">
                        {t("footer.tagline", "Die Plattform für Energy Sharing Communities. Energie teilen. Verstehen. Optimieren.")}
                    </p>

                    <p className="text-xs mt-4 text-gray-500">
                        {t("footer.company_prefix", "Ein Produkt der")}{" "}
                        <a
                            href="https://www.smartevo.de"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-white hover:underline font-semibold"
                        >
                            smartEvo GmbH
                        </a>
                    </p>
                </div>

                {/* LEGAL LINKS */}
                <div>
                    <h4 className="text-white mb-3 font-medium flex items-center gap-1.5">
                        <span>⚖️</span>
                        <span>{t("footer.legal_title", "Rechtliches & Compliance")}</span>
                    </h4>

                    <ul className="space-y-2 text-sm">
                        <li>
                            {onOpenImpressum ? (
                                <button onClick={onOpenImpressum} className="hover:text-white transition cursor-pointer text-left">
                                    {t("legal.impressum_title", "Impressum")}
                                </button>
                            ) : (
                                <Link to="/impressum" className="hover:text-white transition">
                                    {t("legal.impressum_title", "Impressum")}
                                </Link>
                            )}
                        </li>
                        <li>
                            {onOpenDatenschutz ? (
                                <button onClick={onOpenDatenschutz} className="hover:text-white transition cursor-pointer text-left">
                                    {t("legal.privacy_title", "Datenschutzerklärung")}
                                </button>
                            ) : (
                                <Link to="/datenschutz" className="hover:text-white transition">
                                    {t("legal.privacy_title", "Datenschutzerklärung")}
                                </Link>
                            )}
                        </li>
                        <li>
                            {onOpenAgb ? (
                                <button onClick={onOpenAgb} className="hover:text-white transition cursor-pointer text-left">
                                    {t("legal.terms_title_short", "AGB & Nutzungsbedingungen")}
                                </button>
                            ) : (
                                <Link to="/agb" className="hover:text-white transition">
                                    {t("legal.terms_title_short", "AGB & Nutzungsbedingungen")}
                                </Link>
                            )}
                        </li>
                        <li>
                            {onOpenWiderruf ? (
                                <button onClick={onOpenWiderruf} className="hover:text-white transition cursor-pointer text-left">
                                    {t("legal.cancellation_title_short", "Widerrufsbelehrung")}
                                </button>
                            ) : (
                                <Link to="/widerruf" className="hover:text-white transition">
                                    {t("legal.cancellation_title_short", "Widerrufsbelehrung")}
                                </Link>
                            )}
                        </li>
                        <li className="pt-1">
                            <button
                                type="button"
                                onClick={handleOpenCookies}
                                className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1 transition cursor-pointer"
                            >
                                <span>🍪</span>
                                <span>{t("cookies.settings_link", "Cookie-Einstellungen")}</span>
                            </button>
                        </li>
                    </ul>
                </div>

                {/* INFO */}
                <div>
                    <h4 className="text-white mb-3 font-medium">Info</h4>

                    <p className="text-sm text-gray-400 leading-relaxed">
                        {t("footer.info_desc", "Diese Plattform wird zur Visualisierung von Energieflüssen und zur Unterstützung von Energy Sharing Communities verwendet.")}
                    </p>

                    <p className="text-xs mt-4 text-gray-500">
                        {t("footer.ai_notice", "Entwickelt nach höchsten Sicherheits- und Datenschutzstandards (DSGVO / TDDDG).")}
                    </p>
                </div>

            </div>

            {/* COPYRIGHT */}
            <div className="text-center text-xs text-gray-500 mt-10 border-t border-gray-800 pt-6">
                © {new Date().getFullYear()} smartEvo GmbH – {t("footer.all_rights_reserved", "Alle Rechte vorbehalten")}
            </div>

        </footer>
    );
}
