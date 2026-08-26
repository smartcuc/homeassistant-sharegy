/*
# src/pages/Impressum.jsx
*/

import LegalModalWrapper from "../components/legal/LegalModalWrapper";
import { useTranslation } from "react-i18next";

export default function Impressum({ onClose }) {
    const { t } = useTranslation();

    return (
        <LegalModalWrapper title={t("legal.impressum_title", "Impressum")} onClose={onClose}>
            <section className="space-y-4">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    Angaben gemäß § 5 Digitale-Dienste-Gesetz (DDG)
                </h2>

                <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 text-sm space-y-1 font-medium">
                    <p className="font-bold text-base text-gray-900">smartEvo GmbH</p>
                    <p>Zeisigweg 17</p>
                    <p>50389 Wesseling</p>
                    <p>Deutschland</p>
                </div>
            </section>

            <section className="space-y-3">
                <h3 className="text-base font-bold text-gray-900">Vertreten durch</h3>
                <p>
                    <strong>Geschäftsführer:</strong> Rüdiger Könen
                </p>
            </section>

            <section className="space-y-3">
                <h3 className="text-base font-bold text-gray-900">Kontakt</h3>
                <div className="space-y-1">
                    <p>
                        <strong>E-Mail:</strong>{" "}
                        <a href="mailto:info@smartevo.de" className="text-indigo-600 hover:underline">
                            info@smartevo.de
                        </a>
                    </p>
                    <p>
                        <strong>Support:</strong>{" "}
                        <a href="mailto:support@sharegy.de" className="text-indigo-600 hover:underline">
                            support@sharegy.de
                        </a>
                    </p>
                    <p>
                        <strong>Website:</strong>{" "}
                        <a href="https://www.smartevo.de" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">
                            www.smartevo.de
                        </a>{" "}
                        /{" "}
                        <a href="https://sharegy.de" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">
                            sharegy.de
                        </a>
                    </p>
                </div>
            </section>

            <section className="space-y-3">
                <h3 className="text-base font-bold text-gray-900">Registereintrag</h3>
                <p>
                    <strong>Registergericht:</strong> Amtsgericht Köln<br />
                    <strong>Handelsregisternummer:</strong> HRB (in Eintragung / Köln)
                </p>
            </section>

            <section className="space-y-3">
                <h3 className="text-base font-bold text-gray-900">Umsatzsteuer-Identifikationsnummer</h3>
                <p>
                    Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz (UStG):<br />
                    <span className="font-mono bg-slate-100 px-2 py-0.5 rounded text-xs">DE (Beantragt / in Zuteilung)</span>
                </p>
            </section>

            <section className="space-y-3">
                <h3 className="text-base font-bold text-gray-900">Verantwortlich für journalistisch-redaktionelle Inhalte</h3>
                <p>
                    Gemäß § 18 Abs. 2 Medienstaatsvertrag (MStV):<br />
                    Rüdiger Könen<br />
                    Zeisigweg 17<br />
                    50389 Wesseling
                </p>
            </section>

            <section className="space-y-3 border-t pt-4">
                <h3 className="text-base font-bold text-gray-900">EU-Streitschlichtung & Verbraucherstreitbeilegung</h3>
                <p className="text-xs text-gray-600 leading-relaxed">
                    Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:{" "}
                    <a
                        href="https://ec.europa.eu/consumers/odr"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-indigo-600 hover:underline"
                    >
                        https://ec.europa.eu/consumers/odr
                    </a>
                    .<br />
                    Unsere E-Mail-Adresse findest du oben im Impressum.
                </p>
                <p className="text-xs text-gray-600 leading-relaxed">
                    Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen (§ 36 VSBG).
                </p>
            </section>

            <section className="space-y-3 border-t pt-4">
                <h3 className="text-base font-bold text-gray-900">Haftung für Inhalte und Links</h3>
                <p className="text-xs text-gray-600 leading-relaxed">
                    Als Diensteanbieter sind wir gemäß § 7 Abs. 1 DDG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 DDG sind wir als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen.
                </p>
                <p className="text-xs text-gray-600 leading-relaxed">
                    Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich.
                </p>
            </section>
        </LegalModalWrapper>
    );
}
