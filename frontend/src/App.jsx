/*
# src/App.jsx
*/

import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import { useEffect } from "react";

import { ThemeProvider } from "./theme/ThemeContext";
import { defaultTheme } from "./theme/themes";

import AppRoutes from "./AppRoutes";   // ✅ PUBLIC
import PrivateApp from "./PrivateApp"; // ✅ PRIVATE
import AdminApp from "./AdminApp";     // ✅ ADMIN
import CookieConsentBanner from "./components/legal/CookieConsentBanner";
import ScrollToTop from "./components/common/ScrollToTop";
import { initializeNativeBridge } from "./utils/nativeBridge";

function NativeLifecycleManager() {
  const navigate = useNavigate();
  useEffect(() => {
    initializeNativeBridge(navigate);
  }, [navigate]);
  return null;
}

export default function App() {

  return (
    <ThemeProvider theme={defaultTheme}>

      <BrowserRouter>
        {/* 🔄 AUTOMATISCHER SCROLL-TO-TOP BEI JEDEM ROUTENWECHSEL */}
        <ScrollToTop />
        {/* 📱 NATIVE ANDROID/CAPACITOR BRIDGE LIFECYCLE */}
        <NativeLifecycleManager />

        <Routes>


          {/* 🔒 PRIVATE */}
          <Route path="/app/*" element={<PrivateApp />} />

          {/* 🔐 ADMIN */}
          <Route path="/admin/*" element={<AdminApp />} />

          {/* 🔓 PUBLIC */}
          <Route path="/*" element={<AppRoutes />} />

        </Routes>

        {/* 🍪 GLOBAL DSGVO & TDDDG COOKIE CONSENT MANAGER */}
        <CookieConsentBanner />

      </BrowserRouter>

    </ThemeProvider>
  );
}
