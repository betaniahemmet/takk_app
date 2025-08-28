// app/components/src/VideoPlayer.jsx
import React, { useEffect, useRef, useState } from "react";

export default function VideoPlayer({
  src,
  muted = false,
  onEnd,
  className = "",
  videoRef: externalRef,  // lets parent control (Spela klipp)
  controls = false,
  fallbackRatio = "1 / 1", // keep square until metadata arrives
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
    try { v.currentTime = 0; } catch {}
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
        preload="metadata"
        onLoadedMetadata={onLoadedMeta}
        onEnded={onEnd}
        // Keep aspect by containing within wrapper, never stretch
        className="block w-full h-full object-contain"
        {...(controls ? { controls: true } : {})}
      />
    </div>
  );
}

