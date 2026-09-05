/*
# src/hooks/useUserPreference.js
*/

import { useEffect, useRef, useCallback, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export default function useUserPreference(key) {
    const readyRef = useRef(false);
    const storageKey = `sharegy_pref_${key}`;

    const query = useQuery({
        queryKey: ["user-preference", key],
        queryFn: () => apiFetch(`/api/user-settings/${key}/`),
        staleTime: 60000,
    });

    const [value, setLocalValue] = useState(() => {
        try {
            const cached = localStorage.getItem(storageKey);
            return cached ? JSON.parse(cached) : {};
        } catch {
            return {};
        }
    });

    useEffect(() => {
        if (!query.isSuccess) {
            return;
        }

        const serverVal = query.data?.value ?? {};
        setLocalValue(serverVal);
        try {
            localStorage.setItem(storageKey, JSON.stringify(serverVal));
        } catch {
            // ignore localStorage quota errors
        }

        readyRef.current = true;
    }, [query.isSuccess, query.data, storageKey]);

    const setValue = useCallback(
        async (nextValue) => {
            setLocalValue(nextValue);
            try {
                localStorage.setItem(storageKey, JSON.stringify(nextValue));
            } catch {
                // ignore
            }

            if (!readyRef.current) {
                return;
            }

            try {
                await apiFetch(`/api/user-settings/${key}/`, {
                    method: "PATCH",
                    body: JSON.stringify({
                        value: nextValue,
                    }),
                });
            } catch (err) {
                console.error("Failed to persist user preference:", err);
            }
        },
        [key, storageKey]
    );

    return {
        ...query,
        value,
        isReady: query.isSuccess,
        setValue,
    };
}
