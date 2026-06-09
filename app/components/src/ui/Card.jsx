// app/components/src/ui/Card.jsx
export default function Card({
    className = "", // now applies to the INNER content wrapper
    containerClassName = "", // optional: for styles on the OUTER wrapper
    children,
    ...props
}) {
    return (
        <div
            className={[
                "relative rounded-2xl shadow-soft",
                "border border-black/5 dark:border-white/10",
                containerClassName, // <- outer styles here if needed
            ].join(" ")}
            {...props}
        >
            {/* Translucent background only */}
            <div
                className="absolute inset-0 rounded-2xl bg-white/85 dark:bg-slate-900/75 backdrop-blur-sm"
                aria-hidden="true"
            />
            {/* Content wrapper — z-[1] ensures outlines render above the backdrop-blur sibling */}
            <div className={`relative z-[1] ${className}`}>{children}</div>
        </div>
    );
}
