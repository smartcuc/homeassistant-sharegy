import { useTheme } from "../../theme/ThemeContext";

export default function DashboardLayout({ children }) {
    const theme = useTheme();

    return (
        <div className={`w-full ${theme?.colors?.bg || ""}`}>
            <div className="px-4 sm:px-6 pt-4 pb-8 max-w-7xl mx-auto space-y-5">
                {children}
            </div>
        </div>
    );
}


