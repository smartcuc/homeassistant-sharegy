/*
# src/features/help/context/useHelpDrawer.js
*/

import { useContext } from "react";
import { HelpDrawerContext } from "./helpDrawerContextInstance";

export function useHelpDrawer() {
    const context = useContext(HelpDrawerContext);
    if (!context) {
        throw new Error("useHelpDrawer must be used within a HelpDrawerProvider");
    }
    return context;
}
