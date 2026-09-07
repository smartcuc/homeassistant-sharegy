/*
# src/features/help/pages/HelpCenterPage.jsx
*/

import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { fetchHelpCategories, fetchHelpArticles } from "../api";

export default function HelpCenterPage() {
    const { t, i18n } = useTranslation();
    const [selectedCategory, setSelectedCategory] = useState("all");
    const [searchQuery, setSearchQuery] = useState("");

    const isEnglish = i18n.language?.startsWith("en");

    const categoriesQuery = useQuery({
        queryKey: ["help-categories"],
        queryFn: fetchHelpCategories,
    });

    const articlesQuery = useQuery({
        queryKey: ["help-articles", selectedCategory, searchQuery],
        queryFn: () =>
            fetchHelpArticles({
                category: selectedCategory === "all" ? "" : selectedCategory,
                search: searchQuery,
            }),
    });

    const categories = categoriesQuery.data || [];
    const articles = articlesQuery.data || [];

    const featuredArticles = articles.filter((a) => a.is_featured);

    const activeCategoryObj = categories.find((c) => c.key === selectedCategory);
    const activeCategoryTitle = activeCategoryObj
        ? (isEnglish && activeCategoryObj.title_en ? activeCategoryObj.title_en : activeCategoryObj.title_de)
        : null;

    const handleSelectCategory = (catKey) => {
        setSelectedCategory(catKey);
        setTimeout(() => {
            const el = document.getElementById("articles-list");
            if (el) {
                el.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        }, 50);
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8 animate-fade-in">
            {/* Hero Header & Search */}
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 p-8 sm:p-12 text-white shadow-xl">
                <div className="relative z-10 max-w-2xl space-y-4">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/15 text-xs font-semibold text-indigo-300">
                        <span>📚</span> {t("help.center_badge", "Sharegy Wissensportal & Benutzerhandbuch")}
                    </div>

                    <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white">
                        {t("help.hero_title", "Wie können wir dir heute helfen?")}
                    </h1>

                    <p className="text-sm text-indigo-200 leading-relaxed">
                        {t("help.hero_subtitle", "Finde Schritt-für-Schritt-Anleitungen für Wechselrichter, den Smart Energy Optimizer, dynamische Tarife und die Alarmzentrale.")}
                    </p>

                    {/* Search Input */}
                    <div className="relative pt-2">
                        <span className="absolute inset-y-0 left-0 pl-4 pt-2 flex items-center pointer-events-none text-gray-400 text-lg">
                            🔍
                        </span>
                        <input
                            type="text"
                            placeholder={t("help.hero_search_placeholder", "Suche nach 'SMA', 'Prognose', 'Wallbox', 'Mieterstrom'...")}
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-12 pr-4 py-3.5 bg-white text-gray-900 placeholder-gray-400 rounded-2xl text-sm font-medium shadow-lg focus:outline-none focus:ring-4 focus:ring-indigo-500/30 transition"
                        />
                    </div>
                </div>

                {/* Background Glow */}
                <div className="absolute right-0 top-0 -mt-12 -mr-12 w-96 h-96 rounded-full bg-indigo-500/20 blur-3xl pointer-events-none" />
                <div className="absolute right-32 bottom-0 w-64 h-64 rounded-full bg-amber-500/10 blur-2xl pointer-events-none" />
            </div>

            {/* Category Grid */}
            <div className="space-y-4">
                <h2 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <span>🗂️</span> {t("help.categories_title", "Themenbereiche")}
                </h2>

                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3.5">
                    <button
                        type="button"
                        onClick={() => handleSelectCategory("all")}
                        className={`p-4 rounded-2xl border text-left transition cursor-pointer flex flex-col justify-between ${selectedCategory === "all"
                            ? "bg-indigo-50/80 dark:bg-indigo-950/40 border-indigo-300 dark:border-indigo-600 ring-2 ring-indigo-500/20 shadow-xs"
                            : "bg-white dark:bg-slate-900 border-gray-200 dark:border-slate-800 hover:border-gray-300 dark:hover:border-slate-700 hover:shadow-xs"
                            }`}
                    >
                        <div className="text-2xl mb-2">✨</div>
                        <div>
                            <div className="text-sm font-bold text-gray-900 dark:text-white">
                                {t("common.all", "Alle Themen")}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                                {articles.length} {t("help.articles_count", "Artikel")}
                            </div>
                        </div>
                    </button>

                    {categories.map((cat) => {
                        const title = isEnglish && cat.title_en ? cat.title_en : cat.title_de;
                        const isSelected = selectedCategory === cat.key;

                        return (
                            <button
                                type="button"
                                key={cat.id}
                                onClick={() => handleSelectCategory(cat.key)}
                                className={`p-4 rounded-2xl border text-left transition cursor-pointer flex flex-col justify-between ${isSelected
                                    ? "bg-indigo-50/80 dark:bg-indigo-950/40 border-indigo-300 dark:border-indigo-600 ring-2 ring-indigo-500/20 shadow-xs"
                                    : "bg-white dark:bg-slate-900 border-gray-200 dark:border-slate-800 hover:border-gray-300 dark:hover:border-slate-700 hover:shadow-xs"
                                    }`}
                            >
                                <div className="text-2xl mb-2">{cat.icon}</div>
                                <div>
                                    <div className="text-sm font-bold text-gray-900 dark:text-white line-clamp-1">
                                        {title}
                                    </div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                                        {cat.article_count} {t("help.articles_count", "Artikel")}
                                    </div>
                                </div>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Featured Articles */}
            {selectedCategory === "all" && !searchQuery && featuredArticles.length > 0 && (
                <div className="space-y-4">
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                        <span>⭐</span> {t("help.featured_title", "Häufig gelesene Anleitungen")}
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {featuredArticles.map((fa) => {
                            const title = isEnglish && fa.title_en ? fa.title_en : fa.title_de;
                            const summary = isEnglish && fa.summary_en ? fa.summary_en : fa.summary_de;

                            return (
                                <Link
                                    key={fa.id}
                                    to={`/app/help/${fa.slug}`}
                                    className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition space-y-3 flex flex-col justify-between group"
                                >
                                    <div className="space-y-2">
                                        <div className="flex items-center gap-2 text-xs font-semibold text-indigo-600 dark:text-indigo-400">
                                            <span>{fa.category_icon || "📖"}</span>
                                            <span>{isEnglish && fa.category_title_en ? fa.category_title_en : fa.category_title_de}</span>
                                        </div>

                                        <h3 className="text-sm font-bold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition leading-snug">
                                            {title}
                                        </h3>

                                        {summary && (
                                             <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 leading-relaxed">
                                                {summary}
                                            </p>
                                        )}
                                    </div>

                                    <div className="text-xs font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-1 group-hover:translate-x-1 transition pt-2">
                                        <span>Anleitung lesen</span>
                                        <span>→</span>
                                    </div>
                                </Link>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Articles List Anchor */}
            <div id="articles-list" className="space-y-4 scroll-mt-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="flex items-center flex-wrap gap-2">
                        <h2 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                            <span>📄</span>
                            <span>
                                {selectedCategory !== "all" && activeCategoryTitle
                                    ? `${t("help.articles_title", "Artikel")}: ${activeCategoryTitle}`
                                    : t("help.all_articles", "Alle Artikel")}
                            </span>
                            {searchQuery && (
                                <span className="text-xs font-normal text-gray-500 dark:text-gray-400">
                                    ({t("help.search_results_for", "Suchergebnisse für")} "{searchQuery}")
                                </span>
                            )}
                        </h2>

                        {selectedCategory !== "all" && (
                            <button
                                type="button"
                                onClick={() => setSelectedCategory("all")}
                                className="inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/60 dark:hover:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 transition cursor-pointer"
                                title={t("help.clear_filter", "Filter aufheben")}
                            >
                                <span>{activeCategoryObj?.icon || "🏷️"}</span>
                                <span>{activeCategoryTitle}</span>
                                <span className="font-bold ml-0.5">✕</span>
                            </button>
                        )}
                    </div>

                    <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">
                        {articles.length} {t("help.articles_count", "Artikel gefunden")}
                    </span>
                </div>

                {articlesQuery.isLoading ? (
                    <div className="py-16 text-center text-gray-400 animate-pulse">
                        {t("common.loading", "Lade Artikel...")}
                    </div>
                ) : articles.length === 0 ? (
                    <div className="p-12 text-center bg-white dark:bg-slate-900 rounded-3xl border border-gray-200 dark:border-slate-800 text-gray-500 dark:text-gray-400 space-y-3">
                        <div className="text-4xl">🔍</div>
                        <div className="text-base font-bold text-gray-900 dark:text-white">{t("help.no_articles_found", "Keine Artikel gefunden")}</div>
                        <p className="text-xs text-gray-400 max-w-sm mx-auto">
                            {t("help.no_articles_desc", "Für diesen Suchbegriff oder diese Kategorie existieren noch keine Beiträge.")}
                        </p>
                        {selectedCategory !== "all" && (
                            <button
                                type="button"
                                onClick={() => setSelectedCategory("all")}
                                className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white transition cursor-pointer"
                            >
                                <span>Alle Artikel anzeigen</span>
                            </button>
                        )}
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                        {articles.map((art) => {
                            const title = isEnglish && art.title_en ? art.title_en : art.title_de;
                            const summary = isEnglish && art.summary_en ? art.summary_en : art.summary_de;

                            return (
                                <Link
                                    key={art.id}
                                    to={`/app/help/${art.slug}`}
                                    className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-xs transition space-y-2.5 flex flex-col justify-between group"
                                >
                                    <div className="space-y-1.5">
                                        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                                            <span className="font-semibold text-indigo-600 dark:text-indigo-400 flex items-center gap-1">
                                                <span>{art.category_icon || "📖"}</span>
                                                <span>{isEnglish && art.category_title_en ? art.category_title_en : art.category_title_de}</span>
                                            </span>
                                            <span className="text-[11px] text-gray-400 font-mono">
                                                {art.views_count} {t("help.views_count", "Aufrufe")}
                                            </span>
                                        </div>

                                        <h3 className="text-sm font-bold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition leading-snug">
                                            {title}
                                        </h3>

                                        {summary && (
                                            <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 leading-relaxed">
                                                {summary}
                                            </p>
                                        )}
                                    </div>

                                    <div className="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-slate-800 text-[11px] text-gray-400">
                                        <div className="flex flex-wrap gap-1">
                                            {(art.tags || []).slice(0, 3).map((tag, i) => (
                                                <span key={i} className="px-1.5 py-0.5 bg-gray-100 dark:bg-slate-800 rounded-md text-gray-600 dark:text-gray-300 font-mono">
                                                    #{tag}
                                                </span>
                                            ))}
                                        </div>
                                        <span className="font-bold text-indigo-600 dark:text-indigo-400 group-hover:translate-x-0.5 transition">
                                            {t("help.open_link", "Öffnen →")}
                                        </span>
                                    </div>
                                </Link>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}


