/*
# src/features/help/components/HelpArticleEditorModal.jsx
*/

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { updateHelpArticle } from "../api";

export default function HelpArticleEditorModal({ article, isOpen, onClose, onSaved }) {
    const { t } = useTranslation();
    const [activeLang, setActiveLang] = useState("de");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");

    const [formData, setFormData] = useState({
        title_de: article?.title_de || "",
        title_en: article?.title_en || "",
        summary_de: article?.summary_de || "",
        summary_en: article?.summary_en || "",
        content_de: article?.content_de || "",
        content_en: article?.content_en || "",
        context_key: article?.context_key || "",
        tags: (article?.tags || []).join(", "),
        is_published: article?.is_published ?? true,
        is_featured: article?.is_featured ?? false,
    });

    if (!isOpen || !article) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrorMsg("");
        setIsSubmitting(true);

        try {
            const payload = {
                ...formData,
                tags: formData.tags
                    .split(",")
                    .map((t) => t.trim().toLowerCase())
                    .filter(Boolean),
            };

            const updated = await updateHelpArticle(article.slug, payload);
            if (onSaved) onSaved(updated);
            onClose();
        } catch (err) {
            setErrorMsg(err.message || "Fehler beim Speichern des Hilfeartikels.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fade-in">
            <div className="bg-white rounded-3xl shadow-2xl border border-gray-200 w-full max-w-4xl max-h-[92vh] flex flex-col overflow-hidden">
                {/* Header */}
                <div className="p-6 border-b border-gray-100 flex items-center justify-between bg-slate-50/80">
                    <div className="flex items-center gap-3">
                        <span className="text-2xl p-2 bg-indigo-50 text-indigo-600 rounded-xl border border-indigo-100">✏️</span>
                        <div>
                            <h2 className="text-lg font-bold text-gray-900">
                                {t("help.edit_article_title", "Hilfeartikel bearbeiten (Staff Live-Editor)")}
                            </h2>
                            <p className="text-xs text-gray-500 font-mono">
                                Slug: {article.slug}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <div className="inline-flex bg-gray-100 p-1 rounded-xl text-xs font-semibold">
                            <button
                                type="button"
                                onClick={() => setActiveLang("de")}
                                className={`px-3 py-1.5 rounded-lg transition ${activeLang === "de" ? "bg-white text-gray-900 shadow-xs font-bold" : "text-gray-500"}`}
                            >
                                🇩🇪 Deutsch
                            </button>
                            <button
                                type="button"
                                onClick={() => setActiveLang("en")}
                                className={`px-3 py-1.5 rounded-lg transition ${activeLang === "en" ? "bg-white text-gray-900 shadow-xs font-bold" : "text-gray-500"}`}
                            >
                                🇬🇧 English
                            </button>
                        </div>

                        <button
                            type="button"
                            onClick={onClose}
                            className="w-8 h-8 rounded-full bg-white border border-gray-200 text-gray-400 hover:text-gray-700 flex items-center justify-center text-sm font-bold transition cursor-pointer"
                        >
                            ✕
                        </button>
                    </div>
                </div>

                {/* Form Body */}
                <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-4">
                    {errorMsg && (
                        <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs font-semibold rounded-xl">
                            ⚠️ {errorMsg}
                        </div>
                    )}

                    {activeLang === "de" ? (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                                    Titel (Deutsch) *
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={formData.title_de}
                                    onChange={(e) => setFormData({ ...formData, title_de: e.target.value })}
                                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                                    Kurzbeschreibung (Drawer & Suchergebnisse)
                                </label>
                                <textarea
                                    rows={2}
                                    value={formData.summary_de}
                                    onChange={(e) => setFormData({ ...formData, summary_de: e.target.value })}
                                    className="w-full px-3.5 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                                    Inhalt in Markdown (Deutsch) *
                                </label>
                                <textarea
                                    rows={12}
                                    required
                                    value={formData.content_de}
                                    onChange={(e) => setFormData({ ...formData, content_de: e.target.value })}
                                    className="w-full px-3.5 py-2.5 font-mono text-xs bg-slate-900 text-slate-100 border border-slate-700 rounded-xl focus:ring-2 focus:ring-indigo-500 transition leading-relaxed"
                                />
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                                    Title (English)
                                </label>
                                <input
                                    type="text"
                                    value={formData.title_en}
                                    onChange={(e) => setFormData({ ...formData, title_en: e.target.value })}
                                    className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                                    Summary (English)
                                </label>
                                <textarea
                                    rows={2}
                                    value={formData.summary_en}
                                    onChange={(e) => setFormData({ ...formData, summary_en: e.target.value })}
                                    className="w-full px-3.5 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                                    Markdown Content (English)
                                </label>
                                <textarea
                                    rows={12}
                                    value={formData.content_en}
                                    onChange={(e) => setFormData({ ...formData, content_en: e.target.value })}
                                    className="w-full px-3.5 py-2.5 font-mono text-xs bg-slate-900 text-slate-100 border border-slate-700 rounded-xl focus:ring-2 focus:ring-indigo-500 transition leading-relaxed"
                                />
                            </div>
                        </div>
                    )}

                    {/* Metadata Settings */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-gray-100">
                        <div>
                            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                                {t("help.context_key_label", "Kontext-Schlüssel (für Drawer-Matching)")}
                            </label>
                            <input
                                type="text"
                                placeholder="z. B. forecast, energy_dashboard, tariffs, alerts"
                                value={formData.context_key}
                                onChange={(e) => setFormData({ ...formData, context_key: e.target.value })}
                                className="w-full px-3.5 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs font-mono font-medium focus:bg-white focus:ring-2 focus:ring-indigo-500 transition"
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                                {t("help.tags_label", "Tags (kommagetrennt)")}
                            </label>
                            <input
                                type="text"
                                placeholder="solar, modbus, sma, inverter"
                                value={formData.tags}
                                onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                                className="w-full px-3.5 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs font-medium focus:bg-white focus:ring-2 focus:ring-indigo-500 transition"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-6 pt-2">
                        <label className="flex items-center gap-2 text-xs font-semibold text-gray-700 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={formData.is_published}
                                onChange={(e) => setFormData({ ...formData, is_published: e.target.checked })}
                                className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                            />
                            <span>{t("help.published_label", "Veröffentlicht (sichtbar für Nutzer)")}</span>
                        </label>

                        <label className="flex items-center gap-2 text-xs font-semibold text-gray-700 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={formData.is_featured}
                                onChange={(e) => setFormData({ ...formData, is_featured: e.target.checked })}
                                className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                            />
                            <span>{t("help.featured_label", "Hervorgehoben (Top-FAQ Startseite)")}</span>
                        </label>
                    </div>

                    {/* Footer Actions */}
                    <div className="pt-4 border-t border-gray-100 flex items-center justify-end gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-xs font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-xl transition cursor-pointer"
                        >
                            {t("common.cancel", "Abbrechen")}
                        </button>

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="px-5 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-xs transition cursor-pointer disabled:opacity-50"
                        >
                            {isSubmitting ? t("common.saving", "Speichere...") : t("help.save_changes_live", "Änderungen live speichern")}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

