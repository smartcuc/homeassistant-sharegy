/*
# src/features/market/api.js
*/

import { apiFetch } from "../../api/client";

export async function fetchHomeTariff() {
    return await apiFetch("/api/market/tariff/");
}

export async function saveHomeTariff(payload) {
    return await apiFetch("/api/market/tariff/", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export async function fetchTibberHomes(token) {
    return await apiFetch("/api/market/tariff/tibber-homes/", {
        method: "POST",
        body: JSON.stringify({ tibber_token: token }),
    });
}
