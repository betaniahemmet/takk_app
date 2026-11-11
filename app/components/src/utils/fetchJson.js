// Fetch JSON and throw on HTTP errors, so callers can tell
// "not found" apart from "network/server problem".
export class FetchError extends Error {
    constructor(status) {
        super(`HTTP ${status}`);
        this.status = status;
    }
}

export async function fetchJson(url, options) {
    const res = await fetch(url, options);
    if (!res.ok) throw new FetchError(res.status);
    return res.json();
}

// Map an error from fetchJson to the message key used by <LoadError>
export const errorKind = (err) => (err?.status === 404 ? "notfound" : "failed");
