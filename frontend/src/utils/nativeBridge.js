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

            // Deep-Linking / App URL Open Listener (z.B. https://sharegy.de/t/<token>)
            CapacitorApp.addListener("appUrlOpen", (data) => {
                try {
                    const url = new URL(data.url);
                    const path = url.pathname + url.search;
                    if (path && typeof navigateCallback === "function") {
                        navigateCallback(path);
                    }
                } catch {
                    // Fallback
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
