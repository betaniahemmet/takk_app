import React, { useEffect, useState, useRef } from "react";
import { useParams, useNavigate, useSearchParams, Link } from "react-router-dom";
import { Undo2 } from "lucide-react";
import AppShell from "../AppShell.jsx";
import Button from "../ui/Button.jsx";
import Card from "../ui/Card.jsx";
import VideoPlayer from "../VideoPlayer.jsx";
import HomeButton from "../ui/HomeButton.jsx";
import { trackPageView, trackLevelStarted, trackSignCompleted, trackLevelCompleted } from "../utils/analytics.js";

function Training() {
    const { n } = useParams();
    const nav = useNavigate();
    const [searchParams] = useSearchParams();
    const [level, setLevel] = useState(null);
    const [i, setI] = useState(0);
    const [showPictograms, setShowPictograms] = useState(false);
    const [picIndex, setPicIndex] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const vRef = useRef(null);

    useEffect(() => {
        trackPageView("training");
        trackLevelStarted(Number(n));
    }, []);

    useEffect(() => {
        fetch(`/api/levels/${n}`)
            .then((r) => r.json())
            .then((data) => {
                setLevel(data);
                const startId = searchParams.get("start");
                if (startId) {
                    const idx = (data.signs || []).findIndex((s) => s.id === startId);
                    if (idx > 0) setI(idx);
                }
            });
    }, [n]);

    const current = level?.signs?.[i];
    const nextSign = level?.signs?.[i + 1];

    if (!level?.id) {
        return (
            <AppShell title={`Träning - Nivå ${n}`}>
                <Card className="p-5 text-sm text-[var(--muted)]">Laddar…</Card>
            </AppShell>
        );
    }

    const handleVideoEnd = async () => {
        setIsPlaying(false); // ← Add this

        const pics = current?.pictograms || [];
        if (pics.length === 0) return;

        setShowPictograms(true);

        for (let i = 0; i < pics.length; i++) {
            setPicIndex(i);
            await new Promise((resolve) => setTimeout(resolve, 1200));
        }
    };

    const playClip = () => {
        // First, show video and hide pictograms
        setShowPictograms(false);
        setPicIndex(0);
        setIsPlaying(true);

        // Wait a tick for React to re-render
        setTimeout(() => {
            const v = vRef.current;
            if (!v) {
                setIsPlaying(false);
                return;
            }

            try {
                v.pause();
                v.currentTime = 0;
                const p = v.play();
                if (p && typeof p.then === "function") {
                    p.catch(() => setIsPlaying(false));
                }
            } catch {
                setIsPlaying(false);
            }
        }, 0);
    };

    const next = () => {
        const v = vRef.current;
        if (v) v.pause();

        if (current?.id) trackSignCompleted(current.id, "training");

        // Reset pictogram state for next sign
        setShowPictograms(false);
        setPicIndex(0);
        setIsPlaying(false);

        if (i + 1 < level.signs.length) setI(i + 1);
        else {
            trackLevelCompleted(Number(n));
            nav(`/game/niva/${n}`);
        }
    };

    return (
        <AppShell title={`Träning - ${level.name || `Nivå ${n}`}`}>
            <Card className="p-5 space-y-4">
                <div className="flex items-center justify-between">
                    <div className="text-lg font-semibold">{current?.label || current?.id}</div>
                    <div className="flex items-center gap-1">
                        <Link
                            to={`/game/niva/${n}`}
                            className="inline-flex items-center justify-center w-10 h-10 rounded-full hover:bg-black/5 dark:hover:bg-white/5 transition"
                            aria-label="Tillbaka till teckenlistan"
                        >
                            <Undo2 className="w-5 h-5" />
                        </Link>
                        <HomeButton />
                    </div>
                </div>

                {/* Video or Pictograms */}
                <div className="relative w-full aspect-square overflow-hidden rounded-lg bg-black/5 dark:bg-white/5">
                    <div
                        className={`absolute inset-0 transition-opacity duration-700 ${
                            !showPictograms ? "opacity-100" : "opacity-0"
                        }`}
                    >
                        <VideoPlayer
                            src={current.video}
                            muted={false}
                            preload="metadata"
                            videoRef={vRef}
                            onEnd={handleVideoEnd}
                        />
                        {nextSign?.video && (
                            <video
                                key={nextSign.video}
                                src={nextSign.video}
                                preload="auto"
                                style={{ display: "none" }}
                                aria-hidden="true"
                            />
                        )}
                    </div>

                    <div
                        className={`absolute inset-0 transition-opacity duration-700 ${
                            showPictograms ? "opacity-100" : "opacity-0"
                        }`}
                    >
                        {current.pictograms?.map((p, idx) => (
                            <img
                                key={idx}
                                src={p}
                                alt=""
                                className={`absolute inset-0 w-full h-full object-contain transition-opacity duration-700 ${
                                    idx === picIndex ? "opacity-100" : "opacity-0"
                                }`}
                            />
                        ))}
                    </div>
                </div>

                <div className="flex items-center justify-between">
                    <div className="text-sm text-[var(--muted)]">
                        {i + 1}/{level.signs.length}
                    </div>
                    <div className="flex gap-3">
                        <Button variant="primary" onClick={playClip} disabled={isPlaying}>
                            {isPlaying ? "Spelar..." : "Spela video"}
                        </Button>
                        <Button onClick={next}>Nästa</Button>
                    </div>
                </div>
            </Card>
        </AppShell>
    );
}

export default Training;
