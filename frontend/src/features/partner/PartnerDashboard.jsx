import useModalDismiss from "../../hooks/useModalDismiss";
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../api/client";
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
  BatteryCharging,
  Cpu,
  ArrowUpRight,
  Send,
  Building,
  Check,
  AlertCircle
} from "lucide-react";

export default function PartnerDashboard() {
  const { t } = useTranslation();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterHealth, setFilterHealth] = useState("all");
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [diagLoading, setDiagLoading] = useState(false);
  const [diagResult, setDiagResult] = useState(null);

  // Quick Onboard Modal State
  const [showOnboardModal, setShowOnboardModal] = useState(false);
  useModalDismiss(Boolean(selectedAsset), () => setSelectedAsset(null));
  useModalDismiss(showOnboardModal, () => setShowOnboardModal(false));
  const [onboardForm, setOnboardForm] = useState({
    customer_email: "",
    home_name: "",
    street: "",
    city: "",
    postal_code: "",
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
      setOnboardForm({ customer_email: "", home_name: "", street: "", city: "", postal_code: "" });
      fetchFleet();
    } catch (err) {
      setOnboardError(err?.message || "Inbetriebnahme fehlgeschlagen.");
    } finally {
      setOnboardSubmitting(false);
    }
  };

  if (loading && !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        <div className="flex items-center gap-3">
          <RefreshCw className="w-6 h-6 animate-spin text-sky-400" />
          <span className="text-lg font-medium">{t("partner.loading", "Lade Installateurs- & Partner-Flotte…")}</span>
        </div>
      </div>
    );
  }

  const filteredHomes = (data?.homes || []).filter((h) => {
    const matchesSearch =
      h.name.toLowerCase().includes(search.toLowerCase()) ||
      h.customer_name.toLowerCase().includes(search.toLowerCase()) ||
      h.customer_email.toLowerCase().includes(search.toLowerCase()) ||
      h.address.toLowerCase().includes(search.toLowerCase());
    const matchesHealth = filterHealth === "all" || h.health === filterHealth;
    return matchesSearch && matchesHealth;
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/80 backdrop-blur border border-slate-800 p-6 rounded-3xl shadow-2xl">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-sky-500/10 border border-sky-500/30 rounded-2xl text-sky-400">
                <Wrench className="w-6 h-6" />
              </div>
              <h1 className="text-2xl md:text-3xl font-bold tracking-tight">
                {data?.partner_company?.name || t("partner.portal_title", "Installateurs- & Partner-Portal")}
              </h1>
              <span className="px-3 py-1 text-xs font-semibold uppercase tracking-wider rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300">
                {data?.partner_company?.tier_display || t("partner.tier_default", "Fachpartner")}
              </span>
            </div>
            <p className="text-sm text-slate-400">
              {t("partner.subtitle", "Zentrale Flotten-Telemetrie, Störungsampel & 1-Klick Fernwartung betreuter Kundenanlagen.")}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowOnboardModal(true)}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-medium text-sm rounded-xl shadow-lg shadow-sky-500/20 transition duration-200"
            >
              <PlusCircle className="w-4 h-4" />
              <span>{t("partner.quick_onboard_btn", "Schnell-Inbetriebnahme")}</span>
            </button>
            <button
              onClick={fetchFleet}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-slate-300 transition"
              title={t("common.refresh", "Aktualisieren")}
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-2xl flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl text-blue-400">
              <Building className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">{data?.summary?.total_homes || 0}</div>
              <div className="text-xs text-slate-400">{t("partner.kpi_managed_homes", "Betreute Liegenschaften")}</div>
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-2xl flex items-center gap-4">
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-400">
              <Sun className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">{data?.summary?.total_pv_power_kw || 0} kW</div>
              <div className="text-xs text-slate-400">{t("partner.kpi_pv_power", "Aktive PV-Leistung")}</div>
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-2xl flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">{data?.summary?.total_wallbox_power_kw || 0} kW</div>
              <div className="text-xs text-slate-400">{t("partner.kpi_wallbox_power", "Wallbox Ladeleistung")}</div>
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-2xl flex items-center gap-4">
            <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">{data?.summary?.active_alerts_count || 0}</div>
              <div className="text-xs text-slate-400">{t("partner.kpi_alerts", "Aktive Störungen / Warnungen")}</div>
            </div>
          </div>
        </div>

        {/* Filter & Search */}
        <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder={t("partner.search_placeholder", "Suche nach Kunde, Anlage, PLZ oder Adresse…")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-900/80 border border-slate-800 pl-10 pr-4 py-2.5 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
            />
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            <button
              onClick={() => setFilterHealth("all")}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition ${
                filterHealth === "all" ? "bg-slate-700 text-white" : "bg-slate-900/80 text-slate-400 hover:text-slate-200"
              }`}
            >
              {t("partner.filter_all", { count: data?.summary?.total_homes || 0, defaultValue: `Alle (${data?.summary?.total_homes || 0})` })}
            </button>
            <button
              onClick={() => setFilterHealth("ok")}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition ${
                filterHealth === "ok" ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30" : "bg-slate-900/80 text-slate-400 hover:text-emerald-400"
              }`}
            >
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              {t("partner.filter_ok", { count: data?.summary?.status_counts?.ok || 0, defaultValue: `Optimal (${data?.summary?.status_counts?.ok || 0})` })}
            </button>
            <button
              onClick={() => setFilterHealth("warning")}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition ${
                filterHealth === "warning" ? "bg-amber-500/20 text-amber-300 border border-amber-500/30" : "bg-slate-900/80 text-slate-400 hover:text-amber-400"
              }`}
            >
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              {t("partner.filter_warning", { count: data?.summary?.status_counts?.warning || 0, defaultValue: `Warnung (${data?.summary?.status_counts?.warning || 0})` })}
            </button>
            <button
              onClick={() => setFilterHealth("error")}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition ${
                filterHealth === "error" ? "bg-rose-500/20 text-rose-300 border border-rose-500/30" : "bg-slate-900/80 text-slate-400 hover:text-rose-400"
              }`}
            >
              <XCircle className="w-3.5 h-3.5 text-rose-400" />
              {t("partner.filter_error", { count: data?.summary?.status_counts?.error || 0, defaultValue: `Störung (${data?.summary?.status_counts?.error || 0})` })}
            </button>
          </div>
        </div>

        {/* Flotten-Tabelle */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-xs uppercase tracking-wider text-slate-400 bg-slate-950/40">
                  <th className="py-4 px-6">{t("partner.th_status", "Status")}</th>
                  <th className="py-4 px-6">{t("partner.th_asset_customer", "Anlage & Kunde")}</th>
                  <th className="py-4 px-6">{t("partner.th_location", "Standort")}</th>
                  <th className="py-4 px-6">{t("partner.th_components", "Komponenten")}</th>
                  <th className="py-4 px-6">{t("partner.th_live_power", "Live-Leistung")}</th>
                  <th className="py-4 px-6 text-right">{t("partner.th_actions", "Aktionen")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-sm">
                {filteredHomes.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-slate-500">
                      {t("partner.no_assets_found", "Keine Kundenanlagen gefunden.")}
                    </td>
                  </tr>
                ) : (
                  filteredHomes.map((home) => (
                    <tr key={home.id} className="hover:bg-slate-800/30 transition">
                      <td className="py-4 px-6">
                        {home.health === "ok" && (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                            {t("partner.badge_online", "Online")}
                          </span>
                        )}
                        {home.health === "warning" && (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 border border-amber-500/20 text-amber-400">
                            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                            {t("partner.badge_check", "Prüfen")}
                          </span>
                        )}
                        {home.health === "error" && (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-rose-500/10 border border-rose-500/20 text-rose-400">
                            <span className="w-2 h-2 rounded-full bg-rose-400 animate-ping"></span>
                            {t("partner.badge_error", "Störung")}
                          </span>
                        )}
                      </td>
                      <td className="py-4 px-6">
                        <div className="font-semibold text-slate-100">{home.name}</div>
                        <div className="text-xs text-slate-400">{home.customer_name} ({home.customer_email})</div>
                      </td>
                      <td className="py-4 px-6 text-slate-300 text-xs">
                        {home.address || t("partner.no_address", "Keine Adresse")}
                      </td>
                      <td className="py-4 px-6">
                        <div className="flex items-center gap-2 text-xs text-slate-300">
                          <span className="px-2 py-0.5 bg-slate-800 rounded-md">⚡ {home.wallboxes_count} WB</span>
                          <span className="px-2 py-0.5 bg-slate-800 rounded-md">☀️ {home.inverters_count} WR</span>
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        <div className="text-xs space-y-0.5">
                          <div className="text-amber-400">☀️ {home.pv_power_w} W</div>
                          <div className="text-sky-400">⚡ {home.wallbox_power_w} W</div>
                        </div>
                      </td>
                      <td className="py-4 px-6 text-right">
                        <button
                          onClick={() => {
                            setSelectedAsset(home);
                            handleRunDiagnostics(home.id, "ping");
                          }}
                          className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-sky-400 hover:text-sky-300 text-xs font-medium rounded-lg border border-slate-700 transition"
                        >
                          {t("partner.btn_remote_maintenance", "Fernwartung")}
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Fernwartungs-Modal */}
        {selectedAsset && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm" onClick={() => { setSelectedAsset(null); setShowOnboardModal(false); }}>
            <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 space-y-6 shadow-2xl animate-in fade-in zoom-in duration-150" onClick={(e) => e.stopPropagation()}>
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-sky-400" />
                    <h3 className="text-lg font-bold">{t("partner.modal_remote_title", { name: selectedAsset.name, defaultValue: `Fernwartung: ${selectedAsset.name}` })}</h3>
                  </div>
                  <p className="text-xs text-slate-400">{t("partner.modal_customer_label", { name: selectedAsset.customer_name, defaultValue: `Kunde: ${selectedAsset.customer_name}` })}</p>
                </div>
                <button
                  onClick={() => setSelectedAsset(null)}
                  className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-3">
                <div className="text-xs font-medium text-slate-400">{t("partner.action_execute_label", "Wartungs-Aktion ausführen:")}</div>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => handleRunDiagnostics(selectedAsset.id, "ping")}
                    disabled={diagLoading}
                    className="p-3 bg-slate-800/80 hover:bg-slate-700 border border-slate-700 rounded-xl text-left transition"
                  >
                    <div className="text-xs font-semibold text-slate-200">{t("partner.action_ping_title", "Live-Ping & Status")}</div>
                    <div className="text-[11px] text-slate-400">{t("partner.action_ping_desc", "Verbindung prüfen")}</div>
                  </button>
                  <button
                    onClick={() => handleRunDiagnostics(selectedAsset.id, "ocpp_trigger")}
                    disabled={diagLoading}
                    className="p-3 bg-slate-800/80 hover:bg-slate-700 border border-slate-700 rounded-xl text-left transition"
                  >
                    <div className="text-xs font-semibold text-slate-200">{t("partner.action_ocpp_title", "OCPP Reset / Trigger")}</div>
                    <div className="text-[11px] text-slate-400">{t("partner.action_ocpp_desc", "Hard/Soft Reboot")}</div>
                  </button>
                </div>
              </div>

              {/* Diagnose-Ergebnis */}
              <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 font-mono text-xs space-y-2">
                <div className="text-slate-400 flex items-center justify-between">
                  <span>{t("partner.console_title", "Diagnose-Konsole")}</span>
                  {diagLoading && <RefreshCw className="w-3.5 h-3.5 animate-spin text-sky-400" />}
                </div>
                {diagResult ? (
                  <div className="space-y-1">
                    <div className="text-emerald-400">✓ {diagResult.message}</div>
                    {diagResult.asset_type && (
                      <div className="text-slate-400">{t("partner.console_asset_type", { type: diagResult.asset_type, defaultValue: `Asset-Typ: ${diagResult.asset_type}` })}</div>
                    )}
                    {diagResult.status && (
                      <div className="text-slate-300">{t("partner.console_ocpp_status", { status: diagResult.status, code: diagResult.error_code, defaultValue: `OCPP-Status: ${diagResult.status} (Fehlercode: ${diagResult.error_code})` })}</div>
                    )}
                  </div>
                ) : (
                  <div className="text-slate-600">{t("partner.console_waiting", "Warte auf Diagnose-Ausführung…")}</div>
                )}
              </div>

              <div className="flex justify-end">
                <button
                  onClick={() => setSelectedAsset(null)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-xl transition"
                >
                  {t("common.close", "Schließen")}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Quick Onboarding Modal */}
        {showOnboardModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 space-y-6 shadow-2xl animate-in fade-in zoom-in duration-150">
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <PlusCircle className="w-5 h-5 text-sky-400" />
                    <h3 className="text-lg font-bold">{t("partner.onboard_modal_title", "1-Klick Kunden-Inbetriebnahme")}</h3>
                  </div>
                  <p className="text-xs text-slate-400">
                    {t("partner.onboard_modal_desc", "Legen Sie eine neue Kundenanlage an. Die Wartungsfreigabe für Ihren Betrieb wird sofort aktiviert.")}
                  </p>
                </div>
                <button
                  onClick={() => setShowOnboardModal(false)}
                  className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleQuickOnboardSubmit} className="space-y-4">
                {onboardError && (
                  <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{onboardError}</span>
                  </div>
                )}

                {onboardSuccess && (
                  <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
                    <Check className="w-4 h-4 flex-shrink-0" />
                    <span>{onboardSuccess}</span>
                  </div>
                )}

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">{t("partner.onboard_email_label", "Kunden E-Mail-Adresse *")}</label>
                  <input
                    type="email"
                    required
                    placeholder="kunde@musterhaus.de"
                    value={onboardForm.customer_email}
                    onChange={(e) => setOnboardForm({ ...onboardForm, customer_email: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 px-3.5 py-2 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">{t("partner.onboard_home_name_label", "Bezeichnung der Anlage *")}</label>
                  <input
                    type="text"
                    required
                    placeholder="z.B. Einfamilienhaus Schmidt"
                    value={onboardForm.home_name}
                    onChange={(e) => setOnboardForm({ ...onboardForm, home_name: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 px-3.5 py-2 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                  />
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="col-span-2">
                    <label className="block text-xs font-semibold text-slate-300 mb-1">{t("partner.onboard_street_label", "Straße & Hausnummer")}</label>
                    <input
                      type="text"
                      placeholder="Sonnenallee 12"
                      value={onboardForm.street}
                      onChange={(e) => setOnboardForm({ ...onboardForm, street: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 px-3.5 py-2 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">{t("partner.onboard_zip_label", "PLZ")}</label>
                    <input
                      type="text"
                      placeholder="80331"
                      value={onboardForm.postal_code}
                      onChange={(e) => setOnboardForm({ ...onboardForm, postal_code: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 px-3.5 py-2 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">{t("partner.onboard_city_label", "Ort")}</label>
                  <input
                    type="text"
                    placeholder="München"
                    value={onboardForm.city}
                    onChange={(e) => setOnboardForm({ ...onboardForm, city: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 px-3.5 py-2 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                  />
                </div>

                <div className="flex justify-end gap-3 pt-3">
                  <button
                    type="button"
                    onClick={() => setShowOnboardModal(false)}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium rounded-xl transition"
                  >
                    {t("common.cancel", "Abbrechen")}
                  </button>
                  <button
                    type="submit"
                    disabled={onboardSubmitting}
                    className="flex items-center gap-2 px-5 py-2 bg-sky-500 hover:bg-sky-400 text-white text-sm font-semibold rounded-xl shadow-lg shadow-sky-500/20 transition"
                  >
                    {onboardSubmitting && <RefreshCw className="w-4 h-4 animate-spin" />}
                    <span>{t("partner.onboard_submit_btn", "Anlage anlegen")}</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

