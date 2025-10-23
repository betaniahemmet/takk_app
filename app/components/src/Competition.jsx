import React, { useEffect, useState, useMemo, useRef } from "react";
import Card from "./ui/Card.jsx";
import Button from "./ui/Button.jsx";
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
    const vRef = useRef(null);
    
    // Fetch signs + distractors once
    useEffect(() => {
        fetch("/api/signs")
            .then((r) => r.json())
            .then(setSigns);
        fetch("/api/distractors")
            .then((r) => r.json())
            .then(setDistractors);
    }, []);

    const allSignIds = useMemo(() => Object.keys(signs || {}), [signs]);

    // pick next sign
    const nextSign = () => {
        setCurrent((c) => c + 1);
    };

    // compute possible answers
    const makeChoices = useMemo(() => {
        return () => {
            if (!allSignIds.length) return [];
            const target = allSignIds[current % allSignIds.length];
            const targetLabel = signs[target]?.label || target;
            const wordCount = targetLabel.trim().split(/\s+/).length;
            const pool = [...(distractors[String(wordCount)] || []), ...allSignIds.map(id => signs[id]?.label)];
            const uniq = [...new Set(pool.filter(x => x && x !== targetLabel))];
            const shuffled = uniq.sort(() => Math.random() - 0.5).slice(0, 3);
            return [targetLabel, ...shuffled].sort(() => Math.random() - 0.5);
        };
    }, [signs, distractors, current, allSignIds]);

    const [choices, setChoices] = useState([]);

    useEffect(() => {
        setChoices(makeChoices());
    }, [makeChoices]);


    const handleAnswer = (choice) => {
        const target = allSignIds[current % allSignIds.length];
        const correct = signs[target]?.label;
        if (choice === correct) {
            const base = Math.random() * (1.17 - 1.15) + 1.15;
            const pts = base + streak * 0.05;
            setScore((s) => s + pts);
            setStreak((s) => s + 1);
            nextSign();
        } else {
            endGame();
        }
    };

    const endGame = async () => {
        setPhase("end");
        setShowOverlay(true);
        try {
            const res = await fetch("/api/score", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: tag, score }),
            });
            const data = await res.json();
            setScores(data.scores || []);
            setMadeTop(data.madeTop);
        } catch (err) {
            console.error(err);
        }
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
                </Card>
            </AppShellCompetition>
        );
    }

    if (phase === "play") {
        const target = allSignIds[current % allSignIds.length];
        const label = signs[target]?.label;

        return (
            <AppShellCompetition>
                <div className="p-5">
                    <Card className="p-5 space-y-5">
                        <VideoPlayer src={signs[target]?.video} muted videoRef={vRef} />

                        {/* Video controls row */}
                        <div className="flex justify-end gap-2">
                            <Button
                                variant="primary"
                                className="w-1/2"
                                onClick={() => {
                                    const v = vRef.current;
                                    if (v) {
                                        v.currentTime = 0;
                                        v.play();
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
                                    className="w-full"
                                    onClick={() => handleAnswer(c)}
                                >
                                    {c}
                                </Button>
                            ))}
                        </div>
                    </Card>

                    {/* Streak outside card */}
                    <div className="text-sm opacity-70 text-center mt-3">
                        Streak: {streak}
                    </div>
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
                    />
                </div>
            </AppShellCompetition>
        );
    }
}

function Scoreboard({ scores, showOverlay, setShowOverlay, score, madeTop, onRestart }) {
    return (
        <div className="relative">
            <Card className="p-5 space-y-3">
                <h2 className="text-lg font-semibold">🏆 Topp 20</h2>
                <ul className="space-y-1 text-sm">
                    {scores.map((s, i) => (
                        <li
                            key={i}
                            className={`flex justify-between ${i === 0 ? "font-bold" : ""}`}
                        >
                            <span>
                                {i + 1}. {s.name}
                            </span>
                            <span>{s.score.toFixed(2)}</span>
                        </li>
                    ))}
                </ul>
                <div className="flex flex-col gap-2 mt-4">
                    <Button variant="primary" onClick={onRestart}>
                        Spela igen
                    </Button>
                    <Button variant="outline" onClick={() => (window.location.href = "/")}>
                        Till huvudmenyn
                    </Button>
                </div>
            </Card>

            {showOverlay && (
                <div className="fixed inset-0 flex items-center justify-center bg-black/40 backdrop-blur-sm">
                    <Card className="p-6 text-center space-y-4 bg-white/20 backdrop-blur-md text-white rounded-2xl shadow-lg">
                        <h1 className="text-2xl font-bold">Du fick {score.toFixed(2)} poäng!</h1>
                        {madeTop && <p className="text-sm">🎉 Du kom med på topplistan!</p>}
                        <Button variant="outline" onClick={() => setShowOverlay(false)}>
                            Stäng
                        </Button>
                    </Card>
                </div>
            )}
        </div>
    );
}
