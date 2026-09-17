/*
# src/pages/admin/GgvAdminPage.jsx
# Dedicated Admin Page for Gemeinschaftliche Gebäudeversorgung (§ 42b EnWG)
# WEG / Multi-family residential model: On-site solar sharing by MEA (1/1000) without residual power supply
*/

import { useEffect, useState, useMemo } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { apiFetch } from "../../api/client";
import { useTranslation } from "react-i18next";
import { QRCodeSVG } from "qrcode.react";
import { useUser } from "../../hooks/useUser";
import MsbSmartMeterHub from "../../features/community/components/MsbSmartMeterHub";
import CommunityShareModal from "../../features/community/components/CommunityShareModal";
import CommunityInviteModal from "../../features/community/components/CommunityInviteModal";
import VirtualMasterMeterHub from "../../features/community/components/VirtualMasterMeterHub";
import TenantSetupWizardModal from "../../features/community/components/TenantSetupWizardModal";
import WhitelabelSettingsModal from "../../features/tenant/components/WhitelabelSettingsModal";

export default function GgvAdminPage() {
    const { t } = useTranslation();
    const { isStaffOrAdmin, hasCommunityAdminAccess } = useUser();
    const [searchParams, setSearchParams] = useSearchParams();
    const initialTab = searchParams.get("tab");

    const [tenant, setTenant] = useState(null);
    const [members, setMembers] = useState([]);
    const [invites, setInvites] = useState([]);
    const [logs, setLogs] = useState([]);
    const [cockpit, setCockpit] = useState(null);
    const [tariffData, setTariffData] = useState(null);
    const [statementsData, setStatementsData] = useState(null);
    const [sharesData, setSharesData] = useState(null);
    const [timeRange, setTimeRange] = useState("today");

    const allowedTabs = ["cockpit", "units", "settlement", "meters", "msb", "audit"];
    const [activeTab, setActiveTab] = useState(
        allowedTabs.includes(initialTab) ? initialTab : "cockpit"
    );

    const [loading, setLoading] = useState(true);
    const [shareModalOpen, setShareModalOpen] = useState(false);
    const [inviteModalOpen, setInviteModalOpen] = useState(false);
    const [wizardOpen, setWizardOpen] = useState(false);
    const [whitelabelModalOpen, setWhitelabelModalOpen] = useState(false);
    const [settling, setSettling] = useState(false);
    const [downloadingId, setDownloadingId] = useState(null);
    const [exportingFormat, setExportingFormat] = useState(null);
    const [activeQrToken, setActiveQrToken] = useState(null);
    const [copiedToken, setCopiedToken] = useState(null);

    async function loadData() {
        setLoading(true);
        try {
            const data = await apiFetch("/api/my-tenant/");
            setTenant(data.tenant);
            setMembers(data.members || []);
            setInvites(data.invites || []);

            if (data.tenant) {
                const [cockpitRes, tariffsRes, statementsRes, sharesRes, logRes] = await Promise.all([
                    apiFetch("/api/billing/community/cockpit/").catch(() => null),
                    apiFetch("/api/billing/community/tariffs/").catch(() => null),
                    apiFetch("/api/billing/community/statements/").catch(() => null),
                    apiFetch("/api/billing/community/shares/").catch(() => null),
                    apiFetch("/api/audit-log/").catch(() => []),
                ]);

                setCockpit(cockpitRes);
                setTariffData(tariffsRes);
                setStatementsData(statementsRes);
                setSharesData(sharesRes);
                setLogs(logRes || []);
            }
        } catch (err) {
            console.error("GGV Admin load failed:", err);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadData();
    }, []);

    useEffect(() => {
        const tab = searchParams.get("tab");
        if (tab && allowedTabs.includes(tab) && tab !== activeTab) {
            setActiveTab(tab);
        }
    }, [searchParams]);

    function handleTabChange(newTab) {
        const targetTab = allowedTabs.includes(newTab) ? newTab : "cockpit";
        setActiveTab(targetTab);
        setSearchParams(
            (prev) => {
                const next = new URLSearchParams(prev);
                if (targetTab === "cockpit") {
                    next.delete("tab");
                } else {
                    next.set("tab", targetTab);
                }
                return next;
            },
            { replace: true }
        );
    }

    async function triggerSettlement() {
        setSettling(true);
        try {
            const now = new Date();
            const res = await apiFetch("/api/billing/community/statements/generate/", {
                method: "POST",
                body: JSON.stringify({
                    tenant_id: tenant.id,
                    year: now.getFullYear(),
                    month: now.getMonth() + 1,
                }),
            });
            alert(res.message || "GGV-Solarabrechnung erfolgreich generiert.");
            const statementsRes = await apiFetch("/api/billing/community/statements/").catch(() => null);
            setStatementsData(statementsRes);
        } catch (err) {
            alert("Abrechnungsfehler: " + (err.message || "Unbekannter Fehler"));
        } finally {
            setSettling(false);
        }
    }

    async function createInvite(role) {
        try {
            const data = await apiFetch("/api/create-invite/", {
                method: "POST",
                body: JSON.stringify({
                    tenant_id: tenant.id,
                    role: role,
                }),
            });
            await loadData();
            return data;
        } catch (err) {
            alert("Fehler beim Erstellen des Einladungslinks: " + (err.message || ""));
            throw err;
        }
    }

    async function downloadStatementPdf(statementId, statementNumber) {
        setDownloadingId(statementId);
        try {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            const response = await fetch(`/api/billing/community/statements/${statementId}/pdf/`, {
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "X-Tenant-ID": tenant?.id || "",
                },
            });
            if (!response.ok) throw new Error("Download fehlgeschlagen.");
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `GGV_Solarabrechnung_${statementNumber}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            alert("Fehler beim Herunterladen des GGV-Abrechnungsnachweises.");
        } finally {
            setDownloadingId(null);
        }
    }

    async function exportStatements(format = "xlsx") {
        setExportingFormat(format);
        try {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            const response = await fetch(`/api/billing/community/statements/export/?export_format=${format}&tenant_id=${tenant?.id || ""}`, {
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "X-Tenant-ID": tenant?.id || "",
                },
            });
            if (!response.ok) throw new Error("Export fehlgeschlagen.");
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            const ext = format === "xlsx" ? "xlsx" : format === "csv" ? "csv" : "xml";
            a.download = `Sharegy_GGV_WEG_${tenant?.slug || "liegenschaft"}_${new Date().toISOString().slice(0, 10)}.${ext}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            alert(`Fehler beim ${format.toUpperCase()}-Export.`);
        } finally {
            setExportingFormat(null);
        }
    }

    async function updateRole(userId, role) {
        await apiFetch("/api/update-role/", {
            method: "POST",
            body: JSON.stringify({
                tenant_id: tenant.id,
                user_id: userId,
                role: role,
            }),
        });
        loadData();
    }

    async function removeMember(userId) {
        if (!confirm("Möchtest du diese Partei wirklich aus der Gebäudeversorgung entfernen?")) return;
        await apiFetch("/api/remove-member/", {
            method: "POST",
            body: JSON.stringify({
                tenant_id: tenant.id,
                user_id: userId,
            }),
        });
        loadData();
    }

    async function deactivateInvite(token) {
        if (!window.confirm("Möchtest du diesen Einladungslink widerrufen?")) return;
        try {
            await apiFetch("/api/deactivate-invite/", {
                method: "POST",
                body: JSON.stringify({ token }),
            });
            setInvites((prev) => prev.filter((i) => i.token !== token));
            await loadData();
        } catch (err) {
            alert("Fehler beim Deaktivieren des Links.");
        }
    }

    if (loading) {
        return (
            <div className="p-12 text-center text-slate-400 text-sm animate-pulse">
                Lade Gemeinschaftliche Gebäudeversorgung (§ 42b EnWG)...
            </div>
        );
    }

    if (!tenant) {
        return (
            <div className="p-8 max-w-xl mx-auto text-center space-y-4 my-8 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl">
                <div className="text-4xl">⚖️</div>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">Keine GGV-Liegenschaft zugewiesen</h2>
                <p className="text-xs text-slate-500">Du bist aktuell keiner Liegenschaft der Gemeinschaftlichen Gebäudeversorgung zugeordnet.</p>
                <Link to="/app/dashboard" className="inline-block px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-semibold">
                    Zum Dashboard
                </Link>
            </div>
        );
    }

    const currentStats = cockpit ? (timeRange === "today" ? cockpit.today : cockpit.month) : null;
    const activeTariff = tariffData ? tariffData.active_tariff : null;
    const statements = statementsData ? statementsData.statements : [];

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* HEADER */}
            <div className="space-y-4 pb-4 border-b border-slate-200 dark:border-slate-800">
                <div className="flex items-start gap-3.5">
                    <div className="w-10 h-10 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-xl shrink-0 mt-0.5">
                        ⚖️
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2.5">
                            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white truncate">
                                {tenant.name}
                            </h1>
                            <span className="shrink-0 text-xs font-bold px-3 py-1 rounded-full border flex items-center gap-1.5 bg-purple-50 dark:bg-purple-950/50 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800">
                                <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse"></span>
                                {t("admin_ggv.title", "⚖️ Gemeinschaftliche Gebäudeversorgung (§ 42b EnWG)")}
                            </span>
                            <span className="shrink-0 text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                                {t("admin_ggv.badge_model", "WEG & Mehrparteienhaus")}
                            </span>
                        </div>
                        <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
                            {t("admin_ggv.subtitle", "Vor-Ort-Solarstromaufteilung nach Miteigentumsanteilen (MEA in 1/1000). Keine Reststrom-Lieferantenpflicht – jeder Eigentümer/Nutzer behält seinen eigenen Reststromvertrag.")}
                        </p>
                    </div>
                </div>

                {/* ACTION BUTTONS */}
                <div className="flex flex-wrap items-center gap-2.5 pt-1">
                    <button
                        type="button"
                        onClick={() => setWhitelabelModalOpen(true)}
                        className="px-3.5 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 hover:bg-purple-50 dark:hover:bg-purple-950/40 text-slate-700 dark:text-slate-200 hover:text-purple-600 dark:hover:text-purple-400 border border-slate-200 dark:border-slate-800 hover:border-purple-300 transition-all shadow-xs flex items-center gap-2 cursor-pointer"
                    >
                        <span>🎨</span>
                        <span>{t("tenant.whitelabel_btn", "Whitelabel & Branding")}</span>
                    </button>
                    <button
                        type="button"
                        onClick={() => setWizardOpen(true)}
                        className="px-3.5 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 hover:bg-purple-50 dark:hover:bg-purple-950/40 text-slate-700 dark:text-slate-200 hover:text-purple-600 dark:hover:text-purple-400 border border-slate-200 dark:border-slate-800 hover:border-purple-300 transition-all shadow-xs flex items-center gap-2 cursor-pointer"
                    >
                        <span>✨</span>
                        <span>{t("admin_ggv.btn_wizard", "WEG-Gebäude-Assistent (3 Schritte)")}</span>
                    </button>
                    <button
                        type="button"
                        onClick={() => setShareModalOpen(true)}
                        className="px-3.5 py-2 rounded-xl text-xs font-bold bg-purple-50 dark:bg-purple-950/40 hover:bg-purple-100 dark:hover:bg-purple-900/60 text-purple-800 dark:text-purple-300 border border-purple-200 dark:border-purple-800/80 transition-all shadow-xs flex items-center gap-2 cursor-pointer"
                    >
                        <span>📢</span>
                        <span>{t("admin_ggv.btn_share", "Liegenschaft teilen")}</span>
                    </button>
                </div>
            </div>

            {/* TAB SWITCHER */}
            <div className="flex flex-wrap bg-slate-100 dark:bg-slate-800/70 p-1 rounded-xl text-xs font-semibold gap-1">
                <button
                    onClick={() => handleTabChange("cockpit")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "cockpit" ? "bg-white dark:bg-slate-900 text-purple-600 dark:text-purple-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("admin_ggv.tab_cockpit", "⚖️ GGV-Solarcockpit")}
                </button>
                <button
                    onClick={() => handleTabChange("units")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "units" ? "bg-white dark:bg-slate-900 text-purple-600 dark:text-purple-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("admin_ggv.tab_units", "🏢 Eigentümer & MEA")} ({members.length})
                </button>
                <button
                    onClick={() => handleTabChange("settlement")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "settlement" ? "bg-white dark:bg-slate-900 text-purple-600 dark:text-purple-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("admin_ggv.tab_settlement", "💰 Solar- & WEG-Abrechnung")}
                </button>
                <button
                    onClick={() => handleTabChange("meters")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "meters" ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("admin_ggv.tab_meters", "⚡ Messkonzept & Zähler")}
                </button>
                <button
                    onClick={() => handleTabChange("msb")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "msb" ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs font-bold" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("admin_ggv.tab_msb", "⚡ Zählerverwaltung")}
                </button>
                <button
                    onClick={() => handleTabChange("audit")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "audit" ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("admin_ggv.tab_audit", "📜 WEG-Audit & Beschlüsse")}
                </button>
            </div>

            {/* TAB 1: COCKPIT */}
            {activeTab === "cockpit" && cockpit && (
                <div className="space-y-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-bold text-slate-800 dark:text-slate-200">
                            {t("admin_ggv.balance_title", "Gebäude-Solarbilanz & MEA-Aufteilung (§ 42b EnWG)")}
                        </h2>
                        <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg text-xs font-semibold">
                            <button
                                onClick={() => setTimeRange("today")}
                                className={`px-2.5 py-1 rounded-md transition ${timeRange === "today" ? "bg-white dark:bg-slate-900 text-purple-600 dark:text-purple-400 shadow-xs" : "text-slate-500"}`}
                            >
                                {t("common.today", "Heute")}
                            </button>
                            <button
                                onClick={() => setTimeRange("month")}
                                className={`px-2.5 py-1 rounded-md transition ${timeRange === "month" ? "bg-white dark:bg-slate-900 text-purple-600 dark:text-purple-400 shadow-xs" : "text-slate-500"}`}
                            >
                                {t("common.this_month", "Dieser Monat")}
                            </button>
                        </div>
                    </div>

                    {/* KPI CARDS */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
                        <div className="bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 rounded-2xl p-4">
                            <div className="flex items-center justify-between text-amber-700 dark:text-amber-300 text-xs font-bold uppercase">
                                <span>{t("admin_ggv.kpi_pv_gen", "PV-Erzeugung")}</span>
                                <span>☀️</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-amber-900 dark:text-amber-100">
                                {Number(currentStats?.produced_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-amber-700/80 dark:text-amber-300/80 mt-0.5">{t("admin_ggv.kpi_pv_gen_sub", "Gemeinschaftsanlage")}</div>
                        </div>

                        <div className="bg-purple-500/5 dark:bg-purple-500/10 border border-purple-500/20 rounded-2xl p-4">
                            <div className="flex items-center justify-between text-purple-700 dark:text-purple-300 text-xs font-bold uppercase">
                                <span>{t("admin_ggv.kpi_demand", "Hausbedarf")}</span>
                                <span>🏢</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-purple-900 dark:text-purple-100">
                                {Number(currentStats?.consumed_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-purple-700/80 dark:text-purple-300/80 mt-0.5">{t("admin_ggv.kpi_demand_sub", "Summe aller Parteien")}</div>
                        </div>

                        <div className="bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-4">
                            <div className="flex items-center justify-between text-emerald-700 dark:text-emerald-300 text-xs font-bold uppercase">
                                <span>{t("admin_ggv.kpi_shared", "Vor-Ort verteilt")}</span>
                                <span>⚖️</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-emerald-900 dark:text-emerald-100">
                                {Number(currentStats?.shared_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-emerald-700/80 dark:text-emerald-300/80 mt-0.5 font-semibold">
                                {t("admin_ggv.kpi_shared_sub", "MEA-Abdeckung: {{autarky}}%", { autarky: currentStats?.autarky_pct ?? 0 })}
                            </div>
                        </div>

                        <div className="bg-cyan-500/5 dark:bg-cyan-500/10 border border-cyan-500/20 rounded-2xl p-4">
                            <div className="flex items-center justify-between text-cyan-700 dark:text-cyan-300 text-xs font-bold uppercase">
                                <span>{t("admin_ggv.kpi_grid_export", "Netzeinspeisung")}</span>
                                <span>🌐</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-cyan-900 dark:text-cyan-100">
                                {Math.max(0, Number(currentStats?.produced_kwh ?? 0) - Number(currentStats?.shared_kwh ?? 0)).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-cyan-700/80 dark:text-cyan-300/80 mt-0.5">{t("admin_ggv.kpi_grid_export_sub", "Überschuss ins Netz")}</div>
                        </div>

                        <div className="bg-indigo-500/5 dark:bg-indigo-500/10 border border-indigo-500/20 rounded-2xl p-4 col-span-2 sm:col-span-1">
                            <div className="flex items-center justify-between text-indigo-700 dark:text-indigo-300 text-xs font-bold uppercase">
                                <span>{t("admin_ggv.kpi_cost_benefit", "WEG-Kostenvorteil")}</span>
                                <span>💰</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-indigo-900 dark:text-indigo-100">
                                {Number(currentStats?.savings_eur ?? 0).toFixed(2)} <span className="text-xs font-normal">€</span>
                            </div>
                            <div className="text-[11px] text-indigo-700/80 dark:text-indigo-300/80 mt-0.5 font-semibold">
                                {t("admin_ggv.kpi_cost_benefit_sub", "Vermiedener Netzbezug")}
                            </div>
                        </div>
                    </div>

                    {/* HINWEISBOX GGV RECHTSGRUNDLAGE */}
                    <div className="bg-purple-50/50 dark:bg-purple-950/20 border border-purple-200 dark:border-purple-800/60 rounded-2xl p-4 text-xs text-purple-900 dark:text-purple-200 flex items-start gap-3">
                        <span className="text-lg shrink-0">ℹ️</span>
                        <div>
                            <strong>{t("admin_ggv.legal_hint_title", "Hinweis zur Abrechnung gem. § 42b EnWG:")}</strong> {t("admin_ggv.legal_hint", "In der Gemeinschaftlichen Gebäudeversorgung findet keine Reststromlieferung durch die Gemeinschaft oder den WEG-Verwalter statt. Jede Partei bezieht ihren darüber hinausgehenden Strombedarf über ihren individuellen Stromliefervertrag.")}
                        </div>
                    </div>
                </div>
            )}

            {/* TAB 2: UNITS & OWNERS */}
            {activeTab === "units" && (
                <div className="space-y-6">
                    <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs space-y-5">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100 dark:border-slate-800">
                            <div>
                                <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                    <span>🏢</span>
                                    <span>{t("admin_ggv.units_title", "Wohnungseigentümer & MEA-Schlüssel ({{count}})", { count: members.length })}</span>
                                </h2>
                                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                                    {t("admin_ggv.units_subtitle", "Verwalte Miteigentumsanteile (in 1/1000 MEA), Einladungslinks und Stimmberechtigungen für die Liegenschaft.")}
                                </p>
                            </div>
                            <button
                                type="button"
                                onClick={() => setInviteModalOpen(true)}
                                className="px-4 py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-bold shadow-xs transition-all flex items-center gap-2 cursor-pointer"
                            >
                                <span>+</span>
                                <span>{t("admin_ggv.btn_invite_owner", "Wohnungseigentümer einladen")}</span>
                            </button>
                        </div>

                        {/* INVITES */}
                        <div className="space-y-3">
                            <div className="text-xs font-bold text-slate-700 dark:text-slate-300">
                                {t("admin_ggv.open_invites", "Offene Einladungslinks: ({{count}})", { count: invites.length })}
                            </div>
                            {invites.length === 0 ? (
                                <div className="p-4 text-center rounded-2xl bg-slate-50 dark:bg-slate-800/30 border border-dashed text-xs text-slate-400">
                                    {t("admin_ggv.no_open_invites", "Keine offenen Einladungslinks für Eigentümer oder Mieter vorhanden.")}
                                </div>
                            ) : (
                                invites.map((i) => {
                                    const fullInviteUrl = `${window.location.origin}/onboarding?invite=${i.token}`;
                                    const isCopied = copiedToken === i.token;
                                    const isQrOpen = activeQrToken === i.token;
                                    return (
                                        <div key={i.token} className="border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 p-4 rounded-2xl flex flex-col gap-3">
                                            <div className="flex items-center justify-between">
                                                <span className="text-xs font-bold text-slate-900 dark:text-white">⚖️ WEG-Einladung</span>
                                                <div className="flex items-center gap-2">
                                                    <button
                                                        type="button"
                                                        onClick={() => {
                                                            navigator.clipboard.writeText(fullInviteUrl);
                                                            setCopiedToken(i.token);
                                                            setTimeout(() => setCopiedToken(null), 2500);
                                                        }}
                                                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 text-purple-600 border border-slate-200 dark:border-slate-700 cursor-pointer"
                                                    >
                                                        {isCopied ? "✓ Kopiert" : "📋 Link kopieren"}
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => setActiveQrToken(isQrOpen ? null : i.token)}
                                                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 cursor-pointer"
                                                    >
                                                        📱 QR-Code
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => deactivateInvite(i.token)}
                                                        className="px-2.5 py-1.5 text-xs text-rose-600 hover:bg-rose-50 rounded-lg cursor-pointer"
                                                    >
                                                        Widerrufen
                                                    </button>
                                                </div>
                                            </div>
                                            {isQrOpen && (
                                                <div className="p-4 bg-white dark:bg-slate-900 rounded-2xl border flex items-center gap-4">
                                                    <QRCodeSVG value={fullInviteUrl} size={110} level="M" />
                                                    <div className="text-xs">
                                                        <h5 className="font-bold">QR-Code für Eigentümer</h5>
                                                        <p className="text-slate-500 text-[11px]">Eigentümer scannen den Code, um ihrer Wohneinheit beizutreten.</p>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    );
                                })
                            )}
                        </div>

                        {/* MEMBERS TABLE */}
                        <div className="space-y-2.5 pt-4 border-t border-slate-100 dark:border-slate-800">
                            <div className="text-xs font-bold text-slate-700 dark:text-slate-300">{t("admin_ggv.registered_owners", "Registrierte Wohnungseigentümer / Parteien:")}</div>
                            {members.map((m) => (
                                <div key={m.id} className="border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 p-3.5 rounded-2xl flex items-center justify-between">
                                    <div className="flex items-center gap-2.5">
                                        <div className="w-8 h-8 rounded-full bg-purple-500/10 text-purple-600 font-bold text-xs flex items-center justify-center">
                                            {m.email?.slice(0, 2).toUpperCase()}
                                        </div>
                                        <div>
                                            <div className="text-xs font-semibold text-slate-900 dark:text-white">{m.email}</div>
                                            <div className="text-[10px] text-purple-600 dark:text-purple-400">{t("admin_ggv.participant_badge", "§ 42b EnWG Teilnehmer")}</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <select
                                            value={m.role}
                                            onChange={(e) => updateRole(m.id, e.target.value)}
                                            className="text-xs border rounded-xl px-3 py-1.5 bg-white dark:bg-slate-800 cursor-pointer"
                                        >
                                            <option value="member">⚖️ Wohnungseigentümer</option>
                                            <option value="user_admin">👥 WEG-Beirat</option>
                                            <option value="auditor">📊 Rechnungsprüfer</option>
                                            <option value="admin">🏛️ WEG-Verwalter</option>
                                        </select>
                                        <button onClick={() => removeMember(m.id)} className="text-rose-600 text-xs px-2.5 py-1.5 cursor-pointer">
                                            {t("admin_ggv.remove_member", "Entfernen")}
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                </div>
            )}

            {/* TAB 3: SETTLEMENT */}
            {activeTab === "settlement" && (
                <div className="space-y-6">
                    {activeTariff && (
                        <div className="bg-gradient-to-br from-slate-900 to-purple-950 text-white rounded-2xl p-6 border border-purple-800/50 shadow-md space-y-6">
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-xl">⚖️</span>
                                        <h2 className="text-lg font-black">{activeTariff.name}</h2>
                                        <span className="bg-emerald-400/20 text-emerald-300 text-[10px] font-bold px-2 py-0.5 rounded-full border border-emerald-400/30">
                                            {t("admin_ggv.active_badge", "Aktiv")}
                                        </span>
                                    </div>
                                    <p className="text-xs text-purple-200/80 mt-1">
                                        {t("admin_ggv.settlement_subtitle", "Vor-Ort-Solarstromabrechnung gem. § 42b EnWG (Reine Solaraufteilung, keine Reststromabrechnung)")}
                                    </p>
                                </div>
                                <button
                                    onClick={triggerSettlement}
                                    disabled={settling}
                                    className="px-4 py-2 bg-purple-500 hover:bg-purple-600 disabled:opacity-50 text-white rounded-xl text-xs font-bold cursor-pointer"
                                >
                                    {settling ? t("common.calculating", "Berechne...") : t("admin_ggv.trigger_settlement_btn", "Solarabrechnung anstoßen")}
                                </button>
                            </div>

                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-4 border-t border-purple-800/60">
                                <div>
                                    <div className="text-[11px] text-purple-300 font-semibold uppercase">{t("admin_ggv.fee_solar_use", "Solar-Nutzungsentgelt")}</div>
                                    <div className="text-2xl font-black mt-1 text-white">
                                        {Number(activeTariff?.sharing_price_ct_kwh ?? 0).toFixed(2)} <span className="text-xs font-normal">Ct/kWh</span>
                                    </div>
                                    <div className="text-[10px] text-purple-300/70 mt-0.5">{t("admin_ggv.fee_solar_use_sub", "Umlage an WEG-Rücklage")}</div>
                                </div>
                                <div>
                                    <div className="text-[11px] text-purple-300 font-semibold uppercase">{t("admin_ggv.fee_admin", "Verwaltungskosten")}</div>
                                    <div className="text-2xl font-black mt-1 text-amber-300">
                                        {Number(activeTariff?.community_fee_ct_kwh ?? 0).toFixed(2)} <span className="text-xs font-normal">Ct/kWh</span>
                                    </div>
                                    <div className="text-[10px] text-purple-300/70 mt-0.5">{t("admin_ggv.fee_admin_sub", "Software & Zählerbetrieb")}</div>
                                </div>
                                <div>
                                    <div className="text-[11px] text-purple-300 font-semibold uppercase">{t("admin_ggv.allocation_model", "Aufteilungsmodell")}</div>
                                    <div className="text-2xl font-black mt-1 text-emerald-300">
                                        MEA Quote
                                    </div>
                                    <div className="text-[10px] text-purple-300/70 mt-0.5">{t("admin_ggv.allocation_model_sub", "1/1000 Miteigentum")}</div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* STATEMENTS LIST */}
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                                    {t("admin_ggv.statements_title", "Monatliche Solar-Abrechnungsnachweise der WEG")}
                                </h3>
                                <p className="text-xs text-slate-500">
                                    {t("admin_ggv.statements_subtitle", "Eichrechtskonforme Nachweise für die Eigentümerversammlung und Betriebskostenabrechnung")}
                                </p>
                            </div>
                            <div className="flex items-center gap-1.5">
                                <button onClick={() => exportStatements("xlsx")} className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-xs rounded-lg border">
                                    Excel
                                </button>
                                <button onClick={() => exportStatements("csv")} className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-xs rounded-lg border">
                                    CSV
                                </button>
                            </div>
                        </div>

                        {statements.length > 0 ? (
                            <div className="space-y-3">
                                {statements.map((stmt) => (
                                    <div key={stmt.id} className="border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 p-4 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4">
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <span className="font-mono font-bold text-xs">{stmt.statement_number}</span>
                                                <span className="text-[10px] bg-slate-200 dark:bg-slate-700 px-2 py-0.5 rounded">{stmt.period_start} bis {stmt.period_end}</span>
                                            </div>
                                            <div className="text-xs text-slate-500 mt-1">{t("admin_ggv.owner_label", "Eigentümer:")} <span className="font-medium text-slate-700 dark:text-slate-300">{stmt.user_email}</span></div>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            <div className="text-right">
                                                <div className="text-xs text-slate-400">{t("admin_ggv.solar_usage_amount", "Solarnutzungsbetrag")}</div>
                                                <div className="text-lg font-black text-slate-900 dark:text-white">{Number(stmt.net_balance_eur ?? 0).toFixed(2)} €</div>
                                            </div>
                                            <button
                                                onClick={() => downloadStatementPdf(stmt.id, stmt.statement_number)}
                                                disabled={downloadingId === stmt.id}
                                                className="px-3 py-1.5 bg-white dark:bg-slate-900 text-purple-600 border border-purple-200 dark:border-purple-800 rounded-lg text-xs font-bold cursor-pointer"
                                            >
                                                📄 PDF
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-xs text-slate-400 bg-slate-50 dark:bg-slate-800/30 rounded-xl border border-dashed">
                                {t("admin_ggv.no_statements_msg", "Noch keine Abrechnungsnachweise erstellt. Klicke auf 'Solarabrechnung anstoßen'.")}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* TAB 4: METERS */}
            {activeTab === "meters" && <VirtualMasterMeterHub tenant={tenant} />}

            {/* TAB 5: MSB */}
            {activeTab === "msb" && <MsbSmartMeterHub tenant={tenant} />}

            {/* TAB 6: AUDIT */}
            {activeTab === "audit" && (
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs">
                    <h2 className="text-sm font-bold text-slate-900 dark:text-white mb-3">{t("admin_ggv.audit_title", "WEG-Audit- & Beschlussprotokoll")}</h2>
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                        {logs.slice(0, 30).map((log, idx) => (
                            <div key={idx} className="border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/30 p-3 rounded-xl text-xs flex justify-between">
                                <div>
                                    <span className="font-semibold">{log.action}</span>
                                    <div className="text-slate-500 mt-0.5">{log.user} → {log.target || "-"}</div>
                                </div>
                                <span className="text-slate-400">{new Date(log.created_at).toLocaleString()}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* MODALS */}
            <TenantSetupWizardModal isOpen={wizardOpen} onClose={() => setWizardOpen(false)} onComplete={() => loadData()} existingTenant={tenant} />
            <CommunityShareModal isOpen={shareModalOpen} onClose={() => setShareModalOpen(false)} kpis={{ autarky_pct: cockpit?.autarky_pct || 90, community_shared_kwh: cockpit?.shared_kwh || 140, self_consumption_pct: cockpit?.self_consumption_pct || 95 }} />
            <WhitelabelSettingsModal isOpen={whitelabelModalOpen} onClose={() => setWhitelabelModalOpen(false)} />
            <CommunityInviteModal isOpen={inviteModalOpen} onClose={() => setInviteModalOpen(false)} tenant={tenant} initialRole="member" onInviteCreated={createInvite} />
        </div>
    );
}
