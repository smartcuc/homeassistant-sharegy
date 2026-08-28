/*
# src/features/support/components/TicketChatModal.jsx
# Modern, real-time Ticket Chat Thread with attachments and status controls
*/

import { useState, useEffect, useRef } from "react";
import {
    X,
    Send,
    Paperclip,
    CheckCircle2,
    AlertTriangle,
    ShieldAlert,
    FileText,
    Download,
    RefreshCw,
    User,
    Bot,
    ChevronDown,
    ChevronUp,
} from "lucide-react";
import { fetchTicketDetail, postTicketMessage, updateTicketStatus } from "../api";

export default function TicketChatModal({ ticketId, isOpen, onClose, onTicketUpdated }) {
    const [ticket, setTicket] = useState(null);
    const [loading, setLoading] = useState(true);
    const [replyText, setReplyText] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [showContext, setShowContext] = useState(false);
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);

    // Separate imperative loader for event handlers (send message, toggle resolve).
    const loadDetail = async () => {
        if (!ticketId) return;
        try {
            const data = await fetchTicketDetail(ticketId);
            setTicket(data);
        } catch (err) {
            console.error("Error loading ticket detail:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (!isOpen || !ticketId) return;
        let cancelled = false;
        (async () => {
            setLoading(true);
            try {
                const data = await fetchTicketDetail(ticketId);
                if (!cancelled) setTicket(data);
            } catch (err) {
                console.error("Error loading ticket detail:", err);
            } finally {
                if (!cancelled) setLoading(false);
            }
        })();
        return () => { cancelled = true; };
    }, [isOpen, ticketId]);

    useEffect(() => {
        if (ticket?.messages?.length) {
            messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
        }
    }, [ticket?.messages]);

    if (!isOpen) return null;

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if ((!replyText.trim() && selectedFiles.length === 0) || submitting) return;

        setSubmitting(true);
        try {
            const formData = new FormData();
            formData.append("body", replyText.trim());
            selectedFiles.forEach((f) => formData.append("attachments", f));

            await postTicketMessage(ticketId, formData);
            setReplyText("");
            setSelectedFiles([]);
            await loadDetail();
            if (onTicketUpdated) onTicketUpdated();
        } catch (err) {
            alert(err.message || "Fehler beim Senden");
        } finally {
            setSubmitting(false);
        }
    };

    const handleToggleResolve = async () => {
        if (!ticket) return;
        const newStatus = ticket.status === "resolved" || ticket.status === "closed" ? "open" : "resolved";
        try {
            await updateTicketStatus(ticketId, newStatus);
            await loadDetail();
            if (onTicketUpdated) onTicketUpdated();
        } catch (err) {
            alert("Status konnte nicht geändert werden: " + err.message);
        }
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case "open":
                return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">Neu / Offen</span>;
            case "in_progress":
                return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300">In Bearbeitung</span>;
            case "waiting_customer":
                return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300">Wartet auf dich</span>;
            case "resolved":
                return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">Gelöst ✓</span>;
            case "closed":
                return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-200 text-slate-600 dark:bg-slate-800 dark:text-slate-400">Geschlossen</span>;
            default:
                return <span className="px-2 py-0.5 rounded text-xs bg-slate-100 dark:bg-slate-800">{status}</span>;
        }
    };

    const getPriorityBadge = (priority) => {
        switch (priority) {
            case "urgent":
                return <span className="text-rose-600 dark:text-rose-400 font-semibold text-xs flex items-center gap-0.5"><ShieldAlert className="w-3 h-3" /> Dringend</span>;
            case "high":
                return <span className="text-orange-600 dark:text-orange-400 font-semibold text-xs flex items-center gap-0.5"><AlertTriangle className="w-3 h-3" /> Hoch</span>;
            default:
                return <span className="text-slate-500 dark:text-slate-400 text-xs">Normal</span>;
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
            <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 w-full max-w-3xl h-[85vh] flex flex-col overflow-hidden">
                {/* Header */}
                <div className="px-5 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-800/40">
                    <div className="flex-1 min-w-0 pr-4">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                            <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-indigo-100 text-indigo-700 dark:bg-indigo-950/80 dark:text-indigo-300">
                                {ticket?.ticket_number || "Lade..."}
                            </span>
                            {ticket && getStatusBadge(ticket.status)}
                            {ticket && getPriorityBadge(ticket.priority)}
                            <span className="text-xs text-slate-400">
                                {ticket?.category}
                            </span>
                        </div>
                        <h2 className="text-base font-bold text-slate-900 dark:text-white truncate">
                            {ticket?.subject || "Support-Ticket"}
                        </h2>
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            type="button"
                            onClick={handleToggleResolve}
                            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5 ${ticket?.status === "resolved" || ticket?.status === "closed"
                                ? "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200"
                                : "bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm"
                                }`}
                        >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            {ticket?.status === "resolved" || ticket?.status === "closed" ? "Wiedereröffnen" : "Als gelöst markieren"}
                        </button>

                        <button
                            type="button"
                            onClick={onClose}
                            className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Technical Context Accordion (Optional details) */}
                {ticket?.context_payload && Object.keys(ticket.context_payload).length > 0 && (
                    <div className="px-5 py-2 bg-indigo-50/50 dark:bg-indigo-950/20 border-b border-indigo-100 dark:border-indigo-900/30 text-xs">
                        <button
                            type="button"
                            onClick={() => setShowContext(!showContext)}
                            className="flex items-center justify-between w-full text-indigo-700 dark:text-indigo-300 font-medium"
                        >
                            <span>🔧 Technische Telemetrie & System-Kontext ({Object.keys(ticket.context_payload).length} Parameter)</span>
                            {showContext ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>
                        {showContext && (
                            <div className="mt-2 p-2.5 rounded bg-white dark:bg-slate-900 border border-indigo-100 dark:border-indigo-900/40 font-mono text-[11px] overflow-x-auto text-slate-700 dark:text-slate-300">
                                <pre>{JSON.stringify(ticket.context_payload, null, 2)}</pre>
                            </div>
                        )}
                    </div>
                )}

                {/* Message Thread */}
                <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-slate-50/30 dark:bg-slate-900/40">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-2">
                            <RefreshCw className="w-6 h-6 animate-spin text-indigo-600" />
                            <span className="text-sm">Lade Ticketverlauf...</span>
                        </div>
                    ) : ticket?.messages?.length === 0 ? (
                        <div className="text-center py-12 text-slate-400 text-sm">
                            Keine Nachrichten vorhanden.
                        </div>
                    ) : (
                        ticket?.messages?.map((msg) => {
                            const isStaff = msg.is_staff_reply;
                            return (
                                <div
                                    key={msg.id}
                                    className={`flex gap-3 max-w-[85%] ${isStaff ? "mr-auto" : "ml-auto flex-row-reverse"}`}
                                >
                                    <div
                                        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-white font-bold text-xs ${isStaff ? "bg-indigo-600" : "bg-emerald-600"
                                            }`}
                                    >
                                        {isStaff ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                                    </div>

                                    <div
                                        className={`rounded-2xl px-4 py-3 shadow-sm ${isStaff
                                            ? "bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 rounded-tl-none"
                                            : "bg-indigo-600 text-white rounded-tr-none"
                                            }`}
                                    >
                                        <div className="flex items-center justify-between gap-4 mb-1 text-[11px] opacity-80 font-medium">
                                            <span>{msg.sender_name} {isStaff && "(Support-Team)"}</span>
                                            <span>
                                                {new Date(msg.created_at).toLocaleString("de-DE", {
                                                    day: "2-digit",
                                                    month: "2-digit",
                                                    hour: "2-digit",
                                                    minute: "2-digit",
                                                })}
                                            </span>
                                        </div>

                                        <p className="text-sm whitespace-pre-wrap leading-relaxed">
                                            {msg.body}
                                        </p>

                                        {/* Attachments */}
                                        {msg.attachments?.length > 0 && (
                                            <div className="mt-2.5 pt-2 border-t border-white/20 dark:border-slate-700/60 space-y-1">
                                                {msg.attachments.map((att) => (
                                                    <a
                                                        key={att.id}
                                                        href={att.file_url}
                                                        target="_blank"
                                                        rel="noreferrer"
                                                        className={`flex items-center gap-1.5 text-xs py-1 px-2 rounded transition-colors ${isStaff
                                                            ? "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-200"
                                                            : "bg-indigo-700/60 text-white hover:bg-indigo-700"
                                                            }`}
                                                    >
                                                        <FileText className="w-3.5 h-3.5" />
                                                        <span className="truncate max-w-[200px]">{att.filename}</span>
                                                        <span className="opacity-70 text-[10px]">({Math.round(att.file_size / 1024)} KB)</span>
                                                        <Download className="w-3 h-3 ml-auto opacity-70" />
                                                    </a>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Footer Reply Form */}
                <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
                    {selectedFiles.length > 0 && (
                        <div className="flex gap-2 mb-2 flex-wrap">
                            {selectedFiles.map((f, i) => (
                                <span
                                    key={i}
                                    className="inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
                                >
                                    <FileText className="w-3 h-3" />
                                    {f.name}
                                    <button
                                        type="button"
                                        onClick={() => setSelectedFiles(selectedFiles.filter((_, idx) => idx !== i))}
                                        className="ml-1 text-slate-400 hover:text-rose-500"
                                    >
                                        &times;
                                    </button>
                                </span>
                            ))}
                        </div>
                    )}

                    <div className="flex items-center gap-2">
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={(e) => setSelectedFiles(Array.from(e.target.files || []))}
                            multiple
                            className="hidden"
                        />
                        <button
                            type="button"
                            onClick={() => fileInputRef.current?.click()}
                            title="Dateianhang hinzufügen"
                            className="p-2.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors shrink-0"
                        >
                            <Paperclip className="w-5 h-5" />
                        </button>

                        <input
                            type="text"
                            value={replyText}
                            onChange={(e) => setReplyText(e.target.value)}
                            placeholder="Antwort schreiben..."
                            disabled={submitting}
                            className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:text-white"
                        />

                        <button
                            type="submit"
                            disabled={(!replyText.trim() && selectedFiles.length === 0) || submitting}
                            className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl text-sm font-semibold transition-all flex items-center gap-1.5 shadow-sm shrink-0"
                        >
                            {submitting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                            <span>Senden</span>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

