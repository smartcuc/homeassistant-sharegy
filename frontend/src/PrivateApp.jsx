import { useUser } from "./hooks/useUser";
import { useSettings } from "./hooks/useSettings";
import Onboarding from "./pages/Onboarding";
import AppShell from "./components/AppShell";
import { Navigate } from "react-router-dom";
import { useEffect } from "react";
import i18n from "./i18n";

import { UserNavigationProvider } from "./context/UserNavigationContext";

export default function PrivateApp() {

    const { user, loading: userLoading } = useUser();
    const { settings, loading: settingsLoading } = useSettings();

    useEffect(() => {
        if (settings?.language && ["de", "en", "pl"].includes(settings.language)) {
            const currentLang = (i18n.resolvedLanguage || i18n.language || "de").substring(0, 2);
            if (currentLang !== settings.language) {
                i18n.changeLanguage(settings.language);
            }
        }
    }, [settings?.language]);

    if (userLoading || settingsLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center text-gray-400">
                Sharegy lädt…
            </div>
        );
    }


    if (!user) {
        return <Navigate to="/" replace />;
    }

    if (!settings) {
        return null;
    }

    if (settings.onboarding_step !== "done") {
        return <Onboarding />;
    }

    return (
        <UserNavigationProvider>
            <AppShell />
        </UserNavigationProvider>
    );
}