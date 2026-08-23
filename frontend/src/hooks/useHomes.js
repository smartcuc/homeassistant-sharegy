/*
# src/hooks/useHomes.js
*/

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export function useHomes() {
    const queryClient = useQueryClient();

    const query = useQuery({
        queryKey: ["homes"],
        queryFn: () => apiFetch("/api/devices/homes/"),
        staleTime: 1000 * 60 * 5,
    });

    const regenerateMutation = useMutation({
        mutationFn: () =>
            apiFetch("/api/devices/homes/regenerate-mqtt/", {
                method: "POST",
            }),
        onSuccess: () => {
            queryClient.invalidateQueries(["homes"]);
        },
    });

    const homes = Array.isArray(query.data) ? query.data : [];
    const primaryHome = homes[0] || null;

    return {
        homes,
        primaryHome,
        isLoading: query.isLoading,
        error: query.error,
        refetch: query.refetch,
        regenerateMqttPassword: regenerateMutation.mutateAsync,
        isRegenerating: regenerateMutation.isLoading,
    };
}

