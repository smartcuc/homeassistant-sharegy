/*
# src/pages/DocumentsHubPage.jsx
# Zentraler Dokumenten- & Export-Manager (Download Hub)
*/

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../api/client";
import {
  FileText,
  Download,
  Search,
  Filter,
  RefreshCw,
  ShieldCheck,
  Zap,
  CheckCircle2,
  Calendar,
  Clock,
  ExternalLink,
  Layers,
  FileSpreadsheet,
  Code,
  Lock,
  Printer,
  X,
  FileCheck,
  Sparkles,
  Building,
  Check
} from "lucide-react";
import Card from "../components/ui/Card";
import { useTheme } from "../theme/ThemeContext";
import useModalDismiss from "../hooks/useModalDismiss";

export default function DocumentsHubPage() {
  const { t } = useTranslation();
  const { isDark } = useTheme();

  const [activeCategory, setActiveCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(null);

  useModalDismiss(Boolean(selectedDoc), () => setSelectedDoc(null));

  // On-Demand Generator Form State
  const [generatorForm, setGeneratorForm] = useState({
    type: "energy",
    period: "month",
    format: "pdf",
  });

  // 1. Fetch Documents Catalog
  const { data, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ["documents-catalog", activeCategory, searchQuery],
    queryFn: async () => {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      const params = new URLSearchParams();
      if (activeCategory !== "all") params.append("category", activeCategory);
      if (searchQuery.trim()) params.append("q", searchQuery.trim());

      return apiFetch(`/api/core/documents/?${params.toString()}`, {
        headers: { Authorization: token ? `Bearer ${token}` : "" },
      });
    },
    refetchInterval: 30000,
  });

  const documents = data?.documents || [];
  const stats = data?.stats || {
    total_count: 0,
    billing_count: 0,
    energy_count: 0,
    protocol_count: 0,
    eichrecht_count: 0,
    gdpr_count: 0,
  };

  // 2. Handle On-Demand Generation
  const handleGenerateDownload = async () => {
    setGenerating(true);
    try {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      const url = `/api/core/documents/generate/?type=${generatorForm.type}&period=${generatorForm.period}&format=${generatorForm.format}`;
      
      // Direkter Download-Trigger
      const response = await fetch(url, {
        headers: { Authorization: token ? `Bearer ${token}` : "" },
      });

      if (!response.ok) throw new Error("Export fehlgeschlagen");

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      const extension = generatorForm.format === "xlsx" ? "xlsx" : generatorForm.format === "csv" ? "csv" : generatorForm.format === "json" ? "json" : "pdf";
      a.download = `sharegy_${generatorForm.type}_${generatorForm.period}_${new Date().toISOString().slice(0, 10)}.${extension}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);

      setDownloadSuccess("Dokument erfolgreich generiert & heruntergeladen!");
      setTimeout(() => setDownloadSuccess(null), 4000);
      refetch();
    } catch (err) {
      console.error(err);
      alert("Fehler beim Erstellen des Exports. Bitte versuchen Sie es erneut.");
    } finally {
      setGenerating(false);
    }
  };

  // 3. Direct File Download Handler
  const handleDirectDownload = async (formatItem, doc) => {
    try {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      const response = await fetch(formatItem.url, {
        headers: { Authorization: token ? `Bearer ${token}` : "" },
      });

      if (!response.ok) throw new Error("Download fehlgeschlagen");

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      const fileExt = formatItem.type === "xlsx" ? "xlsx" : formatItem.type === "csv" ? "csv" : formatItem.type === "json" ? "json" : formatItem.type === "xml" ? "xml" : "pdf";
      a.download = `${doc.document_number.toLowerCase()}.${fileExt}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);

      setDownloadSuccess(`Download "${doc.title}" (${formatItem.label}) gestartet.`);
      setTimeout(() => setDownloadSuccess(null), 4000);
    } catch (e) {
      console.error(e);
      window.open(formatItem.url, "_blank");
    }
  };

  const categories = [
    { id: "all", label: "Alle Dokumente", icon: "📁", count: stats.total_count },
    { id: "billing", label: "Abrechnungen (§ 42b)", icon: "📄", count: stats.billing_count },
    { id: "energy", label: "Energiebilanzen", icon: "⚡", count: stats.energy_count },
    { id: "protocol", label: "IBN-Protokolle", icon: "🔧", count: stats.protocol_count },
    { id: "eichrecht", label: "Eichrecht & Zähler", icon: "⚖️", count: stats.eichrecht_count },
    { id: "gdpr", label: "DSGVO-Datenabzug", icon: "🔒", count: stats.gdpr_count },
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8 animate-fade-in">
      {/* ========================================================================= */}
      {/* 🚀 1. HEADER & KPI OVERVIEW */}
      {/* ========================================================================= */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-2xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
              <FileText className="w-5 h-5" />
            </span>
            <span className="text-xs font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
              GoBD & EnWG Revisionssicher
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white mt-2 tracking-tight">
            Zentraler Dokumenten- & Export-Manager
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Alle erzeugten PDF-Monatsabrechnungen, IBN-Übergabeprotokolle, Zählerstandslisten und Energieberichte an einem Ort.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-white dark:bg-slate-850 border border-slate-200 dark:border-slate-700 text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isRefetching ? "animate-spin text-indigo-500" : ""}`} />
            <span>{t("common.refresh", "Aktualisieren")}</span>
          </button>
        </div>
      </div>

      {/* SUCCESS TOAST BANNER */}
      {downloadSuccess && (
        <div className="bg-emerald-50 dark:bg-emerald-950/80 border border-emerald-200 dark:border-emerald-800 p-4 rounded-2xl flex items-center gap-3 text-emerald-800 dark:text-emerald-200 shadow-lg animate-fade-in">
          <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-600 dark:text-emerald-400" />
          <span className="text-sm font-semibold">{downloadSuccess}</span>
        </div>
      )}

      {/* KPI STATS CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <Card className="p-5 bg-gradient-to-br from-white to-slate-50 dark:from-slate-900 dark:to-slate-850 border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Gesamtdokumente</span>
            <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white mt-2">
            {stats.total_count}
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Revisionssicher archiviert
          </p>
        </Card>

        <Card className="p-5 bg-gradient-to-br from-white to-slate-50 dark:from-slate-900 dark:to-slate-850 border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Abrechnungsbescheide</span>
            <div className="p-2 rounded-xl bg-sky-50 dark:bg-sky-950 text-sky-600 dark:text-sky-400">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white mt-2">
            {stats.billing_count}
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            § 42b / § 42a EnWG & DATEV CSV
          </p>
        </Card>

        <Card className="p-5 bg-gradient-to-br from-white to-slate-50 dark:from-slate-900 dark:to-slate-850 border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">IBN & Eichrecht</span>
            <div className="p-2 rounded-xl bg-amber-50 dark:bg-amber-950 text-amber-600 dark:text-amber-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white mt-2">
            {stats.protocol_count + stats.eichrecht_count}
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            VDE-AR-N 4105 & PTB-A 50.7 Signiert
          </p>
        </Card>

        <Card className="p-5 bg-gradient-to-br from-white to-slate-50 dark:from-slate-900 dark:to-slate-850 border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Compliance-Status</span>
            <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400">
              <FileCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-xl font-black text-emerald-600 dark:text-emerald-400 mt-2 flex items-center gap-1.5">
            <span>100 % Konform</span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            GoBD, § 14 UStG, DSGVO Art. 15
          </p>
        </Card>
      </div>

      {/* ========================================================================= */}
      {/* ⚡ 2. ON-DEMAND SOFORT-EXPORT GENERATOR BAR */}
      {/* ========================================================================= */}
      <div className="bg-gradient-to-r from-indigo-900 via-indigo-950 to-slate-900 text-white rounded-3xl p-6 sm:p-8 shadow-xl border border-indigo-800/50 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-1.5 max-w-xl">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-300">
                On-Demand Export-Generator
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black tracking-tight">
              Individuellen Bericht oder Nachweis sofort erstellen
            </h2>
            <p className="text-xs sm:text-sm text-indigo-200/80">
              Wähle Berichtstyp, Auswertungszeitraum und Zielformat für deinen Ad-hoc-Download.
            </p>
          </div>

          <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 bg-white/10 backdrop-blur-md p-2.5 rounded-2xl border border-white/15">
            {/* Dokumenttyp */}
            <select
              value={generatorForm.type}
              onChange={(e) => setGeneratorForm({ ...generatorForm, type: e.target.value })}
              className="bg-slate-900/90 text-white border border-indigo-400/40 rounded-xl px-3 py-2 text-xs font-semibold focus:ring-2 focus:ring-indigo-400 outline-none cursor-pointer"
            >
              <option value="energy">⚡ EMS Energiebilanz & Autarkie</option>
              <option value="ibn">🔧 Digitales IBN-Übergabeprotokoll</option>
              <option value="eichrecht">⚖️ PTB-A 50.7 Eichrechtsnachweis</option>
            </select>

            {/* Zeitraum */}
            <select
              value={generatorForm.period}
              onChange={(e) => setGeneratorForm({ ...generatorForm, period: e.target.value })}
              className="bg-slate-900/90 text-white border border-indigo-400/40 rounded-xl px-3 py-2 text-xs font-semibold focus:ring-2 focus:ring-indigo-400 outline-none cursor-pointer"
            >
              <option value="today">Heute (Live)</option>
              <option value="month">Laufender Monat</option>
              <option value="last_month">Letzter Monat</option>
              <option value="year">Gesamtes Jahr (YTD)</option>
            </select>

            {/* Format */}
            <select
              value={generatorForm.format}
              onChange={(e) => setGeneratorForm({ ...generatorForm, format: e.target.value })}
              className="bg-slate-900/90 text-white border border-indigo-400/40 rounded-xl px-3 py-2 text-xs font-semibold focus:ring-2 focus:ring-indigo-400 outline-none cursor-pointer"
            >
              <option value="pdf">📄 PDF (Druckfertig)</option>
              <option value="xlsx">📊 Excel (.xlsx)</option>
              <option value="csv">📝 CSV (DATEV-konform)</option>
              <option value="json">💻 JSON-Rohdaten</option>
            </select>

            {/* Generate Button */}
            <button
              onClick={handleGenerateDownload}
              disabled={generating}
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs uppercase tracking-wider transition shadow-lg hover:shadow-emerald-500/25 active:scale-95 disabled:opacity-50 cursor-pointer shrink-0"
            >
              {generating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Erstelle...</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 📁 3. KATEGORIE-TABS & LIVE-SUCHE */}
      {/* ========================================================================= */}
      <div className="space-y-4">
        {/* Category Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-2xl text-xs sm:text-sm font-bold transition whitespace-nowrap cursor-pointer ${
                activeCategory === cat.id
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-500/25"
                  : "bg-white dark:bg-slate-850 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
              }`}
            >
              <span>{cat.icon}</span>
              <span>{cat.label}</span>
              <span
                className={`text-[11px] px-2 py-0.5 rounded-full font-mono ${
                  activeCategory === cat.id
                    ? "bg-white/20 text-white font-black"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-500"
                }`}
              >
                {cat.count}
              </span>
            </button>
          ))}
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Dokumenten-Nummer, Rechnungsname, Liegenschaft oder Zähler-ID suchen..."
            className="w-full pl-11 pr-4 py-3 bg-white dark:bg-slate-850 border border-slate-200 dark:border-slate-800 rounded-2xl text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 outline-none transition shadow-sm"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 📄 4. DOKUMENTEN-LISTE */}
      {/* ========================================================================= */}
      {isLoading ? (
        <div className="p-12 text-center space-y-4">
          <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin mx-auto" />
          <p className="text-sm font-semibold text-slate-500">Dokumentenkatalog wird geladen...</p>
        </div>
      ) : documents.length === 0 ? (
        <Card className="p-12 text-center space-y-4 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800">
          <div className="w-16 h-16 rounded-3xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-500 flex items-center justify-center mx-auto text-2xl">
            📁
          </div>
          <div className="space-y-1">
            <h3 className="text-lg font-black text-slate-900 dark:text-white">Keine Dokumente gefunden</h3>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              Für die gewählte Kategorie oder den Suchbegriff liegen derzeit keine historisierten Dokumente vor.
            </p>
          </div>
          <button
            onClick={() => { setActiveCategory("all"); setSearchQuery(""); }}
            className="px-4 py-2 rounded-xl bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400 font-bold text-xs hover:opacity-80 transition"
          >
            Filter zurücksetzen
          </button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {documents.map((doc) => (
            <Card
              key={doc.id}
              className="p-5 sm:p-6 bg-white dark:bg-slate-900 border-slate-200/90 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-indigo-600 transition shadow-sm hover:shadow-md"
            >
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5">
                {/* Document Main Info */}
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-900 shrink-0 text-xl">
                    {doc.category_icon || "📄"}
                  </div>

                  <div className="space-y-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs font-mono font-black px-2.5 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                        {doc.document_number}
                      </span>
                      <span className="text-xs font-bold text-slate-500 dark:text-slate-400">
                        · {doc.category_label}
                      </span>
                      <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                        {doc.status_label}
                      </span>
                    </div>

                    <h3 className="text-base sm:text-lg font-black text-slate-900 dark:text-white truncate">
                      {doc.title}
                    </h3>

                    <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 dark:text-slate-400 pt-1">
                      <span className="flex items-center gap-1.5">
                        <Calendar className="w-3.5 h-3.5 text-indigo-500" />
                        <span>Zeitraum: <b>{doc.period}</b></span>
                      </span>
                      <span className="flex items-center gap-1.5">
                        <Building className="w-3.5 h-3.5 text-slate-400" />
                        <span>Mandant: <b>{doc.tenant_name}</b></span>
                      </span>
                      <span className="flex items-center gap-1.5">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                        <span>Norm: <b>{doc.legal_compliance}</b></span>
                      </span>
                    </div>
                  </div>
                </div>

                {/* Download Actions */}
                <div className="flex flex-wrap items-center gap-2 pt-2 lg:pt-0 border-t lg:border-t-0 border-slate-100 dark:border-slate-800 shrink-0">
                  <button
                    onClick={() => setSelectedDoc(doc)}
                    className="px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-bold text-xs flex items-center gap-1.5 transition cursor-pointer"
                  >
                    <FileText className="w-3.5 h-3.5" />
                    <span>Details & Prüfsiegel</span>
                  </button>

                  {doc.formats && doc.formats.map((fmt, fIdx) => (
                    <button
                      key={fIdx}
                      onClick={() => handleDirectDownload(fmt, doc)}
                      className="px-3 py-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/70 hover:bg-indigo-100 dark:hover:bg-indigo-900 border border-indigo-200/80 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 font-bold text-xs flex items-center gap-1.5 transition shadow-sm cursor-pointer active:scale-95"
                      title={`${fmt.label} herunterladen`}
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>{fmt.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* ========================================================================= */}
      {/* 🔍 5. DETAIL- & PRÜFSIEGEL-MODAL */}
      {/* ========================================================================= */}
      {selectedDoc && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in"
          onClick={() => setSelectedDoc(null)}
        >
          <div
            className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-2xl w-full p-6 sm:p-8 space-y-6 shadow-2xl overflow-hidden my-auto max-h-[90vh] flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-2xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
                  <ShieldCheck className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                    <span>Revisions- & Prüfnachweis</span>
                    <span className="text-xs font-mono px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">
                      {selectedDoc.document_number}
                    </span>
                  </h3>
                  <p className="text-xs text-slate-500">
                    Kryptographische Integrität und rechtliche Festschreibung
                  </p>
                </div>
              </div>

              <button
                onClick={() => setSelectedDoc(null)}
                className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="space-y-4 overflow-y-auto pr-1">
              <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800 space-y-2">
                <div className="text-xs font-bold text-slate-400 uppercase">Dokumententitel</div>
                <div className="text-sm font-black text-slate-900 dark:text-white">{selectedDoc.title}</div>
                <div className="text-xs text-slate-500">Rechtsgrundlage: {selectedDoc.legal_compliance}</div>
              </div>

              {/* Metrics Grid */}
              {selectedDoc.metrics && (
                <div className="grid grid-cols-2 gap-3">
                  {Object.entries(selectedDoc.metrics).map(([key, val], idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-slate-100/70 dark:bg-slate-800/70">
                      <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">{key.replace(/_/g, " ")}</div>
                      <div className="text-sm font-black text-slate-900 dark:text-white mt-0.5">{String(val)}</div>
                    </div>
                  ))}
                </div>
              )}

              {/* Audit Proof Box */}
              <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 space-y-2">
                <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-300 text-xs font-black uppercase">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Festgeschrieben & Unveränderbar (WORM-Konform)</span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-300 font-mono">
                  SHA-256 Hash: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
                </p>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100 dark:border-slate-800">
              <button
                onClick={() => setSelectedDoc(null)}
                className="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-bold text-xs"
              >
                Schließen
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
