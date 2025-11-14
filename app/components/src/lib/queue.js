// re-queue an item k steps ahead of the *current* index
export function requeueAhead(queue, fromIndex, id, k) {
    if (k <= 0) return queue;
    const q = [...queue];
    const insertAt = Math.min(q.length, fromIndex + k + 1);
    q.splice(insertAt, 0, id);
    return q;
}
