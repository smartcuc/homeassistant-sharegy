/*
# src/features/support/components/SupportDrawer.jsx
# Context-aware Universal Support Drawer with FAQ Deflection & Ticket Management
*/

import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import {
    X,
    LifeBuoy,
    PlusCircle,
    Inbox,
    BookOpen,
    Send,
    AlertCircle,
    CheckCircle2,
    Sparkles,
    ExternalLink,
    ChevronRight,
    RefreshCw,
} from "lucide-react";
import { fetchUserTickets, createTicket, fetchDeflectionSuggestions } from "../api";
import TicketChatModal from "./TicketChatModal";

export default function SupportDrawer({ isOpen, onClose, defaultContext = {} }) {
    const location = useLocation();

    const [activeTab, setActiveTab] = useState("new_ticket"); // 'new_ticket' | 'my_tickets' | 'help'
    const [tickets, setTickets] = useState([]);
    const [loadingTickets, setLoadingTickets] = useState(false);
    const [selectedTicketId, setSelectedTicketId] = useState(null);

    // Form state
    const [subject, setSubject] = useState("");
    const [category, setCategory] = useState("general");
    const [priority, setPriority] = useState("medium");
    const [message, setMessage] = useState("");
    const [attachments, setAttachments] = useState([]);
    const [submitting, setSubmitting] = useState(false);
    const [formSuccess, setFormSuccess] = useState(false);

    // Deflection state
    const [deflectionArticles, setDeflectionArticles] = useState([]);

    // Live search deflection when user types subject (debounced, 300ms)
    useEffect(() => {
        if (!subject || subject.trim().length < 3) {
            // Schedule the clear inside a microtask to avoid setState-in-effect
            const id = setTimeout(() => setDeflectionArticles([]), 0);
            return () => clearTimeout(id);
        }

        const timer = setTimeout(async () => {
            try {
                const results = await fetchDeflectionSuggestions(subject);
                setDeflectionArticles(results);
            } catch (e) {
                console.error("Deflection lookup error:", e);
            }
        }, 300);

        return () => clearTimeout(timer);
    }, [subject]);

    // Standalone loader — called by event handlers (tab switch, after ticket create)
    const loadTickets = async () => {
        setLoadingTickets(true);
        try {
            const data = await fetchUserTickets();
            setTickets(data);
        } catch (err) {
            console.error("Error loading tickets:", err);
        } finally {
            setLoadingTickets(false);
        }
    };

    useEffect(() => {
        if (!isOpen) return;
        let cancelled = false;
        (async () => {
            setLoadingTickets(true);
            try {
                const data = await fetchUserTickets();
                if (!cancelled) setTickets(data);
            } catch (err) {
                console.error("Error loading tickets:", err);
            } finally {
                if (!cancelled) setLoadingTickets(false);
            }
        })();
        return () => { cancelled = true; };
    }, [isOpen]);

    if (!isOpen) return null;

    const handleCreateTicket = async (e) => {
        e.preventDefault();
        if (!subject.trim() || !message.trim() || submitting) return;

        setSubmitting(true);
        try {
            const contextPayload = {
                route: location.pathname,
                url: window.location.href,
                userAgent: navigator.userAgent,
                screen: `${window.innerWidth}x${window.innerHeight}`,
                ...defaultContext,
            };

            const formData = new FormData();
            formData.append("project_key", "sharegy");
            formData.append("subject", subject.trim());
            formData.append("category", category);
            formData.append("priority", priority);
            formData.append("initial_message", message.trim());
            formData.append("context_payload", JSON.stringify(contextPayload));
            attachments.forEach((f) => formData.append("attachments", f));

            const newTicket = await createTicket(formData);
            setFormSuccess(true);
            setSubject("");
            setMessage("");
            setAttachments([]);
            setDeflectionArticles([]);

            await loadTickets();
            setTimeout(() => {
                setFormSuccess(false);
                setSelectedTicketId(newTicket.id);
            }, 800);
        } catch (err) {
            alert(err.message || "Fehler beim Erstellen des Tickets");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <>
            {/* Backdrop */}
            <div
                onClick={onClose}
                className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs transition-opacity animate-in fade-in"
            />

            {/* Slide-over Drawer */}
            <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white dark:bg-slate-900 shadow-2xl border-l border-slate-200 dark:border-slate-800 flex flex-col animate-in slide-in-from-right duration-300">
                {/* Header */}
                <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-800/50">
                    <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-sm">
                            <LifeBuoy className="w-4 h-4" />
                        </div>
                        <div>
                            <h2 className="text-base font-bold text-slate-900 dark:text-white">
                                Sharegy Support & Helpdesk
                            </h2>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                Direkter Kontakt zum Expertenteam
                            </p>
                        </div>
                    </div>

                    <button
                        type="button"
                        onClick={onClose}
                        className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Tab Switcher */}
                <div className="flex border-b border-slate-200 dark:border-slate-800 px-4 pt-2 gap-2 bg-slate-50/30 dark:bg-slate-850">
                    <button
                        type="button"
                        onClick={() => setActiveTab("new_ticket")}
                        className={`pb-2.5 px-3 text-xs font-semibold border-b-2 flex items-center gap-1.5 transition-colors ${activeTab === "new_ticket"
                            ? "border-indigo-600 text-indigo-600 dark:text-indigo-400"
                            : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400"
                            }`}
                    >
                        <PlusCircle className="w-3.5 h-3.5" />
                        Neues Ticket
                    </button>

                    <button
                        type="button"
                        onClick={() => {
                            setActiveTab("my_tickets");
                            loadTickets();
                        }}
                        className={`pb-2.5 px-3 text-xs font-semibold border-b-2 flex items-center gap-1.5 transition-colors ${activeTab === "my_tickets"
                            ? "border-indigo-600 text-indigo-600 dark:text-indigo-400"
                            : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400"
                            }`}
                    >
                        <Inbox className="w-3.5 h-3.5" />
                        Meine Tickets
                        {tickets.length > 0 && (
                            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-indigo-100 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-300 font-bold">
                                {tickets.length}
                            </span>
                        )}
                    </button>

                    <button
                        type="button"
                        onClick={() => setActiveTab("help")}
                        className={`pb-2.5 px-3 text-xs font-semibold border-b-2 flex items-center gap-1.5 transition-colors ${activeTab === "help"
                            ? "border-indigo-600 text-indigo-600 dark:text-indigo-400"
                            : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400"
                            }`}
                    >
                        <BookOpen className="w-3.5 h-3.5" />
                        Wissensportal
                    </button>
                </div>

                {/* Content Body */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {/* TAB 1: NEW TICKET FORM */}
                    {activeTab === "new_ticket" && (
                        <form onSubmit={handleCreateTicket} className="space-y-3.5">
                            {formSuccess ? (
                                <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 flex items-center gap-3">
                                    <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0" />
                                    <div className="text-sm font-medium">
                                        Support-Ticket erfolgreich erstellt! Wir öffnen den Chat...
                                    </div>
                                </div>
                            ) : (
                                <>
                                    {/* Subject */}
                                    <div>
                                        <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                                            Betreff / Kurzbeschreibung *
                                        </label>
                                        <input
                                            type="text"
                                            value={subject}
                                            onChange={(e) => setSubject(e.target.value)}
                                            placeholder="z. B. Wechselrichter verbindet sich nicht"
                                            required
                                            className="w-full px-3.5 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500 dark:text-white"
                                        />
                                    </div>

                                    {/* Deflection Box (Self-Service Suggestions) */}
                                    {deflectionArticles.length > 0 && (
                                        <div className="p-3 rounded-xl bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-200/80 dark:border-indigo-800/60 animate-in fade-in">
                                            <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-900 dark:text-indigo-300 mb-1.5">
                                                <Sparkles className="w-3.5 h-3.5 text-indigo-600 animate-pulse" />
                                                Hilft dir das sofort weiter?
                                            </div>
                                            <div className="space-y-1.5">
                                                {deflectionArticles.map((art) => (
                                                    <a
                                                        key={art.id}
                                                        href={`/help/article/${art.slug}`}
                                                        target="_blank"
                                                        rel="noreferrer"
                                                        className="flex items-center justify-between p-2 rounded-lg bg-white dark:bg-slate-900 border border-indigo-100 dark:border-indigo-900/50 text-xs font-medium text-slate-800 dark:text-slate-200 hover:bg-indigo-50/50 transition-colors group"
                                                    >
                                                        <span className="truncate pr-2">{art.title_de}</span>
                                                        <ExternalLink className="w-3 h-3 text-slate-400 group-hover:text-indigo-600 shrink-0" />
                                                    </a>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Category & Priority Grid */}
                                    <div className="grid grid-cols-2 gap-3">
                                        <div>
                                            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                                                Bereich
                                            </label>
                                            <select
                                                value={category}
                                                onChange={(e) => setCategory(e.target.value)}
                                                className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 dark:text-white"
                                            >
                                                <option value="hardware">⚡ Hardware & Zähler</option>
                                                <option value="forecast">☀️ Solar & Lastprognose</option>
                                                <option value="tariff">💶 Tarife & Börsenpreis</option>
                                                <option value="billing">💳 Abrechnung & Plan</option>
                                                <option value="alerts">🔔 Alarme & Benachrichtigung</option>
                                                <option value="general">💬 Allgemeine Frage</option>
                                            </select>
                                        </div>

                                        <div>
                                            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                                                Dringlichkeit
                                            </label>
                                            <select
                                                value={priority}
                                                onChange={(e) => setPriority(e.target.value)}
                                                className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 dark:text-white"
                                            >
                                                <option value="low">Niedrig (Information)</option>
                                                <option value="medium">Normal</option>
                                                <option value="high">Hoch (Wichtige Störung)</option>
                                                <option value="urgent">Kritisch (Komplettausfall)</option>
                                            </select>
                                        </div>
                                    </div>

                                    {/* Message */}
                                    <div>
                                        <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                                            Detaillierte Fehlerbeschreibung *
                                        </label>
                                        <textarea
                                            value={message}
                                            onChange={(e) => setMessage(e.target.value)}
                                            rows={4}
                                            placeholder="Bitte beschreibe, was passiert ist und welche Schritte du bereits versucht hast..."
                                            required
                                            className="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500 dark:text-white"
                                        />
                                    </div>

                                    {/* Attachments */}
                                    <div>
                                        <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                                            Screenshots / Logs anhängen
                                        </label>
                                        <input
                                            type="file"
                                            multiple
                                            onChange={(e) => setAttachments(Array.from(e.target.files || []))}
                                            className="w-full text-xs text-slate-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200 dark:file:bg-slate-800 dark:file:text-slate-300"
                                        />
                                    </div>

                                    {/* Auto-Context Banner */}
                                    <div className="p-2.5 rounded-lg bg-slate-100 dark:bg-slate-800/60 text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-2">
                                        <AlertCircle className="w-3.5 h-3.5 shrink-0 text-slate-400" />
                                        <span>Aktuelle Seite (`{location.pathname}`) wird zur Diagnose automatisch mitgesendet.</span>
                                    </div>

                                    {/* Submit */}
                                    <button
                                        type="submit"
                                        disabled={!subject.trim() || !message.trim() || submitting}
                                        className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl text-sm font-semibold transition-all shadow-md flex items-center justify-center gap-2"
                                    >
                                        {submitting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                                        <span>Ticket eröffnen</span>
                                    </button>
                                </>
                            )}
                        </form>
                    )}

                    {/* TAB 2: MY TICKETS LIST */}
                    {activeTab === "my_tickets" && (
                        <div className="space-y-2.5">
                            {loadingTickets ? (
                                <div className="flex flex-col items-center justify-center py-12 text-slate-400 gap-2">
                                    <RefreshCw className="w-5 h-5 animate-spin text-indigo-600" />
                                    <span className="text-xs">Lade Tickets...</span>
                                </div>
                            ) : tickets.length === 0 ? (
                                <div className="text-center py-12 text-slate-400">
                                    <Inbox className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                    <p className="text-sm font-medium">Du hast aktuell keine Support-Tickets.</p>
                                    <button
                                        type="button"
                                        onClick={() => setActiveTab("new_ticket")}
                                        className="mt-3 text-xs text-indigo-600 font-semibold hover:underline"
                                    >
                                        + Neues Ticket erstellen
                                    </button>
                                </div>
                            ) : (
                                tickets.map((t) => (
                                    <div
                                        key={t.id}
                                        onClick={() => setSelectedTicketId(t.id)}
                                        className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-850 hover:border-indigo-300 dark:hover:border-indigo-800 transition-all cursor-pointer shadow-xs group"
                                    >
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="font-mono text-[11px] font-bold text-indigo-600 dark:text-indigo-400">
                                                #{t.ticket_number}
                                            </span>
                                            <span
                                                className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${t.status === "open"
                                                    ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                                                    : t.status === "in_progress"
                                                        ? "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300"
                                                        : t.status === "waiting_customer"
                                                            ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
                                                            : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                                                    }`}
                                            >
                                                {t.status_display}
                                            </span>
                                        </div>

                                        <h4 className="text-xs font-bold text-slate-800 dark:text-slate-100 truncate group-hover:text-indigo-600">
                                            {t.subject}
                                        </h4>

                                        <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400">
                                            <span>{t.message_count} Nachricht(en)</span>
                                            <span>
                                                {new Date(t.created_at).toLocaleDateString("de-DE", {
                                                    day: "2-digit",
                                                    month: "2-digit",
                                                })}
                                            </span>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}

                    {/* TAB 3: HELP CENTER QUICK ACCESS */}
                    {activeTab === "help" && (
                        <div className="space-y-3">
                            <div className="p-4 rounded-xl bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/40 text-center">
                                <BookOpen className="w-8 h-8 mx-auto text-indigo-600 mb-2" />
                                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                                    Digitales Handbuch & FAQ
                                </h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                                    Finde Antworten auf die häufigsten Fragen rund um Wechselrichter, Tarife und Abrechnung.
                                </p>
                                <a
                                    href="/help"
                                    className="mt-3 inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-700 transition-colors shadow-sm"
                                >
                                    <span>Wissensportal öffnen</span>
                                    <ChevronRight className="w-3.5 h-3.5" />
                                </a>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Ticket Chat Modal */}
            <TicketChatModal
                ticketId={selectedTicketId}
                isOpen={!!selectedTicketId}
                onClose={() => setSelectedTicketId(null)}
                onTicketUpdated={loadTickets}
            />
        </>
    );
}

