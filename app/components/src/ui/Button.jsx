// app/components/src/ui/Button.jsx
export default function Button({ as: Tag = "button", variant = "primary", className = "", ...props }) {
  const base =
    "inline-flex items-center justify-center px-4 py-2 rounded-2xl text-sm font-semibold transition shadow-soft active:shadow-none";
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600",
    muted: "bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-white/10 dark:text-white dark:hover:bg-white/20",
    ghost: "bg-transparent text-[var(--fg)] hover:bg-black/5 dark:text-[var(--fg)] dark:hover:bg-white/10",
    danger: "bg-rose-600 text-white hover:bg-rose-700",
  };
  return <Tag className={`${base} ${variants[variant] || variants.primary} ${className}`} {...props} />;
}
