import { useEffect } from "react";

/**
 * Custom hook to handle Escape key dismissal for modal dialogs and drawers.
 * Can be called as:
 * - useModalDismiss(isOpen, onClose)
 * - useModalDismiss(onClose)  // when component is conditionally mounted
 */
export function useModalDismiss(isOpenOrOnClose, possibleOnClose) {
    const handler = typeof isOpenOrOnClose === "function" ? isOpenOrOnClose : possibleOnClose;
    const active = typeof isOpenOrOnClose === "boolean" ? isOpenOrOnClose : true;

    useEffect(() => {
        if (!active || typeof handler !== "function") return;

        function handleKeyDown(event) {
            if (event.key === "Escape" || event.key === "Esc") {
                event.stopPropagation();
                handler();
            }
        }

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [active, handler]);
}

export default useModalDismiss;
