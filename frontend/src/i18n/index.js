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
        interpolation: {
            escapeValue: false, // React handles XSS
        },
        detection: {
            order: ["localStorage", "navigator"],
            caches: ["localStorage"],
        },
    });

export default i18n;

