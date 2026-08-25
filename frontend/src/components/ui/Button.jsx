/*
# src/components/ui/Button.jsx
*/

import { useTheme, defaultTheme } from "../../theme/ThemeContext";

export default function Button({ children, onClick, variant = "primary", type = "button", disabled = false, className = "", ...props }) {
    const theme = useTheme() || defaultTheme; // ✅ FIX
    const variants = {
        primary: "text-white",
        secondary: "border text-gray-700",
    };

    return (
        <button
            type={type}
            disabled={disabled}
            onClick={onClick}
            className={`
                px-4 py-2
                ${theme.radius.md}
                ${variants[variant]}
                transition-all duration-150
                active:scale-[0.97]
                ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
                ${className}
            `}
            style={{
                background:
                    variant === "primary" ? theme.primary : "transparent",
                borderColor:
                    variant === "secondary" ? "#e5e7eb" : "transparent",
            }}
            {...props}
        >
            {children}
        </button>
    );
}
