import React, { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import AppShell from "../AppShell.jsx";
import Button from "../ui/Button.jsx";
import Card from "../ui/Card.jsx";
import VideoPlayer from "../VideoPlayer.jsx";

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
        <AppShell title={`Träning — ${level.name || `Nivå ${n}`}`}>
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

export default Training;