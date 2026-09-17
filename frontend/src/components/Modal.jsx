import useModalDismiss from "../hooks/useModalDismiss";
/*
# src/components/Modal.jsx
*/

export default function Modal({ title, children, onClose }) {
    useModalDismiss(onClose);
    return (
        <div 
            className="fixed inset-0 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200"
            onClick={onClose}
        >
            <div 
                className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-200"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="p-5 sm:p-6 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center bg-slate-50/60 dark:bg-slate-800/40 shrink-0">
                    <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        {title}
                    </h2>

                    <button
                        type="button"
                        onClick={onClose}
                        className="w-8 h-8 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center justify-center text-sm font-bold transition cursor-pointer"
                        aria-label="Schließen"
                    >
                        ✕
                    </button>
                </div>

                {/* Content */}
                <div className="p-5 sm:p-6 text-slate-700 dark:text-slate-300 text-xs sm:text-sm leading-relaxed overflow-y-auto flex-1">
                    {children}
                </div>
            </div>
        </div>
    );
}
