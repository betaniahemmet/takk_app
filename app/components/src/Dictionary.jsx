import React, { useState, useEffect, useMemo, useRef } from "react";
import AppShell from "./AppShell.jsx";
import Card from "./ui/Card.jsx";
import Button from "./ui/Button.jsx";
import VideoPlayer from "./VideoPlayer.jsx";

export default function Dictionary() {
	// --- State ---
	const [signs, setSigns] = useState([]);
	const [query, setQuery] = useState("");
	const [selected, setSelected] = useState(null);
	const [picIndex, setPicIndex] = useState(0);
	const [showVideo, setShowVideo] = useState(false);
	const vRef = useRef(null);
    const [fadingOut, setFadingOut] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);


	// --- Load signs from backend ---
	useEffect(() => {
		fetch("/api/signs")
			.then((r) => r.json())
			.then((data) => setSigns(data.signs || []))
			.catch(() => setSigns([]));
	}, []);

	// --- Filter signs by query ---
	const filtered = useMemo(() => {
		const q = query.trim().toLowerCase();
		return (signs || [])
			.filter((s) => s.label.toLowerCase().includes(q))
			.sort((a, b) => a.label.localeCompare(b.label));
	}, [signs, query]);

	// --- Delay helper ---
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));

	// --- Pictogram → video sequence ---
    const playSequence = async () => {
        if (!selected || isPlaying) return; // 🚫 ignore clicks while active
        setIsPlaying(true);

        const pics = [...(selected.pictograms || [])].sort();

        // 1️⃣ Start with video visible
        setShowVideo(true);
        setPicIndex(0);

        await delay(150); // give React time to mount <video>

        const v = vRef.current;
        try {
            v.currentTime = 0;
            const p = v.play();
            if (p && typeof p.then === "function") p.catch(() => {});
        } catch {}
        

        // 2️⃣ When the video finishes, fade it out and show pictograms
        if (v) {
            v.onended = async () => {
                setFadingOut(true);
                await delay(600); // fade duration
                setShowVideo(false);
                setFadingOut(false);

                if (!pics.length) {
                    setIsPlaying(false);
                    return;
                }

                const frameMs = 800;
                for (let i = 0; i < pics.length; i++) {
                    setPicIndex(i);
                    await delay(frameMs);
                }

                // stay on last pictogram
                setPicIndex(pics.length - 1);
                setIsPlaying(false); // ✅ unlock
            };
        } else {
            setIsPlaying(false);
        }
    };
    


	// --- When showVideo becomes true, play the video ---
	useEffect(() => {
		if (showVideo && vRef.current) {
			try {
				const v = vRef.current;
				v.pause();
				v.currentTime = 0;
				const p = v.play();
				if (p && typeof p.then === "function") p.catch(() => {});
			} catch {}
		}
	}, [showVideo]);

	return (
		<AppShell title="Dictionary">
			<Card className="p-5 space-y-5">
				{/* Search input */}
				<input
					type="text"
					placeholder="Sök tecken…"
					value={query}
					onChange={(e) => setQuery(e.target.value)}
					className="w-full p-2 border rounded-md border-black/10 dark:border-white/10 bg-white/80 dark:bg-black/30"
				/>

                {/* Player area */}
                {selected && (
                    <div className="space-y-4 text-center">
                        <div className="text-lg font-semibold">{selected.label}</div>

                        {/* consistent media frame */}
                        <div className="relative w-full max-w-sm mx-auto aspect-square overflow-hidden rounded-lg bg-black/5 dark:bg-white/5 flex justify-center items-center">
                            {/* pictograms */}
                            {!showVideo &&
                                (selected.pictograms || []).map((p, i) => (
                                    <img
                                        key={i}
                                        src={p}
                                        alt=""
                                        className={`absolute inset-0 w-full h-full object-contain transition-opacity duration-700 ${
                                            i === picIndex ? "opacity-100" : "opacity-0"
                                        }`}
                                    />
                                ))}

                            {/* video */}
                            {showVideo && (
                                <div
                                    className={`absolute inset-0 transition-opacity duration-700 ${
                                        fadingOut ? "opacity-0" : "opacity-100"
                                    }`}
                                >
                                    <VideoPlayer
                                        src={selected.video}
                                        videoRef={vRef}
                                        muted={false}
                                    />
                                </div>
                            )}
                        </div>

                        <Button
                            variant={isPlaying ? "muted" : "primary"}
                            onClick={playSequence}
                            disabled={isPlaying}
                        >
                            {isPlaying ? "Spelar…" : "Spela video"}
                        </Button>

                        <hr className="border-black/10 dark:border-white/10" />
                    </div>
                )}


				{/* Sign list */}
				<ul className="divide-y divide-black/10 dark:divide-white/10">
					{filtered.map((sign) => (
						<li
							key={sign.id}
							onClick={() => {
                                setIsPlaying(false);
                                setShowVideo(false);
                                setFadingOut(false);
                                setPicIndex(0);
                                setSelected(sign);
                            }}
							className="py-2 px-2 cursor-pointer hover:bg-black/5 dark:hover:bg-white/5 rounded-md"
						>
							{sign.label}
						</li>
					))}
				</ul>
			</Card>
		</AppShell>
	);
}