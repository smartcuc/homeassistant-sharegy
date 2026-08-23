/*
# src/i18n/index.js
*/

import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import de from "./locales/de.json";
import en from "./locales/en.json";
import pl from "./locales/pl.json";

const resources = {
    de: { translation: de },
    en: { translation: en },
    pl: { translation: pl },
};

i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources,
        fallbackLng: "de",
        supportedLngs: ["de", "en", "pl"],
        nonExplicitSupportedLngs: true,
        load: "languageOnly",
        debug: false,
        interpolation: {
            escapeValue: false,
        },
        detection: {
            order: ["localStorage", "navigator"],
            lookupLocalStorage: "i18nextLng",
            caches: ["localStorage"],
        },
    });

export const texts = {
    de: {
        welcome: "Willkommen",
        start: "Start",
        profile: "Dein Profil",
        next: "Weiter",
        usage_question: "Wie nutzt du Sharegy?",
        standalone: "Eigenes System",
        tenant: "Community",
        standalone_desc: "Du nutzt dein eigenes EMS",
        tenant_desc: "Du bist Teil einer Energie-Community",
        join_tenant: "Community auswählen",
        tenant_dashboard: "Tenant Dashboard",
        invites: "Einladungen",
        members: "Mitglieder",
        viewer_invite: "Viewer Einladung",
        editor_invite: "Editor Einladung",
        admin_invite: "Admin Einladung",
        invite_link: "Einladungslink",
        audit_log: "Aktivität",
        member_removed: "Mitglied entfernt",
        role_updated: "Rolle geändert",
        invite_created: "Einladung erstellt",
        invite_deactivated: "Einladung deaktiviert",
    },
    en: {
        welcome: "Welcome",
        start: "Start",
        profile: "Your profile",
        next: "Next",
        usage_question: "How do you use Sharegy?",
        standalone: "Own system",
        tenant: "Community",
        standalone_desc: "You use your own EMS",
        tenant_desc: "You are part of a community",
        join_tenant: "Select community",
        tenant_dashboard: "Tenant Dashboard",
        invites: "Invites",
        members: "Members",
        viewer_invite: "Viewer Invite",
        editor_invite: "Editor Invite",
        admin_invite: "Admin Invite",
        invite_link: "Invite link",
        audit_log: "Activity",
        member_removed: "Member removed",
        role_updated: "Role updated",
        invite_created: "Invite created",
        invite_deactivated: "Invite deactivated",
    },
    pl: {
        welcome: "Witamy",
        start: "Start",
        profile: "Twój profil",
        next: "Dalej",
        usage_question: "Jak korzystasz z Sharegy?",
        standalone: "Własny system",
        tenant: "Społeczność",
        standalone_desc: "Korzystasz z własnego EMS",
        tenant_desc: "Jesteś częścią społeczności energetycznej",
        join_tenant: "Wybierz społeczność",
        tenant_dashboard: "Panel społeczności",
        invites: "Zaproszenia",
        members: "Członkowie",
        viewer_invite: "Zaproszenie dla Widza",
        editor_invite: "Zaproszenie dla Edytora",
        admin_invite: "Zaproszenie dla Administratora",
        invite_link: "Link do zaproszenia",
        audit_log: "Dziennik aktywności",
        member_removed: "Usunięto członka",
        role_updated: "Zaktualizowano rolę",
        invite_created: "Utworzono zaproszenie",
        invite_deactivated: "Dezaktywowano zaproszenie",
    },
};

export default i18n;
