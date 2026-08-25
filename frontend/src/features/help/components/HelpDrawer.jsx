/*
# src/features/help/components/HelpDrawer.jsx
*/

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useHelpDrawer } from "../context/useHelpDrawer";
import { fetchContextArticles, fetchHelpArticles } from "../api";
import HelpArticleEditorModal from "./HelpArticleEditorModal";

export default function HelpDrawer() {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const { isOpen, closeHelp, contextKey } = useHelpDrawer();
    const [searchTerm, setSearchTerm] = useState("");
    const [editingArticle, setEditingArticle] = useState(null);

    const currentUser = JSON.parse(localStorage.getItem("user") || "null");
    const isStaff = currentUser?.is_staff || false;
    const isEnglish = i18n.language?.startsWith("en");

    // 1. Kontext-spezifische Artikel laden
    const contextQuery = useQuery({
        queryKey: ["help-context", contextKey],
        queryFn: () => fetchContextArticles(contextKey),
        enabled: isOpen && !searchTerm,
    });

    // 2. Such-Ergebnisse laden (wenn Suchbegriff eingegeben)
    const searchQuery = useQuery({
        queryKey: ["help-search", searchTerm],
        queryFn: () => fetchHelpArticles({ search: searchTerm }),
        enabled: isOpen && searchTerm.length >= 2,
    });

    if (!isOpen) return null;

    const displayedArticles = searchTerm.length >= 2
        ? searchQuery.data || []
        : contextQuery.data?.articles || [];

    const handleArticleClick = (slug) => {
        closeHelp();
        navigate(`/app/help/${slug}`);
    };

    return (
        <>
            {/* Backdrop */}
            <div
                onClick={closeHelp}
                className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-2xs transition-opacity animate-fade-in"
            />

            {/* Slide-Over Drawer */}
            <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white shadow-2xl flex flex-col border-l border-gray-200 transform transition-transform duration-300 ease-in-out">
                {/* Header */}
                <div className="p-5 border-b border-gray-100 flex items-center justify-between bg-gradient-to-r from-slate-900 to-indigo-950 text-white">
                    <div className="flex items-center gap-3">
                        <span className="text-2xl p-2 rounded-xl bg-white/10 border border-white/15">💡</span>
                        <div>
                            <h2 className="text-base font-bold tracking-tight">
                                {t("help.drawer_title", "Hilfe & Schnellanleitungen")}
                            </h2>
                            <p className="text-xs text-indigo-200/80">
                                {contextKey ? `Kontext: ${contextKey}` : t("help.drawer_subtitle", "Tipps & Benutzerhandbuch")}
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={closeHelp}
                        className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 text-white flex items-center justify-center text-sm font-bold transition cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                {/* Search Bar */}
                <div className="p-4 bg-gray-50 border-b border-gray-200">
                    <div className="relative">
                        <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400 text-sm">
                            🔍
                        </span>
                        <input
                            type="text"
                            placeholder={t("help.search_placeholder", "Wissensportal durchsuchen...")}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-9 pr-8 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition shadow-2xs"
                        />
                        {searchTerm && (
                            <button
                                onClick={() => setSearchTerm("")}
                                className="absolute inset-y-0 right-0 pr-3 flex items-center text-xs text-gray-400 hover:text-gray-600 cursor-pointer"
                            >
                                ✕
                            </button>
                        )}
                    </div>
                </div>

                {/* Articles List Body */}
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                    <div className="flex items-center justify-between px-1">
                        <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider">
                            {searchTerm.length >= 2
                                ? `${t("help.search_results", "Suchergebnisse")} (${displayedArticles.length})`
                                : t("help.context_recommendations", "Passende Themen für diese Seite")}
                        </span>

                        <Link
                            to="/app/help"
                            onClick={closeHelp}
                            className="text-[11px] font-bold text-indigo-600 hover:text-indigo-700 hover:underline flex items-center gap-1"
                        >
                            <span>Handbuch ↗</span>
                        </Link>
                    </div>

                    {(contextQuery.isLoading || searchQuery.isLoading) && (
                        <div className="py-12 text-center text-gray-400 animate-pulse text-xs">
                            {t("common.loading", "Lade Hilfethemen...")}
                        </div>
                    )}

                    {displayedArticles.length === 0 && !contextQuery.isLoading && !searchQuery.isLoading && (
                        <div className="p-8 text-center bg-gray-50 rounded-2xl border border-gray-200 text-gray-500 text-xs space-y-2">
                            <div className="text-3xl">🔍</div>
                            <div className="font-semibold">Keine passenden Artikel gefunden</div>
                            <p className="text-[11px] text-gray-400">
                                Versuche andere Suchbegriffe oder stöbere im vollständigen Handbuch.
                            </p>
                        </div>
                    )}

                    {displayedArticles.map((article) => {
                        const title = isEnglish && article.title_en ? article.title_en : article.title_de;
                        const summary = isEnglish && article.summary_en ? article.summary_en : article.summary_de;

                        return (
                            <div
                                key={article.id}
                                className="p-4 rounded-2xl bg-white border border-gray-200 hover:border-indigo-300 hover:shadow-xs transition space-y-2 group cursor-pointer"
                                onClick={() => handleArticleClick(article.slug)}
                            >
                                <div className="flex items-start justify-between gap-2">
                                    <div className="flex items-center gap-1.5 text-xs text-indigo-600 font-semibold">
                                        <span>{article.category_icon || "📖"}</span>
                                        <span>{isEnglish && article.category_title_en ? article.category_title_en : article.category_title_de}</span>
                                    </div>

                                    {isStaff && (
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setEditingArticle(article);
                                            }}
                                            className="text-[10px] px-2 py-0.5 bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 rounded-lg transition font-medium cursor-pointer"
                                            title="Staff: Artikel bearbeiten"
                                        >
                                            ✏️ Edit
                                        </button>
                                    )}
                                </div>

                                <h3 className="text-xs font-bold text-gray-900 group-hover:text-indigo-600 transition leading-snug">
                                    {title}
                                </h3>

                                {summary && (
                                    <p className="text-[11px] text-gray-500 line-clamp-2 leading-relaxed">
                                        {summary}
                                    </p>
                                )}

                                <div className="flex items-center justify-between pt-1 text-[10px] text-gray-400">
                                    <div className="flex flex-wrap gap-1">
                                        {(article.tags || []).slice(0, 3).map((tag, i) => (
                                            <span key={i} className="px-1.5 py-0.5 bg-gray-100 rounded-md text-gray-600 font-mono">
                                                #{tag}
                                            </span>
                                        ))}
                                    </div>
                                    <span className="font-semibold text-indigo-500 group-hover:translate-x-0.5 transition">
                                        Lesen →
                                    </span>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Footer Link */}
                <div className="p-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between text-xs">
                    <span className="text-gray-500 font-medium">Fragen offen?</span>
                    <Link
                        to="/app/help"
                        onClick={closeHelp}
                        className="px-3 py-1.5 bg-white border border-gray-200 hover:border-indigo-300 text-indigo-700 font-semibold rounded-xl transition shadow-2xs"
                    >
                        📚 Vollständiges FAQ & Handbuch
                    </Link>
                </div>
            </div>

            {/* Staff Editor Modal */}
            {editingArticle && (
                <HelpArticleEditorModal
                    article={editingArticle}
                    isOpen={Boolean(editingArticle)}
                    onClose={() => setEditingArticle(null)}
                    onSaved={() => {
                        contextQuery.refetch();
                        searchQuery.refetch();
                    }}
                />
            )}
        </>
    );
}

