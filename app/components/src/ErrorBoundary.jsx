// ErrorBoundary.jsx — catches render errors so the app never goes blank.
//
// Most likely cause in practice: a deploy replaced the hashed page chunks
// (Quiz-abc123.js etc.) while someone had the app open. Their next lazy
// page load 404s. Reloading fetches the new index.html and fixes it, so we
// do that automatically once; a second failure within a minute shows a message.
import React from "react";

const RELOAD_FLAG = "takk_chunk_reload_at";

function isChunkLoadError(error) {
    const msg = String(error?.message || error || "");
    return /dynamically imported module|Importing a module script failed|Failed to fetch dynamically|ChunkLoadError/i.test(
        msg
    );
}

function reloadedRecently() {
    try {
        const at = Number(sessionStorage.getItem(RELOAD_FLAG) || 0);
        return Date.now() - at < 60_000;
    } catch {
        return true; // no storage: don't risk a reload loop
    }
}

export default class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError() {
        return { hasError: true };
    }

    componentDidCatch(error) {
        if (isChunkLoadError(error) && !reloadedRecently()) {
            try {
                sessionStorage.setItem(RELOAD_FLAG, String(Date.now()));
            } catch {}
            window.location.reload();
            return;
        }
        console.error("App error:", error);
    }

    render() {
        if (!this.state.hasError) return this.props.children;
        return (
            <div className="min-h-screen flex items-center justify-center p-5 bg-[var(--bg)] text-[var(--fg)]">
                <div className="max-w-sm w-full space-y-4 text-center rounded-2xl p-6 bg-[var(--card)] shadow">
                    <p className="text-lg font-semibold">Något gick fel.</p>
                    <p className="text-sm opacity-80">Appen kan ha uppdaterats. Ladda om sidan för att fortsätta.</p>
                    <button
                        type="button"
                        className="w-full rounded-xl px-4 py-2 font-medium bg-[var(--ring)] text-white"
                        onClick={() => {
                            window.location.href = "/";
                        }}
                    >
                        Ladda om
                    </button>
                </div>
            </div>
        );
    }
}
