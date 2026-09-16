/*
# src/features/support/components/SupportDrawer.jsx
# Context-aware Universal Support & Knowledge Base Drawer
*/

import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { useLocation, useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
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
    Lock,
    Crown,
    Search,
    Edit3,
    Lightbulb,
    FileText,
} from "lucide-react";
import { fetchUserTickets, createTicket, fetchDeflectionSuggestions } from "../api";
import { fetchContextArticles, fetchHelpArticles } from "../../help/api";
import { useUser } from "../../../hooks/useUser";
import TicketChatModal from "./TicketChatModal";
import HelpArticleEditorModal from "../../help/components/HelpArticleEditorModal";

export default function SupportDrawer({ isOpen, onClose, defaultContext = {}, initialTab = "help" }) {
    const location = useLocation();
    const navigate = useNavigate();
    const { t, i18n } = useTranslation();
    const { user } = useUser();

    // Permissions
    const isStaffOrAdmin = Boolean(
        user?.is_staff ||
        user?.is_superuser ||
        user?.is_platform_admin ||
        user?.is_platform_helpdesk ||
        user?.memberships?.some((m) => ["admin", "user_admin", "helpdesk"].includes(m.role))
    );
    const isPro = Boolean(user?.is_pro);
    const canChoosePriority = isStaffOrAdmin || isPro;
    const isEnglish = i18n.language?.startsWith("en");

    const [activeTab, setActiveTab] = useState(initialTab); // 'help' | 'new_ticket' | 'my_tickets'
    const [tickets, setTickets] = useState([]);
    const [loadingTickets, setLoadingTickets] = useState(false);
    const [selectedTicketId, setSelectedTicketId] = useState(null);

    // Form state for ticket creation
    const [subject, setSubject] = useState("");
    const [category, setCategory] = useState("general");
    const [priority, setPriority] = useState("low");
    const [message, setMessage] = useState("");
    const [attachments, setAttachments] = useState([]);
    const [submitting, setSubmitting] = useState(false);
    const [formSuccess, setFormSuccess] = useState(false);

    // Deflection state in ticket form
    const [deflectionArticles, setDeflectionArticles] = useState([]);

    // Knowledge Base / Help Tab state
    const [helpSearchTerm, setHelpSearchTerm] = useState("");
    const [helpArticles, setHelpArticles] = useState([]);
    const [loadingHelpArticles, setLoadingHelpArticles] = useState(false);
    const [editingArticle, setEditingArticle] = useState(null);

    // Calculate context key from location path
    const getContextKey = () => {
        if (defaultContext.contextKey) return defaultContext.contextKey;
        const path = location.pathname.replace(/^\/app\/?/, "");
        if (!path) return "dashboard";
        return path.split("/")[0] || "dashboard";
    };
    const contextKey = getContextKey();

    // Load Help articles (Context-based or Search)
    const loadHelpContent = async (search = "") => {
        setLoadingHelpArticles(true);
        try {
            if (search.trim().length >= 2) {
                const results = await fetchHelpArticles({ search: search.trim() });
                setHelpArticles(results || []);
            } else {
                const contextData = await fetchContextArticles(contextKey);
                setHelpArticles(contextData?.articles || []);
            }
        } catch (err) {
            console.error("Error loading help articles in SupportDrawer:", err);
        } finally {
            setLoadingHelpArticles(false);
        }
    };

    // Live search deflection when user types subject (debounced, 300ms)
    useEffect(() => {
        if (!subject || subject.trim().length < 3) {
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

    // Help tab search debouncing
    useEffect(() => {
        if (!isOpen || activeTab !== "help") return;
        const timer = setTimeout(() => {
            loadHelpContent(helpSearchTerm);
        }, 250);
        return () => clearTimeout(timer);
    }, [isOpen, activeTab, helpSearchTerm, contextKey]);

    // Tickets Loader
    const loadTickets = async () => {
        setLoadingTickets(true);
        try {
            const data = await fetchUserTickets();
            setTickets(data || []);
        } catch (err) {
            console.error("Error loading tickets:", err);
        } finally {
            setLoadingTickets(false);
        }
    };

    useEffect(() => {
        if (!isOpen) return;
        if (user) {
            loadTickets();
        }
    }, [isOpen, user]);

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

    /* ESC schließen */
    useEffect(() => {
        if (!isOpen) return;
        function handleKey(e) {
            if (e.key === "Escape") onClose();
        }
        window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [isOpen, onClose]);

    const handleArticleClick = (slug) => {
        onClose();
        navigate(`/app/help/${slug}`);
    };

    if (!isOpen) return null;

    return createPortal(
        <>
            {/* Backdrop */}
            <div
                onClick={onClose}
                className="fixed inset-0 z-40 bg-slate-950/60 backdrop-blur-xs transition-opacity animate-in fade-in cursor-pointer"
            />

            {/* Slide-over Drawer */}
            <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white dark:bg-slate-900 shadow-2xl border-l border-slate-200 dark:border-slate-800 flex flex-col animate-in slide-in-from-right duration-300">
                
                {/* Header */}
                <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/70 dark:bg-slate-800/60">
                    <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-sm">
                            <LifeBuoy className="w-4 h-4" />
                        </div>
                        <div>
                            <h2 className="text-base font-bold text-slate-900 dark:text-white">
                                {t("support.title", "Hilfe- & Support-Center")}
                            </h2>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                {t("support.subtitle", "Hilfecenter, Anleitungen & Support-Anfragen")}
                            </p>
                        </div>
                    </div>

                    <button
                        type="button"
                        onClick={onClose}
                        className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Tab Switcher */}
                <div className="flex border-b border-slate-200 dark:border-slate-800 px-4 pt-2 gap-1 bg-slate-50/30 dark:bg-slate-850">
                    <button
                        type="button"
                        onClick={() => setActiveTab("help")}
                        className={`pb-2.5 px-3 text-xs font-semibold border-b-2 flex items-center gap-1.5 transition-colors ${activeTab === "help"
                            ? "border-indigo-600 text-indigo-600 dark:text-indigo-400"
                            : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400"
                            }`}
                    >
                        <BookOpen className="w-3.5 h-3.5" />
                        {t("support.tab_faq", "Hilfecenter & FAQs")}
                    </button>

                    <button
                        type="button"
                        onClick={() => setActiveTab("new_ticket")}
                        className={`pb-2.5 px-3 text-xs font-semibold border-b-2 flex items-center gap-1.5 transition-colors ${activeTab === "new_ticket"
                            ? "border-indigo-600 text-indigo-600 dark:text-indigo-400"
                            : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400"
                            }`}
                    >
                        <PlusCircle className="w-3.5 h-3.5" />
                        {t("support.new_ticket", "Neue Anfrage")}
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
                        {t("support.my_tickets", "Meine Anfragen")}
                        {tickets.length > 0 && (
                            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-indigo-100 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-300 font-bold">
                                {tickets.length}
                            </span>
                        )}
                    </button>
                </div>

                {/* Content Body */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    
                    {/* TAB 1: KNOWLEDGE BASE / HELP CENTER */}
                    {activeTab === "help" && (
                        <div className="space-y-4">
                            {/* Live Search Bar */}
                            <div className="relative">
                                <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                                <input
                                    type="text"
                                    placeholder={t("help.search_placeholder", "Wissensportal & FAQ durchsuchen...")}
                                    value={helpSearchTerm}
                                    onChange={(e) => setHelpSearchTerm(e.target.value)}
                                    className="w-full pl-9 pr-8 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-900 dark:text-white placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition shadow-2xs"
                                />
                                {helpSearchTerm && (
                                    <button
                                        onClick={() => setHelpSearchTerm("")}
                                        className="absolute right-3 top-2.5 text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                                    >
                                        ✕
                                    </button>
                                )}
                            </div>

                            {/* Section Header */}
                            <div className="flex items-center justify-between px-1">
                                <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                                    <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
                                    {helpSearchTerm.length >= 2
                                        ? `Suchergebnisse (${helpArticles.length})`
                                        : `Empfehlungen für ${contextKey.toUpperCase()}`}
                                </span>

                                <Link
                                    to="/app/help"
                                    onClick={onClose}
                                    className="text-[11px] font-bold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                                >
                                    <span>Vollständiges Handbuch</span>
                                    <ExternalLink className="w-3 h-3" />
                                </Link>
                            </div>

                            {/* Loading State */}
                            {loadingHelpArticles && (
                                <div className="py-12 text-center text-slate-400 animate-pulse text-xs">
                                    Lade Hilfethemen...
                                </div>
                            )}

                            {/* Empty State */}
                            {!loadingHelpArticles && helpArticles.length === 0 && (
                                <div className="p-8 text-center bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-200 dark:border-slate-800 text-slate-500 text-xs space-y-2">
                                    <div className="text-3xl">🔍</div>
                                    <div className="font-semibold">Keine passenden Artikel gefunden</div>
                                    <p className="text-[11px] text-slate-400">
                                        Versuche einen anderen Suchbegriff oder öffne ein Support-Ticket für persönliche Hilfe.
                                    </p>
                                    <button
                                        type="button"
                                        onClick={() => setActiveTab("new_ticket")}
                                        className="mt-2 text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline inline-flex items-center gap-1"
                                    >
                                        <span>Ticket an den Support stellen</span>
                                        <ChevronRight className="w-3.5 h-3.5" />
                                    </button>
                                </div>
                            )}

                            {/* Article List */}
                            {!loadingHelpArticles && helpArticles.length > 0 && (
                                <div className="space-y-2.5">
                                    {helpArticles.map((article) => {
                                        const title = isEnglish && article.title_en ? article.title_en : article.title_de;
                                        const summary = isEnglish && article.summary_en ? article.summary_en : article.summary_de;
                                        const catTitle = isEnglish && article.category_title_en ? article.category_title_en : article.category_title_de;

                                        return (
                                            <div
                                                key={article.id}
                                                onClick={() => handleArticleClick(article.slug)}
                                                className="p-3.5 rounded-xl bg-white dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80 hover:border-indigo-400 dark:hover:border-indigo-500 hover:shadow-xs transition space-y-2 group cursor-pointer"
                                            >
                                                <div className="flex items-start justify-between gap-2">
                                                    <div className="flex items-center gap-1.5 text-xs text-indigo-600 dark:text-indigo-400 font-semibold">
                                                        <span>{article.category_icon || "📖"}</span>
                                                        <span>{catTitle}</span>
                                                    </div>

                                                    {isStaffOrAdmin && (
                                                        <button
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                setEditingArticle(article);
                                                            }}
                                                            className="text-[10px] px-2 py-0.5 bg-amber-50 dark:bg-amber-950/40 hover:bg-amber-100 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800 rounded-lg transition font-medium cursor-pointer"
                                                            title="Staff: Artikel bearbeiten"
                                                        >
                                                            ✏️ Edit
                                                        </button>
                                                    )}
                                                </div>

                                                <h3 className="text-xs font-bold text-slate-900 dark:text-slate-100 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition leading-snug">
                                                    {title}
                                                </h3>

                                                {summary && (
                                                    <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed">
                                                        {summary}
                                                    </p>
                                                )}

                                                <div className="flex items-center justify-between pt-1 text-[10px] text-slate-400">
                                                    <div className="flex flex-wrap gap-1">
                                                        {(article.tags || []).slice(0, 3).map((tag, i) => (
                                                            <span key={i} className="px-1.5 py-0.5 bg-slate-100 dark:bg-slate-700 rounded-md text-slate-600 dark:text-slate-300 font-mono text-[9px]">
                                                                #{tag}
                                                            </span>
                                                        ))}
                                                    </div>
                                                    <span className="font-semibold text-indigo-600 dark:text-indigo-400 group-hover:translate-x-0.5 transition inline-flex items-center gap-0.5">
                                                        Lesen →
                                                    </span>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}

                            {/* Knowledge Base Footer Banner */}
                            <div className="p-4 rounded-xl bg-indigo-50/60 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/50 flex items-center justify-between text-xs">
                                <div className="space-y-0.5">
                                    <span className="font-bold text-slate-800 dark:text-slate-200">Nicht fündig geworden?</span>
                                    <p className="text-[11px] text-slate-500 dark:text-slate-400">Öffne ein Ticket direkt bei unseren Experten.</p>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => setActiveTab("new_ticket")}
                                    className="px-3 py-1.5 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition shadow-2xs cursor-pointer"
                                >
                                    Ticket erstellen
                                </button>
                            </div>
                        </div>
                    )}

                    {/* TAB 2: NEW TICKET FORM */}
                    {activeTab === "new_ticket" && (
                        !user ? (
                            <div className="p-6 rounded-2xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center space-y-4 my-4">
                                <div className="w-12 h-12 rounded-2xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mx-auto shadow-sm">
                                    <Lock className="w-6 h-6" />
                                </div>
                                <div className="space-y-1.5">
                                    <h3 className="text-base font-bold text-slate-900 dark:text-white">
                                        Anmeldung erforderlich
                                    </h3>
                                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed max-w-xs mx-auto">
                                        Nur registrierte Benutzer können Support-Tickets eröffnen. Melde dich bitte an, um Unterstützung durch unser Team zu erhalten.
                                    </p>
                                </div>
                                <div className="pt-2 flex flex-col gap-2">
                                    <button
                                        onClick={() => {
                                            onClose();
                                            navigate("/auth/login");
                                        }}
                                        className="w-full py-2.5 rounded-xl bg-indigo-600 text-white text-xs font-bold hover:bg-indigo-700 transition shadow-sm cursor-pointer"
                                    >
                                        Jetzt Anmelden
                                    </button>
                                    <button
                                        onClick={() => setActiveTab("help")}
                                        className="w-full py-2 rounded-xl text-indigo-600 dark:text-indigo-400 text-xs font-semibold hover:underline cursor-pointer"
                                    >
                                        Im Wissensportal nach Lösungen suchen
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <form onSubmit={handleCreateTicket} className="space-y-4">
                                {formSuccess && (
                                    <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200 flex items-center gap-2 text-xs animate-in fade-in">
                                        <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
                                        <span>Support-Ticket erfolgreich erstellt! Wir öffnen den Chat...</span>
                                    </div>
                                )}

                                {/* Subject */}
                                <div className="space-y-1">
                                    <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                                        {t("support.subject", "Betreff / Kurzbeschreibung")} *
                                    </label>
                                    <input
                                        type="text"
                                        required
                                        value={subject}
                                        onChange={(e) => setSubject(e.target.value)}
                                        placeholder="z.B. Wechselrichter meldet Kommunikationsfehler"
                                        className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-medium focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition shadow-2xs"
                                    />
                                </div>

                                {/* Live FAQ Deflection Suggestion Banner */}
                                {deflectionArticles.length > 0 && (
                                    <div className="p-3.5 rounded-xl bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800 space-y-2 animate-in fade-in">
                                        <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-900 dark:text-indigo-200">
                                            <Sparkles className="w-3.5 h-3.5 text-indigo-600 animate-pulse" />
                                            <span>Möglicherweise hilft dir dieser Artikel sofort:</span>
                                        </div>
                                        <div className="space-y-1.5">
                                            {deflectionArticles.map((art) => (
                                                <div
                                                    key={art.id}
                                                    onClick={() => handleArticleClick(art.slug)}
                                                    className="p-2.5 rounded-lg bg-white dark:bg-slate-800 border border-indigo-100 dark:border-slate-700 hover:border-indigo-400 transition cursor-pointer flex items-center justify-between text-xs group"
                                                >
                                                    <span className="font-semibold text-slate-800 dark:text-slate-100 group-hover:text-indigo-600 truncate pr-2">
                                                        {isEnglish && art.title_en ? art.title_en : art.title_de}
                                                    </span>
                                                    <ExternalLink className="w-3 h-3 text-slate-400 group-hover:text-indigo-600 shrink-0" />
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Category & Priority */}
                                <div className="grid grid-cols-2 gap-3">
                                    <div className="space-y-1">
                                        <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                                            {t("support.category", "Bereich")}
                                        </label>
                                        <select
                                            value={category}
                                            onChange={(e) => setCategory(e.target.value)}
                                            className="w-full px-2.5 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-medium"
                                        >
                                            <option value="general">Allgemeine Anfrage</option>
                                            <option value="devices">Hardware & Zähler</option>
                                            <option value="energy">Energie & Steuerung</option>
                                            <option value="forecast">Solar-Prognose</option>
                                            <option value="billing">Tarife & Abrechnung</option>
                                            <option value="community">Energy Community</option>
                                            <option value="wallbox">Wallbox & Smart Charging</option>
                                        </select>
                                    </div>

                                    <div className="space-y-1">
                                        <div className="flex items-center justify-between">
                                            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                                                {t("support.priority", "Dringlichkeit")}
                                            </label>
                                            {!canChoosePriority && (
                                                <span className="text-[10px] text-slate-400 font-semibold flex items-center gap-0.5">
                                                    <Lock className="w-2.5 h-2.5" /> Free
                                                </span>
                                            )}
                                        </div>

                                        {canChoosePriority ? (
                                            <select
                                                value={priority}
                                                onChange={(e) => setPriority(e.target.value)}
                                                className="w-full px-2.5 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-medium"
                                            >
                                                <option value="low">Niedrig (Standard)</option>
                                                <option value="medium">Mittel (Normal)</option>
                                                <option value="high">Hoch (Eilt)</option>
                                                {isStaffOrAdmin && (
                                                    <option value="urgent">Kritisch (Notfall / Ausfall)</option>
                                                )}
                                            </select>
                                        ) : (
                                            <div
                                                title="Pro-Nutzer und Community-Admins können höhere Prioritätsstufen wählen."
                                                className="w-full px-2.5 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800/50 text-slate-500 dark:text-slate-400 text-xs flex items-center justify-between cursor-not-allowed"
                                            >
                                                <span>Niedrig (Free Standard)</span>
                                                <Link
                                                    to="/app/billing"
                                                    onClick={onClose}
                                                    className="text-[10px] font-bold text-amber-600 dark:text-amber-400 hover:underline flex items-center gap-0.5 ml-1"
                                                >
                                                    <Crown className="w-3 h-3" /> Pro
                                                </Link>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Message */}
                                <div className="space-y-1">
                                    <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                                        {t("support.description", "Detaillierte Beschreibung")} *
                                    </label>
                                    <textarea
                                        required
                                        rows={4}
                                        value={message}
                                        onChange={(e) => setMessage(e.target.value)}
                                        placeholder="Beschreibe dein Anliegen möglichst präzise..."
                                        className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-medium focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition shadow-2xs"
                                    />
                                </div>

                                {/* Attachments */}
                                <div className="space-y-1">
                                    <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                                        Dateianhänge (Screenshots, Logs)
                                    </label>
                                    <input
                                        type="file"
                                        multiple
                                        onChange={(e) => setAttachments(Array.from(e.target.files))}
                                        className="w-full text-xs text-slate-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                                    />
                                </div>

                                {/* Submit button */}
                                <button
                                    type="submit"
                                    disabled={submitting}
                                    className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-sm transition disabled:opacity-50 cursor-pointer"
                                >
                                    {submitting ? (
                                        <RefreshCw className="w-4 h-4 animate-spin" />
                                    ) : (
                                        <>
                                            <Send className="w-3.5 h-3.5" />
                                            <span>{t("support.submit", "Ticket jetzt absenden")}</span>
                                        </>
                                    )}
                                </button>
                            </form>
                        )
                    )}

                    {/* TAB 3: MY TICKETS LIST */}
                    {activeTab === "my_tickets" && (
                        !user ? (
                            <div className="p-6 rounded-2xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center space-y-3 my-4">
                                <Lock className="w-8 h-8 mx-auto text-slate-400" />
                                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                                    Anmeldung erforderlich
                                </h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400">
                                    Bitte melde dich an, um deine bestehenden Support-Tickets einzusehen.
                                </p>
                                <button
                                    onClick={() => {
                                        onClose();
                                        navigate("/auth/login");
                                    }}
                                    className="mt-2 py-2 px-4 rounded-xl bg-indigo-600 text-white text-xs font-bold hover:bg-indigo-700 transition cursor-pointer"
                                >
                                    Anmelden
                                </button>
                            </div>
                        ) : loadingTickets ? (
                            <div className="py-12 text-center text-slate-400 animate-pulse text-xs">
                                Lade deine Tickets...
                            </div>
                        ) : (
                            <div className="space-y-2.5">
                                {tickets.length === 0 ? (
                                    <div className="p-8 text-center bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-200 dark:border-slate-800 text-slate-500 text-xs space-y-2">
                                        <Inbox className="w-8 h-8 mx-auto text-slate-300 dark:text-slate-600" />
                                        <p className="text-sm font-medium">Du hast aktuell keine Support-Tickets.</p>
                                        <button
                                            type="button"
                                            onClick={() => setActiveTab("new_ticket")}
                                            className="mt-2 text-xs font-bold text-indigo-600 hover:underline inline-flex items-center gap-1"
                                        >
                                            <span>Neues Ticket erstellen</span>
                                            <ChevronRight className="w-3 h-3" />
                                        </button>
                                    </div>
                                ) : (
                                    tickets.map((t) => (
                                        <div
                                            key={t.id}
                                            onClick={() => setSelectedTicketId(t.id)}
                                            className="p-3.5 rounded-xl bg-white dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80 hover:border-indigo-300 dark:hover:border-indigo-500 transition cursor-pointer shadow-2xs group"
                                        >
                                            <div className="flex items-center justify-between text-xs mb-1">
                                                <span className="font-mono text-[10px] text-slate-400">
                                                    #{t.id.slice(0, 8)}
                                                </span>
                                                <span
                                                    className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${t.status === "open"
                                                        ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-200"
                                                        : t.status === "in_progress"
                                                            ? "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-200"
                                                            : t.status === "resolved"
                                                                ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200"
                                                                : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                                                        }`}
                                                >
                                                    {t.status_display}
                                                </span>
                                            </div>

                                            <h4 className="text-xs font-bold text-slate-800 dark:text-slate-100 truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
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
                        )
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

            {/* Staff Article Editor Modal */}
            {editingArticle && (
                <HelpArticleEditorModal
                    article={editingArticle}
                    isOpen={Boolean(editingArticle)}
                    onClose={() => setEditingArticle(null)}
                    onSaved={() => {
                        loadHelpContent(helpSearchTerm);
                    }}
                />
            )}
        </>,
        document.body
    );
}
