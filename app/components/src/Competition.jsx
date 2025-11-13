import React, { useEffect, useState, useMemo, useRef } from "react";
import Card from "./ui/Card.jsx";
import Button from "./ui/Button.jsx";
import { Home } from "lucide-react";
import Input from "./ui/Input.jsx";
import VideoPlayer from "./VideoPlayer.jsx";
import AppShellCompetition from "./AppShellCompetition.jsx";

export default function Competition() {
    const [phase, setPhase] = useState("name"); // name | play | end
    const [tag, setTag] = useState("");
    const [signs, setSigns] = useState([]);
    const [current, setCurrent] = useState(0);
    const [streak, setStreak] = useState(0);
    const [score, setScore] = useState(0);
    const [distractors, setDistractors] = useState({});
    const [showOverlay, setShowOverlay] = useState(false);
    const [scores, setScores] = useState([]);
    const [madeTop, setMadeTop] = useState(false);
    const [order, setOrder] = useState([]); // shuffled order of signs
    const [hasPlayedVideo, setHasPlayedVideo] = useState(false);
    const vRef = useRef(null);
    const chimeRef = useRef(null);
    const ENABLE_SOUND = true;
    const CONFIRM_MS = 800; // short pause before next sign

    // Fetch signs + distractors once
    useEffect(() => {
        Promise.all([fetch("/api/signs"), fetch("/api/distractors")])
            .then(async ([signsRes, distRes]) => {
                const signsPayload = await signsRes.json();
                const distData = await distRes.json();
                const signsArray = signsPayload.signs || [];
                const signsMap = {};
                for (const s of signsArray) {
                    signsMap[s.id] = s;
                }

                setSigns(signsMap);
                setDistractors(distData);

                const shuffled = Object.keys(signsMap).sort(() => Math.random() - 0.5);
                setOrder(shuffled);
                console.log("Loaded", shuffled.length, "signs");
            })
            .catch((err) => console.error("Fetch error:", err));
    }, []);

    const allSignIds = useMemo(() => Object.keys(signs || {}), [signs]);

    // pick next sign
    const nextSign = () => {
        setCurrent((c) => c + 1);
        setHasPlayedVideo(false);
    };

    // compute possible answers
    const makeChoices = useMemo(() => {
        return () => {
            if (!order.length) return [];
            const target = order[current];
            const targetSign = signs[target];
            if (!targetSign) return [];

            const targetLabel = targetSign.label || target;
            const targetPicCount = (targetSign.pictograms || []).length;

            // Get matching distractors from JSON
            const matchingDistractors = distractors[String(targetPicCount)] || [];

            // Get matching signs (same pictogram count)
            const matchingSigns = order
                .filter((id) => id !== target)
                .map((id) => signs[id])
                .filter((s) => s && (s.pictograms || []).length === targetPicCount)
                .map((s) => s.label);

            // Combine pools
            const pool = [...matchingDistractors, ...matchingSigns];
            const uniq = [...new Set(pool.filter((x) => x && x !== targetLabel))];

            // Pick 3 distractors + 1 correct, then shuffle
            const choices = [targetLabel, ...uniq.sort(() => Math.random() - 0.5).slice(0, 3)];
            return choices.sort(() => Math.random() - 0.5);
        };
    }, [order, current, signs, distractors]);

    const [choices, setChoices] = useState([]);

    useEffect(() => {
        if (phase === "play") {
            setChoices(makeChoices());
        }
    }, [makeChoices, phase, current]);

    const handleAnswer = (choice) => {
        const target = order[current];
        const correct = signs[target]?.label;

        if (choice === correct) {
            const base = Math.random() * (1.17 - 1.15) + 1.15;
            const pts = base + streak * 0.05;
            setScore((s) => s + pts);
            setStreak((s) => s + 1);

            // ✅ play chime and wait briefly before next sign
            if (ENABLE_SOUND && chimeRef.current) {
                try {
                    chimeRef.current.currentTime = 0;
                    chimeRef.current.play().catch(() => {});
                } catch {}
            }

            setTimeout(() => {
                // stop after last sign
                if (current + 1 >= order.length) {
                    endGame();
                } else {
                    nextSign();
                }
            }, CONFIRM_MS);
        } else {
            endGame();
        }
    };

    const endGame = async () => {
        setPhase("end");
        setMadeTop(false); // reset before new result
        try {
            const res = await fetch("/api/score", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: tag, score }),
            });

            if (!res.ok) throw new Error(`Server error ${res.status}`);
            const data = await res.json();
            console.log("📊 madeTop from backend:", data.madeTop, typeof data.madeTop);

            console.log("Score submit response:", data);

            setScores(data.scores || []);
            setMadeTop(!!data.madeTop);
            setShowOverlay(true);
        } catch (err) {
            console.error("Score submit failed:", err);
            setMadeTop(false);
            setShowOverlay(true);
        }
    };

    const resetGame = () => {
        // new randomized order for next session
        setOrder(Object.keys(signs).sort(() => Math.random() - 0.5));

        setCurrent(0);
        setScore(0);
        setStreak(0);
        setChoices([]);
        setShowOverlay(false);
        setMadeTop(false);
        setScores([]);
        setPhase("name"); // switch back to name entry last
    };

    // --- Render sections ---
    if (phase === "name") {
        return (
            <AppShellCompetition>
                <Card className="p-5 space-y-4">
                    <h1 className="text-xl font-semibold text-center">
                        Vad vill du heta i tävlingen?
                    </h1>
                    <Input
                        value={tag}
                        onChange={(e) => setTag(e.target.value.slice(0, 10))} // max 10 characters
                        placeholder="Skriv ditt spelarnamn (max 10 tecken)..."
                    />

                    <Button
                        variant="primary"
                        className="w-full"
                        onClick={() => tag.trim() && setPhase("play")}
                    >
                        Starta tävling
                    </Button>

                    <Button variant="outline" onClick={() => (window.location.href = "/")}>
                        <Home className="w-4 h-4 mr-2" />
                        Till huvudmenyn
                    </Button>
                </Card>
            </AppShellCompetition>
        );
    }

    if (phase === "play") {
        const target = order[current];

        return (
            <AppShellCompetition>
                <div className="p-5">
                    <Card className="p-5 space-y-5">
                        <VideoPlayer
                            src={signs[target]?.video}
                            muted
                            videoRef={vRef}
                            onPlay={() => setHasPlayedVideo(true)}
                        />

                        {/* Video controls row */}
                        <div className="flex justify-end gap-2">
                            <Button
                                variant="primary"
                                className="w-1/2"
                                onClick={() => {
                                    const v = vRef.current;
                                    if (v) {
                                        v.currentTime = 0;
                                        v.play().catch((err) =>
                                            console.warn("Playback failed", err)
                                        );
                                    }
                                }}
                            >
                                Spela klipp
                            </Button>
                        </div>

                        {/* Choices */}
                        <div className="grid gap-3">
                            {choices.map((c, i) => (
                                <Button
                                    key={i}
                                    variant="outline"
                                    className={`w-full ${!hasPlayedVideo ? "opacity-40 cursor-not-allowed" : ""}`}
                                    onClick={() => handleAnswer(c)}
                                    disabled={!hasPlayedVideo}
                                >
                                    {c}
                                </Button>
                            ))}
                        </div>
                    </Card>

                    <audio ref={chimeRef} src="/media/ui/correct.mp3" preload="auto" />

                    {/* Streak outside card */}
                    <div className="text-sm opacity-70 text-center mt-3">Streak: {streak}</div>
                </div>
            </AppShellCompetition>
        );
    }

    if (phase === "end") {
        return (
            <AppShellCompetition>
                <div className="p-5 relative">
                    <Scoreboard
                        scores={scores}
                        showOverlay={showOverlay}
                        setShowOverlay={setShowOverlay}
                        score={score}
                        madeTop={madeTop}
                        onRestart={() => window.location.reload()}
                        resetGame={resetGame}
                    />
                </div>
            </AppShellCompetition>
        );
    }
}

function Scoreboard({ scores, showOverlay, setShowOverlay, score, madeTop, onRestart, resetGame }) {
    return (
        <div className="relative flex justify-center">
            <Card className="p-5 space-y-3 w-full max-w-md text-center shadow-lg">
                <h2 className="text-lg font-semibold">🏆 Topp 10</h2>
                <ul className="space-y-1 text-sm text-center">
                    {scores.slice(0, 10).map((s, i) => (
                        <li
                            key={i}
                            className={`flex justify-between items-center px-2 ${i === 0 ? "font-bold" : ""}`}
                        >
                            <span className="flex-1 text-left">
                                {i + 1}. {s.name}
                            </span>
                            <span className="flex-1 text-right">{s.score.toFixed(2)}</span>
                        </li>
                    ))}
                </ul>
                <div className="flex flex-col gap-2 mt-6">
                    <Button variant="primary" onClick={resetGame}>
                        Spela igen
                    </Button>
                    <Button variant="outline" onClick={() => (window.location.href = "/")}>
                        <Home className="w-4 h-4 mr-2" />
                        Till huvudmenyn
                    </Button>
                </div>
            </Card>

            {showOverlay && (
                <div className="fixed inset-0 flex items-center justify-center bg-black/40 backdrop-blur-sm">
                    <Card className="p-6 text-center space-y-4 bg-white/20 backdrop-blur-md text-white rounded-2xl shadow-lg">
                        <h1 className="text-2xl font-bold">Du fick {score.toFixed(2)} poäng!</h1>
                        {madeTop ? (
                            <p className="text-sm">🎉 Du kom med på topplistan!</p>
                        ) : (
                            <p className="text-sm opacity-80">
                                Bra jobbat! Försök igen för att nå topplistan.
                            </p>
                        )}

                        <Button variant="outline" onClick={() => setShowOverlay(false)}>
                            Stäng
                        </Button>
                    </Card>
                </div>
            )}
        </div>
    );
}
