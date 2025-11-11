import {Link} from "react-router-dom";
import Button from "./ui/Button.jsx";
import Card from "./ui/Card.jsx";
import AppShell from "./AppShell.jsx";
import { Layers, Trophy, Book } from "lucide-react";


function Home() {
    return (
        <AppShell title="TAKK">
            <Card className="p-5 space-y-6">
                <h1 className="text-xl font-semibold">Välj läge</h1>
                <div className="grid gap-3">
                    <Link to="/game">
                        <Button variant="primary" className="w-full !justify-start text-left">
                            <div className="flex items-start gap-3">
                                <Layers className="w-5 h-5 mt-0.5 flex-shrink-0" />
                                <div className="flex flex-col">
                                    <span className="font-semibold">Steg för steg</span>
                                    <span className="text-sm opacity-80 font-normal">
                                        Lär dig tecken i nivåer
                                    </span>
                                </div>
                            </div>
                        </Button>
                    </Link>
                    <Link to="/dictionary">
                        <Button variant="primary" className="w-full !justify-start text-left">
                            <div className="flex items-start gap-3">
                                <Book className="w-5 h-5 mt-0.5 flex-shrink-0" />
                                <div className="flex flex-col">
                                    <span className="font-semibold">Ordbok</span>
                                    <span className="text-sm opacity-80 font-normal">
                                        Slå upp tecken
                                    </span>
                                </div>
                            </div>
                        </Button>
                    </Link>
                    <Link to="/competition">
                        <Button variant="primary" className="w-full !justify-start text-left">
                            <div className="flex items-start gap-3">
                                <Trophy className="w-5 h-5 mt-0.5 flex-shrink-0" />
                                <div className="flex flex-col">
                                    <span className="font-semibold">Tävling</span>
                                    <span className="text-sm opacity-80 font-normal">
                                        Utmana dig och jämför poäng
                                    </span>
                                </div>
                            </div>
                        </Button>
                    </Link>
                </div>
            </Card>
        </AppShell>
    );
}

export default Home;