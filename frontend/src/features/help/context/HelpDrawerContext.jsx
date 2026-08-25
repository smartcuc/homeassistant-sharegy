/*
# src/features/help/context/HelpDrawerContext.jsx
*/

import { useState, useMemo } from "react";
import { useLocation } from "react-router-dom";
import { HelpDrawerContext } from "./helpDrawerContextInstance";

function getContextKeyFromPath(path) {
    if (path.includes("/forecast") || path.includes("/solarforecast")) {
        return "forecast";
    }
    if (path.includes("/energy") || path.includes("/dashboard")) {
        return "energy_dashboard";
    }
    if (path.includes("/market") || path.includes("/tariff")) {
        return "tariffs";
    }
    if (path.includes("/alerts")) {
        return "alerts";
    }
    if (path.includes("/devices") || path.includes("/producers")) {
        return "devices";
    }
    if (path.includes("/optimizer")) {
        return "optimizer";
    }
    if (path.includes("/billing")) {
        return "billing";
    }
    return "";
}

export function HelpDrawerProvider({ children }) {
    const [isOpen, setIsOpen] = useState(false);
    const [customContextKey, setCustomContextKey] = useState(null);
    const [selectedArticleSlug, setSelectedArticleSlug] = useState(null);
    const location = useLocation();

    // Derived context key without calling setState inside an effect
    const derivedKey = useMemo(() => getContextKeyFromPath(location.pathname), [location.pathname]);
    const contextKey = customContextKey ?? derivedKey;

    const openHelp = (customKey = null, articleSlug = null) => {
        if (customKey) setCustomContextKey(customKey);
        setSelectedArticleSlug(articleSlug);
        setIsOpen(true);
    };

    const closeHelp = () => {
        setIsOpen(false);
        setSelectedArticleSlug(null);
        setCustomContextKey(null);
    };

    const toggleHelp = () => {
        setIsOpen((prev) => !prev);
    };

    return (
        <HelpDrawerContext.Provider
            value={{
                isOpen,
                openHelp,
                closeHelp,
                toggleHelp,
                contextKey,
                setContextKey: setCustomContextKey,
                selectedArticleSlug,
                setSelectedArticleSlug,
            }}
        >
            {children}
        </HelpDrawerContext.Provider>
    );
}
