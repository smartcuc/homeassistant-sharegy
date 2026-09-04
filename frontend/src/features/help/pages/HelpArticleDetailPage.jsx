/*
# src/features/help/pages/HelpArticleDetailPage.jsx
*/

import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { fetchHelpArticle, sendArticleFeedback } from "../api";
import HelpArticleEditorModal from "../components/HelpArticleEditorModal";
import MarkdownViewer from "../components/MarkdownViewer";
import { useUser } from "../../../hooks/useUser";

export default function HelpArticleDetailPage() {
    const { slug } = useParams();
    const { t, i18n } = useTranslation();
    const { user } = useUser();
    const [feedbackSent, setFeedbackSent] = useState(false);
    const [isEditing, setIsEditing] = useState(false);

    const isStaff = Boolean(user?.is_staff || user?.is_superuser || user?.is_platform_admin);
    const isEnglish = i18n.language?.startsWith("en");

    const query = useQuery({
        queryKey: ["help-article", slug],
        queryFn: () => fetchHelpArticle(slug),
    });

    const feedbackMutation = useMutation({
        mutationFn: (helpful) => sendArticleFeedback(slug, helpful),
        onSuccess: () => {
            setFeedbackSent(true);
            query.refetch();
        },
    });

    if (query.isLoading) {
        return (
            <div className="p-8 max-w-7xl mx-auto text-center text-gray-400 animate-pulse">
                {t("common.loading", "Lade Artikel...")}
            </div>
        );
    }

    if (query.isError || !query.data) {
        return (
            <div className="p-8 max-w-7xl mx-auto space-y-4">
                <div className="p-6 bg-red-50 border border-red-200 rounded-2xl text-red-700">
                    ⚠️ {t("help.article_not_found", "Der angeforderte Hilfe-Artikel wurde nicht gefunden.")}
                </div>
                <Link to="/app/help" className="inline-block text-sm font-semibold text-indigo-600 hover:underline">
                    ← {t("help.back_to_overview", "Zurück zum Wissensportal")}
                </Link>
            </div>
        );
    }

    const article = query.data;
    const title = isEnglish && article.title_en ? article.title_en : article.title_de;
    const summary = isEnglish && article.summary_en ? article.summary_en : article.summary_de;
    const content = isEnglish && article.content_en ? article.content_en : article.content_de;
    const categoryTitle = isEnglish && article.category_title_en ? article.category_title_en : article.category_title_de;

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6 animate-fade-in">
            {/* Breadcrumb Navigation */}
            <div className="flex items-center justify-between">
                <nav className="flex items-center gap-2 text-xs font-semibold text-gray-500">
                    <Link to="/app/help" className="hover:text-indigo-600 transition">
                        📚 {t("help.portal", "Wissensportal")}
                    </Link>
                    <span>/</span>
                    <span className="text-gray-700 flex items-center gap-1">
                        <span>{article.category_icon || "📖"}</span>
                        <span>{categoryTitle}</span>
                    </span>
                    <span>/</span>
                    <span className="text-gray-400 truncate max-w-xs">{title}</span>
                </nav>

                {isStaff && (
                    <button
                        onClick={() => setIsEditing(true)}
                        className="text-xs px-3 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 rounded-xl font-semibold flex items-center gap-1.5 transition cursor-pointer shadow-2xs"
                    >
                        <span>✏️</span> {t("help.edit_article_staff_btn", "Artikel bearbeiten (Staff)")}
                    </button>
                )}
            </div>

            {/* Article Card */}
            <article className="bg-white rounded-3xl border border-gray-200 shadow-xs overflow-hidden">
                {/* Header */}
                <div className="p-6 sm:p-8 border-b border-gray-100 bg-slate-50/50 space-y-4">
                    <div className="flex flex-wrap items-center gap-2">
                        <span className="px-2.5 py-1 bg-indigo-50 text-indigo-700 border border-indigo-200/60 rounded-lg text-xs font-bold flex items-center gap-1">
                            <span>{article.category_icon || "📖"}</span>
                            <span>{categoryTitle}</span>
                        </span>

                        {(article.tags || []).map((tag, idx) => (
                            <span key={idx} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-md text-xs font-mono">
                                #{tag}
                            </span>
                        ))}
                    </div>

                    <h1 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight leading-tight">
                        {title}
                    </h1>

                    {summary && (
                        <p className="text-sm sm:text-base text-gray-600 leading-relaxed font-normal">
                            {summary}
                        </p>
                    )}

                    <div className="flex items-center gap-4 text-xs text-gray-400 pt-2">
                        <span>👁️ {article.views_count} {t("help.views", "Aufrufe")}</span>
                        {article.context_key && (
                            <span className="px-2 py-0.5 bg-slate-100 rounded text-slate-600 font-mono text-[10px]">
                                Kontext: {article.context_key}
                            </span>
                        )}
                    </div>
                </div>

                {/* Markdown Content Body */}
                <div className="p-6 sm:p-8">
                    <MarkdownViewer content={content} />
                </div>

                {/* Helpful Feedback Section */}
                <div className="p-6 border-t border-gray-100 bg-gray-50/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                        <div className="text-xs font-bold text-gray-800">
                            {t("help.feedback_question", "War dieser Artikel hilfreich?")}
                        </div>
                        <div className="text-[11px] text-gray-500 mt-0.5">
                            {article.helpful_yes} Nutzer fanden diesen Artikel hilfreich
                        </div>
                    </div>

                    {feedbackSent ? (
                        <div className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-3.5 py-2 rounded-xl border border-emerald-200">
                            ✅ {t("help.feedback_thanks", "Vielen Dank für dein Feedback!")}
                        </div>
                    ) : (
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => feedbackMutation.mutate(true)}
                                disabled={feedbackMutation.isPending}
                                className="px-3.5 py-1.5 bg-white hover:bg-emerald-50 text-gray-700 hover:text-emerald-700 border border-gray-200 hover:border-emerald-300 text-xs font-semibold rounded-xl transition cursor-pointer shadow-2xs"
                            >
                                👍 {t("common.yes", "Ja")}
                            </button>
                            <button
                                onClick={() => feedbackMutation.mutate(false)}
                                disabled={feedbackMutation.isPending}
                                className="px-3.5 py-1.5 bg-white hover:bg-rose-50 text-gray-700 hover:text-rose-700 border border-gray-200 hover:border-rose-300 text-xs font-semibold rounded-xl transition cursor-pointer shadow-2xs"
                            >
                                👎 {t("common.no", "Nein")}
                            </button>
                        </div>
                    )}
                </div>
            </article>

            {/* Back to Overview */}
            <div className="pt-2">
                <Link
                    to="/app/help"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 hover:border-gray-300 text-xs font-bold text-gray-700 rounded-xl transition shadow-2xs"
                >
                    <span>←</span> {t("help.back_to_portal", "Zurück zum Wissensportal")}
                </Link>
            </div>

            {/* Staff Editor Modal */}
            {isEditing && (
                <HelpArticleEditorModal
                    article={article}
                    isOpen={isEditing}
                    onClose={() => setIsEditing(false)}
                    onSaved={() => query.refetch()}
                />
            )}
        </div>
    );
}

