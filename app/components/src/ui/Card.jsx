// app/components/src/ui/Card.jsx
export default function Card({ className = "", ...props }) {
  return (
    <div
      className={[
        "rounded-2xl shadow-soft",
        "border border-black/5 dark:border-white/10",
        "bg-white/80 backdrop-blur-sm dark:bg-black/40",
        className,
      ].join(" ")}
      {...props}
    />
  );
}
