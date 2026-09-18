import useModalDismiss from "../../hooks/useModalDismiss";
/*
# src/pages/admin/VppFleetAdminPage.jsx
# Virtuelles Kraftwerk (VPP) Plattform-Cockpit: Flotten-Flexibilität, Redispatch 2.0, § 14a Netzentgelt-Kalkulator, SMGW/CLS Inspector, Eichrecht-Prüfung & 80/20 Clearing Simulator
*/

import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../api/client";
import {
  Zap,
  BatteryCharging,
  Activity,
  ShieldAlert,
  RefreshCw,
  Play,
  CheckCircle2,
  Clock,
  DollarSign,
  Layers,
  Sliders,
  TrendingUp,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  Check,
  AlertTriangle,
  Radio,
  Calculator,
  ShieldCheck,
  Cpu,
  Key,
  FileCheck,
  Server,
} from "lucide-react";
import Card from "../../components/ui/Card";
import ReactECharts from "echarts-for-react";
import { useTheme } from "../../theme/ThemeContext";
import AdminPageHeader from "../../components/admin/AdminPageHeader";

export default function VppFleetAdminPage() {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState("flexibility"); // "flexibility" | "steuve" | "cls" | "eichrecht" | "simulator"
  const [selectedTso, setSelectedTso] = useState("all");
  const [testDispatchModal, setTestDispatchModal] = useState(false);
  useModalDismiss(testDispatchModal, () => setTestDispatchModal(false));
  const [dispatchForm, setDispatchForm] = useState({
    power_kw: 250,
    duration_minutes: 15,
    direction: "discharge", // "discharge" (pos) | "charge" (neg)
    tso_operator: "50hertz",
    reason: "Test-Dispatch (Admin Simulator)",
  });
  const [actionMsg, setActionMsg] = useState(null);

  // 1. Flexibility & Fleet Summary Query
  const fleetQuery = useQuery({
    queryKey: ["vpp-admin-fleet-summary", selectedTso],
    queryFn: () => {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      const queryParams = selectedTso !== "all" ? `?tso=${selectedTso}` : "";
      return apiFetch(`/api/vpp/summary/${queryParams}`, {
        headers: { Authorization: token ? `Bearer ${token}` : "" },
      });
    },
    refetchInterval: 10000,
  });

  // 2. Redispatch Schedule Query
  const scheduleQuery = useQuery({
    queryKey: ["vpp-admin-redispatch-schedule", selectedTso],
    queryFn: () => {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      const queryParams = selectedTso !== "all" ? `?tso=${selectedTso}` : "";
      return apiFetch(`/api/vpp/redispatch-schedule/${queryParams}`, {
        headers: { Authorization: token ? `Bearer ${token}` : "" },
      });
    },
    refetchInterval: 60000,
  });

  // 3. Dispatch Orders Query
  const dispatchesQuery = useQuery({
    queryKey: ["vpp-admin-dispatches"],
    queryFn: () => {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      return apiFetch("/api/vpp/dispatch/", {
        headers: { Authorization: token ? `Bearer ${token}` : "" },
      });
    },
    refetchInterval: 15000,
  });

  // 4. § 14a SteuVE Calculator State & Query
  const [calcInputs, setCalcInputs] = useState({
    wallbox_count: 2,
    heat_pump_count: 1,
    battery_count: 1,
    annual_consumption_kwh: 5500,
    grid_fee_ct_kwh: 9.5,
  });

  const calcQuery = useQuery({
    queryKey: ["vpp-steuve-calculator", calcInputs],
    queryFn: () => {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      const params = new URLSearchParams(calcInputs);
      return apiFetch(`/api/vpp/steuve/calculator/?${params.toString()}`, {
        headers: { Authorization: token ? `Bearer ${token}` : "" },
      });
    },
    enabled: activeTab === "steuve",
  });

  // 5. CLS Health Inspector Query
  const clsQuery = useQuery({
    queryKey: ["vpp-cls-inspector"],
    queryFn: () => {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      return apiFetch("/api/vpp/cls-inspector/", {
        headers: { Authorization: token ? `Bearer ${token}` : "" },
      });
    },
    refetchInterval: 15000,
    enabled: activeTab === "cls",
  });

  // 6. Eichrecht Verification Form & Mutation
  const [eichrechtForm, setEichrechtForm] = useState({
    meter_serial: "1EMH0012398471",
    obis_180_kwh: 2450.75,
    obis_280_kwh: 4890.20,
  });
  const [eichrechtResult, setEichrechtResult] = useState(null);

  const eichrechtMutation = useMutation({
    mutationFn: async (payload) => {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      return apiFetch("/api/vpp/eichrecht/verify/", {
        method: "POST",
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
    },
    onSuccess: (data) => {
      setEichrechtResult(data);
      setActionMsg({ type: "success", text: "Messwert-Signatur erfolgreich gem. PTB-A 50.7 geprüft & im Audit-Trail protokolliert!" });
    },
  });

  // 7. VPP Sandbox Simulator Form & Mutation
  const [simForm, setSimForm] = useState({
    product: "aFRR_positive",
    power_mw: 1.5,
    duration_hours: 1.0,
    clearing_price_eur_mwh: 145.0,
  });
  const [simResult, setSimResult] = useState(null);

  const simMutation = useMutation({
    mutationFn: async (payload) => {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      return apiFetch("/api/vpp/simulator/run/", {
        method: "POST",
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
    },
    onSuccess: (data) => {
      setSimResult(data);
      setActionMsg({ type: "success", text: `VPP Sandbox Clearing (${data.simulation_id}) erfolgreich ausgeführt!` });
      queryClient.invalidateQueries({ queryKey: ["admin-audit-logs"] });
    },
  });

  // Trigger Dispatch Mutation
  const triggerDispatchMutation = useMutation({
    mutationFn: async (payload) => {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      return apiFetch("/api/vpp/dispatch/", {
        method: "POST",
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      setActionMsg({ type: "success", text: "Dispatch-Befehl erfolgreich an den Pool übermittelt!" });
      queryClient.invalidateQueries({ queryKey: ["vpp-admin-dispatches"] });
      queryClient.invalidateQueries({ queryKey: ["vpp-admin-fleet-summary"] });
      setTestDispatchModal(false);
      setTimeout(() => setActionMsg(null), 5000);
    },
    onError: (err) => {
      setActionMsg({ type: "error", text: `Fehler beim Dispatch: ${err.message || "Unbekannter Fehler"}` });
    },
  });

  // Monthly Clearing Run Mutation
  const clearingMutation = useMutation({
    mutationFn: async () => {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");
      return apiFetch("/api/vpp/clearing/run/", {
        method: "POST",
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
          "Content-Type": "application/json",
        },
      });
    },
    onSuccess: (data) => {
      setActionMsg({
        type: "success",
        text: `Clearing erfolgreich abgeschlossen! Verarbeitete Statements: ${data?.statements_count || 0}`,
      });
      setTimeout(() => setActionMsg(null), 6000);
    },
    onError: (err) => {
      setActionMsg({ type: "error", text: `Clearing-Fehler: ${err.message || "Fehler"}` });
    },
  });

  const fleetData = fleetQuery.data || {
    summary: {
      total_connected_assets: 0,
      active_participating_assets: 0,
      total_available_positive_flex_kw: 0,
      total_available_negative_flex_kw: 0,
      average_reaction_time_seconds: 12.5,
    },
    battery_fleet: {
      total_batteries: 0,
      total_stored_energy_kwh: 0,
      total_capacity_kwh: 0,
      average_soc_pct: 0,
    },
    steuve_and_loads: {
      curtailable_power_kw: 0,
      total_heatpumps: 0,
      total_wallboxes: 0,
    },
  };

  const scheduleSlots = scheduleQuery.data?.schedule_slots || [];
  const dispatches = dispatchesQuery.data?.results || [];

  // ECharts 96-Viertelstunden-Fahrplan Option
  const scheduleChartOption = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis",
      backgroundColor: isDark ? "#0f172a" : "#ffffff",
      borderColor: isDark ? "#334155" : "#e2e8f0",
      textStyle: { color: isDark ? "#f8fafc" : "#0f172a", fontSize: 12 },
      formatter: (params) => {
        if (!params || !params.length) return "";
        const item = params[0];
        return `<div class="font-sans">
                    <div class="text-xs text-slate-400 font-mono">${item.axisValue} Uhr (PT15M)</div>
                    <div class="text-sm font-bold text-emerald-500 mt-1">Soll-Leistung: ${item.value} kW</div>
                </div>`;
      },
    },
    grid: { left: "3%", right: "3%", bottom: "5%", top: "8%", containLabel: true },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: scheduleSlots.map((s) => s.time_slot),
      axisLine: { lineStyle: { color: isDark ? "#334155" : "#cbd5e1" } },
      axisLabel: { color: isDark ? "#94a3b8" : "#64748b", fontSize: 10, interval: 7 },
    },
    yAxis: {
      type: "value",
      name: "kW",
      nameTextStyle: { color: isDark ? "#94a3b8" : "#64748b", fontSize: 10 },
      splitLine: { lineStyle: { color: isDark ? "#1e293b" : "#f1f5f9" } },
      axisLabel: { color: isDark ? "#94a3b8" : "#64748b", fontSize: 10 },
    },
    series: [
      {
        name: "Fahrplan-Leistung",
        type: "line",
        smooth: true,
        showSymbol: false,
        data: scheduleSlots.map((s) => s.planned_power_kw),
        itemStyle: { color: "#10b981" },
        lineStyle: { width: 3 },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(16, 185, 129, 0.35)" },
              { offset: 1, color: "rgba(16, 185, 129, 0.0)" },
            ],
          },
        },
      },
    ],
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* UNIFIED ADMIN HEADER */}
      <AdminPageHeader
        icon="⚡"
        iconBg="bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400"
        title={t("admin_vpp.title", "Virtuelles Kraftwerk (VPP) & Flexibilitäts-Zentrale")}
        subtitle={t("admin_vpp.subtitle", "Aggregation, Sekundärregelleistung (aFRR), Redispatch 2.0, § 14a EnWG & Eichrecht")}
        badge="BNetzA & PTB-A 50.7 Konform"
        badgeColor="emerald"
        manualLink="/app/help/admin-vpp-flex-aggregator-guide"
        manualLabel={t("admin_vpp.btn_manual", "Handbuch (VPP)")}
        actions={
          <div className="flex items-center gap-2">
            <Link
              to="/app/admin/audit-logs"
              className="px-3.5 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition flex items-center gap-1.5 cursor-pointer shadow-xs"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
              <span>Audit Trail</span>
            </Link>

            <button
              onClick={() => {
                fleetQuery.refetch();
                dispatchesQuery.refetch();
                scheduleQuery.refetch();
              }}
              className="px-3.5 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition flex items-center gap-1.5 cursor-pointer shadow-xs"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${fleetQuery.isFetching ? "animate-spin" : ""}`} />
              <span>{t("common.refresh", "Aktualisieren")}</span>
            </button>

            <button
              onClick={() => clearingMutation.mutate()}
              disabled={clearingMutation.isPending}
              className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition shadow-xs flex items-center gap-1.5 cursor-pointer"
            >
              <DollarSign className="w-3.5 h-3.5" />
              <span>{clearingMutation.isPending ? t("admin_vpp.clearing_running", "Clearing läuft...") : t("admin_vpp.run_clearing", "80/20 Clearing")}</span>
            </button>

            <button
              onClick={() => setTestDispatchModal(true)}
              className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition shadow-xs flex items-center gap-1.5 cursor-pointer"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{t("admin_vpp.start_test_dispatch", "Test-Dispatch")}</span>
            </button>
          </div>
        }
      />

      {/* ACTION NOTIFICATION */}
      {actionMsg && (
        <div
          className={`p-3.5 rounded-xl text-xs font-bold flex items-center justify-between animate-in fade-in ${
            actionMsg.type === "success"
              ? "bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200"
              : "bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-200"
          }`}
        >
          <div className="flex items-center gap-2">
            <span>{actionMsg.type === "success" ? "✅" : "❌"}</span>
            <span>{actionMsg.text}</span>
          </div>
          <button onClick={() => setActionMsg(null)} className="opacity-60 hover:opacity-100">
            ✕
          </button>
        </div>
      )}

      {/* 🧭 NAVIGATION TABS */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
        <button
          onClick={() => setActiveTab("flexibility")}
          className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition cursor-pointer ${
            activeTab === "flexibility"
              ? "bg-emerald-600 text-white shadow-xs"
              : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
          }`}
        >
          <Zap className="w-3.5 h-3.5" />
          <span>Flexibilität & Fahrpläne</span>
        </button>

        <button
          onClick={() => setActiveTab("steuve")}
          className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition cursor-pointer ${
            activeTab === "steuve"
              ? "bg-emerald-600 text-white shadow-xs"
              : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
          }`}
        >
          <Calculator className="w-3.5 h-3.5" />
          <span>§ 14a Netzentgelt-Kalkulator</span>
        </button>

        <button
          onClick={() => setActiveTab("cls")}
          className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition cursor-pointer ${
            activeTab === "cls"
              ? "bg-emerald-600 text-white shadow-xs"
              : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
          }`}
        >
          <Radio className="w-3.5 h-3.5" />
          <span>SMGW & CLS-Kanal Inspector</span>
        </button>

        <button
          onClick={() => setActiveTab("eichrecht")}
          className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition cursor-pointer ${
            activeTab === "eichrecht"
              ? "bg-emerald-600 text-white shadow-xs"
              : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
          }`}
        >
          <FileCheck className="w-3.5 h-3.5" />
          <span>Eichrechts-Prüfung (PTB-A 50.7)</span>
        </button>

        <button
          onClick={() => setActiveTab("simulator")}
          className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition cursor-pointer ${
            activeTab === "simulator"
              ? "bg-emerald-600 text-white shadow-xs"
              : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
          }`}
        >
          <Sliders className="w-3.5 h-3.5" />
          <span>VPP Sandbox Clearing Simulator</span>
        </button>
      </div>

      {/* ============================================================ */}
      {/* TAB 1: ⚡ VPP FLEXIBILITÄT & FAHRPLÄNE */}
      {/* ============================================================ */}
      {activeTab === "flexibility" && (
        <div className="space-y-6 animate-fade-in">
          {/* KPI KACHELN */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium mb-2">
                <span>{t("admin_vpp.pos_flex", "Positive Regelleistung (+kW)")}</span>
                <ArrowUpRight className="w-4 h-4 text-emerald-500" />
              </div>
              <div className="text-2xl font-black text-slate-900 dark:text-white">
                {(Number(fleetData.summary.total_available_positive_flex_kw) || 0).toLocaleString("de-DE", {
                  maximumFractionDigits: 1,
                })}{" "}
                <span className="text-sm font-bold text-slate-500">kW</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                🔋 {fleetData.battery_fleet.total_batteries || 0} Speicher • Ø {fleetData.battery_fleet.average_soc_pct || 0}% SoC
              </p>
            </Card>

            <Card className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium mb-2">
                <span>{t("admin_vpp.neg_flex", "Negative Regelleistung (-kW)")}</span>
                <ArrowDownRight className="w-4 h-4 text-sky-500" />
              </div>
              <div className="text-2xl font-black text-slate-900 dark:text-white">
                {(Number(fleetData.summary.total_available_negative_flex_kw) || 0).toLocaleString("de-DE", {
                  maximumFractionDigits: 1,
                })}{" "}
                <span className="text-sm font-bold text-slate-500">kW</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                🔌 SteuVE & Zwangsladung
              </p>
            </Card>

            <Card className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium mb-2">
                <span>{t("admin_vpp.connected_assets", "Verbundene Liegenschaften")}</span>
                <Layers className="w-4 h-4 text-indigo-500" />
              </div>
              <div className="text-2xl font-black text-slate-900 dark:text-white">
                {fleetData.summary.active_participating_assets || 0}{" "}
                <span className="text-xs text-slate-400 font-normal">/ {fleetData.summary.total_connected_assets || 0}</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                🛡️ § 14a EnWG zertifiziert
              </p>
            </Card>

            <Card className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium mb-2">
                <span>{t("admin_vpp.reaction_time", "Reaktionszeit (SLA)")}</span>
                <Clock className="w-4 h-4 text-purple-500" />
              </div>
              <div className="text-2xl font-black text-slate-900 dark:text-white">
                {fleetData.summary.average_reaction_time_seconds || 12.5} <span className="text-sm font-bold text-slate-500">s</span>
              </div>
              <p className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold mt-1">
                aFRR & SRL konform (&lt; 30s)
              </p>
            </Card>
          </div>

          {/* 📈 FAHRPLAN MONITOR & DISPATCH COCKPIT */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                      {t("admin_vpp.schedule_title", "Redispatch 2.0 & aFRR 96-Viertelstunden-Fahrplan")}
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {t("admin_vpp.schedule_subtitle", "Gemeldete Fahrplanleistung an Übertragungsnetzbetreiber (Connect+)")}
                    </p>
                  </div>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-bold border border-emerald-300 dark:border-emerald-800">
                    {t("admin_vpp.live_active", "Live aktiv")}
                  </span>
                </div>

                <div className="h-64">
                  <ReactECharts option={scheduleChartOption} opts={{ renderer: "svg" }} style={{ height: "100%", width: "100%" }} />
                </div>
              </Card>
            </div>

            {/* Live-Filter & ÜNB Zonen */}
            <div>
              <Card className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-4">
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                  {t("admin_vpp.tso_filter_title", "ÜNB & Markt-Filter")}
                </h3>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">
                    {t("admin_vpp.control_area", "Regelzone (ÜNB):")}
                  </label>
                  <select
                    value={selectedTso}
                    onChange={(e) => setSelectedTso(e.target.value)}
                    className="w-full text-xs p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-200"
                  >
                    <option value="all">{t("admin_vpp.all_control_areas", "Alle Regelzonen (Bundesweit)")}</option>
                    <option value="50hertz">50Hertz Transmission</option>
                    <option value="tennet">TenneT TSO</option>
                    <option value="amprion">Amprion GmbH</option>
                    <option value="transnetbw">TransnetBW GmbH</option>
                  </select>
                </div>

                <div className="pt-2 border-t border-slate-100 dark:border-slate-800 space-y-2">
                  <div className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                    {t("admin_vpp.product_classification", "Produkt-Klassifikation:")}
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    <span className="px-2 py-1 rounded-lg text-[10px] font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                      ⚡ aFRR Sekundärregelung
                    </span>
                    <span className="px-2 py-1 rounded-lg text-[10px] font-bold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                      🔋 FCR Primärregelung
                    </span>
                    <span className="px-2 py-1 rounded-lg text-[10px] font-bold bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800">
                      🔌 Redispatch 2.0
                    </span>
                    <span className="px-2 py-1 rounded-lg text-[10px] font-bold bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                      📈 Spotmarkt-Arbitrage
                    </span>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400">
                  {t("admin_vpp.telemetry_protocol", "Telemetrie-Protokoll:")} <b>OpenADR 2.0b / IEC 60870-5-104</b>
                </div>
              </Card>
            </div>
          </div>

          {/* 📜 DISPATCH ORDERS HISTORIE */}
          <Card className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                  {t("admin_vpp.dispatches_title", "Letzte Dispatch-Ereignisse & Abrufe")}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {t("admin_vpp.dispatches_subtitle", "Übersicht der automatisierten Markt- und Netzabrufe")}
                </p>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-slate-800 text-slate-400 font-semibold">
                    <th className="pb-2">{t("admin_vpp.th_timestamp", "Zeitstempel")}</th>
                    <th className="pb-2">{t("admin_vpp.th_order_id", "Order ID")}</th>
                    <th className="pb-2">{t("admin_vpp.th_target_power", "Soll-Leistung")}</th>
                    <th className="pb-2">{t("admin_vpp.th_duration", "Dauer")}</th>
                    <th className="pb-2">{t("common.status", "Status")}</th>
                    <th className="pb-2">{t("admin_vpp.th_fulfillment", "Erfüllung")}</th>
                    <th className="pb-2 text-right">{t("admin_vpp.th_revenue", "Erlös (80/20)")}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {dispatches.length > 0 ? (
                    dispatches.map((d) => (
                      <tr key={d.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition">
                        <td className="py-3 font-mono text-slate-600 dark:text-slate-300">
                          {d.created_at ? new Date(d.created_at).toLocaleString("de-DE") : "–"}
                        </td>
                        <td className="py-3 font-mono text-slate-500">
                          {String(d.id).substring(0, 8)}...
                        </td>
                        <td className="py-3 font-bold text-slate-800 dark:text-slate-200">
                          {d.target_power_kw} kW
                        </td>
                        <td className="py-3 text-slate-600 dark:text-slate-300">
                          {d.duration_minutes || 15} Min
                        </td>
                        <td className="py-3">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              d.status === "completed"
                                ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                                : d.status === "active"
                                ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 animate-pulse"
                                : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                            }`}
                          >
                            {d.status}
                          </span>
                        </td>
                        <td className="py-3 font-semibold text-emerald-600 dark:text-emerald-400">
                          {d.fulfillment_pct ? `${d.fulfillment_pct} %` : "98.5 %"}
                        </td>
                        <td className="py-3 text-right font-bold text-slate-900 dark:text-white">
                          {d.total_revenue_eur ? `${Number(d.total_revenue_eur).toFixed(2)} €` : "–"}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" className="py-6 text-center text-slate-400">
                        {t("common.no_data", "Keine Daten vorhanden.")}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* ============================================================ */}
      {/* TAB 2: ⚖️ § 14a ENWG NETZENTGELT-KALKULATOR */}
      {/* ============================================================ */}
      {activeTab === "steuve" && (
        <div className="space-y-6 animate-fade-in">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Input Parameter Form */}
            <Card className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-4">
              <div className="flex items-center gap-2">
                <Calculator className="w-5 h-5 text-emerald-600" />
                <h3 className="font-bold text-slate-900 dark:text-white text-sm">
                  Liegenschafts- & Geräte-Parameter
                </h3>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-semibold mb-1">
                    Anzahl Wallboxen (§ 14a SteuVE):
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={calcInputs.wallbox_count}
                    onChange={(e) => setCalcInputs({ ...calcInputs, wallbox_count: Number(e.target.value) })}
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-bold"
                  />
                </div>

                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-semibold mb-1">
                    Anzahl Wärmepumpen / Klimaanlagen:
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={calcInputs.heat_pump_count}
                    onChange={(e) => setCalcInputs({ ...calcInputs, heat_pump_count: Number(e.target.value) })}
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-bold"
                  />
                </div>

                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-semibold mb-1">
                    Geschätzter Jahresverbrauch SteuVE (kWh/a):
                  </label>
                  <input
                    type="number"
                    step="100"
                    value={calcInputs.annual_consumption_kwh}
                    onChange={(e) => setCalcInputs({ ...calcInputs, annual_consumption_kwh: Number(e.target.value) })}
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-bold"
                  />
                </div>

                <div>
                  <label className="block text-slate-600 dark:text-slate-400 font-semibold mb-1">
                    Arbeitspreis Netzentgelt VNB (Ct/kWh):
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={calcInputs.grid_fee_ct_kwh}
                    onChange={(e) => setCalcInputs({ ...calcInputs, grid_fee_ct_kwh: Number(e.target.value) })}
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-bold"
                  />
                </div>
              </div>

              <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 rounded-xl border border-emerald-200 dark:border-emerald-800/40 text-[11px] text-emerald-800 dark:text-emerald-300">
                💡 <b>Gesetzliche Grundlage:</b> BNetzA Festlegung BK6-22-300 & BK8-22/010-A (Gültig bundesweit seit 01.01.2024).
              </div>
            </Card>

            {/* Comparison of Modules */}
            <div className="lg:col-span-2 space-y-4">
              {calcQuery.data && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Modul 1 */}
                  <div className={`p-5 rounded-2xl border transition ${
                    calcQuery.data.modul_1_flat.recommended
                      ? "bg-emerald-50/50 dark:bg-emerald-950/30 border-emerald-500 shadow-sm"
                      : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800"
                  }`}>
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-[10px] font-black uppercase text-emerald-600 dark:text-emerald-400 tracking-wider">
                          Pauschale Vergütung
                        </span>
                        <h4 className="font-bold text-slate-900 dark:text-white text-base">
                          {calcQuery.data.modul_1_flat.name}
                        </h4>
                      </div>
                      {calcQuery.data.modul_1_flat.recommended && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-500 text-white">
                          Empfehlung
                        </span>
                      )}
                    </div>

                    <div className="my-4">
                      <div className="text-3xl font-black text-slate-900 dark:text-white">
                        {calcQuery.data.modul_1_flat.annual_savings_eur.toFixed(2)} €
                        <span className="text-xs font-normal text-slate-400"> / Jahr</span>
                      </div>
                      <div className="text-xs text-slate-500 mt-0.5">
                        ~ {calcQuery.data.modul_1_flat.monthly_savings_eur.toFixed(2)} € monatlicher Netzentgelt-Rabatt
                      </div>
                    </div>

                    <p className="text-xs text-slate-600 dark:text-slate-300 mb-3">
                      {calcQuery.data.modul_1_flat.description}
                    </p>

                    <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                      Kein separater Zähler erforderlich.
                    </div>
                  </div>

                  {/* Modul 2 */}
                  <div className={`p-5 rounded-2xl border transition ${
                    calcQuery.data.modul_2_percentage.recommended
                      ? "bg-emerald-50/50 dark:bg-emerald-950/30 border-emerald-500 shadow-sm"
                      : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800"
                  }`}>
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-[10px] font-black uppercase text-indigo-600 dark:text-indigo-400 tracking-wider">
                          60% Arbeitspreis-Erlass
                        </span>
                        <h4 className="font-bold text-slate-900 dark:text-white text-base">
                          {calcQuery.data.modul_2_percentage.name}
                        </h4>
                      </div>
                      {calcQuery.data.modul_2_percentage.recommended && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-500 text-white">
                          Empfehlung
                        </span>
                      )}
                    </div>

                    <div className="my-4">
                      <div className="text-3xl font-black text-slate-900 dark:text-white">
                        {calcQuery.data.modul_2_percentage.annual_savings_eur.toFixed(2)} €
                        <span className="text-xs font-normal text-slate-400"> / Jahr</span>
                      </div>
                      <div className="text-xs text-slate-500 mt-0.5">
                        ~ {calcQuery.data.modul_2_percentage.monthly_savings_eur.toFixed(2)} € monatlicher Netzentgelt-Rabatt
                      </div>
                    </div>

                    <p className="text-xs text-slate-600 dark:text-slate-300 mb-3">
                      {calcQuery.data.modul_2_percentage.description}
                    </p>

                    <div className="text-[11px] font-semibold text-indigo-600 dark:text-indigo-400">
                      Separater Zähler / RLM-Messung erforderlich.
                    </div>
                  </div>
                </div>
              )}

              {/* Environmental impact box */}
              {calcQuery.data && (
                <div className="p-4 bg-slate-900 text-white rounded-2xl flex items-center justify-between">
                  <div className="space-y-0.5">
                    <span className="text-xs text-slate-400">Ökologischer Netzdienlichkeits-Effekt:</span>
                    <div className="font-bold text-emerald-400 text-sm">
                      🌱 ca. {calcQuery.data.co2_avoided_kg_year} kg CO₂/Jahr vermieden durch Peak-Shaving
                    </div>
                  </div>
                  <div className="text-right text-xs text-slate-400 font-mono">
                    EnWG § 14a Stabilitätsbeitrag
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* TAB 3: 📡 SMGW & CLS-KANAL INSPECTOR */}
      {/* ============================================================ */}
      {activeTab === "cls" && (
        <div className="space-y-6 animate-fade-in">
          {clsQuery.data && (
            <div className="space-y-6">
              {/* PKI & Gateway Banner */}
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Radio className="w-5 h-5 text-emerald-500 animate-pulse" />
                    <h3 className="font-black text-slate-900 dark:text-white text-base">
                      {clsQuery.data.smgw_id}
                    </h3>
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20">
                      Online & Gekoppelt
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 font-mono">
                    {clsQuery.data.pki_status.cipher_suite} • {clsQuery.data.pki_status.tls_version}
                  </p>
                </div>

                <div className="text-right text-xs space-y-0.5">
                  <div className="text-slate-400">Zertifikatslaufzeit:</div>
                  <div className="font-bold text-slate-800 dark:text-slate-200 font-mono">
                    {clsQuery.data.pki_status.days_valid} Tage verbleibend ({clsQuery.data.pki_status.certificate_issuer})
                  </div>
                </div>
              </div>

              {/* Active CLS Channels Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {clsQuery.data.cls_channels.map((ch) => (
                  <Card key={ch.id} className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-black text-slate-900 dark:text-white flex items-center gap-1.5">
                        <Cpu className="w-4 h-4 text-indigo-500" />
                        {ch.protocol}
                      </span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                        {ch.status}
                      </span>
                    </div>

                    <div className="text-xs text-slate-600 dark:text-slate-300 font-medium">
                      Ziel: <strong>{ch.target}</strong>
                    </div>

                    <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
                      <span className="text-slate-400">Latenz:</span>
                      <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">{ch.latency_ms} ms</span>
                    </div>
                  </Card>
                ))}
              </div>

              {/* Ready status */}
              <div className="p-4 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/40 rounded-2xl flex items-center justify-between text-xs text-emerald-800 dark:text-emerald-300 font-semibold">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>CLS Dimm-Kanal gem. EnWG § 14a betriebsbereit (Sollwert-Vorgabe 4,2 kW garantiert).</span>
                </div>
                <span className="font-mono text-[11px] opacity-75">Letzter Heartbeat: {new Date().toLocaleTimeString()}</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ============================================================ */}
      {/* TAB 4: ⚖️ EICHRECHTS-PRÜFUNG (PTB-A 50.7) */}
      {/* ============================================================ */}
      {activeTab === "eichrecht" && (
        <div className="space-y-6 animate-fade-in">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Form */}
            <Card className="lg:col-span-5 p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-4">
              <div className="flex items-center gap-2">
                <FileCheck className="w-5 h-5 text-indigo-600" />
                <h3 className="font-bold text-slate-900 dark:text-white text-sm">
                  SML/OBIS Signatur-Prüfung
                </h3>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Smart Meter Seriennummer:</label>
                  <input
                    type="text"
                    value={eichrechtForm.meter_serial}
                    onChange={(e) => setEichrechtForm({ ...eichrechtForm, meter_serial: e.target.value })}
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-mono"
                  />
                </div>

                <div>
                  <label className="block font-semibold mb-1 text-slate-700 dark:text-slate-300">OBIS 1.8.0 Zählerstand (Netzbezug kWh):</label>
                  <input
                    type="number"
                    step="0.01"
                    value={eichrechtForm.obis_180_kwh}
                    onChange={(e) => setEichrechtForm({ ...eichrechtForm, obis_180_kwh: Number(e.target.value) })}
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-mono"
                  />
                </div>

                <div>
                  <label className="block font-semibold mb-1 text-slate-700 dark:text-slate-300">OBIS 2.8.0 Zählerstand (Einspeisung kWh):</label>
                  <input
                    type="number"
                    step="0.01"
                    value={eichrechtForm.obis_280_kwh}
                    onChange={(e) => setEichrechtForm({ ...eichrechtForm, obis_280_kwh: Number(e.target.value) })}
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-mono"
                  />
                </div>

                <button
                  type="button"
                  onClick={() => eichrechtMutation.mutate(eichrechtForm)}
                  disabled={eichrechtMutation.isPending}
                  className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold transition flex items-center justify-center gap-2 cursor-pointer shadow-xs"
                >
                  <Key className="w-4 h-4" />
                  <span>{eichrechtMutation.isPending ? "Signatur wird validiert..." : "Kryptographische Signatur prüfen"}</span>
                </button>
              </div>
            </Card>

            {/* Results */}
            <div className="lg:col-span-7">
              {eichrechtResult ? (
                <Card className="p-5 bg-white dark:bg-slate-900 border border-emerald-500/30 rounded-2xl space-y-4 shadow-sm">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                      <h4 className="font-bold text-slate-900 dark:text-white text-base">
                        {eichrechtResult.status}
                      </h4>
                    </div>
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20">
                      Gültig bis {eichrechtResult.calibrated_until}
                    </span>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
                      <span className="text-slate-400 text-[10px] uppercase font-bold block">SHA-256 Prüfsumme (Payload Digest):</span>
                      <code className="text-emerald-600 dark:text-emerald-400 font-mono break-all text-[11px]">
                        {eichrechtResult.crypto_proof.sha256_hash}
                      </code>
                    </div>

                    <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
                      <span className="text-slate-400 text-[10px] uppercase font-bold block">Public Key Fingerprint:</span>
                      <code className="text-indigo-600 dark:text-indigo-400 font-mono break-all text-[11px]">
                        {eichrechtResult.crypto_proof.public_key_fingerprint}
                      </code>
                    </div>

                    <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
                      <span className="text-slate-400 text-[10px] uppercase font-bold block">PTB Zulassung & Transparenzsoftware-Nachweis:</span>
                      <div className="font-semibold text-slate-800 dark:text-slate-200">
                        Zulassungszeichen: <b>{eichrechtResult.crypto_proof.ptb_approval_code}</b> • 100% kompatibel mit SML-Transparenzsoftware
                      </div>
                    </div>
                  </div>
                </Card>
              ) : (
                <div className="h-full border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl flex flex-col items-center justify-center p-8 text-slate-400 text-center text-xs space-y-2">
                  <Key className="w-8 h-8 text-slate-300 dark:text-slate-600" />
                  <span>Klicken Sie auf „Kryptographische Signatur prüfen“, um den digitalen Konformitätsnachweis gem. PTB-A 50.7 zu berechnen.</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* TAB 5: 🧪 VPP SANDBOX CLEARING SIMULATOR */}
      {/* ============================================================ */}
      {activeTab === "simulator" && (
        <div className="space-y-6 animate-fade-in">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Simulator Controls */}
            <Card className="lg:col-span-5 p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-4">
              <div className="flex items-center gap-2">
                <Sliders className="w-5 h-5 text-indigo-600" />
                <h3 className="font-bold text-slate-900 dark:text-white text-sm">
                  Sandbox Flexibilitäts-Ausschreibung
                </h3>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Markt-Produkt:</label>
                  <select
                    value={simForm.product}
                    onChange={(e) => setSimForm({ ...simForm, product: e.target.value })}
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white font-bold"
                  >
                    <option value="aFRR_positive">⚡ aFRR Sekundärregelung (Positive Flexibilität)</option>
                    <option value="aFRR_negative">🔌 aFRR Sekundärregelung (Negative Flexibilität)</option>
                    <option value="day_ahead_arbitrage">📈 Day-Ahead Spotmarkt-Arbitrage</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Abgerufene Leistung (MW):</label>
                  <input
                    type="number"
                    step="0.1"
                    value={simForm.power_mw}
                    onChange={(e) => setSimForm({ ...simForm, power_mw: Number(e.target.value) })}
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-mono font-bold"
                  />
                </div>

                <div>
                  <label className="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Abrufdauer (Stunden):</label>
                  <input
                    type="number"
                    step="0.25"
                    value={simForm.duration_hours}
                    onChange={(e) => setSimForm({ ...simForm, duration_hours: Number(e.target.value) })}
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-mono font-bold"
                  />
                </div>

                <div>
                  <label className="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Clearing-Preis (€/MWh):</label>
                  <input
                    type="number"
                    step="1"
                    value={simForm.clearing_price_eur_mwh}
                    onChange={(e) => setSimForm({ ...simForm, clearing_price_eur_mwh: Number(e.target.value) })}
                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 font-mono font-bold"
                  />
                </div>

                <button
                  type="button"
                  onClick={() => simMutation.mutate(simForm)}
                  disabled={simMutation.isPending}
                  className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold transition flex items-center justify-center gap-2 cursor-pointer shadow-xs"
                >
                  <Play className="w-4 h-4" />
                  <span>{simMutation.isPending ? "Simulation läuft..." : "Markt-Clearing simulieren"}</span>
                </button>
              </div>
            </Card>

            {/* Results & 80/20 Distribution */}
            <div className="lg:col-span-7">
              {simResult ? (
                <div className="space-y-4">
                  <Card className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl space-y-4 shadow-sm">
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-[10px] text-slate-400 font-mono block">Simulation: {simResult.simulation_id}</span>
                        <h4 className="font-bold text-slate-900 dark:text-white text-base">
                          Clearing-Abrechnung & Erlösverteilung
                        </h4>
                      </div>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20">
                        {simResult.activated_assets_count} Anlagen aktiviert
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="p-3.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/40">
                        <span className="text-emerald-700 dark:text-emerald-300 font-bold block text-[10px] uppercase">
                          80% Kunden-Auszahlung (Prosumer Pool)
                        </span>
                        <div className="text-2xl font-black text-emerald-700 dark:text-emerald-300 mt-1">
                          {simResult.financial_clearing.customer_payout_eur.toFixed(2)} €
                        </div>
                        <span className="text-[10px] text-slate-500">Direkte Gutschrift an Heimspeicher-Besitzer</span>
                      </div>

                      <div className="p-3.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/40">
                        <span className="text-indigo-700 dark:text-indigo-300 font-bold block text-[10px] uppercase">
                          20% Sharegy Aggregator-Marge
                        </span>
                        <div className="text-2xl font-black text-indigo-700 dark:text-indigo-300 mt-1">
                          {simResult.financial_clearing.sharegy_fee_eur.toFixed(2)} €
                        </div>
                        <span className="text-[10px] text-slate-500">Plattform- & Dispatch-Gebühr</span>
                      </div>
                    </div>

                    <div className="p-3.5 bg-slate-950 text-white rounded-xl flex items-center justify-between text-xs">
                      <div className="space-y-0.5">
                        <span className="text-slate-400 text-[10px] uppercase font-bold">Gesamterlöse (Gross):</span>
                        <div className="text-lg font-black text-white">
                          {simResult.financial_clearing.gross_revenue_eur.toFixed(2)} €
                        </div>
                      </div>
                      <div className="text-right text-emerald-400 font-bold">
                        🌱 {simResult.environmental_impact.co2_saved_kg} kg CO₂ eingespart
                      </div>
                    </div>
                  </Card>
                </div>
              ) : (
                <div className="h-full border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl flex flex-col items-center justify-center p-8 text-slate-400 text-center text-xs space-y-2">
                  <DollarSign className="w-8 h-8 text-slate-300 dark:text-slate-600" />
                  <span>Starten Sie eine Simulation, um die 80/20 Erlöse und das Clearing für das Portfolio zu berechnen.</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 🛠️ TEST DISPATCH MODAL */}
      {testDispatchModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs" onClick={() => setTestDispatchModal(false)}>
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                ⚡ {t("admin_vpp.modal_title", "Manuellen Flexibilitäts-Dispatch auslösen")}
              </h3>
              <button
                onClick={() => setTestDispatchModal(false)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-sm cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold mb-1">{t("admin_vpp.target_power_label", "Soll-Leistung (kW):")}</label>
                <input
                  type="number"
                  value={dispatchForm.power_kw}
                  onChange={(e) => setDispatchForm({ ...dispatchForm, power_kw: Number(e.target.value) })}
                  className="w-full p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">{t("admin_vpp.duration_label", "Dauer (Minuten):")}</label>
                <input
                  type="number"
                  value={dispatchForm.duration_minutes}
                  onChange={(e) => setDispatchForm({ ...dispatchForm, duration_minutes: Number(e.target.value) })}
                  className="w-full p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">{t("admin_vpp.direction_label", "Richtung:")}</label>
                <select
                  value={dispatchForm.direction}
                  onChange={(e) => setDispatchForm({ ...dispatchForm, direction: e.target.value })}
                  className="w-full p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                >
                  <option value="discharge">{t("admin_vpp.discharge_option", "Entladung (Positive Flexibilität ins Netz)")}</option>
                  <option value="charge">{t("admin_vpp.charge_option", "Ladung (Negative Flexibilität aus dem Netz)")}</option>
                </select>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-2">
              <button
                onClick={() => setTestDispatchModal(false)}
                className="px-3 py-2 text-slate-500 hover:text-slate-700 text-xs font-semibold cursor-pointer"
              >
                {t("common.cancel", "Abbrechen")}
              </button>
              <button
                onClick={() => triggerDispatchMutation.mutate(dispatchForm)}
                disabled={triggerDispatchMutation.isPending}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition shadow-xs cursor-pointer"
              >
                {triggerDispatchMutation.isPending ? t("common.sending", "Sende...") : t("admin_vpp.start_test_dispatch", "Dispatch ausführen")}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
