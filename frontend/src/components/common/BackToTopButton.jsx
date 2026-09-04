/*
# src/components/common/BackToTopButton.jsx
*/

import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

export default function BackToTopButton({ scrollContainerRef, threshold = 160 }) {
    const { t } = useTranslation();
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const checkScroll = () => {
            const currentScroll = scrollContainerRef?.current
                ? scrollContainerRef.current.scrollTop
                : (window.pageYOffset || document.documentElement.scrollTop || 0);

            setIsVisible(currentScroll > threshold);
        };

        const target = scrollContainerRef?.current;
        if (target) {
            target.addEventListener("scroll", checkScroll, { passive: true });
            return () => target.removeEventListener("scroll", checkScroll);
        } else {
            window.addEventListener("scroll", checkScroll, { passive: true });
            return () => window.removeEventListener("scroll", checkScroll);
        }
    }, [scrollContainerRef, threshold]);

    const scrollToTop = () => {
        if (scrollContainerRef?.current) {
            scrollContainerRef.current.scrollTo({
                top: 0,
                behavior: "smooth",
            });
        }
        window.scrollTo({
            top: 0,
            behavior: "smooth",
        });
    };

    if (!isVisible) return null;

    return (
        <button
            type="button"
            onClick={scrollToTop}
            aria-label={t("common.back_to_top", "Nach oben scrollen")}
            title={t("common.back_to_top", "Nach oben scrollen")}
            className="fixed bottom-6 right-6 z-40 p-3 rounded-full bg-slate-900/85 hover:bg-slate-950 text-white dark:bg-slate-800/90 dark:hover:bg-slate-700 shadow-xl backdrop-blur-md border border-slate-700/50 dark:border-slate-600 transition-all duration-300 transform hover:-translate-y-1 hover:scale-105 active:scale-95 flex items-center justify-center cursor-pointer group animate-in fade-in zoom-in-75 duration-200"
        >
            <svg
                className="w-5 h-5 transition-transform duration-200 group-hover:-translate-y-0.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2.5}
            >
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
        </button>
    );
}
