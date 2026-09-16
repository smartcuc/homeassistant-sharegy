/*
# src/features/help/pages/HelpCenterPage.jsx
*/

import { useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { fetchHelpCategories, fetchHelpArticles } from "../api";
import { useEnergyProfile } from "../../energy/hooks/useEnergyProfile";
import SupportDrawer from "../../support/components/SupportDrawer";

export default function HelpCenterPage() {
    const { t, i18n } = useTranslation();
    const [selectedCategory, setSelectedCategory] = useState("all");
    const [searchQuery, setSearchQuery] = useState("");

    // Support Drawer State
    const [supportDrawerOpen, setSupportDrawerOpen] = useState(false);
    const [supportDrawerTab, setSupportDrawerTab] = useState("new_ticket");

    const isEnglish = i18n.language?.startsWith("en");
    const { profile, profileCode, helpArticleSlug } = useEnergyProfile();

    const categoriesQuery = useQuery({
        queryKey: ["help-categories"],
        queryFn: fetchHelpCategories,
    });

    const articlesQuery = useQuery({
        queryKey: ["help-articles", selectedCategory, searchQuery],
        queryFn: () =>
            fetchHelpArticles({
                category: selectedCategory === "all" ? undefined : selectedCategory,
                search: searchQuery,
            }),
    });

    const categories = categoriesQuery.data || [];
    const articles = articlesQuery.data || [];

    // 🌟 Nur die Top 3 bis 6 am häufigsten gelesenen bzw. gefeatureten Anleitungen anzeigen
    const featuredArticles = useMemo(() => {
        const featured = articles.filter((a) => a.is_featured);
        const pool = featured.length > 0 ? featured : articles;
        return [...pool]
            .sort((a, b) => (b.views_count || 0) - (a.views_count || 0))
            .slice(0, 6);
    }, [articles]);

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

    const handleOpenSupport = (tab = "new_ticket") => {
        setSupportDrawerTab(tab);
        setSupportDrawerOpen(true);
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8 animate-fade-in">
            {/* Kompakter Header & Suche */}
            <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div className="flex items-center gap-2">
                        <h1 className="text-xl sm:text-2xl font-black text-gray-900 dark:text-white flex items-center gap-2">
                            <span>📖</span>
                            <span>{t("help.hero_title", "Handbuch")}</span>
                        </h1>
                        <span className="hidden sm:inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                            {t("help.center_badge", "Online-Handbuch")}
                        </span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-xl">
                        {t("help.hero_subtitle", "Schritt-für-Schritt-Anleitungen für Wechselrichter, Speicher, den Optimizer, dynamische Tarife und die Wallbox.")}
                    </p>
                </div>

                {/* Schlankes Suchfeld */}
                <div className="relative w-full md:w-80 lg:w-96 shrink-0">
                    <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400 text-sm">
                        🔍
                    </span>
                    <input
                        type="text"
                        placeholder={t("help.hero_search_placeholder", "Im Handbuch suchen...")}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-9 pr-8 py-2 bg-gray-50 dark:bg-slate-800 text-gray-900 dark:text-white placeholder-gray-400 border border-gray-200 dark:border-slate-700 rounded-xl text-xs font-medium focus:outline-hidden focus:ring-2 focus:ring-indigo-500 transition"
                    />
                    {searchQuery && (
                        <button
                            type="button"
                            onClick={() => setSearchQuery("")}
                            className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 text-xs cursor-pointer"
                        >
                            ✕
                        </button>
                    )}
                </div>
            </div>

            {/* 🌟 50/50 DUAL HEADER: HANDBUCH-LEITFADEN & PERSÖNLICHER SUPPORT */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
                {/* LINKS: Empfohlener Leitfaden für das Profil oder Handbuch-Intro */}
                {profile ? (
                    <div className="p-5 rounded-2xl bg-gradient-to-br from-indigo-950 via-slate-900 to-indigo-900 text-white shadow-md border border-indigo-800/60 flex flex-col justify-between space-y-4">
                        <div className="space-y-2">
                            <div className="flex items-center gap-2">
                                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-indigo-500/30 text-indigo-300 border border-indigo-400/30">
                                    {t("energy_profile.badge_label", "Energie-Profil")}: {profileCode}
                                </span>
                                <span className="text-xs font-bold text-white">
                                    {profile.profile_name}
                                </span>
                            </div>
                            <h3 className="text-sm sm:text-base font-bold text-white flex items-center gap-1.5">
                                <span>📖</span>
                                <span>{t("help.profile_guide_title", "Empfohlener Leitfaden:")} {t("energy_profile.view_matrix_guide", "Tarif- & Ersparnis-Kompass")}</span>
                            </h3>
                            <p className="text-xs text-indigo-200/80 leading-relaxed line-clamp-2">
                                {profile.tariff_verdict_reason}
                            </p>
                        </div>
                        <div>
                            <Link
                                to={`/app/help/${helpArticleSlug}`}
                                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white text-indigo-950 hover:bg-indigo-50 text-xs font-bold transition shadow-sm cursor-pointer"
                            >
                                <span>📖</span>
                                <span>{t("energy_profile.view_guide_btn", "Leitfaden lesen")}</span>
                                <span>→</span>
                            </Link>
                        </div>
                    </div>
                ) : (
                    <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white shadow-md border border-slate-800 flex flex-col justify-between space-y-4">
                        <div className="space-y-2">
                            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-indigo-500/30 text-indigo-300 border border-indigo-400/30">
                                {t("help.handbook_badge", "Online-Handbuch")}
                            </span>
                            <h3 className="text-sm sm:text-base font-bold text-white flex items-center gap-1.5">
                                <span>📖</span>
                                <span>{t("help.quickstart_title", "Schnellstart & Anleitungen")}</span>
                            </h3>
                            <p className="text-xs text-indigo-200/80 leading-relaxed line-clamp-2">
                                {t("help.quickstart_desc", "Entdecke alle Einrichtungs-Guides für Wechselrichter, Speicher, dynamische Tarife und den Optimizer.")}
                            </p>
                        </div>
                        <div>
                            <button
                                type="button"
                                onClick={() => handleSelectCategory("all")}
                                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white text-indigo-950 hover:bg-indigo-50 text-xs font-bold transition shadow-sm cursor-pointer"
                            >
                                <span>Zu den Kapiteln</span>
                                <span>↓</span>
                            </button>
                        </div>
                    </div>
                )}

                {/* RECHTS: Persönlicher Support & Ticket-Erstellung */}
                <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between space-y-4 hover:border-indigo-300 dark:hover:border-indigo-700 transition">
                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                                {t("help.support_badge", "Technischer Support")}
                            </span>
                            <span className="text-sm">🛟</span>
                        </div>
                        <h3 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white">
                            {t("help.support_card_title", "Frage nicht im Handbuch gefunden?")}
                        </h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                            {t("help.support_card_desc", "Unser Support-Team hilft dir bei Fragen zu Geräten, Abrechnungen oder Einrichtung persönlich weiter.")}
                        </p>
                    </div>
                    <div className="flex items-center flex-wrap gap-2.5 pt-1">
                        <button
                            type="button"
                            onClick={() => handleOpenSupport("new_ticket")}
                            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition shadow-sm cursor-pointer"
                        >
                            <span>🎫</span>
                            <span>{t("help.create_ticket_btn", "Ticket erstellen")}</span>
                        </button>
                        <button
                            type="button"
                            onClick={() => handleOpenSupport("my_tickets")}
                            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold transition cursor-pointer"
                        >
                            <span>📬</span>
                            <span>{t("help.my_tickets_btn", "Meine Anfragen")}</span>
                        </button>
                    </div>
                </div>
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

            {/* 🛟 Integrierter Support-Drawer für Ticket-Erstellung und Live-Hilfe */}
            <SupportDrawer
                isOpen={supportDrawerOpen}
                onClose={() => setSupportDrawerOpen(false)}
                initialTab={supportDrawerTab}
            />
        </div>
    );
}


