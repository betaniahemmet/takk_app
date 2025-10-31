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
	const [fadingOut, setFadingOut] = useState(false);
	const [isPlaying, setIsPlaying] = useState(false);
	const [isSearchOpen, setIsSearchOpen] = useState(false);
	const vRef = useRef(null);

	// --- Load signs from backend ---
	useEffect(() => {
		fetch("/api/signs")
			.then((r) => r.json())
			.then((data) => {
				const all = data.signs || [];
                console.log("Loaded signs from API:", all);
				setSigns(all);

				// Preselect "Hej" or the first sign
				const hej =
					all.find((s) => s.label?.toLowerCase() === "hej") ||
					(all.length > 0 ? all[0] : null);
				if (hej) setSelected(hej);
			})
			.catch(() => setSigns([]));
	}, []);

	// --- Filter signs by query ---
    const filtered = useMemo(() => {
        const q = query.trim().toLowerCase();
        return (Array.isArray(signs) ? signs : [])
            .filter((s) => s && (s.label || "").toLowerCase().includes(q))
            .sort((a, b) => (a.label || "").localeCompare(b.label || ""));
    }, [signs, query]);

	// --- Delay helper ---
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));

	// --- Pictogram → video sequence ---
	const playSequence = async () => {
		if (!selected || isPlaying) return;
		setIsPlaying(true);

		const pics = [...(selected.pictograms || [])].sort();

		setShowVideo(true);
		setPicIndex(0);

		await delay(150);

		const v = vRef.current;
		try {
			v.currentTime = 0;
			const p = v.play();
			if (p && typeof p.then === "function") p.catch(() => {});
		} catch {}

		if (v) {
			v.onended = async () => {
				setFadingOut(true);
				await delay(600);
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

				setPicIndex(pics.length - 1);
				setIsPlaying(false);
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
				{/* Header with search button */}
				<div className="flex items-center justify-between">
					<h1 className="text-lg font-semibold">Tecken</h1>
					<Button variant="outline" onClick={() => setIsSearchOpen(true)}>
						Sök
					</Button>
				</div>

				{/* Player area */}
				{selected && (
					<div className="space-y-4 text-center">
						<div className="text-lg font-semibold">{selected.label}</div>

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
									<VideoPlayer src={selected.video} videoRef={vRef} muted={false} />
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

			{/* Search modal overlay */}
			{isSearchOpen && (
				<div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex flex-col p-5">
					<div className="flex items-center justify-between mb-4">
						<input
							type="text"
							autoFocus
							placeholder="Sök tecken…"
							value={query}
							onChange={(e) => setQuery(e.target.value)}
							className="flex-1 p-2 rounded-md border border-white/20 bg-black/50 text-white placeholder-white/50"
						/>
						<Button
							variant="outline"
							className="ml-3 text-white border-white/30 hover:bg-white/10"
							onClick={() => setIsSearchOpen(false)}
						>
							Avbryt
						</Button>
					</div>

					<div className="overflow-y-auto flex-1">
						<ul className="divide-y divide-white/20">
							{filtered.map((sign) => (
								<li
									key={sign.id}
									onClick={() => {
										setSelected(sign);
										setIsSearchOpen(false);
										setShowVideo(false);
										setPicIndex(0);
									}}
									className="py-3 px-2 text-white cursor-pointer hover:bg-white/10 rounded-md"
								>
									{sign.label}
								</li>
							))}
							{filtered.length === 0 && (
								<li className="text-white/60 text-center mt-6">Inga resultat</li>
							)}
						</ul>
					</div>
				</div>
			)}
		</AppShell>
	);
}
