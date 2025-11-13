import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import AppShell from "./AppShell.jsx";
import Card from "./ui/Card.jsx";
import Button from "./ui/Button.jsx";
import { Home, Send } from "lucide-react";

export default function Feedback() {
    const [message, setMessage] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const nav = useNavigate();

    const handleSubmit = async () => {
        if (!message.trim()) return;

        setSubmitting(true);
        try {
            const res = await fetch("/api/feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message.trim() }),
            });

            if (res.ok) {
                setSubmitted(true);
                setMessage("");
                // Auto-redirect after 2 seconds
                setTimeout(() => nav("/"), 2000);
            } else {
                alert("Något gick fel. Försök igen.");
            }
        } catch (err) {
            console.error("Feedback error:", err);
            alert("Kunde inte skicka feedback. Försök igen.");
        } finally {
            setSubmitting(false);
        }
    };

    if (submitted) {
        return (
            <AppShell title="Feedback">
                <Card className="p-5 text-center space-y-4">
                    <div className="text-xl font-semibold">✅ Tack för din feedback!</div>
                    <p className="text-sm opacity-80">Skickar dig tillbaka till huvudmenyn...</p>
                </Card>
            </AppShell>
        );
    }

    return (
        <AppShell title="Feedback">
            <Card className="p-5 space-y-4">
                <div>
                    <h1 className="text-xl font-semibold">Dela dina tankar</h1>
                    <p className="text-sm opacity-70 mt-1">
                        Berätta vad du tycker om appen – all feedback hjälper oss!
                    </p>
                </div>

                <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Skriv din feedback här..."
                    className="w-full min-h-[200px] p-3 rounded-lg border border-[var(--border)] bg-[var(--background)] text-[var(--foreground)] resize-y focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                    disabled={submitting}
                />

                <div className="flex flex-col gap-2">
                    <Button
                        variant="primary"
                        className="w-full"
                        onClick={handleSubmit}
                        disabled={!message.trim() || submitting}
                    >
                        <Send className="w-4 h-4 mr-2" />
                        {submitting ? "Skickar..." : "Skicka feedback"}
                    </Button>

                    <Button variant="outline" className="w-full" onClick={() => nav("/")}>
                        <Home className="w-4 h-4 mr-2" />
                        Tillbaka till huvudmenyn
                    </Button>
                </div>
            </Card>
        </AppShell>
    );
}
