/*
# src/pages/Widerruf.jsx
*/

import LegalModalWrapper from "../components/legal/LegalModalWrapper";
import { useState } from "react";
import { useTranslation } from "react-i18next";

export default function Widerruf({ onClose }) {
    const { t } = useTranslation();
    const [copied, setCopied] = useState(false);

    const musterText = `An:
smartEvo GmbH
Zeisigweg 17, 50389 Wesseling
E-Mail: info@smartevo.de

Hiermit widerrufe(n) ich/wir (*) den von mir/uns (*) abgeschlossenen Vertrag über die Nutzung des Dienstes Sharegy Pro:

- Bestellt am (*): ____________ / erhalten am (*): ____________
- Name des/der Verbraucher(s): ____________________________
- Anschrift des/der Verbraucher(s): ________________________
- E-Mail-Adresse des Kundenkontos: ________________________

Datum: ____________

Unterschrift des/der Verbraucher(s) (nur bei Mitteilung auf Papier): ____________________

(*) Unzutreffendes streichen.`;

    const handleCopy = () => {
        navigator.clipboard.writeText(musterText);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <LegalModalWrapper title={t("legal.cancellation_title", "Widerrufsbelehrung & Musterformular")} onClose={onClose}>
            {/* Widerrufsbelehrung */}
            <section className="space-y-4">
                <h2 className="text-lg font-bold text-gray-900 border-b pb-2">
                    Widerrufsbelehrung für Verbraucher
                </h2>
                <p>
                    Verbraucher ist jede natürliche Person, die ein Rechtsgeschäft zu Zwecken abschließt, die überwiegend weder ihrer gewerblichen noch ihrer selbständigen beruflichen Tätigkeit zugerechnet werden können (§ 13 BGB).
                </p>

                <div className="space-y-3">
                    <h3 className="text-base font-bold text-gray-900">Widerrufsrecht</h3>
                    <p>
                        Du hast das Recht, binnen vierzehn Tagen ohne Angabe von Gründen diesen Vertrag zu widerrufen.
                    </p>
                    <p>
                        Die Widerrufsfrist beträgt <strong>vierzehn Tage</strong> ab dem Tag des Vertragsschlusses.
                    </p>
                    <p>
                        Um dein Widerrufsrecht auszuüben, musst du uns:
                    </p>
                    <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 text-xs sm:text-sm font-medium space-y-0.5">
                        <p className="font-bold text-gray-900">smartEvo GmbH</p>
                        <p>Zeisigweg 17, 50389 Wesseling, Deutschland</p>
                        <p>E-Mail: <a href="mailto:info@smartevo.de" className="text-indigo-600 hover:underline">info@smartevo.de</a></p>
                    </div>
                    <p>
                        mittels einer eindeutigen Erklärung (z. B. ein mit der Post versandter Brief oder eine E-Mail) über deinen Entschluss, diesen Vertrag zu widerrufen, informieren. Du kannst dafür das beigefügte Muster-Widerrufsformular verwenden, das jedoch nicht vorgeschrieben ist.
                    </p>
                    <p>
                        Zur Wahrung der Widerrufsfrist reicht es aus, dass du die Mitteilung über die Ausübung des Widerrufsrechts vor Ablauf der Widerrufsfrist absendest.
                    </p>
                </div>

                <div className="space-y-3 pt-2">
                    <h3 className="text-base font-bold text-gray-900">Folgen des Widerrufs</h3>
                    <p>
                        Wenn du diesen Vertrag widerrufst, haben wir dir alle Zahlungen, die wir von dir erhalten haben, unverzüglich und spätestens binnen vierzehn Tagen ab dem Tag zurückzuzahlen, an dem die Mitteilung über deinen Widerruf dieses Vertrags bei uns eingegangen ist. Für diese Rückzahlung verwenden wir dasselbe Zahlungsmittel, das du bei der ursprünglichen Transaktion eingesetzt hast, es sei denn, mit dir wurde ausdrücklich etwas anderes vereinbart; in keinem Fall werden dir wegen dieser Rückzahlung Entgelte berechnet.
                    </p>
                    <p>
                        Hast du verlangt, dass die Dienstleistungen während der Widerrufsfrist beginnen sollen, so hast du uns einen angemessenen Betrag zu zahlen, der dem Anteil der bis zu dem Zeitpunkt, zu dem du uns von der Ausübung des Widerrufsrechts hinsichtlich dieses Vertrags unterrichtest, bereits erbrachten Dienstleistungen im Vergleich zum Gesamtumfang der im Vertrag vorgesehenen Dienstleistungen entspricht.
                    </p>
                </div>
            </section>

            {/* Muster-Widerrufsformular */}
            <section className="space-y-3 border-t pt-6">
                <div className="flex items-center justify-between">
                    <h2 className="text-lg font-bold text-gray-900">
                        Muster-Widerrufsformular
                    </h2>
                    <button
                        type="button"
                        onClick={handleCopy}
                        className="text-xs px-3 py-1.5 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-700 font-bold hover:bg-indigo-100 transition cursor-pointer flex items-center gap-1.5"
                    >
                        <span>📋</span>
                        <span>{copied ? "Kopiert!" : "Muster kopieren"}</span>
                    </button>
                </div>
                <p className="text-xs text-gray-600">
                    (Wenn du den Vertrag widerrufen willst, kannst du dieses Formular ausfüllen und an uns per E-Mail oder Post senden.)
                </p>

                <pre className="p-4 bg-slate-900 text-slate-200 rounded-2xl text-xs font-mono whitespace-pre-wrap leading-relaxed overflow-x-auto border border-slate-800">
                    {musterText}
                </pre>
            </section>
        </LegalModalWrapper>
    );
}

