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

// 🔄 Automatische Behandlung von veralteten Chunks nach neuem Deployment (Vite Dynamic Imports)
window.addEventListener("vite:preloadError", (event) => {
  const reloadKey = "sharegy_chunk_reload";
  const lastReload = sessionStorage.getItem(reloadKey);
  const now = Date.now();
  if (!lastReload || now - Number(lastReload) > 10000) {
    sessionStorage.setItem(reloadKey, String(now));
    window.location.reload();
  }
});

window.addEventListener("unhandledrejection", (event) => {
  const msg = event?.reason?.message || String(event?.reason || "");
  if (
    msg.includes("Failed to fetch dynamically imported module") ||
    msg.includes("error loading dynamically imported module") ||
    msg.includes("Importing a module script failed") ||
    msg.includes("Loading chunk")
  ) {
    const reloadKey = "sharegy_chunk_reload";
    const lastReload = sessionStorage.getItem(reloadKey);
    const now = Date.now();
    if (!lastReload || now - Number(lastReload) > 10000) {
      sessionStorage.setItem(reloadKey, String(now));
      window.location.reload();
    }
  }
});

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