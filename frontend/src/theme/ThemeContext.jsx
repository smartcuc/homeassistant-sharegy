/*
# src/theme/ThemeContext.jsx
*/

import React, { createContext, useContext, useState, useEffect } from "react";

const ThemeContext = createContext(null);

// ✅ DEFAULT THEME
export const defaultTheme = {
    colors: {
        bg: "bg-gray-50",
        card: "bg-white border border-gray-200",

        primary: "#6366f1",
        secondary: "#9333ea",

        text: "text-gray-900",
        textMuted: "text-gray-500",

        border: "border-gray-200",
        hover: "hover:bg-gray-100",
    },

    radius: {
        md: "rounded-lg",
        lg: "rounded-2xl",
    },

    spacing: {
        section: "mb-10",
        card: "p-6",
    },
};

// ✅ PROVIDER
export function ThemeProvider({ theme = {}, children }) {
    // Mode can be: "light" | "dark" | "system"
    const [mode, setMode] = useState(() => {
        const stored = localStorage.getItem("sharegy_theme_mode");
        if (stored === "dark" || stored === "light" || stored === "system") {
            return stored;
        }
        return "light";
    });

    const [resolvedDark, setResolvedDark] = useState(() => {
        if (mode === "dark") return true;
        if (mode === "light") return false;
        return typeof window !== "undefined" && window.matchMedia?.("(prefers-color-scheme: dark)").matches;
    });

    useEffect(() => {
        const root = document.documentElement;
        let isDark = false;

        if (mode === "dark") {
            isDark = true;
        } else if (mode === "light") {
            isDark = false;
        } else {
            isDark = typeof window !== "undefined" && window.matchMedia?.("(prefers-color-scheme: dark)").matches;
        }

        setResolvedDark(isDark);
        if (isDark) {
            root.classList.add("dark");
        } else {
            root.classList.remove("dark");
        }

        localStorage.setItem("sharegy_theme_mode", mode);
    }, [mode]);

    // Listen to system theme changes when mode === "system"
    useEffect(() => {
        if (mode !== "system" || typeof window === "undefined" || !window.matchMedia) return;
        const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
        const handleChange = (e) => {
            const isDark = e.matches;
            setResolvedDark(isDark);
            if (isDark) {
                document.documentElement.classList.add("dark");
            } else {
                document.documentElement.classList.remove("dark");
            }
        };

        mediaQuery.addEventListener("change", handleChange);
        return () => mediaQuery.removeEventListener("change", handleChange);
    }, [mode]);

    const toggleTheme = () => {
        setMode((prev) => (prev === "dark" ? "light" : "dark"));
    };

    const setThemeMode = (newMode) => {
        setMode(newMode);
    };

    const value = {
        ...defaultTheme,
        ...theme,
        mode,
        isDark: resolvedDark,
        toggleTheme,
        setThemeMode,
        colors: {
            ...defaultTheme.colors,
            ...theme?.colors,
        },
        radius: {
            ...defaultTheme.radius,
            ...theme?.radius,
        },
        spacing: {
            ...defaultTheme.spacing,
            ...theme?.spacing,
        },
    };

    return (
        <ThemeContext.Provider value={value}>
            {children}
        </ThemeContext.Provider>
    );
}

// ✅ HOOK
export function useTheme() {
    const context = useContext(ThemeContext);
    if (!context) {
        return {
            ...defaultTheme,
            mode: "light",
            isDark: false,
            toggleTheme: () => {},
            setThemeMode: () => {},
        };
    }
    return context;
}

