/*
# Header.jsx
*/

export default function Header({ theme }) {

    const primary = theme?.primary || "#f97316";
    const secondary = theme?.secondary || "#7c3aed";

    return (
        <header className="bg-white shadow-sm border-b">
            <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">

                <div
                    className="text-2xl font-bold"
                    style={{
                        background: `linear-gradient(to right, ${primary}, ${secondary})`,
                        WebkitBackgroundClip: "text",
                        color: "transparent",
                    }}
                >
                    sharegy
                </div>

            </div>
        </header>
    );
}

