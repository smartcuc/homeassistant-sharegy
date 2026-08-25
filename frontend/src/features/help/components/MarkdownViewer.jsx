/*
# src/features/help/components/MarkdownViewer.jsx
*/

function parseInline(text) {
    if (!text) return text;

    const parts = [];
    let keyIdx = 0;
    // Regex for inline code `...`, bold **...**, and links [text](url)
    const regex = /(`[^`]+`|\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))/g;
    let match;
    let lastIndex = 0;

    while ((match = regex.exec(text)) !== null) {
        if (match.index > lastIndex) {
            parts.push(text.slice(lastIndex, match.index));
        }

        const token = match[0];
        if (token.startsWith("`") && token.endsWith("`")) {
            parts.push(
                <code
                    key={keyIdx++}
                    className="px-1.5 py-0.5 bg-slate-100 text-indigo-700 font-mono text-xs rounded border border-slate-200/80 font-semibold"
                >
                    {token.slice(1, -1)}
                </code>
            );
        } else if (token.startsWith("**") && token.endsWith("**")) {
            parts.push(
                <strong key={keyIdx++} className="font-bold text-gray-900">
                    {token.slice(2, -2)}
                </strong>
            );
        } else if (token.startsWith("[") && token.includes("](")) {
            const linkMatch = token.match(/\[([^\]]+)\]\(([^)]+)\)/);
            if (linkMatch) {
                parts.push(
                    <a
                        key={keyIdx++}
                        href={linkMatch[2]}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-indigo-600 hover:text-indigo-800 underline font-medium"
                    >
                        {linkMatch[1]}
                    </a>
                );
            } else {
                parts.push(token);
            }
        }
        lastIndex = regex.lastIndex;
    }

    if (lastIndex < text.length) {
        parts.push(text.slice(lastIndex));
    }

    return parts.length > 0 ? parts : text;
}

export default function MarkdownViewer({ content }) {
    if (!content) return null;

    const lines = content.split("\n");
    const elements = [];
    let idx = 0;
    let i = 0;

    while (i < lines.length) {
        const line = lines[i];

        // 1. Code Block: ```...```
        if (line.startsWith("```")) {
            const lang = line.slice(3).trim();
            const codeLines = [];
            i++;
            while (i < lines.length && !lines[i].startsWith("```")) {
                codeLines.push(lines[i]);
                i++;
            }
            elements.push(
                <div
                    key={idx++}
                    className="my-4 rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 text-slate-100 shadow-md"
                >
                    {lang && (
                        <div className="px-4 py-1.5 bg-slate-900/90 text-slate-400 text-[11px] font-mono border-b border-slate-800 flex items-center justify-between">
                            <span>{lang.toUpperCase()}</span>
                            <span className="text-[10px] text-slate-500">Snippet</span>
                        </div>
                    )}
                    <pre className="p-4 font-mono text-xs overflow-x-auto leading-relaxed text-emerald-300">
                        {codeLines.join("\n")}
                    </pre>
                </div>
            );
            i++;
            continue;
        }

        // 2. Alert Callout Blocks: > [!TIP], > [!NOTE], > [!WARNING], > [!IMPORTANT]
        if (line.startsWith("> [!")) {
            let alertType = "note";
            if (line.includes("[!TIP]")) alertType = "tip";
            else if (line.includes("[!WARNING]")) alertType = "warning";
            else if (line.includes("[!IMPORTANT]")) alertType = "important";

            const alertLines = [];
            i++;
            while (i < lines.length && lines[i].startsWith(">")) {
                alertLines.push(lines[i].replace(/^>\s?/, ""));
                i++;
            }

            const alertStyles = {
                tip: {
                    bg: "bg-emerald-50/90 border-emerald-200 text-emerald-950",
                    badge: "bg-emerald-100 text-emerald-800 border-emerald-300/60",
                    icon: "💡",
                    title: "Praxis-Tipp",
                },
                note: {
                    bg: "bg-blue-50/90 border-blue-200 text-blue-950",
                    badge: "bg-blue-100 text-blue-800 border-blue-300/60",
                    icon: "ℹ️",
                    title: "Hinweis",
                },
                warning: {
                    bg: "bg-amber-50/90 border-amber-200 text-amber-950",
                    badge: "bg-amber-100 text-amber-800 border-amber-300/60",
                    icon: "⚠️",
                    title: "Wichtiger Hinweis",
                },
                important: {
                    bg: "bg-purple-50/90 border-purple-200 text-purple-950",
                    badge: "bg-purple-100 text-purple-800 border-purple-300/60",
                    icon: "📌",
                    title: "Wichtig",
                },
            }[alertType];

            elements.push(
                <div
                    key={idx++}
                    className={`my-4 p-4 rounded-2xl border ${alertStyles.bg} shadow-2xs space-y-1.5`}
                >
                    <div className="flex items-center gap-2 font-bold text-xs">
                        <span className="text-base">{alertStyles.icon}</span>
                        <span
                            className={`px-2 py-0.5 rounded-md text-[11px] font-bold border ${alertStyles.badge}`}
                        >
                            {alertStyles.title}
                        </span>
                    </div>
                    <div className="text-xs sm:text-sm leading-relaxed pl-6 space-y-1">
                        {alertLines.map((al, aIdx) => (
                            <p key={aIdx}>{parseInline(al)}</p>
                        ))}
                    </div>
                </div>
            );
            continue;
        }

        // 3. Generic Blockquote / Formula Card: > ...
        if (line.startsWith(">")) {
            const quoteLines = [line.replace(/^>\s?/, "")];
            i++;
            while (i < lines.length && lines[i].startsWith(">")) {
                quoteLines.push(lines[i].replace(/^>\s?/, ""));
                i++;
            }

            elements.push(
                <div
                    key={idx++}
                    className="my-3 p-4 rounded-2xl bg-indigo-50/70 border border-indigo-200/80 text-gray-900 text-xs sm:text-sm shadow-2xs space-y-1.5"
                >
                    {quoteLines.map((ql, qIdx) => (
                        <p key={qIdx} className="leading-relaxed font-medium">
                            {parseInline(ql)}
                        </p>
                    ))}
                </div>
            );
            continue;
        }

        // 4. Headings
        if (line.startsWith("# ")) {
            elements.push(
                <h1
                    key={idx++}
                    className="text-xl sm:text-2xl font-black text-gray-900 tracking-tight pt-2 pb-1 border-b border-gray-100"
                >
                    {parseInline(line.slice(2))}
                </h1>
            );
            i++;
            continue;
        }

        if (line.startsWith("## ")) {
            elements.push(
                <h2
                    key={idx++}
                    className="text-lg sm:text-xl font-bold text-gray-900 tracking-tight pt-4 pb-1"
                >
                    {parseInline(line.slice(3))}
                </h2>
            );
            i++;
            continue;
        }

        if (line.startsWith("### ")) {
            elements.push(
                <h3
                    key={idx++}
                    className="text-sm sm:text-base font-bold text-gray-800 tracking-tight pt-2"
                >
                    {parseInline(line.slice(4))}
                </h3>
            );
            i++;
            continue;
        }

        // 5. Horizontal Rule
        if (line.trim() === "---" || line.trim() === "***") {
            elements.push(<hr key={idx++} className="my-4 border-t border-gray-200" />);
            i++;
            continue;
        }

        // 6. Bullet Lists (*, -)
        if (line.match(/^(\s*)[*-] /)) {
            const listItems = [];
            while (i < lines.length && lines[i].match(/^(\s*)[*-] /)) {
                const text = lines[i].replace(/^(\s*)[*-] /, "");
                listItems.push(text);
                i++;
            }
            elements.push(
                <ul
                    key={idx++}
                    className="my-2 space-y-1.5 pl-5 list-disc list-outside text-xs sm:text-sm text-gray-700"
                >
                    {listItems.map((item, lIdx) => (
                        <li key={lIdx} className="leading-relaxed">
                            {parseInline(item)}
                        </li>
                    ))}
                </ul>
            );
            continue;
        }

        // 7. Numbered Lists (1., 2.)
        if (line.match(/^(\s*)\d+\.\s/)) {
            const listItems = [];
            while (i < lines.length && lines[i].match(/^(\s*)\d+\.\s/)) {
                const text = lines[i].replace(/^(\s*)\d+\.\s/, "");
                listItems.push(text);
                i++;
            }
            elements.push(
                <ol
                    key={idx++}
                    className="my-2 space-y-1.5 pl-5 list-decimal list-outside text-xs sm:text-sm text-gray-700"
                >
                    {listItems.map((item, lIdx) => (
                        <li key={lIdx} className="leading-relaxed">
                            {parseInline(item)}
                        </li>
                    ))}
                </ol>
            );
            continue;
        }

        // 8. Regular Paragraph
        if (line.trim().length > 0) {
            elements.push(
                <p key={idx++} className="text-xs sm:text-sm leading-relaxed text-gray-700 font-normal">
                    {parseInline(line)}
                </p>
            );
        }

        i++;
    }

    return <div className="space-y-3 font-sans">{elements}</div>;
}

