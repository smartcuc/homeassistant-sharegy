/*
# src/App.jsx
*/

import { BrowserRouter, Routes, Route } from "react-router-dom";

import { ThemeProvider } from "./theme/ThemeContext";
import { defaultTheme } from "./theme/themes";

import AppRoutes from "./AppRoutes";   // ✅ PUBLIC
import PrivateApp from "./PrivateApp"; // ✅ PRIVATE
import AdminApp from "./AdminApp";     // ✅ ADMIN


export default function App() {

  return (
    <ThemeProvider theme={defaultTheme}>

      <BrowserRouter>

        <Routes>

          {/* 🔒 PRIVATE */}
          <Route path="/app/*" element={<PrivateApp />} />

          {/* 🔐 ADMIN */}
          <Route path="/admin/*" element={<AdminApp />} />

          {/* 🔓 PUBLIC */}
          <Route path="/*" element={<AppRoutes />} />

        </Routes>

      </BrowserRouter>

    </ThemeProvider>
  );
}
