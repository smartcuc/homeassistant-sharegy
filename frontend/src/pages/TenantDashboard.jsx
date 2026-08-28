/*
# src/pages/TenantDashboard.jsx
*/

import { useEffect, useState } from "react";

import { apiFetch } from "../api/client";
import { texts } from "../i18n";
import { useLang } from "../hooks/useLang";

export default function TenantDashboard() {
    const [tenant, setTenant] = useState(null);
    const [members, setMembers] = useState([]);
    const [invites, setInvites] = useState([]);
    const [logs, setLogs] = useState([]);

    const { lang } = useLang();
    const t = texts[lang];

    // ✅ Daten laden
    async function loadData() {
        try {
            const data = await apiFetch("/api/my-tenant/");

            setTenant(data.tenant);
            setMembers(data.members || []);
            setInvites(data.invites || []);

            const logData = await apiFetch("/api/audit-log/");
            setLogs(logData || []);
        } catch (err) {
            console.error("Load failed:", err);
        }
    }

    useEffect(() => {
        loadData();
    }, []);

    // ✅ INVITE ERSTELLEN
    async function createInvite(role) {
        const data = await apiFetch("/api/create-invite/", {
            method: "POST",
            body: JSON.stringify({
                tenant_id: tenant.id,
                role: role,
            }),
        });

        await loadData();

        alert(`${t.invite_link}:\n${window.location.origin}${data.link}`);
    }

    // ✅ ROLE UPDATE
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

    // ✅ MEMBER ENTFERNEN
    async function removeMember(userId) {
        await apiFetch("/api/remove-member/", {
            method: "POST",
            body: JSON.stringify({
                tenant_id: tenant.id,
                user_id: userId,
            }),
        });

        loadData();
    }

    // ✅ INVITE DEAKTIVIEREN
    async function deactivateInvite(token) {
        await apiFetch("/api/deactivate-invite/", {
            method: "POST",
            body: JSON.stringify({ token }),
        });

        loadData();
    }

    // ✅ ACTION TEXT
    function formatAction(log) {
        switch (log.action) {
            case "member_removed":
                return t.member_removed || "Mitglied entfernt";
            case "role_updated":
                return t.role_updated || "Rolle geändert";
            case "invite_created":
                return t.invite_created || "Invite erstellt";
            case "invite_deactivated":
                return t.invite_deactivated || "Invite deaktiviert";
            default:
                return log.action;
        }
    }

    function formatDate(date) {
        return new Date(date).toLocaleString();
    }

    return (
        <div className="p-6 max-w-4xl mx-auto">

            {/* ✅ TITLE */}
            <h1 className="text-2xl font-bold mb-6">
                {t.tenant_dashboard} – {tenant?.name}
            </h1>

            {/* ✅ INVITES */}
            <section className="mb-8">
                <h2 className="text-lg font-semibold mb-3">
                    {t.invites || "Einladungslinks"}
                </h2>

                {/* ✅ CREATE */}
                <div className="flex flex-wrap gap-2 mb-4">
                    <button
                        onClick={() => createInvite("member")}
                        className="bg-emerald-600 hover:bg-emerald-700 text-white px-3.5 py-1.5 rounded-lg text-xs font-semibold shadow-xs transition"
                    >
                        ⚡ Mitglied einladen
                    </button>

                    <button
                        onClick={() => createInvite("user_admin")}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-3.5 py-1.5 rounded-lg text-xs font-semibold shadow-xs transition"
                    >
                        👥 Userverwaltung
                    </button>

                    <button
                        onClick={() => createInvite("helpdesk")}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-3.5 py-1.5 rounded-lg text-xs font-semibold shadow-xs transition"
                    >
                        🛟 Helpdesk
                    </button>

                    <button
                        onClick={() => createInvite("auditor")}
                        className="bg-slate-700 hover:bg-slate-800 text-white px-3.5 py-1.5 rounded-lg text-xs font-semibold shadow-xs transition"
                    >
                        📊 Auditor / Beirat
                    </button>

                    <button
                        onClick={() => createInvite("admin")}
                        className="bg-red-600 hover:bg-red-700 text-white px-3.5 py-1.5 rounded-lg text-xs font-semibold shadow-xs transition"
                    >
                        🏛️ Energy-Admin
                    </button>
                </div>

                {/* ✅ LIST */}
                <div className="space-y-2">
                    {invites.map(i => (
                        <div key={i.token} className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-3.5 rounded-xl flex flex-col shadow-xs">

                            <div className="flex justify-between items-center">
                                <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                                    {i.role_display || i.role}
                                </span>

                                <span className="text-xs text-slate-400">
                                    Verwendet: {i.used}
                                </span>
                            </div>

                            <div className="text-xs font-mono text-slate-500 dark:text-slate-400 break-all mt-1 bg-slate-50 dark:bg-slate-800/50 p-1.5 rounded-lg">
                                {window.location.origin}/onboarding?invite={i.token}
                            </div>

                            <div className="flex gap-3 mt-2">

                                <button
                                    onClick={() =>
                                        navigator.clipboard.writeText(
                                            window.location.origin + "/onboarding?invite=" + i.token
                                        )
                                    }
                                    className="text-indigo-600 dark:text-indigo-400 font-semibold text-xs hover:underline cursor-pointer"
                                >
                                    Link kopieren
                                </button>

                                <button
                                    onClick={() => deactivateInvite(i.token)}
                                    className="text-red-500 text-xs hover:underline cursor-pointer"
                                >
                                    Deaktivieren
                                </button>

                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* ✅ MEMBERS */}
            <section>
                <h2 className="text-lg font-semibold mb-3">
                    {t.members || "Mitglieder & Rollen"}
                </h2>

                <div className="space-y-2">
                    {members.map(m => (
                        <div
                            key={m.id}
                            className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-3.5 rounded-xl flex justify-between items-center shadow-xs"
                        >
                            <span className="text-sm font-medium text-slate-900 dark:text-slate-100">{m.email}</span>

                            <div className="flex gap-2 items-center">

                                <select
                                    value={m.role}
                                    onChange={(e) =>
                                        updateRole(m.id, e.target.value)
                                    }
                                    className="text-xs font-medium border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-lg px-2.5 py-1.5 dark:text-white"
                                >
                                    <option value="member">⚡ Mitglied</option>
                                    <option value="user_admin">👥 Energy-Userverwaltung</option>
                                    <option value="helpdesk">🛟 Energy-Helpdesk</option>
                                    <option value="auditor">📊 Auditor / Kassenprüfer</option>
                                    <option value="admin">🏛️ Energy-Admin</option>
                                </select>

                                <button
                                    onClick={() => removeMember(m.id)}
                                    className="text-red-600 hover:text-red-700 text-xs font-semibold px-2 py-1 rounded hover:bg-red-50 dark:hover:bg-red-950/30 transition cursor-pointer"
                                >
                                    Entfernen
                                </button>

                            </div>
                        </div>
                    ))}
                </div>
            </section>


            {/* ✅ AUDIT LOG */}
            <section className="mt-10">
                <h2 className="text-lg font-semibold mb-3">
                    {t.audit_log || "Aktivität"}
                </h2>

                <div className="space-y-2 max-h-80 overflow-y-auto">

                    {logs
                        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                        .slice(0, 30)
                        .map((log, idx) => (

                            <div
                                key={idx}
                                className={`border p-3 rounded text-sm ${log.action === "member_removed"
                                    ? "border-red-400"
                                    : ""
                                    }`}
                            >
                                <div className="flex justify-between">
                                    <span className="font-medium">
                                        {formatAction(log)}
                                    </span>

                                    <span className="text-gray-400 text-xs">
                                        {formatDate(log.created_at)}
                                    </span>
                                </div>

                                <div className="text-xs text-gray-500 mt-1">
                                    {log.user} → {log.target || "-"}
                                </div>

                            </div>
                        ))}

                </div>
            </section>

        </div>
    );
}

