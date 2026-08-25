/*
# src/features/help/api.js
*/

import { apiFetch } from "../../api/client";

export async function fetchHelpCategories() {
    return apiFetch("/api/help/categories/");
}

export async function fetchHelpArticles(params = {}) {
    const query = new URLSearchParams();
    if (params.search) query.set("search", params.search);
    if (params.category) query.set("category", params.category);
    if (params.featured) query.set("featured", "true");
    if (params.context_key) query.set("context_key", params.context_key);

    const qs = query.toString();
    return apiFetch(`/api/help/articles/${qs ? `?${qs}` : ""}`);
}

export async function fetchContextArticles(key = "") {
    return apiFetch(`/api/help/context/?key=${encodeURIComponent(key)}`);
}

export async function fetchHelpArticle(slug) {
    return apiFetch(`/api/help/articles/${encodeURIComponent(slug)}/`);
}

export async function sendArticleFeedback(slug, helpful) {
    return apiFetch(`/api/help/articles/${encodeURIComponent(slug)}/feedback/`, {
        method: "POST",
        body: JSON.stringify({ helpful }),
    });
}

export async function updateHelpArticle(slug, data) {
    return apiFetch(`/api/help/articles/${encodeURIComponent(slug)}/`, {
        method: "PATCH",
        body: JSON.stringify(data),
    });
}

