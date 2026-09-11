/**
 * frontend/src/utils/nativeBridge.js
 * 
 * Native Capacitor Bridge for Sharegy Mobile App.
 * Handles Android Status Bar styling, Splash Screen hiding, Hardware Back Button, and Haptic Feedback.
 */

import { Capacitor } from "@capacitor/core";
import { App as CapacitorApp } from "@capacitor/app";
import { StatusBar, Style } from "@capacitor/status-bar";
import { SplashScreen } from "@capacitor/splash-screen";
import { Haptics, ImpactStyle } from "@capacitor/haptics";

export const isNativePlatform = () => Capacitor.isNativePlatform();
export const getPlatform = () => Capacitor.getPlatform(); // 'android' | 'ios' | 'web'

/**
 * Initializes native mobile plugins on app launch.
 * @param {Function} navigateCallback React-Router navigate function (e.g. useNavigate())
 */
export async function initializeNativeBridge(navigateCallback) {
    if (!isNativePlatform()) {
        return;
    }

    try {
        // 1. Status Bar Setup
        if (Capacitor.isPluginAvailable("StatusBar")) {
            await StatusBar.setStyle({ style: Style.Dark });
            if (getPlatform() === "android") {
                await StatusBar.setBackgroundColor({ color: "#0F172A" });
                await StatusBar.setOverlaysWebView({ overlay: false });
            }
        }

        // 2. Hide Splash Screen smoothly once UI is ready
        if (Capacitor.isPluginAvailable("SplashScreen")) {
            await SplashScreen.hide({ fadeOutDuration: 300 });
        }

        // 3. Android Hardware Back Button Handling
        if (Capacitor.isPluginAvailable("App")) {
            CapacitorApp.addListener("backButton", ({ canGoBack }) => {
                if (window.location.pathname === "/app/dashboard" || window.location.pathname === "/") {
                    // Auf Hauptseiten App minimieren
                    CapacitorApp.minimizeApp();
                } else if (canGoBack && typeof navigateCallback === "function") {
                    navigateCallback(-1);
                } else if (typeof navigateCallback === "function") {
                    navigateCallback("/app/dashboard");
                }
            });

            // Deep-Linking / App URL Open Listener (z.B. sharegy://magic?token=<token> oder https://sharegy.de/t/<token>)
            CapacitorApp.addListener("appUrlOpen", (data) => {
                try {
                    console.log("Deep link received by App:", data?.url);
                    if (!data || !data.url) return;

                    const rawUrl = String(data.url).trim();

                    // 1. Custom Scheme: sharegy://magic?token=xyz oder sharegy://t/xyz
                    if (rawUrl.toLowerCase().startsWith("sharegy://")) {
                        const withoutScheme = rawUrl.replace(/^sharegy:\/\//i, "");

                        if (withoutScheme.includes("token=")) {
                            const params = new URLSearchParams(withoutScheme.split("?")[1] || "");
                            const token = params.get("token") || params.get("code");
                            if (token && typeof navigateCallback === "function") {
                                navigateCallback(`/t/${encodeURIComponent(token)}`);
                                return;
                            }
                        }

                        // Path based: sharegy://t/XYZ oder sharegy://magic/XYZ
                        const parts = withoutScheme.split("?")[0].split("/").filter(Boolean);
                        if (parts.length > 0) {
                            const lastSegment = parts[parts.length - 1];
                            if (lastSegment && typeof navigateCallback === "function") {
                                navigateCallback(`/t/${encodeURIComponent(lastSegment)}`);
                                return;
                            }
                        }
                    }

                    // 2. HTTPS standard URL: https://sharegy.de/t/xyz oder https://sharegy.de/app/...
                    const url = new URL(rawUrl);
                    if (url.pathname.startsWith("/t/")) {
                        const token = url.pathname.replace(/^\/t\//, "").split("/")[0];
                        if (token && typeof navigateCallback === "function") {
                            navigateCallback(`/t/${encodeURIComponent(token)}`);
                            return;
                        }
                    }

                    const path = url.pathname + url.search;
                    if (path && typeof navigateCallback === "function") {
                        navigateCallback(path);
                    }
                } catch (deepErr) {
                    console.warn("Deep link parse error:", deepErr);
                }
            });
        }
    } catch (err) {
        console.warn("Native bridge initialization notice:", err);
    }
}

/**
 * Triggers light haptic feedback on interactive buttons/switches.
 */
export async function triggerHapticFeedback(style = ImpactStyle.Light) {
    if (!isNativePlatform() || !Capacitor.isPluginAvailable("Haptics")) {
        return;
    }
    try {
        await Haptics.impact({ style });
    } catch {
        // Ignore fallback
    }
}
