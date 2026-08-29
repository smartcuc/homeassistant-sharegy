/*
# src/components/common/ScrollToTop.jsx
*/

import { useEffect } from "react";
import { useLocation } from "react-router-dom";

/**
 * Automatischer Scroll-to-Top bei jedem Routenwechsel.
 * Setzt sowohl window.scrollTo(0, 0) als auch alle inneren
 * scrollbaren Container (z. B. overflow-auto in AppShell) sofort auf 0 zurück.
 */
export default function ScrollToTop() {
    const { pathname, search } = useLocation();

    useEffect(() => {
        // 1. Globales Fenster nach ganz oben scrollen
        window.scrollTo({
            top: 0,
            left: 0,
            behavior: "instant",
        });

        // 2. Alle inneren Scroll-Container (z. B. AppShell content area) auf Position 0 setzen
        const scrollableContainers = document.querySelectorAll(
            ".overflow-auto, .overflow-y-auto, [data-scroll-container], main"
        );
        scrollableContainers.forEach((container) => {
            container.scrollTop = 0;
        });
    }, [pathname, search]);

    return null;
}
