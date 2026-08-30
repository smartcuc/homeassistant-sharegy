import "./i18n";   // ✅ 1. MUST BE FIRST IMPORT
import React from "react";
import ReactDOM from "react-dom/client";
import { I18nextProvider } from "react-i18next";
import i18n from "./i18n";
import App from "./App";
import "./index.css";   // ✅ CSS
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { initSentry } from "./tracking/sentry";

// 🛡️ Sentry Error Tracking aktivieren
initSentry();


// ✅ globaler Cache
const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <I18nextProvider i18n={i18n}>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </I18nextProvider>
  </React.StrictMode>
);