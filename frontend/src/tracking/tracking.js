import { apiFetch } from "../api/client"

let queue = []

function getOrCreateId(key) {
    let value = localStorage.getItem(key)
    if (!value) {
        value = crypto.randomUUID()
        localStorage.setItem(key, value)
    }
    return value
}

export function getTrackingContext() {
    const params = new URLSearchParams(window.location.search)

    return {
        anonymous_id: getOrCreateId("anonymous_id"),
        session_id: getOrCreateId("session_id"),
        source: params.get("src"),
        campaign: params.get("campaign"),
    }
}

function flushQueue() {
    if (queue.length === 0) return

    const payload = [...queue]
    queue = []

    apiFetch("/api/tracking/track/batch/", {
        method: "POST",
        body: JSON.stringify({ events: payload }),
    }).catch(() => { })
}

setInterval(flushQueue, 5000)

export function trackEvent(name, data = {}) {
    const context = getTrackingContext()

    queue.push({
        name,
        metadata: {
            ...context,
            ...data,
        },
    })
}
