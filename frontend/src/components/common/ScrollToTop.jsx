/*
# src/components/common/ScrollToTop.jsx
*/

import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { initGA, trackPageView } from "../../tracking/ga";

/**
 * Automatischer Scroll-to-Top und GA4 PageView Tracking bei jedem Routenwechsel.
 */
export default function ScrollToTop() {
    const { pathname, search } = useLocation();

    useEffect(() => {
        // GA4 Initialisierung
        initGA();
    }, []);

    useEffect(() => {
        // 1. Globales Fenster nach ganz oben scrollen
        window.scrollTo({
            top: 0,
            left: 0,
            behavior: "instant",
        });

        // 2. Alle inneren Scroll-Container auf Position 0 setzen
        const scrollableContainers = document.querySelectorAll(
            ".overflow-auto, .overflow-y-auto, [data-scroll-container], main"
        );
        scrollableContainers.forEach((container) => {
            container.scrollTop = 0;
        });

        // 3. Google Analytics 4 Page View tracken
        trackPageView(pathname + (search || ""));
    }, [pathname, search]);

    return null;
}

