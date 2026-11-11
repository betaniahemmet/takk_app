// ui/LoadError.jsx — shown instead of "Laddar…" when data could not be loaded
import { Link } from "react-router-dom";
import Button from "./Button.jsx";
import Card from "./Card.jsx";

const MESSAGES = {
    notfound: "Det här finns inte.",
    failed: "Kunde inte ladda. Kontrollera uppkopplingen och försök igen.",
};

export default function LoadError({ kind = "failed" }) {
    return (
        <Card className="p-5 space-y-4 text-center">
            <p className="text-sm">{MESSAGES[kind] || MESSAGES.failed}</p>
            <div className="grid gap-2">
                {kind !== "notfound" && (
                    <Button variant="primary" className="w-full" onClick={() => window.location.reload()}>
                        Försök igen
                    </Button>
                )}
                <Button as={Link} to="/" variant="outline" className="w-full">
                    Till startsidan
                </Button>
            </div>
        </Card>
    );
}
