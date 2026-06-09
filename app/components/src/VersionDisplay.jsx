import { useEffect, useRef, useState } from 'react';

export function VersionDisplay() {
  const [version, setVersion] = useState('');
  const [open, setOpen] = useState(false);
  const closeBtnRef = useRef(null);

  useEffect(() => {
    fetch('/api/version')
      .then(r => r.json())
      .then(data => setVersion(data.version))
      .catch(() => setVersion('unknown'));
  }, []);

  useEffect(() => {
    if (!open) return;
    closeBtnRef.current?.focus();
    const onKey = (e) => { if (e.key === 'Escape') setOpen(false); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open]);

  if (!version) return null;

  const credits = [
    { role: 'Idé & innehåll',  name: 'Philip Ashton' },
    { role: 'Film & redigering', name: 'Tomas Arvidsson' },
    { role: 'Projektledning',   name: 'Maria Johansson' },
    { role: 'Utveckling',       name: 'Henrik Björserud' },
  ];

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="block w-full text-xs text-center py-2 text-gray-400/60 dark:text-white/30 hover:text-gray-500 dark:hover:text-white/50 transition-colors"
      >
        v{version}
      </button>

      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
          onClick={() => setOpen(false)}
        >
          <div
            className="w-full max-w-xs rounded-2xl overflow-hidden shadow-2xl"
            onClick={e => e.stopPropagation()}
          >
            {/* Logo section — always light so the logo reads correctly */}
            <div className="bg-white flex flex-col items-center px-8 pt-8 pb-6 gap-3">
              <img
                src="/media/ui/logo-webb-betania.png"
                alt="Föreningen Betaniahemmet"
                className="w-44"
              />
              <a
                href="https://betaniahemmet.se"
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-blue-500 hover:text-blue-700 transition-colors"
              >
                betaniahemmet.se ↗
              </a>
            </div>

            {/* Credits section — follows dark/light mode */}
            <div className="bg-white/90 dark:bg-slate-900/95 px-8 py-6 space-y-4">
              {credits.map(({ role, name }) => (
                <div key={name}>
                  <div className="text-[10px] uppercase tracking-[0.15em] text-gray-400 dark:text-white/35 mb-0.5">
                    {role}
                  </div>
                  <div className="text-sm font-medium text-gray-800 dark:text-white">
                    {name}
                  </div>
                </div>
              ))}

              <button
                ref={closeBtnRef}
                onClick={() => setOpen(false)}
                className="w-full mt-2 pt-4 border-t border-black/8 dark:border-white/10 text-xs text-gray-400 dark:text-white/35 hover:text-gray-600 dark:hover:text-white/60 transition-colors"
              >
                Stäng
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
