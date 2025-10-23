// app/components/src/ui/Button.jsx
export default function Button({
    as: Tag = "button",
    variant = "primary",
    className = "",
    ...props
}) {
    const base =
        "inline-flex items-center justify-center px-4 py-2 rounded-2xl text-sm font-semibold transition shadow-soft active:shadow-none";

    const variants = {
        primary: "bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600",
        muted: "bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-white/10 dark:text-white dark:hover:bg-white/20",
        outline:
            "bg-transparent border border-gray-300 text-gray-900 hover:bg-black/5 dark:border-white/20 dark:text-white dark:hover:bg-white/10",
        secondary:
            "bg-slate-700 text-white hover:bg-slate-800 dark:bg-slate-600 dark:hover:bg-slate-700",
        ghost: "bg-transparent text-[var(--fg)] hover:bg-black/5 dark:text-[var(--fg)] dark:hover:bg-white/10",
        // keep danger if you use it elsewhere
        danger: "bg-rose-600 text-white hover:bg-rose-700",
    };

    return (
        <Tag
            className={`${base} ${variants[variant] || variants.primary} ${className}`}
            {...props}
        />
    );
}
