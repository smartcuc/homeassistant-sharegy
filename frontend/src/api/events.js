import { apiFetch } from "./client";

export async function fetchEvents() {
    return apiFetch("/api/v1/events/");
}