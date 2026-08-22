/*
# src/features/forecast/hooks/useSolarForecast.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../../../api/client";

export function useSolarForecast(stringId = "all") {
    return useQuery({
        queryKey: ["solar-forecast", stringId],
        queryFn: () => {
            const queryParam = stringId && stringId !== "all" ? `?string_id=${stringId}` : "";
            return apiFetch(`/api/forecast/home/${queryParam}`);
        },
    });
}
