import React from "react";

/**
 * AppShellCompetition
 * Identical layout to AppShell but with an animated synthwave gradient tint.
 */
export default function AppShellCompetition({ children }) {
    return (
        <div className="relative min-h-dvh overflow-hidden text-white">
            {/* Background image — same composition as AppShell */}
            <picture className="pointer-events-none absolute inset-0 z-0 overflow-hidden">
                <img
                    src="/media/ui/takk-bg-alpha-2000.webp"
                    srcSet="/media/ui/takk-bg-alpha-1200.webp 1200w, /media/ui/takk-bg-alpha-2000.webp 2000w, /media/ui/takk-bg-alpha-2800.webp 2800w"
                    sizes="100vw"
                    alt=""
                    aria-hidden="true"
                    decoding="async"
                    loading="eager"
                    fetchPriority="low"
                    className="
                        absolute left-auto
                        w-[100vw] right-[-4%] bottom-[-12%]
                        sm:w-[110vw] sm:right-[-4%] sm:bottom-[-16%]
                        md:w-[115vw] md:right-[-8%] md:bottom-[-98%]
                        lg:w-[120vw] lg:right-[-10%] lg:bottom-[-98%]
                    "
                />
            </picture>

            {/* Animated synthwave gradient overlay */}
            <div className="absolute inset-0 z-[1] bg-gradient-to-r from-cyan-500/60 via-fuchsia-600/50 to-purple-700/60 animate-gradient-slow" />

            {/* Subtle dark overlay for contrast */}
            <div className="absolute inset-0 z-[2] bg-black/25" />

            {/* Foreground content (identical to AppShell) */}
            <main className="relative z-10 mx-auto max-w-md p-5">
                
                {children}
            </main>
        </div>
    );
}
