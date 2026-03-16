// app/components/src/VideoPlayer.jsx
import React, { useEffect, useRef, useState } from "react";

export default function VideoPlayer({
    src,
    muted = false,
    onEnd,
    onPlay,
    className = "",
    videoRef: externalRef, // lets parent control (Spela klipp)
    controls = false,
    fallbackRatio = "1 / 1", // keep square until metadata arrives
    preload = "metadata",
    mouthCoord = null, // {x, y} as percentages — renders a blur overlay over the mouth
}) {
    const innerRef = useRef(null);
    const ref = externalRef || innerRef;
    const [ratio, setRatio] = useState(null); // e.g., "1 / 1", "16 / 9"

    // Reset when src/muted changes
    useEffect(() => {
        const v = ref.current;
        if (!v) return;
        setRatio(null);
        v.pause();
        try {
            v.currentTime = 0;
        } catch {}
        v.muted = muted;
        v.load();
    }, [src, muted, ref]);

    const onLoadedMeta = (e) => {
        const v = e.currentTarget;
        // Build a CSS aspect-ratio string like "1920 / 1080" → browser simplifies
        if (v.videoWidth && v.videoHeight) {
            setRatio(`${v.videoWidth} / ${v.videoHeight}`);
        } else {
            setRatio(null); // fallback
        }
    };

    return (
        <div
            className={`relative rounded-2xl overflow-hidden bg-black ${className}`}
            style={{ aspectRatio: ratio || fallbackRatio }}
        >
            <video
                key={src}
                ref={ref}
                src={src}
                muted={muted}
                playsInline
                preload={preload}
                onLoadedMetadata={onLoadedMeta}
                onEnded={onEnd}
                onPlay={onPlay}
                // Keep aspect by containing within wrapper, never stretch
                className="block w-full h-full object-contain"
                {...(controls ? { controls: true } : {})}
            />
            {mouthCoord && (
                <div
                    style={{
                        position: "absolute",
                        left: `${mouthCoord.x - 6}%`,
                        top: `${mouthCoord.y - 5}%`,
                        width: "12%",
                        height: "10%",
                        backdropFilter: "blur(12px)",
                        background: "rgba(0,0,0,0.25)",
                        borderRadius: "4px",
                        pointerEvents: "none",
                    }}
                />
            )}
        </div>
    );
}
