import { Link, useParams, useNavigate } from "react-router-dom";
import React, { useEffect, useState } from "react";
import Button from "./ui/Button.jsx";
import Card from "./ui/Card.jsx";
import AppShell from "./AppShell.jsx";

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

export { GameLevels, LevelDetail };
