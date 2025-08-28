// In AppShell (root layout)
export default function AppShell({ children }) {
  return (
    <div className="relative min-h-dvh overflow-hidden">
      {/* BG image (bottom) */}
      <picture className="pointer-events-none absolute inset-0 z-0 overflow-hidden">
        <img
          src="/media/ui/takk-bg-2000.webp"
          srcSet="/media/ui/takk-bg-1200.webp 1200w, /media/ui/takk-bg-2000.webp 2000w, /media/ui/takk-bg-2800.webp 2800w"
          sizes="100vw"
          alt=""
          aria-hidden="true"
          decoding="async"
          loading="eager"
          fetchPriority="low"
          className="
            absolute opacity-60 left-auto

            /* MOBILE: bigger + a bit lower, anchored to right */
            w-[100vw] right-[-4%] bottom-[-12%]

            /* SMALL (≥640px): slightly bigger + lower */
            sm:w-[110vw] sm:right-[-4%] sm:bottom-[-16%]

            /* DESKTOP (≥768px): push far lower + a bit off to the right */
            md:w-[115vw] md:right-[-8%] md:bottom-[-98%]

            /* LARGE (≥1024px): even lower */
            lg:w-[120vw] lg:right-[-10%] lg:bottom-[-98%]
          "
        />

      </picture>

      {/* Gradient overlay (dims for contrast) */}
      <div className="absolute inset-0 z-[1] bg-gradient-to-b from-black/25 via-transparent to-black/35" />

      {/* Foreground content */}
      <main className="relative z-10 mx-auto max-w-md p-5">
        {children}
      </main>
    </div>
  );
}
