/*
# src/features/support/pages/AgentSupportHubPage.jsx
# Unified Support Agent Command Center for Sharegy & Factofy
*/

import { useState, useEffect } from "react";

import { LifeBuoy, Search, RefreshCw, Send } from "lucide-react";
import {
    fetchAgentTickets,
    fetchTicketDetail,
    updateAgentTicket,
    postAgentInternalNote,
    postTicketMessage,
    fetchCannedResponses,
} from "../api";

export default function AgentSupportHubPage() {

    const [kpis, setKpis] = useState({ total: 0, open: 0, in_progress: 0, waiting_customer: 0, resolved: 0, sharegy_count: 0, factofy_count: 0 });
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);

    // Filters
    const [selectedProject, setSelectedProject] = useState("all"); // 'all' | 'sharegy' | 'factofy'
    const [selectedStatus, setSelectedStatus] = useState("all");
    const [selectedPriority] = useState("all");
    const [searchQuery, setSearchQuery] = useState("");

    // Selected Ticket Pane
    const [activeTicket, setActiveTicket] = useState(null);
    const [loadingDetail, setLoadingDetail] = useState(false);
    const [replyText, setReplyText] = useState("");
    const [isInternalNote, setIsInternalNote] = useState(false);
    const [cannedResponses, setCannedResponses] = useState([]);
    const [submittingReply, setSubmittingReply] = useState(false);

    // Bump refreshCounter to trigger a re-fetch from event handlers.
    const [refreshCounter, setRefreshCounter] = useState(0);
    const triggerRefresh = () => setRefreshCounter((c) => c + 1);

    useEffect(() => {
        let cancelled = false;
        (async () => {
            setLoading(true);
            try {
                const data = await fetchAgentTickets({
                    project_key: selectedProject,
                    status: selectedStatus,
                    priority: selectedPriority,
                    search: searchQuery,
                });
                if (!cancelled) {
                    setKpis(data.kpis);
                    setTickets(data.tickets);
                }
            } catch (err) {
                console.error("Error loading agent tickets:", err);
            } finally {
                if (!cancelled) setLoading(false);
            }
        })();
        return () => { cancelled = true; };
    }, [selectedProject, selectedStatus, selectedPriority, refreshCounter]); // eslint-disable-line react-hooks/exhaustive-deps

    const handleSearchSubmit = (e) => {
        e.preventDefault();
        triggerRefresh();
    };

    const handleSelectTicket = async (ticketId) => {
        setLoadingDetail(true);
        try {
            const detail = await fetchTicketDetail(ticketId);
            setActiveTicket(detail);
            const responses = await fetchCannedResponses(detail.project_key);
            setCannedResponses(responses);
        } catch (err) {
            alert("Ticket konnte nicht geladen werden: " + err.message);
        } finally {
            setLoadingDetail(false);
        }
    };

    const handleSendAgentReply = async (e) => {
        e.preventDefault();
        if (!replyText.trim() || !activeTicket || submittingReply) return;

        setSubmittingReply(true);
        try {
            if (isInternalNote) {
                await postAgentInternalNote(activeTicket.id, replyText.trim());
            } else {
                const formData = new FormData();
                formData.append("body", replyText.trim());
                await postTicketMessage(activeTicket.id, formData);
            }
            setReplyText("");
            const updated = await fetchTicketDetail(activeTicket.id);
            setActiveTicket(updated);
            triggerRefresh();
        } catch (err) {
            alert("Fehler beim Senden: " + err.message);
        } finally {
            setSubmittingReply(false);
        }
    };

    const handleStatusChange = async (newStatus) => {
        if (!activeTicket) return;
        try {
            await updateAgentTicket(activeTicket.id, { status: newStatus });
            const updated = await fetchTicketDetail(activeTicket.id);
            setActiveTicket(updated);
            triggerRefresh();
        } catch (err) {
            alert("Statusänderung fehlgeschlagen: " + err.message);
        }
    };

    const insertCanned = (body) => {
        setReplyText((prev) => (prev ? `${prev}\n${body}` : body));
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-6">
            <div className="max-w-7xl mx-auto space-y-6">
                {/* Header & Project Switcher */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
                    <div>
                        <div className="flex items-center gap-2.5 mb-1">
                            <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-sm">
                                <LifeBuoy className="w-5 h-5" />
                            </div>
                            <h1 className="text-xl font-bold text-slate-900 dark:text-white">
                                Support & Incident Hub
                            </h1>
                            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">
                                Multi-Project Triage
                            </span>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                            Zentrale Bearbeitung aller Kunden- & Systemtickets aus Sharegy HEMS und Factofy Digital Twin
                        </p>
                    </div>

                    {/* Project Filter Pills */}
                    <div className="flex items-center gap-2 p-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 self-start md:self-auto">
                        <button
                            type="button"
                            onClick={() => setSelectedProject("all")}
                            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${selectedProject === "all"
                                ? "bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-300 shadow-xs"
                                : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                                }`}
                        >
                            🌐 Alle ({kpis.total})
                        </button>
                        <button
                            type="button"
                            onClick={() => setSelectedProject("sharegy")}
                            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${selectedProject === "sharegy"
                                ? "bg-emerald-600 text-white shadow-xs"
                                : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                                }`}
                        >
                            ☀️ Sharegy ({kpis.sharegy_count})
                        </button>
                        <button
                            type="button"
                            onClick={() => setSelectedProject("factofy")}
                            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${selectedProject === "factofy"
                                ? "bg-blue-600 text-white shadow-xs"
                                : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                                }`}
                        >
                            🏙️ Factofy ({kpis.factofy_count})
                        </button>
                    </div>
                </div>

                {/* KPI Overview Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
                    <div
                        onClick={() => setSelectedStatus("open")}
                        className={`p-4 rounded-xl border transition-all cursor-pointer ${selectedStatus === "open"
                            ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-500 shadow-xs"
                            : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-emerald-300"
                            }`}
                    >
                        <div className="text-xs font-medium text-emerald-700 dark:text-emerald-400 mb-1">Neu / Offen</div>
                        <div className="text-2xl font-black text-slate-900 dark:text-white">{kpis.open}</div>
                    </div>

                    <div
                        onClick={() => setSelectedStatus("in_progress")}
                        className={`p-4 rounded-xl border transition-all cursor-pointer ${selectedStatus === "in_progress"
                            ? "bg-blue-50 dark:bg-blue-950/40 border-blue-500 shadow-xs"
                            : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-blue-300"
                            }`}
                    >
                        <div className="text-xs font-medium text-blue-700 dark:text-blue-400 mb-1">In Bearbeitung</div>
                        <div className="text-2xl font-black text-slate-900 dark:text-white">{kpis.in_progress}</div>
                    </div>

                    <div
                        onClick={() => setSelectedStatus("waiting_customer")}
                        className={`p-4 rounded-xl border transition-all cursor-pointer ${selectedStatus === "waiting_customer"
                            ? "bg-amber-50 dark:bg-amber-950/40 border-amber-500 shadow-xs"
                            : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-amber-300"
                            }`}
                    >
                        <div className="text-xs font-medium text-amber-700 dark:text-amber-400 mb-1">Wartet auf Kunde</div>
                        <div className="text-2xl font-black text-slate-900 dark:text-white">{kpis.waiting_customer}</div>
                    </div>

                    <div
                        onClick={() => setSelectedStatus("resolved")}
                        className={`p-4 rounded-xl border transition-all cursor-pointer ${selectedStatus === "resolved"
                            ? "bg-slate-100 dark:bg-slate-800 border-slate-500 shadow-xs"
                            : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-400"
                            }`}
                    >
                        <div className="text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">Gelöst</div>
                        <div className="text-2xl font-black text-slate-900 dark:text-white">{kpis.resolved}</div>
                    </div>
                </div>

                {/* 2-Column Split: Ticket List (Left) + Detail & Chat Thread (Right) */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                    {/* LEFT COLUMN: TICKET LIST */}
                    <div className="lg:col-span-5 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm flex flex-col h-[750px]">
                        {/* Search Bar */}
                        <form onSubmit={handleSearchSubmit} className="p-3 border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-850 flex gap-2">
                            <div className="relative flex-1">
                                <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    placeholder="Ticket-Nr, Kunde, Begriff..."
                                    className="w-full pl-9 pr-3 py-1.5 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 dark:text-white"
                                />
                            </div>
                            <button
                                type="submit"
                                className="px-3 py-1.5 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-semibold hover:bg-slate-300"
                            >
                                Suchen
                            </button>
                        </form>

                        {/* List */}
                        <div className="flex-1 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800/60">
                            {loading ? (
                                <div className="p-12 text-center text-slate-400 text-xs">
                                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-indigo-600" />
                                    Lade Tickets...
                                </div>
                            ) : tickets.length === 0 ? (
                                <div className="p-12 text-center text-slate-400 text-xs">
                                    Keine Tickets für diesen Filter gefunden.
                                </div>
                            ) : (
                                tickets.map((t) => {
                                    const isSelected = activeTicket?.id === t.id;
                                    return (
                                        <div
                                            key={t.id}
                                            onClick={() => handleSelectTicket(t.id)}
                                            className={`p-3.5 transition-all cursor-pointer ${isSelected
                                                ? "bg-indigo-50/80 dark:bg-indigo-950/40 border-l-4 border-indigo-600"
                                                : "hover:bg-slate-50 dark:hover:bg-slate-800/40"
                                                }`}
                                        >
                                            <div className="flex items-center justify-between mb-1">
                                                <div className="flex items-center gap-1.5">
                                                    <span
                                                        className={`text-[9px] font-bold px-1.5 py-0.2 rounded uppercase ${t.project_key === "factofy"
                                                            ? "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300"
                                                            : "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                                                            }`}
                                                    >
                                                        {t.project_key}
                                                    </span>
                                                    <span className="font-mono text-xs font-bold text-slate-800 dark:text-slate-200">
                                                        #{t.ticket_number}
                                                    </span>
                                                </div>
                                                <span className="text-[10px] text-slate-400">
                                                    {new Date(t.created_at).toLocaleDateString("de-DE", {
                                                        day: "2-digit",
                                                        month: "2-digit",
                                                        hour: "2-digit",
                                                        minute: "2-digit",
                                                    })}
                                                </span>
                                            </div>

                                            <h4 className="text-xs font-semibold text-slate-900 dark:text-white truncate">
                                                {t.subject}
                                            </h4>

                                            <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
                                                <span className="truncate max-w-[180px]">
                                                    {t.contact_name || t.contact_email || "Gast"}
                                                </span>
                                                <span className="font-medium">{t.status_display}</span>
                                            </div>
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </div>

                    {/* RIGHT COLUMN: ACTIVE TICKET DETAIL & CHAT */}
                    <div className="lg:col-span-7 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm h-[750px] flex flex-col">
                        {loadingDetail ? (
                            <div className="flex-1 flex flex-col items-center justify-center text-slate-400 text-xs gap-2">
                                <RefreshCw className="w-6 h-6 animate-spin text-indigo-600" />
                                <span>Lade Ticket-Details...</span>
                            </div>
                        ) : !activeTicket ? (
                            <div className="flex-1 flex flex-col items-center justify-center text-slate-400 p-8 text-center">
                                <LifeBuoy className="w-12 h-12 opacity-30 mb-3" />
                                <h3 className="text-sm font-bold text-slate-700 dark:text-slate-300">
                                    Kein Ticket ausgewählt
                                </h3>
                                <p className="text-xs max-w-sm mt-1">
                                    Wähle links ein Support-Ticket aus, um den Nachrichtenverlauf zu sehen und Antworten oder interne Notizen zu verfassen.
                                </p>
                            </div>
                        ) : (
                            <>
                                {/* Ticket Detail Header */}
                                <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-850">
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center gap-2">
                                            <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                                                #{activeTicket.ticket_number}
                                            </span>
                                            <span className="text-xs font-semibold uppercase px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                                                {activeTicket.project_key}
                                            </span>
                                        </div>

                                        {/* Status Changer */}
                                        <div className="flex items-center gap-1.5">
                                            <select
                                                value={activeTicket.status}
                                                onChange={(e) => handleStatusChange(e.target.value)}
                                                className="text-xs font-semibold px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 dark:text-white"
                                            >
                                                <option value="open">🟢 Neu / Offen</option>
                                                <option value="in_progress">🔵 In Bearbeitung</option>
                                                <option value="waiting_customer">🟡 Wartet auf Kunde</option>
                                                <option value="resolved">✅ Gelöst</option>
                                                <option value="closed">⬛ Geschlossen</option>
                                            </select>
                                        </div>
                                    </div>

                                    <h2 className="text-sm font-bold text-slate-900 dark:text-white mb-1">
                                        {activeTicket.subject}
                                    </h2>

                                    <div className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-3 flex-wrap">
                                        <span>Kunde: <b>{activeTicket.contact_name || activeTicket.contact_email}</b></span>
                                        {activeTicket.contact_email && <span>E-Mail: <b>{activeTicket.contact_email}</b></span>}
                                        <span>Kategorie: <b>{activeTicket.category}</b></span>
                                    </div>

                                    {/* Context Details */}
                                    {activeTicket.context_payload && Object.keys(activeTicket.context_payload).length > 0 && (
                                        <div className="mt-2 p-2 rounded-lg bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/30 text-[11px] font-mono text-indigo-900 dark:text-indigo-300 overflow-x-auto">
                                            <b>🔧 Kontext:</b> {JSON.stringify(activeTicket.context_payload)}
                                        </div>
                                    )}
                                </div>

                                {/* Thread */}
                                <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/20 dark:bg-slate-900/40">
                                    {activeTicket.messages?.map((msg) => {
                                        const isInternal = msg.is_internal_note;
                                        const isStaff = msg.is_staff_reply;
                                        return (
                                            <div
                                                key={msg.id}
                                                className={`p-3.5 rounded-xl text-xs leading-relaxed ${isInternal
                                                    ? "bg-amber-50 dark:bg-amber-950/30 border border-amber-300 dark:border-amber-700/60 text-amber-950 dark:text-amber-200"
                                                    : isStaff
                                                        ? "bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/40 text-slate-900 dark:text-white ml-6"
                                                        : "bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white mr-6"
                                                    }`}
                                            >
                                                <div className="flex items-center justify-between mb-1 font-semibold text-[11px] opacity-75">
                                                    <span>
                                                        {isInternal && "🔒 INTERNE NOTIZ: "}
                                                        {msg.sender_name} {isStaff && "(Support-Agent)"}
                                                    </span>
                                                    <span>
                                                        {new Date(msg.created_at).toLocaleTimeString("de-DE", {
                                                            hour: "2-digit",
                                                            minute: "2-digit",
                                                        })}
                                                    </span>
                                                </div>
                                                <p className="whitespace-pre-wrap">{msg.body}</p>
                                            </div>
                                        );
                                    })}
                                </div>

                                {/* Reply / Note Editor */}
                                <form onSubmit={handleSendAgentReply} className="p-3 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2">
                                    {/* Toolbar */}
                                    <div className="flex items-center justify-between gap-2 text-xs">
                                        <div className="flex items-center gap-1">
                                            <button
                                                type="button"
                                                onClick={() => setIsInternalNote(false)}
                                                className={`px-2.5 py-1 rounded-md font-semibold transition-colors ${!isInternalNote
                                                    ? "bg-indigo-600 text-white"
                                                    : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300"
                                                    }`}
                                            >
                                                Öffentliche Antwort
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => setIsInternalNote(true)}
                                                className={`px-2.5 py-1 rounded-md font-semibold transition-colors ${isInternalNote
                                                    ? "bg-amber-500 text-white"
                                                    : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300"
                                                    }`}
                                            >
                                                🔒 Interne Notiz (Gelb)
                                            </button>
                                        </div>

                                        {/* Canned Snippet dropdown */}
                                        {cannedResponses.length > 0 && (
                                            <div className="flex items-center gap-1">
                                                <span className="text-[11px] text-slate-400">Textbaustein:</span>
                                                <select
                                                    onChange={(e) => {
                                                        const selected = cannedResponses.find((r) => r.id.toString() === e.target.value);
                                                        if (selected) insertCanned(selected.body_de);
                                                        e.target.value = "";
                                                    }}
                                                    className="text-[11px] px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 dark:text-white"
                                                >
                                                    <option value="">Auswählen...</option>
                                                    {cannedResponses.map((r) => (
                                                        <option key={r.id} value={r.id}>
                                                            {r.title} (!{r.shortcut})
                                                        </option>
                                                    ))}
                                                </select>
                                            </div>
                                        )}
                                    </div>

                                    {/* Textarea */}
                                    <div className="flex gap-2">
                                        <textarea
                                            value={replyText}
                                            onChange={(e) => setReplyText(e.target.value)}
                                            rows={3}
                                            placeholder={
                                                isInternalNote
                                                    ? "Interne Notiz für das Team erfassen (Kunde sieht dies nicht)..."
                                                    : "Antwort an den Kunden verfassen..."
                                            }
                                            className={`flex-1 p-2.5 text-xs rounded-xl border focus:outline-none focus:ring-2 dark:text-white ${isInternalNote
                                                ? "border-amber-300 dark:border-amber-700/60 bg-amber-50/50 dark:bg-amber-950/20 focus:ring-amber-500"
                                                : "border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-indigo-500"
                                                }`}
                                        />
                                        <button
                                            type="submit"
                                            disabled={!replyText.trim() || submittingReply}
                                            className={`px-4 rounded-xl text-xs font-bold text-white flex flex-col items-center justify-center gap-1 shadow-sm transition-all shrink-0 ${isInternalNote
                                                ? "bg-amber-600 hover:bg-amber-700"
                                                : "bg-indigo-600 hover:bg-indigo-700"
                                                }`}
                                        >
                                            <Send className="w-4 h-4" />
                                            <span>{isInternalNote ? "Notiz" : "Senden"}</span>
                                        </button>
                                    </div>
                                </form>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

