import React, { useEffect, useState, useMemo, useRef } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Link, useParams, useNavigate } from "react-router-dom";
import "./index.css";
import AppShell from "./AppShell.jsx";
import Button from "./ui/Button.jsx";
import Card from "./ui/Card.jsx";
import VideoPlayer from "./VideoPlayer.jsx";
import Competition from "./Competition.jsx";

// Utility
const shuffle = (arr) => [...arr].sort(() => Math.random() - 0.5);

/* Home (unchanged) */
function Home() {
    /* …keep your existing Home … */ return (
        <AppShell title="TAKK">
            <Card className="p-5 space-y-6">
                <h1 className="text-xl font-semibold">Välj läge</h1>
                <div className="grid gap-3">
                    <Link to="/game">
                        <Button variant="primary" className="w-full">
                            Game
                        </Button>
                    </Link>
                    <Link to="/dictionary">
                        <Button variant="primary" className="w-full">
                            Dictionary
                        </Button>
                    </Link>
                    <Link to="/competition">
                        <Button variant="primary" className="w-full">
                            Competition
                        </Button>
                    </Link>
                </div>
            </Card>
        </AppShell>
    );
}

/* Levels list fed by /api/levels (unchanged) */
function GameLevels() {
    const [levels, setLevels] = useState(null);
    useEffect(() => {
        fetch("/api/levels")
            .then((r) => r.json())
            .then((d) => setLevels(d.levels || []));
    }, []);
    return (
        <AppShell title="Nivåer">
            <div className="space-y-3">
                {!levels && <Card className="p-5 text-sm text-[var(--muted)]">Laddar…</Card>}
                {levels?.map((l) => (
                    <Link key={l.id} to={`/game/niva/${l.id}`}>
                        <Card className="p-5 hover:shadow-sm transition">
                            <div className="flex items-center justify-between mt-1">
                                <div className="font-semibold">{l.name || `Nivå ${l.id}`}</div>
                                <div className="text-sm text-[var(--muted)]">
                                    {(l.signs || []).length} tecken
                                </div>
                            </div>
                        </Card>
                    </Link>
                ))}
            </div>
        </AppShell>
    );
}

function LevelDetail() {
    const { n } = useParams();
    const nav = useNavigate();
    const [level, setLevel] = useState(null);
    useEffect(() => {
        fetch(`/api/levels/${n}`)
            .then((r) => r.json())
            .then(setLevel);
    }, [n]);

    if (!level?.id)
        return (
            <AppShell title={`Nivå ${n}`}>
                <Card className="p-5 text-sm text-[var(--muted)]">Laddar…</Card>
            </AppShell>
        );

    // LevelDetail()
    return (
        <AppShell title={level.name || `Nivå ${n}`}>
            <Card className="p-5 space-y-4">
                <div className="grid gap-3">
                    <Button
                        variant="primary"
                        className="w-full"
                        onClick={() => nav(`/game/niva/${n}/training`)}
                    >
                        Träning
                    </Button>
                    <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => nav(`/game/niva/${n}/quiz`)}
                    >
                        Gissa
                    </Button>
                </div>
                <hr className="border-black/5 dark:border-white/10" /> {/* divider */}
                <div>
                    <div className="text-sm font-semibold mb-2">Tecken i nivån</div>
                    <ul className="space-y-2">
                        {(level.signs || []).map((s) => (
                            <li key={s.id} className="flex items-center justify-between">
                                <span>{s.label || s.id}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </Card>
        </AppShell>
    );
}

function Training() {
    const { n } = useParams();
    const nav = useNavigate();
    const [level, setLevel] = useState(null);
    const [i, setI] = useState(0);
    const vRef = useRef(null);

    useEffect(() => {
        fetch(`/api/levels/${n}`)
            .then((r) => r.json())
            .then(setLevel);
    }, [n]);

    const current = level?.signs?.[i];

    if (!level?.id) {
        return (
            <AppShell title={`Träning - Nivå ${n}`}>
                <Card className="p-5 text-sm text-[var(--muted)]">Laddar…</Card>
            </AppShell>
        );
    }

    const playClip = () => {
        const v = vRef.current;
        if (!v) return;
        try {
            v.pause();
            v.currentTime = 0;
            const p = v.play();
            if (p && typeof p.then === "function") p.catch(() => {});
        } catch {}
    };

    const next = () => {
        const v = vRef.current;
        if (v) v.pause();
        if (i + 1 < level.signs.length) setI(i + 1);
        else nav(`/game/niva/${n}`);
    };

    return (
        <AppShell title={`Träning – ${level.name || `Nivå ${n}`}`}>
            <Card className="p-5 space-y-4">
                <div className="text-lg font-semibold">{current?.label || current?.id}</div>

                <VideoPlayer src={current.video} muted={false} videoRef={vRef} />

                <div className="flex items-center justify-between">
                    <div className="text-sm text-[var(--muted)]">
                        {i + 1}/{level.signs.length}
                    </div>
                    <div className="flex gap-3">
                        <Button variant="primary" onClick={playClip}>
                            Spela klipp
                        </Button>
                        <Button onClick={next}>Nästa</Button>
                    </div>
                </div>
            </Card>
        </AppShell>
    );
}

function Quiz() {
    const { n } = useParams();
    const nav = useNavigate();

    // ----- state/refs (hooks) -----
    const [level, setLevel] = useState(null);
    const [order, setOrder] = useState([]);
    const [idx, setIdx] = useState(0);
    const [eliminated, setEliminated] = useState(new Set());
    const [confirmingId, setConfirmingId] = useState(null);
    const vRef = useRef(null);
    const chimeRef = useRef(null);

    const CONFIRM_MS = 600;
    const ENABLE_SOUND = true;

    // Load level + build order
    useEffect(() => {
        fetch(`/api/levels/${n}`)
            .then((r) => r.json())
            .then((L) => {
                setLevel(L);
                setOrder(shuffle((L.signs || []).map((s) => s.id)));
            });
    }, [n]);

    // Derived
    const signsMap = useMemo(() => {
        const m = {};
        (level?.signs || []).forEach((s) => (m[s.id] = s));
        return m;
    }, [level]);

    const qid = order[idx];
    const q = qid ? signsMap[qid] : null;

    // Build options
    const options = useMemo(() => {
        if (!level || !q) return [];
        const pool = (level.signs || []).filter((s) => s.id !== q.id);
        const others = shuffle(pool)
            .slice(0, 3)
            .map((s) => ({ id: s.id, label: s.label || s.id }));
        const correct = { id: q.id, label: q.label || q.id };
        return shuffle([correct, ...others]);
    }, [level, q]);

    // 🔑 Reset eliminated/confirming on new question
    useEffect(() => {
        setEliminated(new Set());
        setConfirmingId(null);
    }, [qid]);

    // ----- guards (after ALL hooks) -----
    if (!level) {
        return (
            <AppShell title={`Gissa - Nivå ${n}`}>
                <Card className="p-5 text-sm text-[var(--muted)]">Laddar…</Card>
            </AppShell>
        );
    }
    if (!q) {
        return (
            <AppShell title={`Gissa - Nivå ${n}`}>
                <Card className="p-5">Inga frågor.</Card>
            </AppShell>
        );
    }

    // ----- handlers (non-hooks) -----
    const playClip = () => {
        const v = vRef.current;
        if (!v) return;
        try {
            v.pause();
            v.currentTime = 0;
            const p = v.play();
            if (p && typeof p.then === "function") p.catch(() => {});
        } catch {}
    };

    const nextQuestion = () => {
        if (vRef.current) vRef.current.pause();
        setEliminated(new Set());
        setConfirmingId(null);
        setIdx((i) => {
            const next = i + 1;
            if (next < order.length) return next;
            nav("/results");
            return i;
        });
    };

    const onAnswer = (optId) => {
        if (!q || confirmingId) return;
        if (optId === q.id) {
            setConfirmingId(optId);
            if (ENABLE_SOUND && chimeRef.current) {
                try {
                    chimeRef.current.currentTime = 0;
                    chimeRef.current.play().catch(() => {});
                } catch {}
            }
            const isLast = idx + 1 >= order.length;
            if (isLast) {
                const audio = chimeRef.current;
                if (audio) audio.onended = () => nav("/results");
                else setTimeout(() => nav("/results"), 1000);
            } else {
                setTimeout(nextQuestion, CONFIRM_MS);
            }
            return;
        }
        setEliminated((prev) => new Set(prev).add(optId));
        playClip();
    };

    const isLocked = confirmingId !== null;

    // ----- render -----
    return (
        <AppShell title={`Gissa – ${level.name || `Nivå ${n}`}`}>
            <Card className="p-5 space-y-6">
                <VideoPlayer src={q.video} muted={true} videoRef={vRef} />

                <div className="flex justify-end mt-1">
                    <Button variant="outline" onClick={playClip} disabled={isLocked}>
                        Spela klipp
                    </Button>
                </div>

                <div className="grid gap-3 md:gap-4">
                    {options.map((opt) => {
                        const isEliminated = eliminated.has(opt.id);
                        const isConfirm = confirmingId === opt.id;

                        let cls = "w-full";
                        let variant = "muted";
                        let disabled = isEliminated || isLocked;

                        if (isEliminated) cls += " opacity-60 line-through cursor-not-allowed";
                        if (isConfirm) {
                            variant = "primary";
                            cls +=
                                " bg-green-600 hover:bg-green-600 dark:bg-green-600 dark:hover:bg-green-600";
                            disabled = true;
                        }

                        return (
                            <Button
                                key={opt.id}
                                className={cls}
                                variant={variant}
                                disabled={disabled}
                                onClick={() => onAnswer(opt.id)}
                            >
                                {isConfirm ? "✓ " : ""}
                                {opt.label}
                            </Button>
                        );
                    })}
                </div>

                <div className="flex items-center justify-end text-sm text-[var(--muted)]">
                    <span>
                        {idx + 1}/{order.length}
                    </span>
                </div>

                <audio ref={chimeRef} src="/media/ui/correct.mp3" preload="auto" />
            </Card>
        </AppShell>
    );
}

function Results() {
    // We keep reading params so the route still works, but we don’t display them.
    // const params = new URLSearchParams(window.location.search);
    // const score = Number(params.get("score") || 0);
    // const total = Number(params.get("total") || 0);

    return (
        <AppShell title="Resultat">
            <Card className="p-5 text-center space-y-3">
                <div className="text-xl font-semibold">Bra jobbat!</div>
                <div className="grid gap-2 mt-1">
                    <Link to="/game">
                        <Button variant="outline" className="w-full">
                            Till Nivåer
                        </Button>
                    </Link>
                    <Link to="/">
                        <Button variant="primary" className="w-full">
                            Hem
                        </Button>
                    </Link>
                </div>
            </Card>
        </AppShell>
    );
}

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/game" element={<GameLevels />} />
                <Route path="/game/niva/:n" element={<LevelDetail />} />
                <Route path="/game/niva/:n/training" element={<Training />} />
                <Route path="/game/niva/:n/quiz" element={<Quiz />} />
                <Route path="/results" element={<Results />} />
                <Route path="/competition" element={<Competition />} />
                <Route path="/dictionary" element={<Card className="p-5">Kommer snart…</Card>} />
            </Routes>
        </BrowserRouter>
    );
}

createRoot(document.getElementById("root")).render(<App />);
