import React, { createContext, useContext, useState, useEffect } from "react";
import { apiFetch } from "../api/client";

const TenantThemingContext = createContext(null);

export const TenantThemingProvider = ({ children }) => {
  const [theming, setTheming] = useState({
    primaryColor: "#0284c7", // default sky-600
    secondaryColor: "#0f172a", // slate-900
    accentColor: "#38bdf8", // sky-400
    buttonColor: "#0284c7",
    logoUrl: "",
    faviconUrl: "",
    companyLegalName: "Sharegy GmbH",
    supportEmail: "support@sharegy.de",
    customDomain: "",
    isWhitelabelActive: false,
    loaded: false,
  });

  const applyThemeVariables = (themeData) => {
    const root = document.documentElement;
    if (themeData.primaryColor) {
      root.style.setProperty("--brand-primary", themeData.primaryColor);
    }
    if (themeData.secondaryColor) {
      root.style.setProperty("--brand-secondary", themeData.secondaryColor);
    }
    if (themeData.accentColor) {
      root.style.setProperty("--brand-accent", themeData.accentColor);
    }
    if (themeData.buttonColor) {
      root.style.setProperty("--brand-button", themeData.buttonColor);
    }
  };

  const fetchTheming = async () => {
    try {
      // 1. Prüfe ob Domain ein Whitelabel-Host ist
      const hostname = window.location.hostname;
      if (hostname !== "localhost" && hostname !== "127.0.0.1" && !hostname.includes("sharegy.de")) {
        const domainData = await apiFetch(`/api/core/tenant/by-domain/?domain=${hostname}`).catch(() => null);
        if (domainData && domainData.is_whitelabel_active) {
          const t = domainData;
          const data = {
            primaryColor: t.primary_color || "#0284c7",
            secondaryColor: t.secondary_color || "#0f172a",
            accentColor: t.accent_color || "#38bdf8",
            buttonColor: t.button_color || "#0284c7",
            logoUrl: t.logo_url || "",
            faviconUrl: t.favicon_url || "",
            companyLegalName: t.company_legal_name || "Energiepartner",
            supportEmail: t.support_email || "",
            customDomain: t.custom_domain || hostname,
            isWhitelabelActive: true,
            loaded: true,
          };
          setTheming(data);
          applyThemeVariables(data);
          return;
        }
      }

      // 2. Regulärer Tenant-Call
      const tenantTheming = await apiFetch("/api/core/tenant/theming/").catch(() => null);
      if (tenantTheming) {
        const t = tenantTheming;
        const data = {
          primaryColor: t.primary_color || "#0284c7",
          secondaryColor: t.secondary_color || "#0f172a",
          accentColor: t.accent_color || "#38bdf8",
          buttonColor: t.button_color || "#0284c7",
          logoUrl: t.logo_url || "",
          faviconUrl: t.favicon_url || "",
          companyLegalName: t.company_legal_name || "Sharegy GmbH",
          supportEmail: t.support_email || "support@sharegy.de",
          customDomain: t.custom_domain || "",
          isWhitelabelActive: t.is_whitelabel_active || false,
          loaded: true,
        };
        setTheming(data);
        applyThemeVariables(data);
        return;
      }
    } catch (err) {
      console.warn("TenantTheming fetch error:", err);
    } finally {
      setTheming((prev) => ({ ...prev, loaded: true }));
    }
  };

  const updatePreviewTheme = (updatedFields) => {
    const updated = { ...theming, ...updatedFields };
    setTheming(updated);
    applyThemeVariables(updated);
  };

  useEffect(() => {
    fetchTheming();
  }, []);

  return (
    <TenantThemingContext.Provider value={{ theming, updatePreviewTheme, reloadTheming: fetchTheming }}>
      {children}
    </TenantThemingContext.Provider>
  );
};

export const useTenantTheming = () => {
  const context = useContext(TenantThemingContext);
  if (!context) {
    return {
      theming: {
        primaryColor: "#0284c7",
        secondaryColor: "#0f172a",
        accentColor: "#38bdf8",
        buttonColor: "#0284c7",
        logoUrl: "",
        companyLegalName: "Sharegy",
        supportEmail: "support@sharegy.de",
        isWhitelabelActive: false,
        loaded: true,
      },
      updatePreviewTheme: () => {},
      reloadTheming: () => {},
    };
  }
  return context;
};
