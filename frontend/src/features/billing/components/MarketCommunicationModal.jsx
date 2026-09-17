import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import {
  FileText,
  Send,
  Download,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  X,
  Building2,
  Layers,
  Database,
  ShieldCheck,
  Code2,
  Clock
} from "lucide-react";

export default function MarketCommunicationModal({ isOpen, onClose, tenantId }) {
    const { t } = useTranslation();
  const [makoType, setMakoType] = useState("MSCONS");
  const [provider, setProvider] = useState("powercloud");
  const [loading, setLoading] = useState(false);
  const [exportResult, setExportResult] = useState(null);
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState("export"); // "export" | "logs"
  const [errorMsg, setErrorMsg] = useState(null);

  const fetchLogs = async () => {
    try {
      const res = await apiFetch("/api/billing/mako/logs/");
      setLogs(res?.logs || []);
    } catch (err) {
      console.warn("Fehler beim Laden der Mako-Logs:", err);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchLogs();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleExport = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setErrorMsg(null);
      setExportResult(null);
      const res = await apiFetch("/api/billing/mako/export/", {
        method: "POST",
        body: JSON.stringify({
          tenant_id: tenantId,
          mako_type: makoType,
          provider: provider,
        }),
      });
      setExportResult(res);
      fetchLogs();
    } catch (err) {
      setErrorMsg(err?.message || "Marktkommunikations-Export fehlgeschlagen.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadEdifact = () => {
    if (!exportResult?.raw_edifact_sample) return;
    const blob = new Blob([exportResult.raw_edifact_sample], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${makoType}_${new Date().toISOString().slice(0, 10)}.edi`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/75 backdrop-blur-md animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header (Fixed) */}
        <div className="p-6 md:p-8 pb-4 border-b border-slate-800 shrink-0 space-y-4">
          <div className="flex justify-between items-start">
            <div className="space-y-1">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400">
                  <FileText className="w-5 h-5" />
                </div>
                <h2 className="text-xl md:text-2xl font-bold text-white">
                  BNetzA AS4 Marktkommunikations-Adapter
                </h2>
              </div>
              <p className="text-xs md:text-sm text-slate-400">
                Automatisierte EDIFACT-Generierung & AS4-Dispatch für 15-Minuten-Lastgänge (Energy Sharing / MSCONS) und Zählpunkt-Stammdaten (UTILMD).
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Tab Navigation */}
          <div className="flex border-b border-slate-800/80">
            <button
              onClick={() => setActiveTab("export")}
              className={`px-4 py-2 text-xs font-semibold uppercase tracking-wider border-b-2 transition ${
                activeTab === "export"
                  ? "border-emerald-500 text-emerald-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              EDIFACT Export & AS4 Dispatch
            </button>
            <button
              onClick={() => setActiveTab("logs")}
              className={`px-4 py-2 text-xs font-semibold uppercase tracking-wider border-b-2 transition ${
                activeTab === "logs"
                  ? "border-emerald-500 text-emerald-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Übertragungs-Protokoll ({logs.length})
            </button>
          </div>
        </div>

        {/* Scrollable Body */}
        <div className="p-6 md:p-8 overflow-y-auto space-y-6 flex-1">
          {errorMsg && (
            <div className="p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

        {activeTab === "export" ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Left Column: Config */}
            <form onSubmit={handleExport} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-2">
                  {t("mako.format_type", "Nachrichten-Format & Transaktionstyp")}
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setMakoType("MSCONS")}
                    className={`p-3 rounded-xl border text-left transition cursor-pointer ${
                      makoType === "MSCONS"
                        ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-300"
                        : "bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    <div className="text-xs font-bold">MSCONS 2.2b</div>
                    <div className="text-[11px] opacity-80">15m-Lastgänge & Zählerstände</div>
                  </button>
                  <button
                    type="button"
                    onClick={() => setMakoType("UTILMD")}
                    className={`p-3 rounded-xl border text-left transition cursor-pointer ${
                      makoType === "UTILMD"
                        ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-300"
                        : "bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    <div className="text-xs font-bold">UTILMD 2.4</div>
                    <div className="text-[11px] opacity-80">Zählpunkt & Stammdaten</div>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  {t("mako.target_system", "Ziel-Abrechnungssystem / AS4-Gateway")}
                </label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 px-3.5 py-2.5 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  <option value="powercloud">powercloud (BNetzA AS4 Connect)</option>
                  <option value="schleupen">Schleupen.CS 3.0 / AS4 Broker</option>
                  <option value="sap_isu">SAP IS-U / SAP Cloud for Utilities</option>
                  <option value="wilken">Wilken ENER:GY Mako Hub</option>
                  <option value="direct_as4">Zertifiziertes AS4-Gateway (Direct PKI)</option>
                </select>
              </div>

              <div className="p-4 bg-slate-950/70 border border-slate-800/80 rounded-2xl text-xs space-y-2 text-slate-400">
                <div className="flex items-center gap-2 text-emerald-400 font-semibold">
                  <ShieldCheck className="w-4 h-4" />
                  <span>{t("mako.compliance_title", "BNetzA GPKE / WiM Konformität")}</span>
                </div>
                <p>
                  {t("mako.compliance_desc", "Erzeugt standardisierte EDIFACT UNA/UNB/UNH/UNT Segmente mit automatischem Prüfsummenabgleich für die Gemeinschaftliche Gebäudeversorgung nach § 42b EnWG.")}
                </p>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-emerald-600/20 transition cursor-pointer"
                >
                  {loading ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                  <span>{t("mako.generate_send", "EDIFACT generieren & an AS4 senden")}</span>
                </button>
              </div>
            </form>

            {/* Right Column: EDIFACT Raw Preview */}
            <div className="space-y-3">
              <div className="flex justify-between items-center text-xs">
                <span className="font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <Code2 className="w-3.5 h-3.5 text-emerald-400" />
                  {t("mako.raw_preview", "EDIFACT Rohdaten-Vorschau")}
                </span>
                {exportResult?.raw_edifact_sample && (
                  <button
                    onClick={handleDownloadEdifact}
                    className="flex items-center gap-1 text-emerald-400 hover:text-emerald-300 font-medium cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>{t("mako.download_edi", "Download (.edi)")}</span>
                  </button>
                )}
              </div>

              <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 font-mono text-xs text-slate-300 h-64 overflow-y-auto whitespace-pre-wrap leading-relaxed">
                {exportResult ? (
                  exportResult.raw_edifact_sample
                ) : (
                  <span className="text-slate-600">
                    {t("mako.preview_placeholder", "Klicken Sie auf 'EDIFACT generieren & an AS4 senden', um die Vorschau zu laden.")}
                  </span>
                )}
              </div>

              {exportResult?.dispatch_info && (
                <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-xs space-y-1">
                  <div className="text-emerald-300 font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>{t("mako.sent_confirmed", "AS4 Übertragung bestätigt")}</span>
                  </div>
                  <div className="text-slate-400">
                    Receipt-ID: <span className="font-mono text-slate-200">{exportResult.dispatch_info.receipt_id}</span>
                  </div>
                </div>
              )}
            </div>

          </div>
        ) : (
          /* Logs Tab */
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {logs.length === 0 ? (
              <div className="py-12 text-center text-slate-500 text-sm">
                Noch keine Marktkommunikations-Übertragungen protokolliert.
              </div>
            ) : (
              logs.map((log, idx) => (
                <div
                  key={log.id || idx}
                  className="p-4 bg-slate-950/80 border border-slate-800 rounded-2xl flex items-center justify-between gap-4 text-xs"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded-md font-mono font-semibold bg-emerald-500/20 text-emerald-400">
                        {log.mako_type}
                      </span>
                      <span className="font-semibold text-slate-200">{log.provider}</span>
                      <span className="text-slate-400 font-mono">({log.receipt_id})</span>
                    </div>
                    <div className="text-slate-400">{log.message}</div>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-500 font-mono flex-shrink-0">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{new Date(log.created_at).toLocaleString("de-DE")}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
        </div>

        {/* Footer (Fixed at bottom) */}
        <div className="p-4 md:p-6 border-t border-slate-800 shrink-0 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium rounded-xl transition cursor-pointer"
          >
            Schließen
          </button>
        </div>

      </div>
    </div>
  );
}
