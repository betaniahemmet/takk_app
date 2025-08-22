// app/components/src/ui/Card.jsx
export default function Card({ className = "", ...props }) {
  return (
    <div
      className={`rounded-2xl border border-black/5 dark:border-white/10 bg-[var(--card)] shadow-soft ${className}`}
      {...props}
    />
  );
}
