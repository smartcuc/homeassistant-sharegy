/*
# src/features/support/api.js
# REST API client for Universal Support Desk (Sharegy & Factofy)
*/

const API_BASE = "/api/support";

/**
 * Get cookie for CSRF protection in Django
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const defaultHeaders = () => {
    const headers = {};
    const csrftoken = getCookie("csrftoken");
    if (csrftoken) {
        headers["X-CSRFToken"] = csrftoken;
    }
    return headers;
};

export async function fetchUserTickets(params = {}) {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/tickets/${query ? `?${query}` : ""}`, {
        headers: defaultHeaders(),
    });
    if (!res.ok) throw new Error("Fehler beim Laden der Support-Tickets");
    return res.json();
}

export async function fetchTicketDetail(ticketId) {
    const res = await fetch(`${API_BASE}/tickets/${ticketId}/`, {
        headers: defaultHeaders(),
    });
    if (!res.ok) throw new Error("Ticket konnte nicht geladen werden");
    return res.json();
}

export async function createTicket(ticketData) {
    let body;
    const headers = defaultHeaders();

    if (ticketData instanceof FormData) {
        body = ticketData;
    } else {
        headers["Content-Type"] = "application/json";
        body = JSON.stringify(ticketData);
    }

    const res = await fetch(`${API_BASE}/tickets/`, {
        method: "POST",
        headers,
        body,
    });
    if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.detail || "Fehler beim Erstellen des Tickets");
    }
    return res.json();
}

export async function postTicketMessage(ticketId, messageData) {
    let body;
    const headers = defaultHeaders();

    if (messageData instanceof FormData) {
        body = messageData;
    } else {
        headers["Content-Type"] = "application/json";
        body = JSON.stringify(messageData);
    }

    const res = await fetch(`${API_BASE}/tickets/${ticketId}/messages/`, {
        method: "POST",
        headers,
        body,
    });
    if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.detail || "Nachricht konnte nicht gesendet werden");
    }
    return res.json();
}

export async function updateTicketStatus(ticketId, newStatus) {
    const res = await fetch(`${API_BASE}/tickets/${ticketId}/`, {
        method: "PATCH",
        headers: {
            ...defaultHeaders(),
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ status: newStatus }),
    });
    if (!res.ok) throw new Error("Status konnte nicht aktualisiert werden");
    return res.json();
}

export async function fetchDeflectionSuggestions(query) {
    if (!query || query.trim().length < 3) return [];
    const res = await fetch(`${API_BASE}/deflection/suggest/?q=${encodeURIComponent(query)}`, {
        headers: defaultHeaders(),
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.suggestions || [];
}

/* =========================================================================
   STAFF / AGENT DASHBOARD ENDPOINTS
   ========================================================================= */

export async function fetchAgentTickets(params = {}) {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/agent/tickets/${query ? `?${query}` : ""}`, {
        headers: defaultHeaders(),
    });
    if (!res.ok) throw new Error("Agent-Tickets konnten nicht geladen werden");
    return res.json();
}

export async function updateAgentTicket(ticketId, data) {
    const res = await fetch(`${API_BASE}/agent/tickets/${ticketId}/`, {
        method: "PATCH",
        headers: {
            ...defaultHeaders(),
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Ticket-Update fehlgeschlagen");
    return res.json();
}

export async function postAgentInternalNote(ticketId, bodyText) {
    const res = await fetch(`${API_BASE}/agent/tickets/${ticketId}/`, {
        method: "POST",
        headers: {
            ...defaultHeaders(),
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ body: bodyText }),
    });
    if (!res.ok) throw new Error("Interne Notiz konnte nicht gespeichert werden");
    return res.json();
}

export async function fetchCannedResponses(projectKey = "sharegy") {
    const res = await fetch(`${API_BASE}/canned-responses/?project_key=${encodeURIComponent(projectKey)}`, {
        headers: defaultHeaders(),
    });
    if (!res.ok) return [];
    return res.json();
}

