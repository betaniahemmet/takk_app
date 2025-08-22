// app/components/src/AppShell.jsx
// (No external font/CDN
export default function AppShell({ title = "TAKK", children }) {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 backdrop-blur bg-[var(--bg)]/70 border-b border-black/5 dark:border-white/10">
        <div className="mx-auto max-w-md px-4 py-3 flex items-center justify-between">
          <div className="text-base font-semibold">{title}</div>
        </div>
      </header>

      <main className="mx-auto max-w-md px-4 py-6 space-y-4">
        {children}
      </main>
    </div>
  );
}
