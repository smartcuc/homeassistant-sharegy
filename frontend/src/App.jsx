/*
# src/App.jsx
*/

import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import { useEffect, lazy, Suspense } from "react";

import { ThemeProvider } from "./theme/ThemeContext";
import { defaultTheme } from "./theme/themes";
import { TenantThemingProvider } from "./context/TenantThemingContext";

import CookieConsentBanner from "./components/legal/CookieConsentBanner";
import ScrollToTop from "./components/common/ScrollToTop";
import { initializeNativeBridge } from "./utils/nativeBridge";

const AppRoutes = lazy(() => import("./AppRoutes"));   // ✅ PUBLIC
const PrivateApp = lazy(() => import("./PrivateApp")); // ✅ PRIVATE
const AdminApp = lazy(() => import("./AdminApp"));     // ✅ ADMIN

function NativeLifecycleManager() {
  const navigate = useNavigate();
  useEffect(() => {
    initializeNativeBridge(navigate);
  }, [navigate]);
  return null;
}

function GlobalRouteFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 text-gray-400 font-medium">
      <div className="flex items-center gap-3">
        <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <span>Sharegy lädt…</span>
      </div>
    </div>
  );
}

export default function App() {

  return (
    <TenantThemingProvider>
      <ThemeProvider theme={defaultTheme}>

        <BrowserRouter>
        {/* 🔄 AUTOMATISCHER SCROLL-TO-TOP BEI JEDEM ROUTENWECHSEL */}
        <ScrollToTop />
        {/* 📱 NATIVE ANDROID/CAPACITOR BRIDGE LIFECYCLE */}
        <NativeLifecycleManager />

        <Suspense fallback={<GlobalRouteFallback />}>
          <Routes>

            {/* 🔒 PRIVATE */}
            <Route path="/app/*" element={<PrivateApp />} />

            {/* 🔐 ADMIN */}
            <Route path="/admin/*" element={<AdminApp />} />

            {/* 🔓 PUBLIC */}
            <Route path="/*" element={<AppRoutes />} />

          </Routes>
        </Suspense>

        {/* 🍪 GLOBAL DSGVO & TDDDG COOKIE CONSENT MANAGER */}
        <CookieConsentBanner />

      </BrowserRouter>

    </ThemeProvider>
    </TenantThemingProvider>
  );
}
