/*
# src/features/support/api.js
# REST API client for Universal Support Desk (Sharegy & Factofy)
*/

import { apiFetch, getApiUrl } from "../../api/client";
import { getCSRFToken } from "../../lib/csrf";

const API_BASE = "/api/support";

const defaultHeaders = () => {
    const headers = {};
    const csrftoken = getCSRFToken();
    if (csrftoken) {
        headers["X-CSRFToken"] = csrftoken;
    }
    return headers;
};

export async function fetchUserTickets(params = {}) {
    const query = new URLSearchParams(params).toString();
    return apiFetch(`${API_BASE}/tickets/${query ? `?${query}` : ""}`);
}

export async function fetchTicketDetail(ticketId) {
    return apiFetch(`${API_BASE}/tickets/${ticketId}/`);
}

export async function createTicket(ticketData) {
    if (ticketData instanceof FormData) {
        const fullUrl = getApiUrl(`${API_BASE}/tickets/`);
        const res = await fetch(fullUrl, {
            method: "POST",
            headers: defaultHeaders(),
            credentials: "include",
            body: ticketData,
        });
        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            throw new Error(errorData.error || errorData.detail || "Fehler beim Erstellen des Tickets");
        }
        return res.json();
    }

    return apiFetch(`${API_BASE}/tickets/`, {
        method: "POST",
        body: JSON.stringify(ticketData),
    });
}

export async function postTicketMessage(ticketId, messageData) {
    if (messageData instanceof FormData) {
        const fullUrl = getApiUrl(`${API_BASE}/tickets/${ticketId}/messages/`);
        const res = await fetch(fullUrl, {
            method: "POST",
            headers: defaultHeaders(),
            credentials: "include",
            body: messageData,
        });
        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            throw new Error(errorData.error || errorData.detail || "Nachricht konnte nicht gesendet werden");
        }
        return res.json();
    }

    return apiFetch(`${API_BASE}/tickets/${ticketId}/messages/`, {
        method: "POST",
        body: JSON.stringify(messageData),
    });
}

export async function updateTicketStatus(ticketId, newStatus) {
    return apiFetch(`${API_BASE}/tickets/${ticketId}/`, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus }),
    });
}

export async function fetchDeflectionSuggestions(query) {
    if (!query || query.trim().length < 3) return [];
    try {
        const data = await apiFetch(`${API_BASE}/deflection/suggest/?q=${encodeURIComponent(query)}`);
        return data.suggestions || [];
    } catch {
        return [];
    }
}

/* =========================================================================
   STAFF / AGENT DASHBOARD ENDPOINTS
   ========================================================================= */

export async function fetchAgentTickets(params = {}) {
    const query = new URLSearchParams(params).toString();
    return apiFetch(`${API_BASE}/agent/tickets/${query ? `?${query}` : ""}`);
}

export async function updateAgentTicket(ticketId, data) {
    return apiFetch(`${API_BASE}/agent/tickets/${ticketId}/`, {
        method: "PATCH",
        body: JSON.stringify(data),
    });
}

export async function postAgentInternalNote(ticketId, bodyText) {
    return apiFetch(`${API_BASE}/agent/tickets/${ticketId}/`, {
        method: "POST",
        body: JSON.stringify({ body: bodyText }),
    });
}

export async function escalateTicketToSmartEvo(ticketId) {
    return apiFetch(`${API_BASE}/agent/tickets/${ticketId}/escalate/`, {
        method: "POST",
    });
}

export async function fetchCannedResponses(projectKey = "sharegy") {
    try {
        return await apiFetch(`${API_BASE}/canned-responses/?project_key=${encodeURIComponent(projectKey)}`);
    } catch {
        return [];
    }
}


