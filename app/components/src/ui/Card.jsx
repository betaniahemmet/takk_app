// app/components/src/ui/Card.jsx
export default function Card({
  className = "",           // now applies to the INNER content wrapper
  containerClassName = "",  // optional: for styles on the OUTER wrapper
  children,
  ...props
}) {
  return (
    <div
      className={[
        "relative rounded-2xl shadow-soft",
        "border border-black/5 dark:border-white/10",
        containerClassName,            // <- outer styles here if needed
      ].join(" ")}
      {...props}
    >
      {/* Translucent background only */}
      <div
        className="absolute inset-0 rounded-2xl bg-white/70 dark:bg-black/40 backdrop-blur-sm"
        aria-hidden="true"
      />
      {/* Content wrapper (receives your p-5, space-y-*, etc.) */}
      <div className={`relative ${className}`}>
        {children}
      </div>
    </div>
  );
}
