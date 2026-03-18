import React, { useState, useEffect, useCallback } from "react";

const SESSION_STORAGE_KEY = "analytics_key";

const EVENT_LABELS = {
    page_view: "Sidvisningar",
    sign_completed: "Tecken klara (träning)",
    sign_viewed: "Tecken visade (ordbok)",
    quiz_attempt: "Quiz genomförda (gissa)",
    competition_attempt: "Tävlingar (tävling)",
    level_started: "Nivåer startade (träning/gissa)",
    level_completed: "Nivåer klara (träning)",
};

const EVENT_TYPES_ORDERED = [
    "page_view",
    "sign_completed",
    "sign_viewed",
    "quiz_attempt",
    "competition_attempt",
    "level_started",
    "level_completed",
];

const BAR_COLORS = [
    "bg-blue-500", "bg-purple-500", "bg-green-500", "bg-yellow-400",
    "bg-pink-500", "bg-indigo-500", "bg-orange-500", "bg-teal-500",
];

// Inline bg colors for stacked bar segments (Tailwind can't interpolate dynamic class names)
const SEGMENT_COLORS = [
    "#3b82f6", "#a855f7", "#22c55e", "#facc15",
    "#ec4899", "#6366f1", "#f97316", "#14b8a6",
];

// --- Sub-components ---

function PasswordGate({ onUnlock }) {
    const [input, setInput] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        try {
            const res = await fetch(`/api/analytics?key=${encodeURIComponent(input)}`);
            if (res.ok) {
                sessionStorage.setItem(SESSION_STORAGE_KEY, input);
                onUnlock(input);
            } else {
                setError("Fel lösenord.");
            }
        } catch {
            setError("Kunde inte ansluta till servern.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
            <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-2xl shadow-lg p-8 w-full max-w-sm space-y-6">
                <h1 className="text-xl font-semibold text-center text-gray-900 dark:text-white">Analytics</h1>
                <form onSubmit={handleSubmit} className="space-y-3">
                    <input
                        type="password"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Lösenord"
                        autoFocus
                        className="w-full px-4 py-2 rounded-lg border border-black/20 dark:border-white/20 bg-white dark:bg-black/30 text-gray-900 dark:text-white placeholder-gray-400 outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    {error && <p className="text-red-500 dark:text-red-400 text-sm">{error}</p>}
                    <button
                        type="submit"
                        disabled={loading || !input}
                        className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium disabled:opacity-50 transition"
                    >
                        {loading ? "Kontrollerar…" : "Logga in"}
                    </button>
                </form>
            </div>
        </div>
    );
}

function MetricCard({ title, children }) {
    return (
        <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-2xl shadow p-5 space-y-4">
            <h2 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">{title}</h2>
            {children}
        </div>
    );
}

function StatBox({ label, value }) {
    return (
        <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-2xl shadow p-5 text-center">
            <div className="text-3xl font-bold text-gray-900 dark:text-white">{value}</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{label}</div>
        </div>
    );
}

function BarRow({ label, value, max, color = "bg-blue-500" }) {
    const pct = max > 0 ? Math.round((value / max) * 100) : 0;
    return (
        <div className="space-y-1">
            <div className="flex justify-between text-sm">
                <span className="text-gray-700 dark:text-gray-300 truncate max-w-[75%]">{label}</span>
                <span className="font-medium text-gray-900 dark:text-white tabular-nums">{value}</span>
            </div>
            <div className="h-2 bg-black/10 dark:bg-white/10 rounded-full overflow-hidden">
                <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
            </div>
        </div>
    );
}

// --- Main Dashboard ---

export default function Analytics() {
    const [key, setKey] = useState(() => sessionStorage.getItem(SESSION_STORAGE_KEY) || "");
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const fetchData = useCallback(async (k) => {
        setLoading(true);
        setError("");
        try {
            const res = await fetch(`/api/analytics?key=${encodeURIComponent(k)}`);
            if (res.status === 401) {
                sessionStorage.removeItem(SESSION_STORAGE_KEY);
                setKey("");
                return;
            }
            if (!res.ok) throw new Error("server error");
            setData(await res.json());
        } catch {
            setError("Kunde inte ladda analytics.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (key) fetchData(key);
    }, [key, fetchData]);

    if (!key) return <PasswordGate onUnlock={setKey} />;

    // Derived values
    const today = new Date().toISOString().slice(0, 10);

    const todayEvents = data
        ? Object.values(data.daily?.[today] || {}).reduce((a, b) => a + b, 0)
        : 0;

    const weekEvents = data
        ? Object.entries(data.daily || {})
              .filter(([d]) => {
                  const diff = (Date.parse(today) - Date.parse(d)) / 86400000;
                  return diff >= 0 && diff < 7;
              })
              .flatMap(([, counts]) => Object.values(counts))
              .reduce((a, b) => a + b, 0)
        : 0;

    const totalEvents = data
        ? Object.values(data.events || {}).reduce((a, b) => a + b, 0)
        : 0;

    const maxEvent = data ? Math.max(...Object.values(data.events || {}), 1) : 1;
    const maxSign = data ? Math.max(...(data.top_signs || []).map(([, c]) => c), 1) : 1;
    const maxLevel = data ? Math.max(...(data.top_levels || []).map(([, c]) => c), 1) : 1;

    // Last 14 days for bar chart
    const dailyLabels = Array.from({ length: 14 }, (_, i) => {
        const d = new Date();
        d.setDate(d.getDate() - (13 - i));
        return d.toISOString().slice(0, 10);
    });

    const dailyCounts = dailyLabels.map((d) =>
        Object.values(data?.daily?.[d] || {}).reduce((a, b) => a + b, 0)
    );
    const dailyMax = Math.max(...dailyCounts, 1);

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
            <div className="max-w-5xl mx-auto p-5 space-y-5">

                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
                        <p className="text-sm text-gray-500 dark:text-gray-400">TAKK Beta Dashboard</p>
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => fetchData(key)}
                            disabled={loading}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium disabled:opacity-50 transition"
                        >
                            {loading ? "Laddar…" : "↻ Uppdatera"}
                        </button>
                        <button
                            onClick={() => {
                                sessionStorage.removeItem(SESSION_STORAGE_KEY);
                                setKey("");
                                setData(null);
                            }}
                            className="px-4 py-2 bg-white/60 dark:bg-white/10 hover:bg-white dark:hover:bg-white/20 text-gray-700 dark:text-white rounded-lg text-sm transition"
                        >
                            Logga ut
                        </button>
                    </div>
                </div>

                {error && (
                    <div className="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-xl p-4 text-sm">
                        {error}
                    </div>
                )}

                {!data && !error && (
                    <div className="text-center text-gray-400 py-20">Laddar data…</div>
                )}

                {data && (
                    <div className="space-y-5">

                        {/* Top stat boxes */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <StatBox label="Unika sessioner" value={data.unique_sessions} />
                            <StatBox label="Totala events" value={totalEvents} />
                            <StatBox label="Events idag" value={todayEvents} />
                            <StatBox label="Events denna vecka" value={weekEvents} />
                        </div>

                        {/* Main grid */}
                        <div className="grid md:grid-cols-2 gap-5">

                            {/* Events by type */}
                            <MetricCard title="Events per typ">
                                <div className="space-y-3">
                                    {Object.entries(data.events || {})
                                        .sort(([, a], [, b]) => b - a)
                                        .map(([type, count], i) => (
                                            <BarRow
                                                key={type}
                                                label={EVENT_LABELS[type] || type}
                                                value={count}
                                                max={maxEvent}
                                                color={BAR_COLORS[i % BAR_COLORS.length]}
                                            />
                                        ))}
                                </div>
                            </MetricCard>

                            {/* Daily activity bar chart */}
                            <MetricCard title="Aktivitet senaste 14 dagarna">
                                {/* Legend */}
                                <div className="grid grid-cols-2 gap-x-4 gap-y-1 mb-3">
                                    {EVENT_TYPES_ORDERED.map((type, i) => (
                                        <div key={type} className="flex items-center gap-1.5 text-xs text-gray-600 dark:text-gray-400">
                                            <span className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ backgroundColor: SEGMENT_COLORS[i] }} />
                                            {EVENT_LABELS[type]}
                                        </div>
                                    ))}
                                </div>
                                {/* Stacked bars */}
                                <div className="flex items-end gap-1 h-36">
                                    {dailyLabels.map((d, i) => {
                                        const count = dailyCounts[i];
                                        const pct = Math.round((count / dailyMax) * 100);
                                        const dayData = data?.daily?.[d] || {};
                                        const segments = EVENT_TYPES_ORDERED
                                            .map((type, ti) => ({ type, count: dayData[type] || 0, color: SEGMENT_COLORS[ti] }))
                                            .filter(s => s.count > 0);
                                        return (
                                            <div key={d} className="flex-1 h-full flex items-end group relative">
                                                <div
                                                    className="w-full rounded-t overflow-hidden flex flex-col-reverse"
                                                    style={{ height: `${Math.max(pct, count > 0 ? 3 : 0)}%` }}
                                                >
                                                    {segments.map(s => (
                                                        <div
                                                            key={s.type}
                                                            style={{ height: `${(s.count / count) * 100}%`, backgroundColor: s.color }}
                                                        />
                                                    ))}
                                                </div>
                                                {/* Tooltip */}
                                                <div className="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 hidden group-hover:block bg-black/80 text-white text-xs rounded px-2 py-1 whitespace-nowrap z-10 pointer-events-none">
                                                    {d.slice(5)}: {count}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                                <div className="flex justify-between text-xs text-gray-400 mt-1">
                                    <span>{dailyLabels[0].slice(5)}</span>
                                    <span>Idag</span>
                                </div>
                            </MetricCard>

                            {/* Top signs */}
                            <MetricCard title="Mest övade tecken (topp 10)">
                                {(data.top_signs || []).length === 0 ? (
                                    <p className="text-sm text-gray-400">Ingen data ännu.</p>
                                ) : (
                                    <div className="space-y-3">
                                        {data.top_signs.map(([signId, count], i) => (
                                            <BarRow
                                                key={signId}
                                                label={`${i + 1}. ${signId}`}
                                                value={count}
                                                max={maxSign}
                                                color="bg-green-500"
                                            />
                                        ))}
                                    </div>
                                )}
                            </MetricCard>

                            {/* Top levels + quiz/comp stats stacked */}
                            <div className="space-y-5">
                                <MetricCard title="Populäraste nivåer (topp 5)">
                                    {(data.top_levels || []).length === 0 ? (
                                        <p className="text-sm text-gray-400">Ingen data ännu.</p>
                                    ) : (
                                        <div className="space-y-3">
                                            {data.top_levels.map(([level, count]) => (
                                                <BarRow
                                                    key={level}
                                                    label={`Nivå ${level}`}
                                                    value={count}
                                                    max={maxLevel}
                                                    color="bg-indigo-500"
                                                />
                                            ))}
                                        </div>
                                    )}
                                </MetricCard>

                                <MetricCard title="Quiz & Tävling">
                                    <div className="grid grid-cols-2 gap-4 text-center">
                                        <div>
                                            <div className="text-2xl font-bold text-gray-900 dark:text-white">
                                                {data.quiz_count ?? 0}
                                            </div>
                                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                                Quiz genomförda
                                            </div>
                                        </div>
                                        <div>
                                            <div className="text-2xl font-bold text-gray-900 dark:text-white">
                                                {data.comp_count ?? 0}
                                            </div>
                                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                                Tävlingar genomförda
                                            </div>
                                        </div>
                                        {(data.comp_count ?? 0) > 0 && (
                                            <div className="col-span-2">
                                                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                                                    {(data.comp_avg_score ?? 0).toFixed(2)}
                                                </div>
                                                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                                    Snittpoäng tävling
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </MetricCard>
                            </div>

                            {/* Recent activity feed — full width */}
                            <MetricCard title="Senaste aktivitet">
                                <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                                    {(data.recent || []).length === 0 ? (
                                        <p className="text-sm text-gray-400">Ingen aktivitet ännu.</p>
                                    ) : (
                                        (data.recent || []).map((event, i) => (
                                            <div
                                                key={i}
                                                className="flex items-start gap-3 text-sm border-b border-black/5 dark:border-white/5 pb-2 last:border-0 last:pb-0"
                                            >
                                                <span className="text-gray-400 dark:text-gray-500 text-xs shrink-0 mt-0.5 tabular-nums">
                                                    {event.timestamp?.slice(11, 16)}
                                                </span>
                                                <div className="min-w-0">
                                                    <span className="font-medium text-gray-800 dark:text-gray-200">
                                                        {EVENT_LABELS[event.event_type] || event.event_type}
                                                    </span>
                                                    {Object.keys(event.data || {}).length > 0 && (
                                                        <span className="text-gray-500 dark:text-gray-400 ml-1">
                                                            —{" "}
                                                            {Object.entries(event.data)
                                                                .map(([k, v]) => `${k}: ${v}`)
                                                                .join(", ")}
                                                        </span>
                                                    )}
                                                    <div className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                                                        {event.timestamp?.slice(0, 10)} · session {event.session_id?.slice(0, 8)}…
                                                    </div>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </MetricCard>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
