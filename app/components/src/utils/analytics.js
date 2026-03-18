const SESSION_KEY = "takk_session_id";

function generateUUID() {
    // crypto.randomUUID() requires a secure context (HTTPS/localhost).
    // Fall back to Math.random() for plain HTTP on local network.
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
        return crypto.randomUUID();
    }
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0;
        return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
    });
}

function getOrCreateSessionId() {
    let id = localStorage.getItem(SESSION_KEY);
    if (!id) {
        id = generateUUID();
        localStorage.setItem(SESSION_KEY, id);
    }
    return id;
}

async function trackEvent(eventType, data = {}) {
    try {
        await fetch("/api/track", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: getOrCreateSessionId(),
                event_type: eventType,
                data,
            }),
        });
    } catch {
        // Tracking failures are silent — never surface errors to users
    }
}

export const trackPageView = (page) => trackEvent("page_view", { page });
export const trackSignCompleted = (signId, mode) => trackEvent("sign_completed", { sign_id: signId, mode });
export const trackQuizAttempt = (level, total) => trackEvent("quiz_attempt", { level, total });
export const trackCompetitionAttempt = (score, total) => trackEvent("competition_attempt", { score, total });
export const trackLevelStarted = (level) => trackEvent("level_started", { level });
export const trackLevelCompleted = (level) => trackEvent("level_completed", { level });
export const trackSignViewed = (signId) => trackEvent("sign_viewed", { sign_id: signId });
