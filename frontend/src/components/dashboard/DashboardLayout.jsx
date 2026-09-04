import { useTheme } from "../../theme/ThemeContext";

export default function DashboardLayout({ children }) {
    const theme = useTheme();

    return (
        <div className={`w-full ${theme?.colors?.bg || ""}`}>
            <div className="max-w-7xl mx-auto space-y-6">
                {children}
            </div>
        </div>
    );
}


