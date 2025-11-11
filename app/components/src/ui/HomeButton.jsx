// ui/HomeButton.jsx
import { Home } from "lucide-react";
import { Link } from "react-router-dom";

export default function HomeButton() {
    return (
        <Link 
            to="/" 
            className="inline-flex items-center justify-center w-10 h-10 rounded-full hover:bg-black/5 dark:hover:bg-white/5 transition"
            aria-label="Till startsidan"
        >
            <Home className="w-5 h-5" />
        </Link>
    );
}