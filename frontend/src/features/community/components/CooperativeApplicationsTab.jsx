import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../../../api/client";

export default function CooperativeApplicationsTab({ tenant }) {
    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const [filterStatus, setFilterStatus] = useState("all");
    const [actionModal, setActionModal] = useState(null); // { type: 'reject' | 'details', app: {...} }
    const [rejectReason, setRejectReason] = useState("");

    const { data, isLoading, error, refetch } = useQuery({
        queryKey: ["cooperativeApplications", tenant?.id],
        queryFn: () => apiFetch(`/api/billing/cooperative/admin/applications/?tenant_id=${tenant?.id || ""}`),
        enabled: Boolean(tenant?.id),
    });

    const approveMutation = useMutation({
        mutationFn: (applicationId) =>
            apiFetch("/api/billing/cooperative/admin/approve/", {
                method: "POST",
                body: JSON.stringify({ application_id: applicationId }),
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["cooperativeApplications", tenant?.id] });
            queryClient.invalidateQueries({ queryKey: ["my-tenant"] });
        },
    });

    const rejectMutation = useMutation({
        mutationFn: ({ applicationId, reason }) =>
            apiFetch("/api/billing/cooperative/admin/reject/", {
                method: "POST",
                body: JSON.stringify({ application_id: applicationId, reason }),
            }),
        onSuccess: () => {
            setActionModal(null);
            setRejectReason("");
            queryClient.invalidateQueries({ queryKey: ["cooperativeApplications", tenant?.id] });
        },
    });

    const applications = data?.applications || [];
    const filteredApps = applications.filter((app) => {
        if (filterStatus === "all") return true;
        return app.status === filterStatus;
    });

    const pendingCount = applications.filter((a) => a.status === "pending").length;

    const publicJoinLink = `${window.location.origin}/join/${tenant?.slug || tenant?.id}`;

    return (
        <div className="space-y-6 animate-in fade-in duration-200">
            {/* STATS & QUICK BANNER */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">{t("cooperative.open_applications", "Offene Anträge")}</div>
                    <div className="text-2xl font-black text-amber-600 dark:text-amber-400 mt-1 flex items-center gap-2">
                        <span>⏳</span> {pendingCount}
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                        Warten auf Vorstandsbeschluss gem. § 15b GenG
                    </p>
                </div>

                <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">{t("cooperative.approved_members", "Genehmigte Mitglieder")}</div>
                    <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1 flex items-center gap-2">
                        <span>🏛️</span> {applications.filter((a) => a.status === "approved").length}
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                        Im digitalen Mitgliederverzeichnis eingetragen
                    </p>
                </div>

                <div className="p-4 rounded-2xl bg-gradient-to-br from-indigo-900 to-slate-900 text-white border border-indigo-800/60 shadow-xs flex flex-col justify-between">
                    <div>
                        <div className="text-xs font-bold text-indigo-300 uppercase tracking-wider">{t("cooperative.public_join_link", "Öffentlicher Beitrittslink")}</div>
                        <div className="text-xs text-indigo-200 mt-1 truncate font-mono">
                            {publicJoinLink}
                        </div>
                    </div>
                    <button
                        type="button"
                        onClick={() => {
                            navigator.clipboard.writeText(publicJoinLink);
                            alert("Beitrittslink in Zwischenablage kopiert!");
                        }}
                        className="mt-3 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 cursor-pointer shadow-xs"
                    >
                        <span>📋</span> Link für Neumitglieder kopieren
                    </button>
                </div>
            </div>

            {/* FILTER & HEADER */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-slate-50 dark:bg-slate-800/40 p-3 rounded-2xl border border-slate-200 dark:border-slate-800">
                <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-slate-800 dark:text-slate-200">
                        📋 Digitale Beitrittsanträge
                    </span>
                    <span className="text-xs bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded-full font-bold">
                        {filteredApps.length} von {applications.length}
                    </span>
                </div>

                <div className="flex items-center gap-1.5">
                    {[
                        { id: "all", label: "Alle" },
                        { id: "pending", label: "⏳ Ausstehend" },
                        { id: "approved", label: "✅ Genehmigt" },
                        { id: "rejected", label: "❌ Abgelehnt" },
                    ].map((f) => (
                        <button
                            key={f.id}
                            type="button"
                            onClick={() => setFilterStatus(f.id)}
                            className={`px-3 py-1 rounded-xl text-xs font-bold transition cursor-pointer ${
                                filterStatus === f.id
                                    ? "bg-indigo-600 text-white shadow-xs"
                                    : "bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 border border-slate-200 dark:border-slate-700"
                            }`}
                        >
                            {f.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* APPLICATIONS TABLE */}
            {isLoading ? (
                <div className="p-12 text-center text-sm text-slate-400">
                    {t("common.loading", "Laden...")}
                </div>
            ) : filteredApps.length === 0 ? (
                <div className="p-12 text-center rounded-2xl bg-white dark:bg-slate-900 border border-dashed border-slate-200 dark:border-slate-800">
                    <span className="text-3xl block mb-2">📬</span>
                    <p className="text-sm font-bold text-slate-700 dark:text-slate-300">
                        {t("cooperative.no_applications_found", "Keine Beitrittsanträge für diese Auswahl gefunden")}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                        {t("cooperative.share_join_link_hint", "Teile den öffentlichen Beitrittslink, um neuen Genossenschaftsmitgliedern die digitale Registrierung zu ermöglichen.")}
                    </p>
                </div>
            ) : (
                <div className="overflow-x-auto rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs">
                    <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
                        <thead className="bg-slate-50 dark:bg-slate-800/80 text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase border-b border-slate-200 dark:border-slate-800">
                            <tr>
                                <th className="py-3 px-4">{t("cooperative.applicant", "Antragsteller")}</th>
                                <th className="py-3 px-4">{t("cooperative.residence_address", "Wohnort / Anschrift")}</th>
                                <th className="py-3 px-4">{t("cooperative.shares_amount", "Anteile & Betrag")}</th>
                                <th className="py-3 px-4">{t("cooperative.statute_consent", "Satzungs-Zustimmung")}</th>
                                <th className="py-3 px-4">{t("cooperative.status_resolution", "Status & Beschluss")}</th>
                                <th className="py-3 px-4 text-right">{t("common.action", "Aktion")}</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                            {filteredApps.map((app) => (
                                <tr key={app.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition">
                                    <td className="py-3 px-4">
                                        <div className="font-bold text-slate-900 dark:text-white">
                                            {app.first_name} {app.last_name}
                                        </div>
                                        <div className="text-[11px] text-slate-400 font-mono">{app.email}</div>
                                        {app.phone && <div className="text-[10px] text-slate-400">📞 {app.phone}</div>}
                                    </td>
                                    <td className="py-3 px-4">
                                        <div>{app.street} {app.house_number}</div>
                                        <div className="text-[11px] text-slate-400">{app.postal_code} {app.city}</div>
                                    </td>
                                    <td className="py-3 px-4">
                                        <div className="font-bold text-indigo-600 dark:text-indigo-400">
                                            {app.shares_count} Geschäftsanteil{app.shares_count > 1 ? "e" : ""}
                                        </div>
                                        <div className="text-[11px] text-slate-400">
                                            {Number(app.total_shares_eur).toFixed(2)} €
                                        </div>
                                    </td>
                                    <td className="py-3 px-4">
                                        {app.statute_accepted ? (
                                            <div className="space-y-0.5">
                                                <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 px-2 py-0.5 rounded-full">
                                                    ✓ Satzung {app.statute_version_accepted}
                                                </span>
                                                <div className="text-[10px] text-slate-400">
                                                    {app.statute_accepted_at ? new Date(app.statute_accepted_at).toLocaleString("de-DE") : "Dokumentiert"}
                                                </div>
                                            </div>
                                        ) : (
                                            <span className="text-rose-600 font-bold">⚠️ Nicht zugestimmt</span>
                                        )}
                                    </td>
                                    <td className="py-3 px-4">
                                        {app.status === "pending" && (
                                            <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800 px-2 py-0.5 rounded-full">
                                                ⏳ Ausstehend
                                            </span>
                                        )}
                                        {app.status === "approved" && (
                                            <div className="space-y-0.5">
                                                <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 px-2 py-0.5 rounded-full">
                                                    ✅ Beschluss: Angenommen
                                                </span>
                                                {app.member_number && (
                                                    <div className="text-[10px] font-mono text-indigo-600 dark:text-indigo-400 font-bold">
                                                        Mitglieds-Nr: {app.member_number}
                                                    </div>
                                                )}
                                                {app.board_approved_at && (
                                                    <div className="text-[10px] text-slate-400">
                                                        am {new Date(app.board_approved_at).toLocaleDateString("de-DE")}
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                        {app.status === "rejected" && (
                                            <div className="space-y-0.5">
                                                <span className="inline-flex items-center gap-1 text-[11px] font-bold text-rose-700 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 px-2 py-0.5 rounded-full">
                                                    ❌ Abgelehnt
                                                </span>
                                                {app.rejection_reason && (
                                                    <div className="text-[10px] text-slate-400 max-w-xs truncate" title={app.rejection_reason}>
                                                        Grund: {app.rejection_reason}
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </td>
                                    <td className="py-3 px-4 text-right">
                                        {app.status === "pending" ? (
                                            <div className="flex items-center justify-end gap-1.5">
                                                <button
                                                    type="button"
                                                    onClick={() => approveMutation.mutate(app.id)}
                                                    disabled={approveMutation.isPending}
                                                    className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-1 cursor-pointer shadow-xs disabled:opacity-50"
                                                >
                                                    <span>✓</span> Aufnehmen
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => setActionModal({ type: "reject", app })}
                                                    className="px-2.5 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 rounded-lg text-xs font-bold transition border border-rose-200 dark:border-rose-800 cursor-pointer"
                                                >
                                                    Ablehnen
                                                </button>
                                            </div>
                                        ) : (
                                            <span className="text-[11px] text-slate-400 font-mono">
                                                Abgeschlossen
                                            </span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* REJECTION MODAL */}
            {actionModal?.type === "reject" && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 max-w-md w-full space-y-4 shadow-2xl">
                        <div className="flex items-center justify-between">
                            <h3 className="text-base font-bold text-slate-900 dark:text-white">
                                Antrag ablehnen
                            </h3>
                            <button
                                type="button"
                                onClick={() => setActionModal(null)}
                                className="text-slate-400 hover:text-slate-600 cursor-pointer text-sm"
                            >
                                ✕
                            </button>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                            Möchtest du den Beitrittsantrag von <strong className="text-slate-800 dark:text-white">{actionModal.app.first_name} {actionModal.app.last_name}</strong> wirklich ablehnen?
                        </p>
                        <div>
                            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                                Begründung für den Vorstandsbeschluss (optional):
                            </label>
                            <textarea
                                rows={3}
                                value={rejectReason}
                                onChange={(e) => setRejectReason(e.target.value)}
                                placeholder="z. B. Außerhalb des genossenschaftlichen Versorgungsgebiets..."
                                className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-3 text-xs text-slate-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-rose-500"
                            />
                        </div>
                        <div className="flex items-center justify-end gap-2 pt-2">
                            <button
                                type="button"
                                onClick={() => setActionModal(null)}
                                className="px-4 py-2 text-xs font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition cursor-pointer"
                            >
                                Abbrechen
                            </button>
                            <button
                                type="button"
                                onClick={() =>
                                    rejectMutation.mutate({
                                        applicationId: actionModal.app.id,
                                        reason: rejectReason,
                                    })
                                }
                                disabled={rejectMutation.isPending}
                                className="px-4 py-2 text-xs font-bold bg-rose-600 hover:bg-rose-500 text-white rounded-xl transition cursor-pointer shadow-xs disabled:opacity-50"
                            >
                                {rejectMutation.isPending ? "Speichere..." : "Antrag ablehnen"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
