/*
# src/pages/Agb.jsx
*/

import LegalModalWrapper from "../components/legal/LegalModalWrapper";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function Agb({ onClose }) {
    const { t } = useTranslation();

    return (
        <LegalModalWrapper title={t("legal.terms_title", "Allgemeine Geschäfts- & Nutzungsbedingungen (AGB)")} onClose={onClose}>
            {/* 1. Geltungsbereich */}
            <section className="space-y-3">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    § 1 Geltungsbereich & Vertragspartner
                </h2>
                <p>
                    (1) Diese Allgemeinen Geschäfts- und Nutzungsbedingungen (nachfolgend „AGB“) gelten für alle Verträge über die Nutzung der webbasierten Plattform <strong>Sharegy</strong> zwischen der <strong>smartEvo GmbH</strong>, Zeisigweg 17, 50389 Wesseling (nachfolgend „Anbieter“) und dem Kunden (nachfolgend „Nutzer“), gleich ob Verbraucher (§ 13 BGB) oder Unternehmer (§ 14 BGB).
                </p>
                <p>
                    (2) Abweichende oder ergänzende Bedingungen des Nutzers werden nicht Vertragsbestandteil, es sei denn, der Anbieter stimmt ihrer Geltung ausdrücklich schriftlich zu.
                </p>
            </section>

            {/* 2. Vertragsgegenstand */}
            <section className="space-y-3">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    § 2 Vertragsgegenstand & Leistungsumfang
                </h2>
                <p>
                    (1) Der Anbieter stellt dem Nutzer eine SaaS-Plattform (Software-as-a-Service) zur Verfügung, die Werkzeuge zur Erfassung, Visualisierung, Steuerung und Optimierung von Energieflüssen (Erzeugung, Speicher, Verbrauch, Netzeinspeisung) sowie zur Analyse von Strommarkttarifen bereitstellt.
                </p>
                <p>
                    (2) Der genaue Funktionsumfang richtet sich nach dem jeweils gebuchten Tarif:
                </p>
                <ul className="list-disc pl-5 space-y-1 text-xs sm:text-sm text-gray-600">
                    <li><strong>Sharegy Free:</strong> Grundlegende Energie-Dashboards, Erfassungs- und Echtzeitvisualisierungen.</li>
                    <li><strong>Sharegy Pro:</strong> Erweiterte Analytics, Multi-Tarif-Arbitrage, historische Zeitreihenanalysen, erweiterte Exporte und priorisierter Support.</li>
                </ul>
                <p>
                    (3) Der Anbieter schuldet keine elektrotechnische Beratung, Energieeffizienzberatung oder Garantie für bestimmte finanzielle Einsparungen.
                </p>
            </section>

            {/* 3. Registrierung & Account */}
            <section className="space-y-3">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    § 3 Registrierung, Vertragsschluss & Pflichten des Nutzers
                </h2>
                <p>
                    (1) Die Nutzung der Plattform setzt die Registrierung mit einer gültigen E-Mail-Adresse voraus. Der Vertrag kommt mit der erfolgreichen Bestätigung des Magic-Login-Links zustande.
                </p>
                <p>
                    (2) Der Nutzer verpflichtet sich, wahrheitsgemäße Angaben zu machen und die ihm übermittelten Zugangslinks geheim zu halten. Bei Verdacht auf Missbrauch ist der Anbieter unverzüglich zu informieren.
                </p>
                <p>
                    (3) Der Nutzer ist für die ordnungsgemäße und sichere Anbindung seiner IoT- und Messgeräte (z. B. Smart Meter Gateways, MQTT-Broker, OCPP-Wallboxen) selbst verantwortlich.
                </p>
            </section>

            {/* 4. Preise & Zahlungsbedingungen */}
            <section className="space-y-3">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    § 4 Preise, Zahlungsbedingungen & Aufrechnung
                </h2>
                <p>
                    (1) Für kostenpflichtige Abonnements (Sharegy Pro) gelten die zum Zeitpunkt des Vertragsschlusses auf der Plattform ausgewiesenen Preise inklusive der gesetzlichen Mehrwertsteuer.
                </p>
                <p>
                    (2) Entgelte sind jeweils im Voraus für den vereinbarten Abrechnungszeitraum (monatlich oder jährlich) fällig.
                </p>
                <p>
                    (3) Das Recht zur Aufrechnung steht dem Nutzer nur zu, wenn seine Gegenansprüche rechtskräftig festgestellt oder unbestritten sind.
                </p>
            </section>

            {/* 5. Widerrufsrecht */}
            <section className="space-y-3 bg-indigo-50/60 p-4 rounded-2xl border border-indigo-100">
                <h2 className="text-base font-bold text-indigo-900">
                    § 5 Widerrufsrecht für Verbraucher
                </h2>
                <p className="text-xs sm:text-sm text-indigo-950">
                    Verbrauchern steht beim Abschluss kostenpflichtiger Verträge im Fernabsatz ein gesetzliches 14-tägiges Widerrufsrecht zu. Einzelheiten findest du in unserer gesonderten{" "}
                    <Link to="/widerruf" className="font-bold underline text-indigo-700 hover:text-indigo-900">
                        Widerrufsbelehrung & Muster-Widerrufsformular
                    </Link>.
                </p>
            </section>

            {/* 6. Verfügbarkeit & Wartung */}
            <section className="space-y-3">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    § 6 Verfügbarkeit, Wartung & Leistungsänderungen
                </h2>
                <p>
                    (1) Der Anbieter bemüht sich um eine durchgehende Verfügbarkeit der Plattform von 99 % im Jahresmittel. Hiervon ausgenommen sind planmäßige Wartungszeiten sowie Ausfälle, die nicht im Einflussbereich des Anbieters liegen (z. B. Störungen von Telekommunikationsnetzen oder API-Ausfälle Dritter).
                </p>
                <p>
                    (2) Der Anbieter behält sich vor, Funktionen zur Verbesserung der Plattform, zur Schließung von Sicherheitslücken oder zur Anpassung an technische Standards weiterzuentwickeln.
                </p>
            </section>

            {/* 7. Haftungsbeschränkung */}
            <section className="space-y-3">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    § 7 Haftung & Gewährleistung
                </h2>
                <p>
                    (1) Für unentgeltlich bereitgestellte Dienste (Sharegy Free) haftet der Anbieter nur für Vorsatz und grobe Fahrlässigkeit (§ 521 BGB).
                </p>
                <p>
                    (2) Bei entgeltlichen Verträgen haftet der Anbieter unbeschränkt bei Vorsatz, grober Fahrlässigkeit, Verletzung von Leben, Körper oder Gesundheit sowie nach dem Produkthaftungsgesetz.
                </p>
                <p>
                    (3) Bei leicht fahrlässiger Verletzung wesentlicher Vertragspflichten (Kardinalpflichten) ist die Haftung der Höhe nach auf den vertragstypisch vorhersehbaren Schaden begrenzt.
                </p>
            </section>

            {/* 8. Laufzeit & Kündigung */}
            <section className="space-y-3">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    § 8 Vertragslaufzeit & Kündigung
                </h2>
                <p>
                    (1) Kostenlose Nutzerkonten können jederzeit ohne Einhaltung einer Frist gelöscht oder gekündigt werden.
                </p>
                <p>
                    (2) Kostenpflichtige Abonnements haben die gewählte Mindestlaufzeit (z. B. 1 Monat oder 1 Jahr) und können jederzeit zum Ende des jeweiligen Abrechnungszeitraums gekündigt werden.
                </p>
                <p>
                    (3) Das Recht zur außerordentlichen Kündigung aus wichtigem Grund bleibt unberührt.
                </p>
            </section>

            {/* 9. Schlussbestimmungen */}
            <section className="space-y-3 border-t pt-4">
                <h2 className="text-base font-bold text-gray-900">
                    § 9 Schlussbestimmungen, Gerichtsstand & anwendbares Recht
                </h2>
                <p className="text-xs text-gray-600">
                    (1) Es gilt das Recht der Bundesrepublik Deutschland unter Ausschluss des UN-Kaufrechts (CISG). Bei Verbrauchern gilt diese Rechtswahl nur insoweit, als nicht zwingende Verbraucherschutzvorschriften des Staates des gewöhnlichen Aufenthalts entzogen werden.
                </p>
                <p className="text-xs text-gray-600">
                    (2) Ist der Nutzer Kaufmann, juristische Person des öffentlichen Rechts oder öffentlich-rechtliches Sondervermögen, ist ausschließlicher Gerichtsstand Köln.
                </p>
            </section>
        </LegalModalWrapper>
    );
}

