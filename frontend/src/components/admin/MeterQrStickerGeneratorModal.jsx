import { useState, useRef } from "react";
import { useTranslation } from "react-i18next";
import { QRCodeSVG } from "qrcode.react";
import { Printer, X, CheckSquare, Square, FileText, Tag, Sparkles, Building2, ShieldCheck } from "lucide-react";

export default function MeterQrStickerGeneratorModal({
  isOpen,
  onClose,
  communityName = "Quartier & Gebäude",
  buildingAddress = "Musterstraße 42, 10115 Berlin",
  units = [],
}) {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState("stickers"); // "stickers" | "letters"
  const [selectedUnitIds, setSelectedUnitIds] = useState(
    () => new Set(units.length ? units.map(u => u.id) : ["we-01", "we-02", "we-03", "we-04", "we-05", "we-06"])
  );
  const [includeLogo, setIncludeLogo] = useState(true);
  const [customContact, setCustomContact] = useState("service@sharegy.de | Tel: 0800-SHAREGY");
  const printRef = useRef(null);

  // Fallback demo units if empty
  const effectiveUnits = units.length ? units : [
    { id: "we-01", name: "WE 01 (EG links)", meterNumber: "1EMH0012849201", tenant: "Familie Müller", token: "magic_we01_sun" },
    { id: "we-02", name: "WE 02 (EG rechts)", meterNumber: "1EMH0012849202", tenant: "M. Schmidt", token: "magic_we02_sun" },
    { id: "we-03", name: "WE 03 (1. OG links)", meterNumber: "1EMH0012849203", tenant: "Dr. Weber", token: "magic_we03_sun" },
    { id: "we-04", name: "WE 04 (1. OG rechts)", meterNumber: "1EMH0012849204", tenant: "L. Becker", token: "magic_we04_sun" },
    { id: "we-05", name: "WE 05 (2. OG links)", meterNumber: "1EMH0012849205", tenant: "S. Fischer", token: "magic_we05_sun" },
    { id: "we-06", name: "Allgemeinstrom (WP/Aufzug)", meterNumber: "1EMH0012849999", tenant: "Hausverwaltung", token: "magic_we06_sun" },
  ];

  if (!isOpen) return null;

  const toggleSelectAll = () => {
    if (selectedUnitIds.size === effectiveUnits.length) {
      setSelectedUnitIds(new Set());
    } else {
      setSelectedUnitIds(new Set(effectiveUnits.map(u => u.id)));
    }
  };

  const toggleUnit = (id) => {
    const next = new Set(selectedUnitIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setSelectedUnitIds(next);
  };

  const filteredUnits = effectiveUnits.filter(u => selectedUnitIds.has(u.id));

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm overflow-y-auto">
      
      {/* Print-Only CSS Styles */}
      <style>{`
        @media print {
          body * {
            visibility: hidden;
          }
          #printable-qr-sheet, #printable-qr-sheet * {
            visibility: visible;
          }
          #printable-qr-sheet {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            background: white !important;
            color: black !important;
            padding: 0;
            margin: 0;
          }
          .page-break {
            page-break-after: always;
          }
          .no-print {
            display: none !important;
          }
        }
      `}</style>

      <div className="relative w-full max-w-5xl bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[92vh]">
        
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between gap-4 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200/60 dark:border-indigo-800/60 flex items-center justify-center text-indigo-600 dark:text-indigo-400 shrink-0">
              <Printer className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                {t("qr_generator.modal_title", "Zähler-QR-Sticker & Mieter-Onboarding-Generator")}
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-100 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                  A4 Print Ready
                </span>
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {t("qr_generator.modal_subtitle", "Druckfertige Klebeschilder für die Hutschiene & Mieter-Willkommensdossiers.")}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              disabled={filteredUnits.length === 0}
              className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-bold text-xs flex items-center gap-2 shadow-sm transition-all cursor-pointer"
            >
              <Printer className="w-4 h-4" />
              {t("qr_generator.print_action", "PDF drucken / exportieren")} ({filteredUnits.length})
            </button>

            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Configuration Toolbar */}
        <div className="p-4 bg-slate-50/80 dark:bg-slate-800/40 border-b border-slate-100 dark:border-slate-800 flex flex-wrap items-center justify-between gap-4 shrink-0 text-xs">
          
          {/* Format Mode Tabs */}
          <div className="flex items-center gap-1 p-1 bg-slate-200/70 dark:bg-slate-800 rounded-xl">
            <button
              onClick={() => setActiveTab("stickers")}
              className={`px-3 py-1.5 rounded-lg font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
                activeTab === "stickers"
                  ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
              }`}
            >
              <Tag className="w-3.5 h-3.5" />
              {t("qr_generator.tab_stickers", "🏷️ Zähler-Klebeschilder (Hutschiene)")}
            </button>
            <button
              onClick={() => setActiveTab("letters")}
              className={`px-3 py-1.5 rounded-lg font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
                activeTab === "letters"
                  ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              {t("qr_generator.tab_letters", "✉️ Mieter-Willkommensbrief (A4)")}
            </button>
          </div>

          {/* Unit selection toggles */}
          <div className="flex items-center gap-3">
            <button
              onClick={toggleSelectAll}
              className="flex items-center gap-1.5 font-bold text-slate-700 dark:text-slate-300 hover:text-indigo-600 cursor-pointer"
            >
              {selectedUnitIds.size === effectiveUnits.length ? (
                <CheckSquare className="w-4 h-4 text-indigo-600" />
              ) : (
                <Square className="w-4 h-4 text-slate-400" />
              )}
              {t("qr_generator.select_all", "Alle Wohneinheiten")} ({selectedUnitIds.size}/{effectiveUnits.length})
            </button>

            <label className="flex items-center gap-1.5 text-slate-600 dark:text-slate-400 cursor-pointer">
              <input
                type="checkbox"
                checked={includeLogo}
                onChange={(e) => setIncludeLogo(e.target.checked)}
                className="rounded border-slate-300 text-indigo-600"
              />
              {t("qr_generator.include_branding", "Branding / Logo")}
            </label>
          </div>
        </div>

        {/* Content Body: Sidebar Selector & Live Print Preview */}
        <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 lg:grid-cols-4 gap-6">
          
          {/* Unit Checkbox List */}
          <div className="lg:col-span-1 space-y-2 border-r border-slate-100 dark:border-slate-800 pr-4">
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
              {t("qr_generator.select_units_title", "Wohneinheiten wählen")}
            </div>

            <div className="space-y-1.5 max-h-[50vh] overflow-y-auto">
              {effectiveUnits.map((u) => {
                const isSelected = selectedUnitIds.has(u.id);
                return (
                  <div
                    key={u.id}
                    onClick={() => toggleUnit(u.id)}
                    className={`p-2.5 rounded-xl border cursor-pointer transition-all flex items-center justify-between text-xs ${
                      isSelected
                        ? "bg-indigo-50/60 dark:bg-indigo-950/40 border-indigo-200 dark:border-indigo-800 font-bold text-indigo-950 dark:text-indigo-200"
                        : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-slate-300"
                    }`}
                  >
                    <div>
                      <div>{u.name}</div>
                      <div className="text-[10px] font-mono text-slate-400 font-normal">{u.meterNumber}</div>
                    </div>
                    {isSelected ? (
                      <CheckSquare className="w-4 h-4 text-indigo-600 shrink-0" />
                    ) : (
                      <Square className="w-4 h-4 text-slate-300 shrink-0" />
                    )}
                  </div>
                );
              })}
            </div>

            {/* Property Contact Info Input */}
            <div className="pt-4 border-t border-slate-100 dark:border-slate-800 space-y-1">
              <label className="text-[10px] font-bold text-slate-400 uppercase">
                {t("qr_generator.contact_label", "Kontaktzeile auf Ausdruck")}
              </label>
              <input
                type="text"
                value={customContact}
                onChange={(e) => setCustomContact(e.target.value)}
                className="w-full px-2.5 py-1.5 rounded-lg text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200"
                placeholder="service@sharegy.de"
              />
            </div>
          </div>

          {/* Live Printable Preview Canvas */}
          <div className="lg:col-span-3 bg-slate-100 dark:bg-slate-950 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-x-auto flex justify-center">
            
            <div
              id="printable-qr-sheet"
              ref={printRef}
              className="bg-white text-slate-900 p-8 shadow-md rounded-xl max-w-2xl w-full min-h-[600px] border border-slate-300 print:border-none print:shadow-none print:rounded-none"
            >
              {/* STICKER MODE PREVIEW */}
              {activeTab === "stickers" && (
                <div className="space-y-6">
                  <div className="border-b-2 border-slate-900 pb-3 flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-black uppercase tracking-wider text-slate-900">
                        {includeLogo && "⚡ SHAREGY | "}ZÄHLER-STICKER SHEET
                      </h4>
                      <p className="text-[11px] text-slate-600">
                        {communityName} • {buildingAddress}
                      </p>
                    </div>
                    <div className="text-right text-[10px] text-slate-500 font-mono">
                      {filteredUnits.length} Zähler • DIN A4
                    </div>
                  </div>

                  {/* 2xN Sticker Grid */}
                  <div className="grid grid-cols-2 gap-4">
                    {filteredUnits.map((u) => {
                      const joinUrl = `https://sharegy.de/join/magic?token=${u.token || "demo"}&unit=${encodeURIComponent(u.id)}`;
                      return (
                        <div
                          key={u.id}
                          className="border-2 border-dashed border-slate-400 p-3.5 rounded-lg flex items-center gap-3.5 bg-white relative"
                        >
                          <div className="p-1.5 bg-white border border-slate-200 rounded shrink-0">
                            <QRCodeSVG
                              value={joinUrl}
                              size={76}
                              level="M"
                              includeMargin={false}
                            />
                          </div>

                          <div className="min-w-0 flex-1 space-y-0.5">
                            <div className="flex items-center justify-between">
                              <span className="text-[9px] font-black uppercase bg-slate-900 text-white px-1.5 py-0.5 rounded">
                                {u.name}
                              </span>
                              {includeLogo && (
                                <span className="text-[9px] font-bold text-indigo-700">⚡ Sharegy</span>
                              )}
                            </div>
                            <div className="text-[10px] font-bold text-slate-800 truncate pt-0.5">
                              {u.tenant}
                            </div>
                            <div className="text-[9px] font-mono text-slate-500">
                              OBIS: {u.meterNumber}
                            </div>
                            <div className="text-[8px] text-slate-600 leading-tight pt-1 border-t border-slate-100 flex items-center gap-1">
                              <Sparkles className="w-2.5 h-2.5 text-amber-600 shrink-0" />
                              <span>Handykamera scannen für Live-Solaranteil</span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  <div className="pt-4 border-t border-slate-200 text-center text-[9px] text-slate-500">
                    Gedruckt über Sharegy HEMS Platform • {customContact}
                  </div>
                </div>
              )}

              {/* WELCOME LETTER MODE PREVIEW */}
              {activeTab === "letters" && (
                <div className="space-y-8">
                  {filteredUnits.map((u, idx) => {
                    const joinUrl = `https://sharegy.de/join/magic?token=${u.token || "demo"}&unit=${encodeURIComponent(u.id)}`;
                    return (
                      <div
                        key={u.id}
                        className={`space-y-6 ${idx > 0 ? "page-break pt-8 border-t-2 border-slate-300 print:border-none print:pt-0" : ""}`}
                      >
                        {/* Letter Header */}
                        <div className="flex items-start justify-between border-b-2 border-slate-900 pb-4">
                          <div>
                            <div className="text-xs font-bold uppercase tracking-wider text-indigo-700">
                              {includeLogo ? "⚡ SHAREGY • GEMEINSCHAFTLICHE GEBÄUDEVERSORGUNG & MIETERSTROM" : "GEBÄUDEVERSORGUNG"}
                            </div>
                            <h2 className="text-xl font-black text-slate-900 mt-1">
                              Willkommen beim Solarstrom im Gebäude!
                            </h2>
                            <p className="text-xs text-slate-600 mt-0.5">
                              {communityName} • {buildingAddress}
                            </p>
                          </div>
                          <div className="text-right">
                            <span className="px-3 py-1 bg-slate-900 text-white text-xs font-bold rounded-lg uppercase">
                              {u.name}
                            </span>
                          </div>
                        </div>

                        {/* Tenant Greeting & Benefits */}
                        <div className="space-y-3 text-xs text-slate-700 leading-relaxed">
                          <p>
                            Sehr geehrte(r) <strong>{u.tenant}</strong>,
                          </p>
                          <p>
                            Ihr Gebäude wurde mit einer modernen Photovoltaikanlage und einem intelligenten Smart Meter
                            ausgestattet. Sie können ab sofort lokal erzeugten, sauberen Solarstrom direkt vom Hausdach
                            beziehen und Ihre Stromkosten spürbar senken.
                          </p>
                        </div>

                        {/* 3 Step Action Guide */}
                        <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                          <h4 className="text-xs font-bold uppercase text-slate-900 flex items-center gap-1.5">
                            <ShieldCheck className="w-4 h-4 text-emerald-600" />
                            So einfach starten Sie (ohne Registrierungsaufwand):
                          </h4>

                          <div className="grid grid-cols-3 gap-3 text-xs">
                            <div className="p-2.5 bg-white border border-slate-200 rounded-lg">
                              <div className="font-bold text-slate-900 mb-1">1. QR-Code scannen</div>
                              <p className="text-[11px] text-slate-600">Öffnen Sie die Kamera Ihres Smartphones und halten Sie sie auf den Code.</p>
                            </div>
                            <div className="p-2.5 bg-white border border-slate-200 rounded-lg">
                              <div className="font-bold text-slate-900 mb-1">2. Live-Anteil sehen</div>
                              <p className="text-[11px] text-slate-600">Sehen Sie sekundengenau, wie viel Solarstrom gerade in Ihrer Wohnung ankommt.</p>
                            </div>
                            <div className="p-2.5 bg-white border border-slate-200 rounded-lg">
                              <div className="font-bold text-slate-900 mb-1">3. Kosten sparen</div>
                              <p className="text-[11px] text-slate-600">Nutzen Sie Großverbraucher (Waschmaschine, Spülmaschine) bevorzugt bei Sonnenschein.</p>
                            </div>
                          </div>
                        </div>

                        {/* QR Code & Meter Callout */}
                        <div className="p-5 border-2 border-indigo-600 rounded-2xl flex items-center justify-between gap-6 bg-indigo-50/30">
                          <div className="space-y-1.5">
                            <div className="text-xs font-black uppercase text-indigo-900">
                              Ihr persönlicher Schnellzugang für {u.name}:
                            </div>
                            <div className="text-xs text-slate-700">
                              Zählernummer: <strong className="font-mono">{u.meterNumber}</strong>
                            </div>
                            <div className="text-[11px] text-slate-500 pt-1">
                              Dieser Code ist fest mit Ihrer Wohneinheit verknüpft und benötigt kein Passwort.
                            </div>
                          </div>

                          <div className="p-2 bg-white border border-slate-300 rounded-xl shrink-0 shadow-xs text-center">
                            <QRCodeSVG
                              value={joinUrl}
                              size={100}
                              level="H"
                              includeMargin={false}
                            />
                            <div className="text-[8px] font-bold text-slate-600 mt-1 uppercase">Jetzt scannen</div>
                          </div>
                        </div>

                        {/* Footer Contact */}
                        <div className="pt-4 border-t border-slate-200 flex items-center justify-between text-[10px] text-slate-500">
                          <div className="flex items-center gap-1.5">
                            <Building2 className="w-3.5 h-3.5 text-slate-400" />
                            <span>Hausverwaltung & Gebäudeservice: {customContact}</span>
                          </div>
                          <span>Powered by Sharegy Platform</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

            </div>
          </div>

        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-slate-50 dark:bg-slate-800/40 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between gap-4 shrink-0 text-xs">
          <div className="text-slate-500 dark:text-slate-400">
            {t("qr_generator.footer_hint", "Tipp: Für Zählerschränke empfehlen wir wetterfeste Polyester- oder Vinyl-Etikettenbögen (z.B. Avery Zweckform A4).")}
          </div>

          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-800 dark:text-slate-200 font-bold transition-colors cursor-pointer"
          >
            {t("common.close", "Schließen")}
          </button>
        </div>

      </div>
    </div>
  );
}
