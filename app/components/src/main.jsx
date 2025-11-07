import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import "./index.css";
import AppShell from "./AppShell.jsx";
import Button from "./ui/Button.jsx";
import Card from "./ui/Card.jsx";

// Import pages
import Home from "./Home.jsx";
import { GameLevels, LevelDetail } from "./Practice.jsx";
import Training from "./practice/Training.jsx";
import Quiz from "./practice/Quiz.jsx";
import Competition from "./Competition.jsx";
import Dictionary from "./Dictionary.jsx";

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
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/game" element={<GameLevels />} />
                <Route path="/game/niva/:n" element={<LevelDetail />} />
                <Route path="/game/niva/:n/training" element={<Training />} />
                <Route path="/game/niva/:n/quiz" element={<Quiz />} />
                <Route path="/competition" element={<Competition />} />
                <Route path="/dictionary" element={<Dictionary />} />
                <Route path="*" element={<NotFound />} />
            </Routes>
        </BrowserRouter>
    );
}

createRoot(document.getElementById("root")).render(<App />);