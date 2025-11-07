import {Link} from "react-router-dom";
import Button from "./ui/Button.jsx";
import Card from "./ui/Card.jsx";
import AppShell from "./AppShell.jsx";


function Home() {
    return (
        <AppShell title="TAKK">
            <Card className="p-5 space-y-6">
                <h1 className="text-xl font-semibold">Välj läge</h1>
                <div className="grid gap-3">
                    <Link to="/game">
                        <Button variant="primary" className="w-full">
                            Game
                        </Button>
                    </Link>
                    <Link to="/dictionary">
                        <Button variant="primary" className="w-full">
                            Dictionary
                        </Button>
                    </Link>
                    <Link to="/competition">
                        <Button variant="primary" className="w-full">
                            Competition
                        </Button>
                    </Link>
                </div>
            </Card>
        </AppShell>
    );
}

export default Home;