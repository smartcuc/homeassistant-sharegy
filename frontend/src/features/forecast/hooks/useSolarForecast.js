/*
# src/features/forecast/hooks/useSolarForecast.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../../../api/client";

export function useSolarForecast(stringId = "all", hours = 24) {
    return useQuery({
        queryKey: ["solar-forecast", stringId, hours],
        queryFn: () => {
            const params = new URLSearchParams();
            if (stringId && stringId !== "all") {
                params.set("string_id", stringId);
            }
            if (hours) {
                params.set("hours", hours);
            }
            const qs = params.toString();
            return apiFetch(`/api/forecast/home/${qs ? `?${qs}` : ""}`);
        },
    });
}
