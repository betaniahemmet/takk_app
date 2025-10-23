import React from "react";

/**
 * AppShellCompetition
 * Provides the animated synthwave background for Competition mode.
 * Keeps layout consistent with other AppShell but adds color motion + optional overlay.
 */
export default function AppShellCompetition({ children }) {
    return (
        <div className="relative min-h-dvh overflow-hidden text-white">
            {/* Faint logo in background */}
            <picture className="pointer-events-none absolute inset-0 z-0 flex items-center justify-center">
                <img
                    src="/media/ui/takk-bg-alpha-2000.webp"
                    alt=""
                    aria-hidden="true"
                    className="opacity-10 w-[80%] object-contain"
                />
            </picture>
            {/* Animated synthwave gradient */}
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 via-fuchsia-600 to-purple-700 animate-gradient-slow" />

            {/* Optional dark overlay to ensure readability */}
            <div className="absolute inset-0 bg-black/25" />

            {/* Foreground content */}
            <main className="relative z-10 mx-auto max-w-md p-5">{children}</main>
        </div>
    );
}
