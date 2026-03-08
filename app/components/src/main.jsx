import React, { lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import "./index.css";
import AppShell from "./AppShell.jsx";
import Button from "./ui/Button.jsx";
import Card from "./ui/Card.jsx";
// Home is eager — it's the first page every user sees
import Home from "./Home.jsx";

// All route-level pages are lazy-loaded
const GameLevels = lazy(() =>
    import("./Practice.jsx").then((m) => ({ default: m.GameLevels }))
);
const LevelDetail = lazy(() =>
    import("./Practice.jsx").then((m) => ({ default: m.LevelDetail }))
);
const Training     = lazy(() => import("./practice/Training.jsx"));
const Quiz         = lazy(() => import("./practice/Quiz.jsx"));
const Competition  = lazy(() => import("./Competition.jsx"));
const Dictionary   = lazy(() => import("./Dictionary.jsx"));
const Feedback     = lazy(() => import("./Feedback.jsx"));
const Introduction = lazy(() => import("./Introduction.jsx"));

function Loading() {
    return (
        <AppShell title="">
            <Card className="p-5 text-sm text-[var(--muted)]">Laddar…</Card>
        </AppShell>
    );
}

// NotFound component (keep it here since it's simple and only used once)
function NotFound() {
    return (
        <AppShell title="404">
            <Card className="p-5 text-center space-y-3">
                <div className="text-xl font-semibold">Sidan finns inte.</div>
                <Link to="/">
                    <Button variant="primary" className="w-full mt-3">
                        Till startsidan
                    </Button>
                </Link>
            </Card>
        </AppShell>
    );
}

function App() {
    return (
        <BrowserRouter>
            <Suspense fallback={<Loading />}>
                <Routes>
                    <Route path="/"                       element={<Home />} />
                    <Route path="/game"                   element={<GameLevels />} />
                    <Route path="/game/niva/:n"           element={<LevelDetail />} />
                    <Route path="/game/niva/:n/training"  element={<Training />} />
                    <Route path="/game/niva/:n/quiz"      element={<Quiz />} />
                    <Route path="/competition"            element={<Competition />} />
                    <Route path="/dictionary"             element={<Dictionary />} />
                    <Route path="/feedback"               element={<Feedback />} />
                    <Route path="/introduktion"           element={<Introduction />} />
                    <Route path="*"                       element={<NotFound />} />
                </Routes>
            </Suspense>
        </BrowserRouter>
    );
}

createRoot(document.getElementById("root")).render(<App />);
