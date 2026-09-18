import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  FileText,
  Printer,
  XCircle,
  CheckCircle2,
  ShieldCheck,
  Zap,
  Sun,
  Battery,
  Building,
  User,
  Calendar,
  Hash,
  Download,
  Check
} from "lucide-react";
import useModalDismiss from "../../../hooks/useModalDismiss";

export default function PartnerHandoverProtocolModal({
  isOpen,
  onClose,
  asset,
  partnerCompany
}) {
  const { t } = useTranslation();
  useModalDismiss(isOpen, onClose);

  const [technicianName, setTechnicianName] = useState(
    partnerCompany?.contact_person || "M. Mustermann (Elektromeister)"
  );
  const [certNumber, setCertNumber] = useState(
    partnerCompany?.trei_number || "TREI-VNB-94821-E"
  );
  const [gridOperator, setGridOperator] = useState("Bayernwerk Netz GmbH / VNB");
  const [notes, setNotes] = useState(
    "Alle Komponenten wurden gemäß VDE-AR-N 4105 und EnWG § 14a erfolgreich parametriert. Not-Abschaltung, 4,2 kW Dimmfunktion und NA-Schutz-Auslösung ordnungsgemäß geprüft."
  );

  if (!isOpen || !asset) return null;

  const protocolId = `IBN-${new Date().getFullYear()}-${String(asset.id || "101").padStart(5, "0")}`;
  const currentDate = new Date().toLocaleDateString("de-DE", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric"
  });

  const handlePrint = () => {
    window.print();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-md animate-fade-in overflow-y-auto"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-4xl w-full p-6 sm:p-8 space-y-6 shadow-2xl overflow-hidden my-auto max-h-[92vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header - Non-Print Actions */}
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4 print:hidden">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/20">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg sm:text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
                <span>{t("partner.protocol_title", "Digitales IBN- & Übergabeprotokoll")}</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300 font-bold">
                  {protocolId}
                </span>
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {t("partner.protocol_subtitle", "Offizieller VDE-AR-N 4105 & EnWG § 14a Nachweis für Endkunde & Netzbetreiber (VNB)")}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handlePrint}
              className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold flex items-center gap-2 shadow-xs transition cursor-pointer"
            >
              <Printer className="w-4 h-4" />
              <span>{t("partner.btn_print_pdf", "Drucken / PDF Export")}</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer"
            >
              <XCircle className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Printable Document Container */}
        <div className="overflow-y-auto space-y-6 pr-1 print:p-0 print:overflow-visible print:text-black">
          {/* Printable Header */}
          <div className="p-5 bg-slate-50 dark:bg-slate-950/60 rounded-2xl border border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <div className="text-xs font-bold uppercase tracking-wider text-sky-600 dark:text-sky-400 mb-0.5">
                {partnerCompany?.name || t("partner.company_default", "Elektro-Fachpartnerbetrieb")}
              </div>
              <h2 className="text-xl font-black text-slate-900 dark:text-white">
                Inbetriebsetzungs- & Übergabeprotokoll
              </h2>
              <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Gemäß Niederspannungsanschlussverordnung (NAV), VDE-AR-N 4105 & EnWG § 14a
              </div>
            </div>
            <div className="text-right text-xs font-mono space-y-1 sm:border-l sm:border-slate-200 sm:dark:border-slate-800 sm:pl-4">
              <div>Protokoll-Nr.: <strong>{protocolId}</strong></div>
              <div>Datum: <strong>{currentDate}</strong></div>
              <div>Status: <span className="text-emerald-600 font-bold">✓ Erfolgreich abgenommen</span></div>
            </div>
          </div>

          {/* Section 1: Betreiber & Liegenschaft */}
          <div className="border border-slate-200 dark:border-slate-800 rounded-2xl p-4.5 space-y-3 bg-white dark:bg-slate-900/60">
            <h4 className="text-xs font-black uppercase text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-2">
              <Building className="w-4 h-4 text-sky-500" />
              <span>1. Angaben zum Anlagenbetreiber & Netzanschlusspunkt</span>
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3.5 text-xs">
              <div>
                <span className="text-slate-400 block mb-0.5">Anlagenbetreiber / Kunde:</span>
                <strong className="text-slate-900 dark:text-slate-100 text-sm">{asset.customer_name || "Musterkunde"}</strong>
                <div className="text-slate-500">{asset.customer_email || "kunde@muster.de"}</div>
              </div>
              <div>
                <span className="text-slate-400 block mb-0.5">Standort der Erzeugungsanlage:</span>
                <strong className="text-slate-900 dark:text-slate-100">{asset.address || "Musterstraße 1, 80331 München"}</strong>
                <div className="text-slate-500">{asset.name}</div>
              </div>
              <div>
                <span className="text-slate-400 block mb-0.5">Zuständiger Verteilnetzbetreiber (VNB):</span>
                <input
                  type="text"
                  value={gridOperator}
                  onChange={(e) => setGridOperator(e.target.value)}
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 px-2 py-1 rounded-lg text-xs font-bold text-slate-900 dark:text-slate-100 print:border-none print:bg-transparent print:p-0"
                />
              </div>
            </div>
          </div>

          {/* Section 2: Erzeugungs- & Speicher-Komponenten */}
          <div className="border border-slate-200 dark:border-slate-800 rounded-2xl p-4.5 space-y-3 bg-white dark:bg-slate-900/60">
            <h4 className="text-xs font-black uppercase text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-2">
              <Sun className="w-4 h-4 text-amber-500" />
              <span>2. Installierte Anlagentechnik & Speichersysteme</span>
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 bg-amber-500/5 border border-amber-500/20 rounded-xl">
                <span className="text-[10px] text-amber-600 uppercase font-bold block">PV-Leistung (kWp)</span>
                <div className="text-base font-black text-slate-900 dark:text-white mt-0.5">
                  {((asset.pv_power_w || 8500) / 1000).toFixed(1)} kWp
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5">{asset.inverters_count || 1}x Wechselrichter</div>
              </div>
              <div className="p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-xl">
                <span className="text-[10px] text-emerald-600 uppercase font-bold block">Batteriespeicher</span>
                <div className="text-base font-black text-slate-900 dark:text-white mt-0.5">
                  {asset.battery_capacity_kwh || 10} kWh
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5">Notstrom / Schwarzstart: Ja</div>
              </div>
              <div className="p-3 bg-sky-500/5 border border-sky-500/20 rounded-xl">
                <span className="text-[10px] text-sky-600 uppercase font-bold block">Ladeinfrastruktur</span>
                <div className="text-base font-black text-slate-900 dark:text-white mt-0.5">
                  {asset.wallboxes_count || 1}x Wallbox (11 kW)
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5">OCPP 1.6J / ISO 15118</div>
              </div>
              <div className="p-3 bg-teal-500/5 border border-teal-500/20 rounded-xl">
                <span className="text-[10px] text-teal-600 uppercase font-bold block">EMS / Smart Meter</span>
                <div className="text-base font-black text-slate-900 dark:text-white mt-0.5">
                  Sharegy Core Gate
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5">Smart Meter Gateway (CLS)</div>
              </div>
            </div>
          </div>

          {/* Section 3: § 14a EnWG & Netzkonformität */}
          <div className="border border-slate-200 dark:border-slate-800 rounded-2xl p-4.5 space-y-3 bg-white dark:bg-slate-900/60">
            <h4 className="text-xs font-black uppercase text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-2">
              <ShieldCheck className="w-4 h-4 text-teal-500" />
              <span>3. Netzanschlussprüfung, NA-Schutz & § 14a EnWG Steuerbarkeit</span>
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
              <label className="flex items-start gap-2 p-2 rounded-xl bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                <span>
                  <strong>§ 14a EnWG Dimm-Funktionstest (4,2 kW):</strong> Erfolgreich per Steuerbox / CLS-Relais ausgelöst und bestätigt.
                </span>
              </label>
              <label className="flex items-start gap-2 p-2 rounded-xl bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                <span>
                  <strong>Zentraler / Integrierter NA-Schutz:</strong> Abschaltzeit & Spannungssteigerungsschutz nach VDE-AR-N 4105 geprüft.
                </span>
              </label>
              <label className="flex items-start gap-2 p-2 rounded-xl bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                <span>
                  <strong>Messkonzept & Zählererfassung:</strong> Zweirichtungszählung (1.8.0 / 2.8.0) sauber kalibriert und im EMS registriert.
                </span>
              </label>
              <label className="flex items-start gap-2 p-2 rounded-xl bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                <span>
                  <strong>Endkunden-Einweisung & App-Login:</strong> Betreiberzugang & Not-Aus-Schalter vollumfänglich übergeben.
                </span>
              </label>
            </div>
          </div>

          {/* Section 4: Techniker-Notizen & Bemerkungen */}
          <div className="border border-slate-200 dark:border-slate-800 rounded-2xl p-4.5 space-y-2 bg-white dark:bg-slate-900/60">
            <span className="text-xs font-bold text-slate-700 dark:text-slate-300 block">
              Prüfvermerk des konzessionierten Fachbetriebs:
            </span>
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 p-2.5 rounded-xl text-xs text-slate-900 dark:text-slate-100 focus:outline-hidden focus:ring-2 focus:ring-sky-500 print:border-none print:bg-transparent print:p-0"
            />
          </div>

          {/* Section 5: Rechtsverbindliche Unterschriftenfelder */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            {/* Installateur Signature */}
            <div className="p-4 border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-2xl space-y-3 bg-slate-50/50 dark:bg-slate-950/30">
              <div className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center justify-between">
                <span>Errichtender Fachbetrieb</span>
                <span className="text-[10px] text-slate-400 font-mono">TREI-Konzession</span>
              </div>
              <div className="space-y-1.5 text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-slate-400 w-24">Monteur/Meister:</span>
                  <input
                    type="text"
                    value={technicianName}
                    onChange={(e) => setTechnicianName(e.target.value)}
                    className="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-2 py-1 rounded text-xs font-bold text-slate-900 dark:text-slate-100 print:border-none print:bg-transparent print:p-0"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-400 w-24">Ausweis-Nr.:</span>
                  <input
                    type="text"
                    value={certNumber}
                    onChange={(e) => setCertNumber(e.target.value)}
                    className="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-2 py-1 rounded text-xs font-bold text-slate-900 dark:text-slate-100 print:border-none print:bg-transparent print:p-0"
                  />
                </div>
              </div>
              <div className="pt-8 border-b border-slate-400 dark:border-slate-600 flex justify-between text-[11px] text-slate-400">
                <span>Ort, Datum</span>
                <span>Unterschrift & Firmenstempel Fachbetrieb</span>
              </div>
            </div>

            {/* Betreiber Signature */}
            <div className="p-4 border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-2xl space-y-3 bg-slate-50/50 dark:bg-slate-950/30">
              <div className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center justify-between">
                <span>Anlagenbetreiber / Kunde</span>
                <span className="text-[10px] text-slate-400 font-mono">Übergabebestätigung</span>
              </div>
              <div className="space-y-1.5 text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-slate-400 w-24">Betreiber:</span>
                  <span className="font-bold text-slate-900 dark:text-slate-100">{asset.customer_name || "Musterkunde"}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-400 w-24">Übergabe:</span>
                  <span className="text-emerald-600 font-semibold">Mangelfrei übergeben</span>
                </div>
              </div>
              <div className="pt-8 border-b border-slate-400 dark:border-slate-600 flex justify-between text-[11px] text-slate-400">
                <span>Ort, Datum</span>
                <span>Unterschrift Anlagenbetreiber</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800 print:hidden">
          <span className="text-xs text-slate-400">
            Tipp: Das Protokoll kann auch direkt als PDF im Browser gespeichert werden.
          </span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-bold rounded-xl transition cursor-pointer"
            >
              {t("common.close", "Schließen")}
            </button>
            <button
              type="button"
              onClick={handlePrint}
              className="px-5 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold flex items-center gap-2 shadow-xs transition cursor-pointer"
            >
              <Printer className="w-4 h-4" />
              <span>{t("partner.btn_print_pdf", "Drucken / PDF Export")}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
