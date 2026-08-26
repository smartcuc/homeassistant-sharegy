/*
# src/pages/Datenschutz.jsx
*/

import LegalModalWrapper from "../components/legal/LegalModalWrapper";
import { useTranslation } from "react-i18next";

export default function Datenschutz({ onClose }) {
    const { t } = useTranslation();

    return (
        <LegalModalWrapper title={t("legal.privacy_title", "Datenschutzerklärung")} onClose={onClose}>
            {/* 1. Einleitung & Verantwortlicher */}
            <section className="space-y-3">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    1. Information über die Erhebung personenbezogener Daten & Verantwortlicher
                </h2>
                <p>
                    Der Schutz deiner persönlichen Daten ist uns ein wichtiges Anliegen. Im Folgenden informieren wir dich über die Erhebung personenbezogener Daten bei Nutzung unserer Plattform <strong>Sharegy</strong> (Web-App, API, Dashboard & Telemetrie-Dienste).
                </p>
                <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 text-sm space-y-1">
                    <p className="font-bold text-gray-900">Verantwortlicher gemäß Art. 4 Abs. 7 EU-Datenschutz-Grundverordnung (DSGVO):</p>
                    <p>smartEvo GmbH</p>
                    <p>Zeisigweg 17, 50389 Wesseling, Deutschland</p>
                    <p>Geschäftsführer: Rüdiger Könen</p>
                    <p>E-Mail: <a href="mailto:info@smartevo.de" className="text-indigo-600 hover:underline">info@smartevo.de</a></p>
                </div>
            </section>

            {/* 2. Rechtsgrundlagen */}
            <section className="space-y-3">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    2. Rechtsgrundlagen der Verarbeitung
                </h2>
                <p>Wir verarbeiten personenbezogene Daten auf folgenden Rechtsgrundlagen:</p>
                <ul className="list-disc pl-5 space-y-1 text-xs sm:text-sm">
                    <li><strong>Einwilligung (Art. 6 Abs. 1 lit. a DSGVO, § 25 Abs. 1 TDDDG):</strong> Für optionale Analyse- und Personalisierungsfunktionen oder externe API-Verknüpfungen (z. B. Tibber API-Token).</li>
                    <li><strong>Vertragserfüllung & vorvertragliche Maßnahmen (Art. 6 Abs. 1 lit. b DSGVO):</strong> Zur Bereitstellung des Energiemanagement-Systems (HEMS/EMS), Verarbeitung von Zähler- und Erzeugungsdaten, Tarifeinstellungen, Rechnungsstellung und Nutzerverwaltung.</li>
                    <li><strong>Rechtliche Verpflichtung (Art. 6 Abs. 1 lit. c DSGVO):</strong> Zur Erfüllung handels- und steuerrechtlicher Aufbewahrungsfristen (z. B. Belegaufbewahrung gem. § 147 AO, § 257 HGB).</li>
                    <li><strong>Berechtigtes Interesse (Art. 6 Abs. 1 lit. f DSGVO):</strong> Zur Gewährleistung der IT-Sicherheit, Betrugsprävention, Lastverteilung und Stabilität der Serverinfrastruktur.</li>
                </ul>
            </section>

            {/* 3. Kategorien verarbeiteter Daten */}
            <section className="space-y-3">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    3. Erhobene Datenarten & Verarbeitungszwecke
                </h2>

                <div className="space-y-4">
                    <div>
                        <h3 className="text-base font-bold text-gray-800">a) Registrierung & Magic-Link Login</h3>
                        <p className="text-xs sm:text-sm text-gray-600">
                            Bei der Anmeldung verarbeiten wir deine E-Mail-Adresse. Zur passwortlosen Authentifizierung generieren wir ein zeitlich limitiertes Einmal-Token (Magic Link), das dir per E-Mail gesendet wird. Nach erfolgreicher Bestätigung wird eine verschlüsselte Session aufgebaut.
                        </p>
                    </div>

                    <div>
                        <h3 className="text-base font-bold text-gray-800">b) Energie-, Mess- & Telemetriedaten (HEMS / EMS)</h3>
                        <p className="text-xs sm:text-sm text-gray-600">
                            Kernfunktion von Sharegy ist das Erfassen und Visualisieren von Energieflüssen. Hierbei verarbeiten wir Messdaten von angeschlossenen Geräten (Smart Meter, Wechselrichter, Batteriespeicher, Wärmepumpen, schaltbare Steckdosen, Matter- und MQTT-Sensoren). Zu den verarbeiteten Werten gehören Wirkleistung (W), Zählerstände (kWh, OBIS 1.8.0 / 2.8.0), Batterieladezustand (SoC %), Netzspannung und Timestamp. Diese Daten werden zur Aggregation, Berechnung von Autarkiegraden, Erzeugungs- und Lastprognosen sowie zur Eigenverbrauchsoptimierung verwendet.
                        </p>
                    </div>

                    <div>
                        <h3 className="text-base font-bold text-gray-800">c) Strommarkt- & Tarifdaten</h3>
                        <p className="text-xs sm:text-sm text-gray-600">
                            Zur Berechnung von Stromkosten, Einspeisevergütungen und Batteriespeicher-Arbitrage verarbeiten wir deine Tarifangaben (z. B. EEG-Vergütungssätze, statische Arbeitspreise oder dynamische Börsenstrompreise). Hierbei nutzen wir öffentlich zugängliche Marktdaten (z. B. EPEX Spot DE-LU über Energy Charts / Fraunhofer ISE).
                        </p>
                    </div>

                    <div>
                        <h3 className="text-base font-bold text-gray-800">d) Abrechnungsdaten & Abonnements (Sharegy Pro)</h3>
                        <p className="text-xs sm:text-sm text-gray-600">
                            Beim Abschluss kostenpflichtiger Tarife verarbeiten wir deine Rechnungsadresse (Name, Anschrift, USt-ID bei Geschäftskunden) und Rechnungsbelege. Die Zahlungsabwicklung erfolgt über zertifizierte Zahlungsdienstleister unter Einhaltung der PCI-DSS-Standards.
                        </p>
                    </div>

                    <div>
                        <h3 className="text-base font-bold text-gray-800">e) Server-Logdateien & Protokollierung</h3>
                        <p className="text-xs sm:text-sm text-gray-600">
                            Beim Aufruf unserer Seiten werden automatisch technische Zugriffsdaten erhoben: IP-Adresse, Datum und Uhrzeit des Abrufs, Browsertyp/-version, Betriebssystem und Referrer-URL. Diese Daten dienen ausschließlich der Systemsicherheit und Fehleranalyse und werden rollierend gelöscht.
                        </p>
                    </div>
                </div>
            </section>

            {/* 4. Cookies & Lokaler Speicher (TDDDG) */}
            <section className="space-y-3">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    4. Cookies & LocalStorage (§ 25 TDDDG)
                </h2>
                <p className="text-xs sm:text-sm text-gray-600">
                    Unsere Anwendung nutzt Session-Cookies (<code className="bg-slate-100 px-1 py-0.5 rounded text-xs">sessionid</code>, <code className="bg-slate-100 px-1 py-0.5 rounded text-xs">csrftoken</code>) und LocalStorage-Schlüssel (<code className="bg-slate-100 px-1 py-0.5 rounded text-xs">i18nextLng</code>, Consent-Status), die für die technische Bereitstellung des Dienstes zwingend erforderlich sind (§ 25 Abs. 2 Nr. 2 TDDDG). Zusätzliche Tracking-Cookies oder Werbe-Tracker Dritter werden nicht ohne deine ausdrückliche Einwilligung geladen.
                </p>
            </section>

            {/* 5. Externe Dienste & Auftragsverarbeiter */}
            <section className="space-y-3">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    5. Weitergabe von Daten & Auftragsverarbeitung
                </h2>
                <p className="text-xs sm:text-sm text-gray-600">
                    Wir setzen vertrauenswürdige Dienstleister im Rahmen von Auftragsverarbeitungsverträgen (AVV gem. Art. 28 DSGVO) ein:
                </p>
                <ul className="list-disc pl-5 space-y-1 text-xs sm:text-sm text-gray-600">
                    <li><strong>Hosting & Serverinfrastruktur:</strong> Serverstandort innerhalb der Europäischen Union / Deutschland.</li>
                    <li><strong>E-Mail-Versand (Transaktionsmails):</strong> Serverbetriebene SMTP-Zustellung über zertifizierte Mailserver für Magic Links und Systembenachrichtigungen.</li>
                    <li><strong>Tibber API (optional):</strong> Nur bei vom Nutzer aktiv hinterlegtem API-Token zur Abfrage individueller Verbrauchs- und Preisdaten.</li>
                </ul>
            </section>

            {/* 6. Speicherdauer */}
            <section className="space-y-3">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    6. Dauer der Speicherung & Löschfristen
                </h2>
                <p className="text-xs sm:text-sm text-gray-600">
                    Personenbezogene Daten werden gelöscht, sobald der Zweck der Speicherung entfällt. Magic-Link-Tokens verfallen automatisch nach 15 Minuten. Rechnungsbelege werden gem. § 147 Abs. 3 AO für 10 Jahre archiviert. Bei Löschung des Benutzerkontos werden alle zugeordneten persönlichen Daten und Token unwiderruflich aus den Produktivdatenbanken entfernt.
                </p>
            </section>

            {/* 7. Rechte der Betroffenen */}
            <section className="space-y-3">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    7. Deine Rechte als betroffene Person
                </h2>
                <p className="text-xs sm:text-sm text-gray-600">
                    Du hast nach der DSGVO folgende Rechte gegenüber dem Verantwortlichen:
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                        <strong>Art. 15 DSGVO:</strong> Recht auf Auskunft über deine verarbeiteten Daten.
                    </div>
                    <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                        <strong>Art. 16 DSGVO:</strong> Recht auf unverzügliche Berichtigung unrichtiger Daten.
                    </div>
                    <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                        <strong>Art. 17 DSGVO:</strong> Recht auf Löschung („Recht auf Vergessenwerden“).
                    </div>
                    <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                        <strong>Art. 18 DSGVO:</strong> Recht auf Einschränkung der Verarbeitung.
                    </div>
                    <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                        <strong>Art. 20 DSGVO:</strong> Recht auf Datenübertragbarkeit in einem maschinenlesbaren Format.
                    </div>
                    <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                        <strong>Art. 21 DSGVO:</strong> Recht auf Widerspruch gegen Verarbeitungen auf Basis berechtigter Interessen.
                    </div>
                </div>
                <p className="text-xs sm:text-sm text-gray-600 pt-2">
                    Zur Ausübung deiner Rechte genügt eine formlose E-Mail an <a href="mailto:info@smartevo.de" className="text-indigo-600 font-semibold hover:underline">info@smartevo.de</a>.
                </p>
            </section>

            {/* 8. Beschwerderecht */}
            <section className="space-y-3 border-t pt-4">
                <h2 className="text-base font-bold text-gray-900">
                    8. Beschwerderecht bei der zuständigen Aufsichtsbehörde
                </h2>
                <p className="text-xs text-gray-600">
                    Unbeschadet eines anderweitigen Rechtsbehelfs steht dir das Recht auf Beschwerde bei einer Datenschutz-Aufsichtsbehörde zu (z. B. Landesbeauftragte für Datenschutz und Informationsfreiheit Nordrhein-Westfalen, LDI NRW, Kavalleriestr. 2-4, 40213 Düsseldorf, <a href="https://www.ldi.nrw.de" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">www.ldi.nrw.de</a>).
                </p>
            </section>
        </LegalModalWrapper>
    );
}