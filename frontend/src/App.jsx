/*
# src/App.jsx
*/

import { BrowserRouter, Routes, Route } from "react-router-dom";

import { ThemeProvider } from "./theme/ThemeContext";
import { defaultTheme } from "./theme/themes";

import AppRoutes from "./AppRoutes";   // ✅ PUBLIC
import PrivateApp from "./PrivateApp"; // ✅ PRIVATE
import AdminApp from "./AdminApp";     // ✅ ADMIN
import CookieConsentBanner from "./components/legal/CookieConsentBanner";
import ScrollToTop from "./components/common/ScrollToTop";

export default function App() {

  return (
    <ThemeProvider theme={defaultTheme}>

      <BrowserRouter>
        {/* 🔄 AUTOMATISCHER SCROLL-TO-TOP BEI JEDEM ROUTENWECHSEL */}
        <ScrollToTop />

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
