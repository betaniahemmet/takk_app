import React, { useEffect, useState, useMemo, useRef } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import AppShell from "../AppShell.jsx";
import Button from "../ui/Button.jsx";
import Card from "../ui/Card.jsx";
import VideoPlayer from "../VideoPlayer.jsx";

const shuffle = (arr) => [...arr].sort(() => Math.random() - 0.5);

function Quiz() {
    // ----- state/refs (hooks) -----

    const { n } = useParams();
    const nav = useNavigate();

    const [level, setLevel] = useState(null); // just id + name
    const [currentSigns, setCurrentSigns] = useState([]); // questions
    const [poolSigns, setPoolSigns] = useState([]); // distractors 1..n

    const [order, setOrder] = useState([]);
    const [idx, setIdx] = useState(0);
    const [eliminated, setEliminated] = useState(new Set());
    const [confirmingId, setConfirmingId] = useState(null);
    const [phase, setPhase] = useState("playing");
    const vRef = useRef(null);
    const chimeRef = useRef(null);
    const CONFIRM_MS = 600;
    const ENABLE_SOUND = true;

    // Load level + build order
    useEffect(() => {
        fetch(`/api/levels/${n}/cumulative`)
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
        // Use cumulativeSigns for distractor pool (all previous levels)
        const pool = (level.cumulativeSigns || []).filter((s) => s.id !== q.id);
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

    if (phase === "finished") {
        return <Results />;
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
            setPhase("finished");
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
                if (audio) audio.onended = () => setPhase("finished");
                else setTimeout(() => setPhase("finished"), 1000);
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
                            Till Huvudmenyn
                        </Button>
                    </Link>
                </div>
            </Card>
        </AppShell>
    );
}

export default Quiz;
