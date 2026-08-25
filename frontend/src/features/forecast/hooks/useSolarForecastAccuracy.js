/*
# src/features/forecast/hooks/useSolarForecastAccuracy.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../../../api/client";

export function useSolarForecastAccuracy(period = "today", stringId = "all") {
    return useQuery({
        queryKey: ["solar-forecast-accuracy", period, stringId],
        queryFn: () => apiFetch(`/api/forecast/accuracy/?period=${period}&string_id=${stringId}`),
        refetchInterval: 60000,
    });
}

