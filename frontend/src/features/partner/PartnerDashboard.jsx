import useModalDismiss from "../../hooks/useModalDismiss";
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router-dom";
import { apiFetch } from "../../api/client";
import AdminPageHeader from "../../components/admin/AdminPageHeader";
import MeterQrStickerGeneratorModal from "../../components/admin/MeterQrStickerGeneratorModal";
import PartnerHandoverProtocolModal from "./components/PartnerHandoverProtocolModal";
import PartnerFleetMap from "./components/PartnerFleetMap";
import {
  Wrench,
  ShieldCheck,
  Zap,
  Activity,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Search,
  PlusCircle,
  RefreshCw,
  Home,
  Sun,
  Battery,
  BatteryCharging,
  Cpu,
  ArrowUpRight,
  Send,
  Building,
  Check,
  AlertCircle,
  Eye,
  FileText,
  Printer,
  SlidersHorizontal,
  LayoutGrid,
  Table as TableIcon,
  Map as MapIcon,
  Wifi,
  Radio
} from "lucide-react";

export default function PartnerDashboard() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterHealth, setFilterHealth] = useState("all");
  const [viewMode, setViewMode] = useState("table"); // "table" | "grid" | "map"
  
  // Diagnostics Modal State
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [diagLoading, setDiagLoading] = useState(false);
  const [diagResult, setDiagResult] = useState(null);
  const [showHandoverProtocol, setShowHandoverProtocol] = useState(false);
  const [protocolAsset, setProtocolAsset] = useState(null);

  // Quick Onboard Modal State
  const [showOnboardModal, setShowOnboardModal] = useState(false);
  const [showStickerModal, setShowStickerModal] = useState(false);
  useModalDismiss(Boolean(selectedAsset), () => { setSelectedAsset(null); setShowHandoverProtocol(false); });
  useModalDismiss(showOnboardModal, () => setShowOnboardModal(false));

  const [onboardForm, setOnboardForm] = useState({
    customer_email: "",
    home_name: "",
    street: "",
    city: "",
    postal_code: "",
    pv_capacity_kwp: 10,
    battery_capacity_kwh: 10,
  });
  const [onboardSuccess, setOnboardSuccess] = useState(null);
  const [onboardError, setOnboardError] = useState(null);
  const [onboardSubmitting, setOnboardSubmitting] = useState(false);

  const fetchFleet = async () => {
    try {
      setLoading(true);
      const res = await apiFetch("/api/partner/fleet/");
      setData(res);
    } catch (err) {
      console.error("Fehler beim Laden des Partner-Dashboards:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFleet();
  }, []);

  const handleRunDiagnostics = async (assetId, action = "ping") => {
    try {
      setDiagLoading(true);
      setDiagResult(null);
      const res = await apiFetch(`/api/partner/diagnostics/${assetId}/`, {
        method: "POST",
        body: JSON.stringify({ action }),
      });
      setDiagResult(res);
    } catch (err) {
      setDiagResult({ success: false, message: "Diagnose fehlgeschlagen. Netzwerkfehler oder Timeout." });
    } finally {
      setDiagLoading(false);
    }
  };

  const handleQuickOnboardSubmit = async (e) => {
    e.preventDefault();
    try {
      setOnboardSubmitting(true);
      setOnboardError(null);
      setOnboardSuccess(null);
      const res = await apiFetch("/api/partner/quick-onboard/", {
        method: "POST",
        body: JSON.stringify(onboardForm),
      });
      setOnboardSuccess(res.message);
      setOnboardForm({ customer_email: "", home_name: "", street: "", city: "", postal_code: "", pv_capacity_kwp: 10, battery_capacity_kwh: 10 });
      fetchFleet();
    } catch (err) {
      setOnboardError(err?.message || "Inbetriebnahme fehlgeschlagen.");
    } finally {
      setOnboardSubmitting(false);
    }
  };

  if (loading && !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white">
        <div className="flex items-center gap-3">
          <RefreshCw className="w-6 h-6 animate-spin text-sky-500" />
          <span className="text-lg font-medium">{t("partner.loading", "Lade Installateurs- & Partner-Flotte…")}</span>
        </div>
      </div>
    );
  }

  const homesList = data?.homes || data?.fleet || [];
  const filteredHomes = homesList.filter((h) => {
    const matchesSearch =
      (h.name || "").toLowerCase().includes(search.toLowerCase()) ||
      (h.customer_name || "").toLowerCase().includes(search.toLowerCase()) ||
      (h.customer_email || "").toLowerCase().includes(search.toLowerCase()) ||
      (h.address || "").toLowerCase().includes(search.toLowerCase());
    const matchesHealth = filterHealth === "all" || h.health === filterHealth;
    return matchesSearch && matchesHealth;
  });

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* UNIFIED ADMIN HEADER */}
        <AdminPageHeader
          icon={<Wrench className="w-5 h-5 text-sky-500" />}
          iconBg="bg-sky-500/10 border-sky-500/20 text-sky-600 dark:text-sky-400"
          title={data?.partner_company?.name || t("partner.portal_title", "Installateurs- & Partner-Portal")}
          subtitle={t("partner.subtitle", "Zentrale Flotten-Telemetrie, Störungsampel & 1-Klick Fernwartung betreuter Kundenanlagen.")}
          manualLink="/app/help/admin-partner-fleet-installer-guide"
          manualLabel={t("partner.btn_manual", "Handbuch (Partner)")}
          actions={
            <>
              <button
                type="button"
                onClick={fetchFleet}
                className="px-3.5 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition flex items-center gap-1.5 cursor-pointer shadow-xs"
                title={t("common.refresh", "Aktualisieren")}
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>{t("common.refresh", "Aktualisieren")}</span>
              </button>
              <button
                type="button"
                onClick={() => setShowStickerModal(true)}
                className="px-3.5 py-2 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 rounded-xl text-xs font-bold hover:bg-indigo-100 dark:hover:bg-indigo-900/60 transition flex items-center gap-1.5 cursor-pointer shadow-xs"
                title={t("partner.btn_qr_stickers", "Zähler-Sticker")}
              >
                <Printer className="w-3.5 h-3.5" />
                <span>{t("partner.btn_qr_stickers", "Zähler-Sticker")}</span>
              </button>
              <button
                type="button"
                onClick={() => setShowOnboardModal(true)}
                className="flex items-center gap-1.5 px-3.5 py-2 bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs rounded-xl shadow-xs transition duration-200 cursor-pointer"
              >
                <PlusCircle className="w-3.5 h-3.5" />
                <span>{t("partner.quick_onboard_btn", "Schnell-IBN")}</span>
              </button>
            </>
          }
        />

        {/* KPI Cards (6 Metriken) */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
          {/* 1. Liegenschaften */}
          <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 p-4 rounded-2xl shadow-xs">
            <div className="flex items-center justify-between text-blue-600 dark:text-blue-400 text-xs font-bold uppercase mb-2">
              <span>{t("partner.kpi_managed_homes", "Betreute Anlagen")}</span>
              <Building className="w-4 h-4" />
            </div>
            <div className="text-2xl font-black text-slate-900 dark:text-white">{data?.summary?.total_homes || 0}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Kunden im Bestand</div>
          </div>

          {/* 2. PV-Leistung */}
          <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 p-4 rounded-2xl shadow-xs">
            <div className="flex items-center justify-between text-amber-600 dark:text-amber-400 text-xs font-bold uppercase mb-2">
              <span>{t("partner.kpi_pv_power", "PV-Leistung")}</span>
              <Sun className="w-4 h-4" />
            </div>
            <div className="text-2xl font-black text-slate-900 dark:text-white">{data?.summary?.total_pv_power_kw || 0} <span className="text-xs font-normal">kW</span></div>
            <div className="text-[11px] text-slate-400 mt-0.5">Erzeugungs-Peak</div>
          </div>

          {/* 3. Batteriespeicher & SoC */}
          <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 p-4 rounded-2xl shadow-xs">
            <div className="flex items-center justify-between text-emerald-600 dark:text-emerald-400 text-xs font-bold uppercase mb-2">
              <span>{t("partner.kpi_storage_capacity", "Heimspeicher")}</span>
              <Battery className="w-4 h-4" />
            </div>
            <div className="text-2xl font-black text-slate-900 dark:text-white">
              {data?.summary?.total_battery_capacity_kwh || 0} <span className="text-xs font-normal">kWh</span>
            </div>
            <div className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold mt-0.5">
              Ø {data?.summary?.avg_battery_soc_pct || 65}% SoC
            </div>
          </div>

          {/* 4. Wallbox Ladeleistung */}
          <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 p-4 rounded-2xl shadow-xs">
            <div className="flex items-center justify-between text-indigo-600 dark:text-indigo-400 text-xs font-bold uppercase mb-2">
              <span>{t("partner.kpi_wallbox_power", "Wallboxen")}</span>
              <Zap className="w-4 h-4" />
            </div>
            <div className="text-2xl font-black text-slate-900 dark:text-white">{data?.summary?.total_wallbox_power_kw || 0} <span className="text-xs font-normal">kW</span></div>
            <div className="text-[11px] text-slate-400 mt-0.5">Ladeleistung gesamt</div>
          </div>

          {/* 5. § 14a Steuerbare Lasten */}
          <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 p-4 rounded-2xl shadow-xs">
            <div className="flex items-center justify-between text-teal-600 dark:text-teal-400 text-xs font-bold uppercase mb-2">
              <span>{t("partner.kpi_steuve_loads", "§ 14a SteuVE")}</span>
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div className="text-2xl font-black text-slate-900 dark:text-white">{data?.summary?.total_steuve_count || 0}</div>
            <div className="text-[11px] text-teal-600 dark:text-teal-400 font-semibold mt-0.5">Netzdienlich bereit</div>
          </div>

          {/* 6. Störungen & Warnungen */}
          <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 p-4 rounded-2xl shadow-xs">
            <div className="flex items-center justify-between text-rose-600 dark:text-rose-400 text-xs font-bold uppercase mb-2">
              <span>{t("partner.kpi_alerts", "Störungen")}</span>
              <AlertTriangle className="w-4 h-4" />
            </div>
            <div className="text-2xl font-black text-rose-600 dark:text-rose-400">{data?.summary?.active_alerts_count || 0}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Handlungsbedarf</div>
          </div>
        </div>

        {/* Filter, Search & View Switcher */}
        <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder={t("partner.search_placeholder", "Suche nach Kunde, Anlage, PLZ oder Adresse…")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 pl-10 pr-4 py-2 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-sky-500 shadow-2xs"
            />
          </div>

          <div className="flex items-center justify-between sm:justify-end gap-2.5 overflow-x-auto pb-1">
            {/* Filter Buttons */}
            <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800/60 p-1 rounded-xl text-xs font-semibold">
              <button
                type="button"
                onClick={() => setFilterHealth("all")}
                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                  filterHealth === "all" ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white font-bold shadow-2xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                }`}
              >
                {t("partner.filter_all", { count: homesList.length, defaultValue: `Alle (${homesList.length})` })}
              </button>
              <button
                type="button"
                onClick={() => setFilterHealth("ok")}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-lg transition cursor-pointer ${
                  filterHealth === "ok" ? "bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 font-bold shadow-2xs" : "text-slate-500 hover:text-emerald-600"
                }`}
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                {t("partner.filter_ok", { count: data?.summary?.status_counts?.ok || 0, defaultValue: `Optimal (${data?.summary?.status_counts?.ok || 0})` })}
              </button>
              <button
                type="button"
                onClick={() => setFilterHealth("warning")}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-lg transition cursor-pointer ${
                  filterHealth === "warning" ? "bg-amber-500/20 text-amber-700 dark:text-amber-300 font-bold shadow-2xs" : "text-slate-500 hover:text-amber-600"
                }`}
              >
                <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                {t("partner.filter_warning", { count: data?.summary?.status_counts?.warning || 0, defaultValue: `Warnung (${data?.summary?.status_counts?.warning || 0})` })}
              </button>
              <button
                type="button"
                onClick={() => setFilterHealth("error")}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-lg transition cursor-pointer ${
                  filterHealth === "error" ? "bg-rose-500/20 text-rose-700 dark:text-rose-300 font-bold shadow-2xs" : "text-slate-500 hover:text-rose-600"
                }`}
              >
                <XCircle className="w-3.5 h-3.5 text-rose-500" />
                {t("partner.filter_error", { count: data?.summary?.status_counts?.error || 0, defaultValue: `Störung (${data?.summary?.status_counts?.error || 0})` })}
              </button>
            </div>

            {/* View Mode Switcher */}
            <div className="flex items-center bg-slate-100 dark:bg-slate-800/60 p-1 rounded-xl">
              <button
                type="button"
                onClick={() => setViewMode("table")}
                className={`p-1.5 rounded-lg transition cursor-pointer ${viewMode === "table" ? "bg-white dark:bg-slate-900 text-sky-600 dark:text-sky-400 shadow-2xs" : "text-slate-400 hover:text-slate-600"}`}
                title={t("partner.view_table", "Tabelle")}
              >
                <TableIcon className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => setViewMode("grid")}
                className={`p-1.5 rounded-lg transition cursor-pointer ${viewMode === "grid" ? "bg-white dark:bg-slate-900 text-sky-600 dark:text-sky-400 shadow-2xs" : "text-slate-400 hover:text-slate-600"}`}
                title={t("partner.view_grid", "Kacheln")}
              >
                <LayoutGrid className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => setViewMode("map")}
                className={`p-1.5 rounded-lg transition cursor-pointer ${viewMode === "map" ? "bg-white dark:bg-slate-900 text-sky-600 dark:text-sky-400 shadow-2xs" : "text-slate-400 hover:text-slate-600"}`}
                title={t("partner.view_map", "Karten-Radar & Route")}
              >
                <MapIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* ======================================================== */}
        {/* VIEW 1: FLOTTEN-TABELLE */}
        {/* ======================================================== */}
        {viewMode === "table" ? (
          <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-3xl overflow-hidden shadow-xs">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-800 text-xs uppercase font-bold text-slate-500 dark:text-slate-400 bg-slate-50/70 dark:bg-slate-950/40">
                    <th className="py-3.5 px-5">{t("partner.th_status", "Status")}</th>
                    <th className="py-3.5 px-5">{t("partner.th_asset_customer", "Anlage & Kunde")}</th>
                    <th className="py-3.5 px-5">{t("partner.th_location", "Standort")}</th>
                    <th className="py-3.5 px-5">{t("partner.th_components", "Komponenten & Speicher")}</th>
                    <th className="py-3.5 px-5">{t("partner.th_live_power", "Live-Telemetrie")}</th>
                    <th className="py-3.5 px-5 text-right">{t("partner.th_actions", "Aktionen")}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 text-xs sm:text-sm">
                  {filteredHomes.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-12 text-center text-slate-400">
                        {t("partner.no_assets_found", "Keine Kundenanlagen gefunden.")}
                      </td>
                    </tr>
                  ) : (
                    filteredHomes.map((home) => (
                      <tr key={home.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition">
                        <td className="py-3.5 px-5">
                          {home.health === "ok" && (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 border border-emerald-500/20 text-emerald-700 dark:text-emerald-400">
                              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                              {t("partner.badge_online", "Online")}
                            </span>
                          )}
                          {home.health === "warning" && (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/10 border border-amber-500/20 text-amber-700 dark:text-amber-400">
                              <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                              {t("partner.badge_check", "Prüfen")}
                            </span>
                          )}
                          {home.health === "error" && (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/10 border border-rose-500/20 text-rose-700 dark:text-rose-400">
                              <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>
                              {t("partner.badge_error", "Störung")}
                            </span>
                          )}
                        </td>
                        <td className="py-3.5 px-5">
                          <div className="font-bold text-slate-900 dark:text-white">{home.name}</div>
                          <div className="text-xs text-slate-500 dark:text-slate-400">{home.customer_name} • {home.customer_email}</div>
                        </td>
                        <td className="py-3.5 px-5 text-slate-600 dark:text-slate-300 text-xs">
                          {home.address || t("partner.no_address", "Keine Adresse")}
                        </td>
                        <td className="py-3.5 px-5">
                          <div className="flex flex-wrap items-center gap-1.5 text-xs">
                            <span className="px-2 py-0.5 bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800/40 rounded-md font-semibold">
                              ☀️ {home.inverters_count || 1} WR
                            </span>
                            <span className="px-2 py-0.5 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/40 rounded-md font-semibold">
                              🔋 {home.battery_capacity_kwh || 10} kWh ({home.battery_soc_pct || 74}% SoC)
                            </span>
                            <span className="px-2 py-0.5 bg-sky-50 dark:bg-sky-950/40 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-800/40 rounded-md font-semibold">
                              ⚡ {home.wallboxes_count || 1} WB
                            </span>
                            <span className="px-2 py-0.5 bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-300 border border-teal-200 dark:border-teal-800/40 rounded-md text-[11px] font-bold">
                              🛡️ § 14a Bereit
                            </span>
                          </div>
                        </td>
                        <td className="py-3.5 px-5">
                          <div className="text-xs space-y-0.5 font-mono font-semibold">
                            <div className="text-amber-600 dark:text-amber-400">☀️ {home.pv_power_w ?? 0} W Erzeugung</div>
                            <div className="text-sky-600 dark:text-sky-400">⚡ {home.wallbox_power_w ?? 0} W Laden</div>
                          </div>
                        </td>
                        <td className="py-3.5 px-5 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <Link
                              to={`/app/energy?home_id=${home.id}&partner_view=true&home_name=${encodeURIComponent(home.name)}&customer=${encodeURIComponent(home.customer_name || "")}`}
                              className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-bold rounded-lg border border-slate-200 dark:border-slate-700 transition flex items-center gap-1 cursor-pointer"
                              title={t("partner.btn_view_customer_ems", "Live-Ansicht")}
                            >
                              <Eye className="w-3.5 h-3.5" />
                              <span className="hidden sm:inline">{t("partner.btn_view_customer_ems", "Live-Ansicht")}</span>
                            </Link>
                            <button
                              type="button"
                              onClick={() => setProtocolAsset(home)}
                              className="px-2.5 py-1.5 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/40 dark:hover:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 text-xs font-bold rounded-lg border border-indigo-200 dark:border-indigo-800/60 transition flex items-center gap-1 cursor-pointer"
                              title={t("partner.btn_handover_protocol", "IBN-Protokoll")}
                            >
                              <FileText className="w-3.5 h-3.5" />
                              <span className="hidden sm:inline">{t("partner.btn_handover_protocol", "IBN-Protokoll")}</span>
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                setSelectedAsset(home);
                                handleRunDiagnostics(home.id, "ping");
                              }}
                              className="px-3 py-1.5 bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold rounded-lg transition flex items-center gap-1 cursor-pointer shadow-2xs"
                            >
                              <Wrench className="w-3.5 h-3.5" />
                              <span>{t("partner.btn_remote_maintenance", "Fernwartung")}</span>
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        ) : viewMode === "grid" ? (
          /* ======================================================== */
          /* VIEW 2: FLOTTEN-KACHELN (GRID VIEW) */
          /* ======================================================== */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredHomes.map((home) => (
              <div key={home.id} className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 shadow-xs flex flex-col justify-between space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">🏡</span>
                      <h4 className="font-bold text-slate-900 dark:text-white truncate">{home.name}</h4>
                    </div>
                    {home.health === "ok" ? (
                      <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">Online</span>
                    ) : (
                      <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-500/10 text-rose-600 border border-rose-500/20">Störung</span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500">{home.customer_name} • {home.address}</p>

                  {/* Battery SoC Progress Bar */}
                  <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-2xl border border-slate-100 dark:border-slate-800 space-y-1.5">
                    <div className="flex items-center justify-between text-xs font-bold">
                      <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                        <Battery className="w-3.5 h-3.5" />
                        Heimspeicher ({home.battery_capacity_kwh || 10} kWh)
                      </span>
                      <span>{home.battery_soc_pct || 74}% SoC</span>
                    </div>
                    <div className="w-full bg-slate-200 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(100, Math.max(5, home.battery_soc_pct || 74))}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Telemetrie Badges */}
                  <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                    <div className="p-2.5 rounded-xl bg-amber-500/5 border border-amber-500/20">
                      <div className="text-[10px] text-amber-600 uppercase font-bold">PV-Leistung</div>
                      <div className="text-sm font-black text-amber-700 dark:text-amber-300">☀️ {home.pv_power_w ?? 0} W</div>
                    </div>
                    <div className="p-2.5 rounded-xl bg-sky-500/5 border border-sky-500/20">
                      <div className="text-[10px] text-sky-600 uppercase font-bold">Wallbox</div>
                      <div className="text-sm font-black text-sky-700 dark:text-sky-300">⚡ {home.wallbox_power_w ?? 0} W</div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-1.5 pt-2 border-t border-slate-100 dark:border-slate-800">
                  <Link
                    to={`/app/energy?home_id=${home.id}&partner_view=true&home_name=${encodeURIComponent(home.name)}&customer=${encodeURIComponent(home.customer_name || "")}`}
                    className="py-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-bold text-center border border-slate-200 dark:border-slate-700 transition flex items-center justify-center gap-1"
                    title={t("partner.btn_view_customer_ems", "Live-Ansicht")}
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">EMS</span>
                  </Link>
                  <button
                    type="button"
                    onClick={() => setProtocolAsset(home)}
                    className="py-2 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/40 dark:hover:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/60 rounded-xl text-xs font-bold text-center flex items-center justify-center gap-1 transition cursor-pointer"
                    title={t("partner.btn_handover_protocol", "IBN-Protokoll")}
                  >
                    <FileText className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">Protokoll</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedAsset(home);
                      handleRunDiagnostics(home.id, "ping");
                    }}
                    className="py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold text-center transition cursor-pointer flex items-center justify-center gap-1 shadow-2xs"
                    title={t("partner.btn_remote_maintenance", "Fernwartung")}
                  >
                    <Wrench className="w-3.5 h-3.5" />
                    <span>Wartung</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* ======================================================== */
          /* VIEW 3: FLOTTEN-RADAR & ROUTENPLANUNG (MAP VIEW) */
          /* ======================================================== */
          <PartnerFleetMap
            homes={filteredHomes}
            onSelectAssetForDiagnostics={(h) => {
              setSelectedAsset(h);
              handleRunDiagnostics(h.id, "ping");
            }}
            onOpenProtocol={(h) => setProtocolAsset(h)}
          />
        )}

        {/* ======================================================== */}
        {/* FERNWARTUNGS- & DIAGNOSE-MODAL */}
        {/* ======================================================== */}
        {selectedAsset && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-fade-in" onClick={() => setSelectedAsset(null)}>
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-xl w-full p-6 space-y-6 shadow-2xl overflow-hidden" onClick={(e) => e.stopPropagation()}>
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-xl bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/20">
                      <Wrench className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-black text-slate-900 dark:text-white">
                      {t("partner.modal_remote_title", { name: selectedAsset.name, defaultValue: `Fernwartung: ${selectedAsset.name}` })}
                    </h3>
                  </div>
                  <p className="text-xs text-slate-500">
                    {t("partner.modal_customer_label", { name: selectedAsset.customer_name, defaultValue: `Kunde: ${selectedAsset.customer_name}` })} • {selectedAsset.address}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedAsset(null)}
                  className="p-1.5 text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>

              {/* Action Grid (6 Fernwartungs-Aktionen) */}
              <div className="space-y-2.5">
                <div className="text-xs font-bold text-slate-700 dark:text-slate-300">{t("partner.action_execute_label", "Wartungs- & Diagnose-Aktion ausführen:")}</div>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => handleRunDiagnostics(selectedAsset.id, "ping")}
                    disabled={diagLoading}
                    className="p-3 bg-slate-50 dark:bg-slate-800/60 hover:bg-sky-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 rounded-2xl text-left transition cursor-pointer"
                  >
                    <div className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                      <Wifi className="w-3.5 h-3.5 text-sky-500" />
                      {t("partner.action_ping_title", "Live-Ping & Status")}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{t("partner.action_ping_desc", "Gateway & Latenz")}</div>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleRunDiagnostics(selectedAsset.id, "ocpp_trigger")}
                    disabled={diagLoading}
                    className="p-3 bg-slate-50 dark:bg-slate-800/60 hover:bg-sky-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 rounded-2xl text-left transition cursor-pointer"
                  >
                    <div className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                      <RefreshCw className="w-3.5 h-3.5 text-indigo-500" />
                      {t("partner.action_ocpp_title", "OCPP Reset")}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{t("partner.action_ocpp_desc", "Hard/Soft Reboot")}</div>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleRunDiagnostics(selectedAsset.id, "steuve_dim")}
                    disabled={diagLoading}
                    className="p-3 bg-slate-50 dark:bg-slate-800/60 hover:bg-sky-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 rounded-2xl text-left transition cursor-pointer"
                  >
                    <div className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5 text-teal-500" />
                      {t("partner.action_steuve_title", "§ 14a Dimm-Test")}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{t("partner.action_steuve_desc", "4,2 kW Not-Drosselung")}</div>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleRunDiagnostics(selectedAsset.id, "bus_scan")}
                    disabled={diagLoading}
                    className="p-3 bg-slate-50 dark:bg-slate-800/60 hover:bg-sky-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 rounded-2xl text-left transition cursor-pointer"
                  >
                    <div className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                      <Cpu className="w-3.5 h-3.5 text-amber-500" />
                      {t("partner.action_bus_title", "Modbus Scan")}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{t("partner.action_bus_desc", "Zähler & BMS Bus")}</div>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleRunDiagnostics(selectedAsset.id, "inverter_reconnect")}
                    disabled={diagLoading}
                    className="p-3 bg-slate-50 dark:bg-slate-800/60 hover:bg-sky-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 rounded-2xl text-left transition cursor-pointer"
                  >
                    <div className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                      <Sun className="w-3.5 h-3.5 text-amber-500" />
                      {t("partner.action_inverter_title", "Inverter Sync")}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{t("partner.action_inverter_desc", "Wechselrichter Sync")}</div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setProtocolAsset(selectedAsset)}
                    className="p-3 bg-indigo-50 dark:bg-indigo-950/40 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 border border-indigo-200 dark:border-indigo-800 rounded-2xl text-left transition cursor-pointer"
                  >
                    <div className="text-xs font-bold text-indigo-700 dark:text-indigo-300 flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5" />
                      {t("partner.action_protocol_title", "IBN-Protokoll")}
                    </div>
                    <div className="text-[10px] text-indigo-600/70 dark:text-indigo-400 mt-0.5">{t("partner.action_protocol_desc", "PDF Übergabenachweis")}</div>
                  </button>
                </div>
              </div>

              {/* Diagnose-Konsole */}
              <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 font-mono text-xs space-y-2 text-slate-200 shadow-inner">
                <div className="text-slate-400 flex items-center justify-between border-b border-slate-800 pb-2">
                  <span className="flex items-center gap-1.5 font-bold">
                    <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
                    {t("partner.console_title", "Diagnose-Konsole & System-Log")}
                  </span>
                  {diagLoading && <RefreshCw className="w-3.5 h-3.5 animate-spin text-sky-400" />}
                </div>
                {diagResult ? (
                  <div className="space-y-1.5 pt-1">
                    <div className="text-emerald-400 font-bold">✓ {diagResult.message}</div>
                    {diagResult.status && (
                      <div className="text-slate-300">Status: <span className="text-sky-300 font-semibold">{diagResult.status}</span></div>
                    )}
                    {diagResult.active_nodes && (
                      <div className="text-slate-400">Gefundene Knoten: {diagResult.active_nodes.join(", ")}</div>
                    )}
                    {diagResult.grid_compliance && (
                      <div className="text-teal-300 font-semibold">⚡ {diagResult.grid_compliance}</div>
                    )}
                  </div>
                ) : (
                  <div className="text-slate-600 py-3 text-center">{t("partner.console_waiting", "Wähle oben eine Diagnose-Aktion aus…")}</div>
                )}
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setSelectedAsset(null)}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-bold rounded-xl transition cursor-pointer"
                >
                  {t("common.close", "Schließen")}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* SCHNELL-INBETRIEBNAHME MODAL */}
        {/* ======================================================== */}
        {showOnboardModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-fade-in" onClick={() => setShowOnboardModal(false)}>
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-lg w-full p-6 space-y-5 shadow-2xl" onClick={(e) => e.stopPropagation()}>
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <div className="p-2 bg-sky-500/10 rounded-xl text-sky-600 dark:text-sky-400 border border-sky-500/20">
                      <PlusCircle className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-black text-slate-900 dark:text-white">{t("partner.onboard_modal_title", "1-Klick Kunden-Inbetriebnahme")}</h3>
                  </div>
                  <p className="text-xs text-slate-500">
                    {t("partner.onboard_modal_desc", "Legen Sie eine neue Kundenanlage an. Die Wartungsfreigabe für Ihren Fachbetrieb wird sofort aktiviert.")}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setShowOnboardModal(false)}
                  className="p-1.5 text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleQuickOnboardSubmit} className="space-y-4">
                {onboardError && (
                  <div className="p-3 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-600 dark:text-rose-300 text-xs flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{onboardError}</span>
                  </div>
                )}

                {onboardSuccess && (
                  <div className="p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-700 dark:text-emerald-300 text-xs flex items-center gap-2">
                    <Check className="w-4 h-4 shrink-0" />
                    <span>{onboardSuccess}</span>
                  </div>
                )}

                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">{t("partner.onboard_email_label", "Kunden E-Mail-Adresse *")}</label>
                  <input
                    type="email"
                    required
                    placeholder="kunde@musterhaus.de"
                    value={onboardForm.customer_email}
                    onChange={(e) => setOnboardForm({ ...onboardForm, customer_email: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-slate-100 focus:outline-hidden focus:ring-2 focus:ring-sky-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">{t("partner.onboard_home_name_label", "Bezeichnung der Anlage *")}</label>
                  <input
                    type="text"
                    required
                    placeholder="z.B. Einfamilienhaus Schmidt"
                    value={onboardForm.home_name}
                    onChange={(e) => setOnboardForm({ ...onboardForm, home_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-slate-100 focus:outline-hidden focus:ring-2 focus:ring-sky-500"
                  />
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="col-span-2">
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">{t("partner.onboard_street_label", "Straße & Hausnummer")}</label>
                    <input
                      type="text"
                      placeholder="Sonnenallee 12"
                      value={onboardForm.street}
                      onChange={(e) => setOnboardForm({ ...onboardForm, street: e.target.value })}
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-slate-100 focus:outline-hidden focus:ring-2 focus:ring-sky-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">{t("partner.onboard_zip_label", "PLZ")}</label>
                    <input
                      type="text"
                      placeholder="80331"
                      value={onboardForm.postal_code}
                      onChange={(e) => setOnboardForm({ ...onboardForm, postal_code: e.target.value })}
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-slate-100 focus:outline-hidden focus:ring-2 focus:ring-sky-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">{t("partner.onboard_city_label", "Ort")}</label>
                    <input
                      type="text"
                      placeholder="München"
                      value={onboardForm.city}
                      onChange={(e) => setOnboardForm({ ...onboardForm, city: e.target.value })}
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-slate-100 focus:outline-hidden focus:ring-2 focus:ring-sky-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">{t("partner.onboard_pv_label", "PV-Leistung (kWp)")}</label>
                    <input
                      type="number"
                      step="0.5"
                      value={onboardForm.pv_capacity_kwp}
                      onChange={(e) => setOnboardForm({ ...onboardForm, pv_capacity_kwp: Number(e.target.value) })}
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-slate-100 focus:outline-hidden focus:ring-2 focus:ring-sky-500 no-spinners"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">{t("partner.onboard_battery_label", "Speicher (kWh)")}</label>
                    <input
                      type="number"
                      step="0.5"
                      value={onboardForm.battery_capacity_kwh}
                      onChange={(e) => setOnboardForm({ ...onboardForm, battery_capacity_kwh: Number(e.target.value) })}
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-xs sm:text-sm text-slate-900 dark:text-slate-100 focus:outline-hidden focus:ring-2 focus:ring-sky-500 no-spinners"
                    />
                  </div>
                </div>

                <div className="flex justify-end gap-2.5 pt-3 border-t border-slate-100 dark:border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowOnboardModal(false)}
                    className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-bold rounded-xl transition cursor-pointer"
                  >
                    {t("common.cancel", "Abbrechen")}
                  </button>
                  <button
                    type="submit"
                    disabled={onboardSubmitting}
                    className="flex items-center gap-2 px-5 py-2.5 bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold rounded-xl shadow-xs transition cursor-pointer"
                  >
                    {onboardSubmitting && <RefreshCw className="w-4 h-4 animate-spin" />}
                    <span>{t("partner.onboard_submit_btn", "Anlage turnkey anlegen")}</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* ZÄHLER-STICKER & MIETER-ONBOARDING GENERATOR MODAL */}
        <MeterQrStickerGeneratorModal
          isOpen={showStickerModal}
          onClose={() => setShowStickerModal(false)}
          communityName={data?.partner_company?.name || "Kundenanlagen"}
        />

        {/* DIGITALES IBN- & ÜBERGABEPROTOKOLL MODAL */}
        <PartnerHandoverProtocolModal
          isOpen={Boolean(protocolAsset)}
          onClose={() => setProtocolAsset(null)}
          asset={protocolAsset}
          partnerCompany={data?.partner_company}
        />

      </div>
    </div>
  );
}
