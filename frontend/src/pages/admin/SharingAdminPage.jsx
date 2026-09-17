/*
# src/pages/admin/SharingAdminPage.jsx
# Dedicated Admin Page for Regionales Energy Sharing (Bürgerenergiegenossenschaft eG)
# Cooperative Model: 15-min iMSys smart-meter matching over distribution grid, AS4/MSCONS EDIFACT dispatch, shares & member registry
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
import VppAggregatorCockpit from "../../features/energy/components/VppAggregatorCockpit";
import TenantSetupWizardModal from "../../features/community/components/TenantSetupWizardModal";
import WhitelabelSettingsModal from "../../features/tenant/components/WhitelabelSettingsModal";
import MarketCommunicationModal from "../../features/billing/components/MarketCommunicationModal";
import CooperativeApplicationsTab from "../../features/community/components/CooperativeApplicationsTab";
import AdminPageHeader from "../../components/admin/AdminPageHeader";

export default function SharingAdminPage() {
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

    const allowedTabs = ["cockpit", "members", "applications", "settlement", "meters", "vpp", "msb", "audit"];
    const [activeTab, setActiveTab] = useState(
        allowedTabs.includes(initialTab) ? initialTab : "cockpit"
    );

    const [loading, setLoading] = useState(true);
    const [shareModalOpen, setShareModalOpen] = useState(false);
    const [inviteModalOpen, setInviteModalOpen] = useState(false);
    const [wizardOpen, setWizardOpen] = useState(false);
    const [whitelabelModalOpen, setWhitelabelModalOpen] = useState(false);
    const [makoModalOpen, setMakoModalOpen] = useState(false);
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
            console.error("Sharing Admin load failed:", err);
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
                    tenant_id: tenant?.id,
                    year: now.getFullYear(),
                    month: now.getMonth() + 1,
                }),
            });
            alert(`Abrechnung erfolgreich angestoßen! ${res.generated_count || 0} Abrechnungsnachweise erzeugt.`);
            const updated = await apiFetch("/api/billing/community/statements/");
            setStatementsData(updated);
        } catch (err) {
            alert("Abrechnung fehlgeschlagen: " + (err.message || "Unbekannt"));
        } finally {
            setSettling(false);
        }
    }

    async function createInvite(e) {
        e.preventDefault();
        try {
            const data = await apiFetch("/api/create-invite/", {
                method: "POST",
                body: JSON.stringify({
                    tenant_id: tenant.id,
                    role: "member",
                }),
            });
            setInvites((prev) => [data, ...prev]);
            setInviteModalOpen(false);
        } catch (err) {
            alert("Fehler beim Erstellen des Einladungslinks.");
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
            a.download = `Genossenschaft_Sharing_Abrechnung_${statementNumber}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            alert("Fehler beim Herunterladen des PDF-Abrechnungsnachweises.");
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
            a.download = `Sharegy_Sharing_eG_${tenant?.slug || "genossenschaft"}_${new Date().toISOString().slice(0, 10)}.${ext}`;
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
        if (!confirm("Möchtest du dieses Mitglied wirklich aus der Genossenschaft entfernen?")) return;
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
                {t("admin_sharing.loading", "Lade Regionales Energy Sharing & Bürgerenergie eG...")}
            </div>
        );
    }

    if (!tenant) {
        return (
            <div className="p-8 max-w-xl mx-auto text-center space-y-4 my-8 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl">
                <div className="text-4xl">⚡</div>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                    {t("admin_sharing.no_cooperative", "Keine Bürgerenergiegenossenschaft zugewiesen")}
                </h2>
                <p className="text-xs text-slate-500">
                    {t("admin_sharing.no_cooperative_desc", "Du bist aktuell keiner Energiegemeinschaft zugeordnet.")}
                </p>
                <Link to="/app/dashboard" className="inline-block px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold">
                    {t("common.to_dashboard", "Zum Dashboard")}
                </Link>
            </div>
        );
    }

    const currentStats = cockpit ? (timeRange === "today" ? cockpit.today : cockpit.month) : null;
    const activeTariff = tariffData ? tariffData.active_tariff : null;
    const statements = statementsData ? statementsData.statements : [];

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* UNIFIED ADMIN HEADER */}
            <AdminPageHeader
                icon="⚡"
                iconBg="bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400"
                title={tenant.name}
                subtitle={t("admin_sharing.subtitle", "15-Minuten Smart-Meter-Bilanzierung & Verteilnetz-Allokation der Bürgerenergiegenossenschaft mit BNetzA AS4/MSCONS Marktkommunikation")}
                manualLink="/app/help/admin-energy-sharing-cooperative-guide"
                manualLabel={t("admin_sharing.btn_manual", "Handbuch (Genossenschaft)")}
                actions={
                    <>
                        <button
                            type="button"
                            onClick={() => setWhitelabelModalOpen(true)}
                            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-800 hover:border-slate-300 transition-all shadow-xs flex items-center gap-1.5 cursor-pointer"
                        >
                            <span>🎨</span>
                            <span>{t("tenant.whitelabel_btn", "Whitelabel")}</span>
                        </button>
                        <button
                            type="button"
                            onClick={() => setMakoModalOpen(true)}
                            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 hover:bg-teal-50 dark:hover:bg-teal-950/40 text-slate-700 dark:text-slate-200 hover:text-teal-600 dark:hover:text-teal-400 border border-slate-200 dark:border-slate-800 hover:border-teal-300 transition-all shadow-xs flex items-center gap-1.5 cursor-pointer"
                        >
                            <span>📄</span>
                            <span>{t("admin_sharing.btn_mako", "AS4 Mako")}</span>
                        </button>
                        <button
                            type="button"
                            onClick={() => setShareModalOpen(true)}
                            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-800 transition-all shadow-xs flex items-center gap-1.5 cursor-pointer"
                        >
                            <span>📢</span>
                            <span>{t("tenant.share_btn", "Teilen")}</span>
                        </button>
                        <button
                            type="button"
                            onClick={() => setWizardOpen(true)}
                            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-xs transition-all flex items-center gap-1.5 cursor-pointer"
                        >
                            <span>✨</span>
                            <span>{t("admin_sharing.btn_wizard", "Assistent")}</span>
                        </button>
                    </>
                }
            />

            {/* TAB SWITCHER */}
            <div className="flex flex-wrap bg-slate-100 dark:bg-slate-800/70 p-1 rounded-xl text-xs font-semibold gap-1">
                <button
                    onClick={() => handleTabChange("cockpit")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "cockpit" ? "bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("sharing_admin.tab_cockpit", "📊 Cockpit")}
                </button>
                <button
                    onClick={() => handleTabChange("members")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "members" ? "bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("sharing_admin.tab_members", "👥 Genossen & Anteile")} ({members.length})
                </button>
                <button
                    onClick={() => handleTabChange("applications")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "applications" ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("sharing_admin.tab_applications", "📋 Beitrittsanträge")}
                </button>
                <button
                    onClick={() => handleTabChange("settlement")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "settlement" ? "bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("sharing_admin.tab_settlement", "💰 Abrechnung (15m)")}
                </button>
                <button
                    onClick={() => handleTabChange("meters")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "meters" ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("sharing_admin.tab_meters", "🏢 Summenzähler")}
                </button>
                <button
                    onClick={() => handleTabChange("vpp")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "vpp" ? "bg-white dark:bg-slate-900 text-amber-600 dark:text-amber-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("sharing_admin.tab_vpp", "🔌 VPP Kraftwerk")}
                </button>
                <button
                    onClick={() => handleTabChange("msb")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "msb" ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs font-bold" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("sharing_admin.tab_msb", "⚡ wMSB Hub")}
                </button>
                <button
                    onClick={() => handleTabChange("audit")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "audit" ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("sharing_admin.tab_audit", "📜 Genossenschafts-Audit")}
                </button>
            </div>

            {/* TAB 1: COCKPIT */}
            {activeTab === "cockpit" && cockpit && (
                <div className="space-y-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-bold text-slate-800 dark:text-slate-200">
                            {t("sharing_admin.cockpit_title", "Bürgerenergie Bilanzen & Verteilnetz-Allokation")}
                        </h2>
                        <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg text-xs font-semibold">
                            <button
                                onClick={() => setTimeRange("today")}
                                className={`px-2.5 py-1 rounded-md transition ${timeRange === "today" ? "bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-xs" : "text-slate-500"}`}
                            >
                                {t("common.today", "Heute")}
                            </button>
                            <button
                                onClick={() => setTimeRange("month")}
                                className={`px-2.5 py-1 rounded-md transition ${timeRange === "month" ? "bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-xs" : "text-slate-500"}`}
                            >
                                {t("common.this_month", "Dieser Monat")}
                            </button>
                        </div>
                    </div>

                    {/* KPI CARDS */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
                        <div className="bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 rounded-2xl p-4">
                            <div className="flex items-center justify-between text-amber-700 dark:text-amber-300 text-xs font-bold uppercase">
                                <span>{t("sharing_admin.kpi_produced", "Erzeugt (2.8.0)")}</span>
                                <span>☀️</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-amber-900 dark:text-amber-100">
                                {Number(currentStats?.produced_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-amber-700/80 dark:text-amber-300/80 mt-0.5">{t("sharing_admin.kpi_produced_sub", "Erzeugungsanlagen eG")}</div>
                        </div>

                        <div className="bg-sky-500/5 dark:bg-sky-500/10 border border-sky-500/20 rounded-2xl p-4">
                            <div className="flex items-center justify-between text-sky-700 dark:text-sky-300 text-xs font-bold uppercase">
                                <span>{t("sharing_admin.kpi_consumed", "Bedarf (1.8.0)")}</span>
                                <span>🏠</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-sky-900 dark:text-sky-100">
                                {Number(currentStats?.consumed_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-sky-700/80 dark:text-sky-300/80 mt-0.5">{t("sharing_admin.kpi_consumed_sub", "Alle Mitglieder")}</div>
                        </div>

                        <div className="bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-4">
                            <div className="flex items-center justify-between text-emerald-700 dark:text-emerald-300 text-xs font-bold uppercase">
                                <span>{t("sharing_admin.kpi_shared", "Geteilt (Sharing)")}</span>
                                <span>🤝</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-emerald-900 dark:text-emerald-100">
                                {Number(currentStats?.shared_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-emerald-700/80 dark:text-emerald-300/80 mt-0.5 font-semibold">
                                {t("sharing_admin.kpi_autarky", { rate: currentStats?.autarky_pct ?? 0, defaultValue: `Autarkiegrad: ${currentStats?.autarky_pct ?? 0}%` })}
                            </div>
                        </div>

                        <div className="bg-rose-500/5 dark:bg-rose-500/10 border border-rose-500/20 rounded-2xl p-4">
                            <div className="flex items-center justify-between text-rose-700 dark:text-rose-300 text-xs font-bold uppercase">
                                <span>{t("sharing_admin.kpi_grid_import", "Netzbezug (Rest)")}</span>
                                <span>🔌</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-rose-900 dark:text-rose-100">
                                {Number(currentStats?.grid_import_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-rose-700/80 dark:text-rose-300/80 mt-0.5">{t("sharing_admin.kpi_grid_import_sub", "Externer Reststrom")}</div>
                        </div>

                        <div className="bg-indigo-500/5 dark:bg-indigo-500/10 border border-indigo-500/20 rounded-2xl p-4 col-span-2 sm:col-span-1">
                            <div className="flex items-center justify-between text-indigo-700 dark:text-indigo-300 text-xs font-bold uppercase">
                                <span>{t("sharing_admin.kpi_savings", "Ersparnis")}</span>
                                <span>💰</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-indigo-900 dark:text-indigo-100">
                                {Number(currentStats?.savings_eur ?? 0).toFixed(2)} <span className="text-xs font-normal">€</span>
                            </div>
                            <div className="text-[11px] text-indigo-700/80 dark:text-indigo-300/80 mt-0.5 font-semibold">
                                {t("sharing_admin.kpi_savings_sub", "inkl. Netzentgelt-Rabatt")}
                            </div>
                        </div>
                    </div>

                    {/* 15 MINUTEN LASTGANG ZEITREIHE */}
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                                    {t("sharing_admin.profile_title", "15-Minuten Lastgang & Peer-to-Peer Allokation (Letzte 24 Stunden)")}
                                </h3>
                                <p className="text-xs text-slate-500">
                                    {t("sharing_admin.profile_sub", "Eichrechtskonforme Erfassung aller 15m-Slots aus OBIS 1.8.0 & 2.8.0 über das öffentliche Verteilnetz")}
                                </p>
                            </div>
                            <div className="flex items-center gap-3 text-xs">
                                <span className="flex items-center gap-1.5 text-amber-600 font-semibold">
                                    <span className="w-2.5 h-2.5 rounded-sm bg-amber-500"></span> {t("sharing_admin.legend_gen", "Erzeugung")}
                                </span>
                                <span className="flex items-center gap-1.5 text-sky-600 font-semibold">
                                    <span className="w-2.5 h-2.5 rounded-sm bg-sky-500"></span> {t("sharing_admin.legend_cons", "Verbrauch")}
                                </span>
                                <span className="flex items-center gap-1.5 text-emerald-600 font-semibold">
                                    <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500"></span> {t("sharing_admin.legend_shared", "Geteilt")}
                                </span>
                            </div>
                        </div>

                        {cockpit.timeseries_24h?.length > 0 ? (
                            <div className="space-y-1 max-h-72 overflow-y-auto pr-1">
                                {cockpit.timeseries_24h.slice(-16).reverse().map((slot, idx) => (
                                    <div key={idx} className="flex items-center justify-between p-2.5 bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 rounded-xl text-xs">
                                        <span className="font-mono text-slate-500">
                                            {new Date(slot.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} Uhr
                                        </span>
                                        <div className="flex items-center gap-4">
                                            <span className="text-amber-600 dark:text-amber-400 font-bold">☀️ {slot.produced_kwh.toFixed(2)} kWh</span>
                                            <span className="text-sky-600 dark:text-sky-400 font-bold">🏠 {slot.consumed_kwh.toFixed(2)} kWh</span>
                                            <span className="text-emerald-600 dark:text-emerald-400 font-black">🤝 {slot.shared_kwh.toFixed(2)} kWh</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-xs text-slate-400 bg-slate-50 dark:bg-slate-800/30 rounded-xl border border-dashed">
                                {t("sharing_admin.profile_empty", "Messwerte des MSB werden alle 15 Minuten automatisch eingelesen.")}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* TAB 2: MEMBERS & SHARES */}
            {activeTab === "members" && (
                <div className="space-y-6">
                    <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs space-y-5">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100 dark:border-slate-800">
                            <div>
                                <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                    <span>👥</span>
                                    <span>{t("sharing_admin.members_title", { count: members.length, defaultValue: `Genossenschaftsmitglieder & Anteile (${members.length})` })}</span>
                                </h2>
                                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                                    {t("sharing_admin.members_sub", "Mitgliederregister, Geschäftsanteile und Rollen nach dem Genossenschaftsgesetz (GenG).")}
                                </p>
                            </div>
                            <button
                                type="button"
                                onClick={() => setInviteModalOpen(true)}
                                className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold shadow-xs transition-all flex items-center gap-2 cursor-pointer"
                            >
                                <span>+</span>
                                <span>{t("sharing_admin.invite_member_btn", "Neues Mitglied einladen")}</span>
                            </button>
                        </div>

                        {/* INVITES */}
                        <div className="space-y-3">
                            <div className="text-xs font-bold text-slate-700 dark:text-slate-300">
                                {t("sharing_admin.active_invites", { count: invites.length, defaultValue: `Aktive Einladungslinks: (${invites.length})` })}
                            </div>
                            {invites.length === 0 ? (
                                <div className="p-4 text-center rounded-2xl bg-slate-50 dark:bg-slate-800/30 border border-dashed text-xs text-slate-400">
                                    {t("sharing_admin.no_invites", "Keine offenen Einladungslinks vorhanden.")}
                                </div>
                            ) : (
                                invites.map((i) => {
                                    const fullInviteUrl = `${window.location.origin}/onboarding?invite=${i.token}`;
                                    const isCopied = copiedToken === i.token;
                                    const isQrOpen = activeQrToken === i.token;
                                    return (
                                        <div key={i.token} className="border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 p-4 rounded-2xl flex flex-col gap-3">
                                            <div className="flex items-center justify-between">
                                                <span className="text-xs font-bold text-slate-900 dark:text-white">{t("sharing_admin.invite_card_title", "⚡ Genossenschafts-Einladung")}</span>
                                                <div className="flex items-center gap-2">
                                                    <button
                                                        type="button"
                                                        onClick={() => {
                                                            navigator.clipboard.writeText(fullInviteUrl);
                                                            setCopiedToken(i.token);
                                                            setTimeout(() => setCopiedToken(null), 2500);
                                                        }}
                                                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 text-emerald-600 border border-slate-200 dark:border-slate-700 cursor-pointer"
                                                    >
                                                        {isCopied ? t("sharing_admin.copied", "✓ Kopiert") : t("sharing_admin.copy_link", "📋 Link kopieren")}
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => setActiveQrToken(isQrOpen ? null : i.token)}
                                                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 cursor-pointer"
                                                    >
                                                        {t("sharing_admin.qr_code_btn", "📱 QR-Code")}
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => deactivateInvite(i.token)}
                                                        className="px-2.5 py-1.5 text-xs text-rose-600 hover:bg-rose-50 rounded-lg cursor-pointer"
                                                    >
                                                        {t("sharing_admin.revoke_btn", "Widerrufen")}
                                                    </button>
                                                </div>
                                            </div>
                                            {isQrOpen && (
                                                <div className="p-4 bg-white dark:bg-slate-900 rounded-2xl border flex items-center gap-4">
                                                    <QRCodeSVG value={fullInviteUrl} size={110} level="M" />
                                                    <div className="text-xs">
                                                        <h5 className="font-bold">{t("sharing_admin.qr_title", "QR-Code für neue Mitglieder")}</h5>
                                                        <p className="text-slate-500 text-[11px]">{t("sharing_admin.qr_sub", "Bürger scannen den Code, um der Genossenschaft digital beizutreten.")}</p>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    );
                                })
                            )}
                        </div>

                        {/* MEMBERS LIST */}
                        <div className="space-y-2.5 pt-4 border-t border-slate-100 dark:border-slate-800">
                            <div className="text-xs font-bold text-slate-700 dark:text-slate-300">{t("sharing_admin.members_list_header", "Genossenschaftsmitglieder:")}</div>
                            {members.map((m) => (
                                <div key={m.id} className="border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 p-3.5 rounded-2xl flex items-center justify-between">
                                    <div className="flex items-center gap-2.5">
                                        <div className="w-8 h-8 rounded-full bg-emerald-500/10 text-emerald-600 font-bold text-xs flex items-center justify-center">
                                            {m.email?.slice(0, 2).toUpperCase()}
                                        </div>
                                        <div>
                                            <div className="text-xs font-semibold text-slate-900 dark:text-white">{m.email}</div>
                                            <div className="text-[10px] text-emerald-600 dark:text-emerald-400">{t("sharing_admin.member_status_active", "Genossenschaftsanteil aktiv • Satzung anerkannt")}</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <select
                                            value={m.role}
                                            onChange={(e) => updateRole(m.id, e.target.value)}
                                            className="text-xs border rounded-xl px-3 py-1.5 bg-white dark:bg-slate-800 cursor-pointer"
                                        >
                                            <option value="member">{t("sharing_admin.role_member", "⚡ Mitglied (eG)")}</option>
                                            <option value="user_admin">{t("sharing_admin.role_user_admin", "👥 Mitgliederverwaltung")}</option>
                                            <option value="auditor">{t("sharing_admin.role_auditor", "📊 Kassenprüfer / Aufsichtsrat")}</option>
                                            <option value="admin">{t("sharing_admin.role_admin", "🏛️ Vorstand (eG)")}</option>
                                        </select>
                                        <button onClick={() => removeMember(m.id)} className="text-rose-600 text-xs px-2.5 py-1.5 cursor-pointer">
                                            {t("sharing_admin.remove_member", "Entfernen")}
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                </div>
            )}

            {/* TAB 3: APPLICATIONS */}
            {activeTab === "applications" && <CooperativeApplicationsTab tenant={tenant} />}

            {/* TAB 4: SETTLEMENT */}
            {activeTab === "settlement" && (
                <div className="space-y-6">
                    {activeTariff && (
                        <div className="bg-gradient-to-br from-indigo-950 to-slate-900 text-white rounded-2xl p-6 border border-indigo-700/50 shadow-md space-y-6">
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-xl">⚡</span>
                                        <h2 className="text-lg font-black">{activeTariff.name}</h2>
                                        <span className="bg-emerald-400/20 text-emerald-300 text-[10px] font-bold px-2 py-0.5 rounded-full border border-emerald-400/30">
                                            {t("sharing_admin.tariff_active", "Aktiv")}
                                        </span>
                                    </div>
                                    <p className="text-xs text-indigo-200/80 mt-1">
                                        {t("sharing_admin.tariff_sub", "Regionales Energy Sharing (15-Minuten-Bilanzierung & Netzentgeltreduktion über das Verteilnetz)")}
                                    </p>
                                </div>
                                <button
                                    onClick={triggerSettlement}
                                    disabled={settling}
                                    className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-white rounded-xl text-xs font-bold cursor-pointer"
                                >
                                    {settling ? t("sharing_admin.calculating", "Berechne...") : t("sharing_admin.trigger_settlement", "Monatsabrechnung anstoßen")}
                                </button>
                            </div>

                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-indigo-800/60">
                                <div>
                                    <div className="text-[11px] text-indigo-300 font-semibold uppercase">{t("sharing_admin.tariff_purchase_price", "Bezugspreis (Sharing)")}</div>
                                    <div className="text-2xl font-black mt-1 text-white">
                                        {Number(activeTariff?.sharing_price_ct_kwh ?? 0).toFixed(2)} <span className="text-xs font-normal">Ct/kWh</span>
                                    </div>
                                    <div className="text-[10px] text-indigo-300/70 mt-0.5">{t("sharing_admin.tariff_purchase_sub", "für Solar-Abnehmer")}</div>
                                </div>
                                <div>
                                    <div className="text-[11px] text-indigo-300 font-semibold uppercase">{t("sharing_admin.tariff_producer_payout", "Einspeisevergütung")}</div>
                                    <div className="text-2xl font-black mt-1 text-emerald-300">
                                        {Number(activeTariff?.producer_payout_ct_kwh ?? 0).toFixed(2)} <span className="text-xs font-normal">Ct/kWh</span>
                                    </div>
                                    <div className="text-[10px] text-indigo-300/70 mt-0.5">{t("sharing_admin.tariff_producer_sub", "Gutschrift an Einspeiser")}</div>
                                </div>
                                <div>
                                    <div className="text-[11px] text-indigo-300 font-semibold uppercase">{t("sharing_admin.tariff_community_fee", "Community-Umlage")}</div>
                                    <div className="text-2xl font-black mt-1 text-amber-300">
                                        {Number(activeTariff?.community_fee_ct_kwh ?? 0).toFixed(2)} <span className="text-xs font-normal">Ct/kWh</span>
                                    </div>
                                    <div className="text-[10px] text-indigo-300/70 mt-0.5">{t("sharing_admin.tariff_community_sub", "Betrieb & Software")}</div>
                                </div>
                                <div>
                                    <div className="text-[11px] text-indigo-300 font-semibold uppercase">{t("sharing_admin.tariff_savings_vs_grid", "Ersparnis vs. Netz")}</div>
                                    <div className="text-2xl font-black mt-1 text-cyan-300">
                                        ~22,00 <span className="text-xs font-normal">Ct/kWh</span>
                                    </div>
                                    <div className="text-[10px] text-indigo-300/70 mt-0.5">{t("sharing_admin.tariff_savings_sub", "ggü. Grundversorger")}</div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* STATEMENTS */}
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                                    {t("sharing_admin.statements_title", "Monatliche Abrechnungsnachweise der Bürgerenergiegenossenschaft")}
                                </h3>
                                <p className="text-xs text-slate-500">
                                    {t("sharing_admin.statements_sub", "15-Minuten-scharfe Verrechnung von Erzeugung, Bezug und internen Gutschriften")}
                                </p>
                            </div>
                            <div className="flex items-center gap-1.5">
                                <button onClick={() => exportStatements("xlsx")} className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-xs rounded-lg border cursor-pointer">
                                    Excel
                                </button>
                                <button onClick={() => exportStatements("csv")} className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-xs rounded-lg border cursor-pointer">
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
                                            <div className="text-xs text-slate-500 mt-1">{t("sharing_admin.statement_member", "Mitglied:")} <span className="font-medium text-slate-700 dark:text-slate-300">{stmt.user_email}</span></div>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            <div className="text-right">
                                                <div className="text-xs text-slate-400">{stmt.is_payout ? t("sharing_admin.statement_credit", "Gutschrift") : t("sharing_admin.statement_claim", "Forderung")}</div>
                                                <div className={`text-lg font-black ${stmt.is_payout ? "text-emerald-600" : "text-rose-600"}`}>
                                                    {stmt.is_payout ? "+" : ""}{Number(stmt.net_balance_eur ?? 0).toFixed(2)} €
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => downloadStatementPdf(stmt.id, stmt.statement_number)}
                                                disabled={downloadingId === stmt.id}
                                                className="px-3 py-1.5 bg-white dark:bg-slate-900 text-indigo-600 border border-indigo-200 dark:border-indigo-800 rounded-lg text-xs font-bold cursor-pointer"
                                            >
                                                📄 PDF
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-xs text-slate-400 bg-slate-50 dark:bg-slate-800/30 rounded-xl border border-dashed">
                                {t("sharing_admin.no_statements", "Noch keine Monatsabrechnungen erstellt. Klicke auf 'Monatsabrechnung anstoßen'.")}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* TAB 5: METERS */}
            {activeTab === "meters" && <VirtualMasterMeterHub tenant={tenant} />}

            {/* TAB 6: VPP */}
            {activeTab === "vpp" && <VppAggregatorCockpit />}

            {/* TAB 7: MSB */}
            {activeTab === "msb" && <MsbSmartMeterHub tenant={tenant} />}

            {/* TAB 8: AUDIT */}
            {activeTab === "audit" && (
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs">
                    <h2 className="text-sm font-bold text-slate-900 dark:text-white mb-3">{t("sharing_admin.audit_title", "Revisionssicheres Genossenschafts-Audit")}</h2>
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
            <CommunityShareModal isOpen={shareModalOpen} onClose={() => setShareModalOpen(false)} kpis={{ autarky_pct: cockpit?.autarky_pct || 88, community_shared_kwh: cockpit?.shared_kwh || 160, self_consumption_pct: cockpit?.self_consumption_pct || 94 }} />
            <WhitelabelSettingsModal isOpen={whitelabelModalOpen} onClose={() => setWhitelabelModalOpen(false)} />
            <MarketCommunicationModal isOpen={makoModalOpen} onClose={() => setMakoModalOpen(false)} tenantId={tenant?.id} />
            <CommunityInviteModal isOpen={inviteModalOpen} onClose={() => setInviteModalOpen(false)} tenant={tenant} initialRole="member" onInviteCreated={createInvite} />
        </div>
    );
}
