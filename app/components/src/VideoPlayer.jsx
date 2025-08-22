// app/components/src/VideoPlayer.jsx
import React, { useEffect, useRef } from "react";

export default function VideoPlayer({
  src,
  muted = false,
  onEnd,
  className = "",
  videoRef: externalRef, // parent can control video via this ref
  controls = false       // keep false; set true if you ever want native controls
}) {
  const innerRef = useRef(null);
  const ref = externalRef || innerRef;

  // When src or mute changes, reset to start and pause
  useEffect(() => {
    const v = ref.current;
    if (!v) return;
    v.pause();
    try { v.currentTime = 0; } catch {}
    v.muted = muted;
  }, [src, muted, ref]);

  return (
    <div className={`rounded-2xl overflow-hidden bg-black ${className}`} style={{ aspectRatio: "16 / 9" }}>
      <video
        ref={ref}
        src={src}
        muted={muted}
        playsInline
        preload="metadata"
        onEnded={onEnd}
        className="h-full w-full"
        {...(controls ? { controls: true } : {})}
      />
    </div>
  );
}
