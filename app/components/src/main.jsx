// …top imports already present:
import React, { useEffect, useState, useMemo, useRef } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Link, useParams, useNavigate } from "react-router-dom";
import "./index.css";
import AppShell from "./AppShell.jsx";
import Button from "./ui/Button.jsx";
import Card from "./ui/Card.jsx"; 
import VideoPlayer from "./VideoPlayer.jsx";


// Utility
const shuffle = (arr) => [...arr].sort(() => Math.random() - 0.5);

/* Home (unchanged) */
function Home() { /* …keep your existing Home … */ return (
  <AppShell title="TAKK">
    <Card className="p-5 space-y-3">
      <h1 className="text-xl font-semibold">Välj läge</h1>
      <div className="grid gap-3">
        <Link to="/game"><Button className="w-full">Game</Button></Link>
        <Link to="/dictionary"><Button variant="muted" className="w-full">Dictionary</Button></Link>
        <Link to="/competition"><Button variant="ghost" className="w-full">Competition</Button></Link>
      </div>
    </Card>
  </AppShell>
);}

/* Levels list fed by /api/levels (unchanged) */
function GameLevels() {
  const [levels, setLevels] = useState(null);
  useEffect(() => { fetch("/api/levels").then(r=>r.json()).then(d=>setLevels(d.levels||[])); }, []);
  return (
    <AppShell title="Nivåer">
      <div className="space-y-3">
        {!levels && <Card className="p-5 text-sm text-[var(--muted)]">Laddar…</Card>}
        {levels?.map(l => (
          <Link key={l.id} to={`/game/niva/${l.id}`}>
            <Card className="p-5 hover:shadow-sm transition">
              <div className="flex items-center justify-between">
                <div className="font-semibold">{l.name || `Nivå ${l.id}`}</div>
                <div className="text-sm text-[var(--muted)]">{(l.signs||[]).length} tecken</div>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </AppShell>
  );
}

/* Level detail (unchanged) */
function LevelDetail() {
  const { n } = useParams();
  const nav = useNavigate();
  const [level, setLevel] = useState(null);
  useEffect(() => { fetch(`/api/levels/${n}`).then(r=>r.json()).then(setLevel); }, [n]);

  if (!level?.id) return (
    <AppShell title={`Nivå ${n}`}>
      <Card className="p-5 text-sm text-[var(--muted)]">Laddar…</Card>
    </AppShell>
  );

  return (
    <AppShell title={level.name || `Nivå ${n}`}>
      <div className="grid gap-3">
        <Button className="w-full" onClick={() => nav(`/game/niva/${n}/training`)}>Träning</Button>
        <Button variant="muted" className="w-full" onClick={() => nav(`/game/niva/${n}/quiz`)}>Gissa</Button>
      </div>
      <Card className="p-5 mt-4">
        <div className="text-sm font-semibold mb-2">Tecken i nivån</div>
        <ul className="space-y-2">
          {(level.signs || []).map(s => (
            <li key={s.id} className="flex items-center justify-between">
              <span>{s.label || s.id}</span>
            </li>
          ))}
        </ul>
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
    fetch(`/api/levels/${n}`).then(r => r.json()).then(setLevel);
  }, [n]);

  const current = level?.signs?.[i];

  if (!level?.id) {
    return (
      <AppShell title={`Träning – Nivå ${n}`}>
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

        <VideoPlayer
          src={current.training_video}
          muted={false}
          videoRef={vRef}
        />

        <div className="flex items-center justify-between">
          <div className="text-sm text-[var(--muted)]">
            {i + 1}/{level.signs.length}
          </div>
          <div className="flex gap-2">
            <Button variant="muted" onClick={playClip}>Spela klipp</Button>
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
  const [level, setLevel] = useState(null);
  const [order, setOrder] = useState([]);
  const [idx, setIdx] = useState(0);
  const [score, setScore] = useState(0);
  const [answered, setAnswered] = useState(null);
  const vRef = useRef(null);

  useEffect(() => {
    fetch(`/api/levels/${n}`).then(r => r.json()).then(L => {
      setLevel(L);
      setOrder(shuffle((L.signs || []).map(s => s.id)));
    });
  }, [n]);

  const signsMap = useMemo(() => {
    const m = {}; (level?.signs || []).forEach(s => m[s.id] = s); return m;
  }, [level]);

  const qid = order[idx];
  const q = qid ? signsMap[qid] : null;

  const options = useMemo(() => {
    if (!level || !q) return [];
    const others = (level.signs || []).filter(s => s.id !== q.id).map(s => s.label || s.id);
    const picks = shuffle(others).slice(0, 3);
    return shuffle([q.label || q.id, ...picks]);
  }, [level, q]);

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

  const onAnswer = (label) => {
    if (!q) return;
    const correct = label === (q.label || q.id);
    setAnswered(correct ? "right" : "wrong");
    if (correct) setScore(s => s + 1);

    setTimeout(() => {
      setAnswered(null);
      if (idx + 1 < order.length) setIdx(idx + 1);
      else nav(`/results?score=${score + (correct ? 1 : 0)}&total=${order.length}`);
    }, 300);
  };

  if (!level) {
    return (
      <AppShell title={`Gissa – Nivå ${n}`}>
        <Card className="p-5 text-sm text-[var(--muted)]">Laddar…</Card>
      </AppShell>
    );
  }
  if (!q) {
    return (
      <AppShell title={`Gissa – Nivå ${n}`}>
        <Card className="p-5">Inga frågor.</Card>
      </AppShell>
    );
  }

  return (
    <AppShell title={`Gissa – ${level.name || `Nivå ${n}`}`}>
      <Card className="p-5 space-y-4">
        <VideoPlayer
          src={q.quiz_video}
          muted={true}
          videoRef={vRef}
        />

        <div className="flex justify-end">
          <Button variant="muted" onClick={playClip}>Spela klipp</Button>
        </div>

        <div className="grid gap-2">
          {options.map((opt) => {
            const isCorrect = opt === (q.label || q.id);
            const variant = answered ? (isCorrect ? "primary" : "muted") : "muted";
            return (
              <Button
                key={opt}
                className="w-full"
                variant={variant}
                onClick={() => !answered && onAnswer(opt)}
              >
                {opt}
              </Button>
            );
          })}
        </div>

        <div className="flex items-center justify-between text-sm text-[var(--muted)]">
          <span>{idx + 1}/{order.length}</span>
          <span>Poäng: {score}</span>
        </div>
      </Card>
    </AppShell>
  );
}


/* Results (very basic) */
function Results() {
  const params = new URLSearchParams(window.location.search);
  const score = Number(params.get("score") || 0);
  const total = Number(params.get("total") || 0);
  return (
    <AppShell title="Resultat">
      <Card className="p-5 text-center space-y-2">
        <div className="text-3xl font-bold">{score}/{total}</div>
        <div className="text-sm text-[var(--muted)]">Bra jobbat!</div>
        <div className="grid gap-2 mt-3">
          <Link to="/game"><Button className="w-full">Till Nivåer</Button></Link>
          <Link to="/"><Button variant="muted" className="w-full">Hem</Button></Link>
        </div>
      </Card>
    </AppShell>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home/>} />
        <Route path="/game" element={<GameLevels/>} />
        <Route path="/game/niva/:n" element={<LevelDetail/>} />
        <Route path="/game/niva/:n/training" element={<Training/>} />
        <Route path="/game/niva/:n/quiz" element={<Quiz/>} />
        <Route path="/results" element={<Results/>} />
        <Route path="/competition" element={<Card className="p-5">Kommer snart…</Card>} />
        <Route path="/dictionary" element={<Card className="p-5">Kommer snart…</Card>} />
      </Routes>
    </BrowserRouter>
  );
}

createRoot(document.getElementById("root")).render(<App />);
