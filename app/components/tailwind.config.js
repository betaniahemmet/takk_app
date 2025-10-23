/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: "class", // use .dark class (toggle or system)
    content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
    theme: {
        extend: {
            fontFamily: {
                // system stack (no external fonts)
                sans: [
                    "ui-sans-serif",
                    "system-ui",
                    "Segoe UI",
                    "Roboto",
                    "Helvetica",
                    "Arial",
                    "Apple Color Emoji",
                    "Segoe UI Emoji",
                ],
                mono: [
                    "ui-monospace",
                    "SFMono-Regular",
                    "Menlo",
                    "Consolas",
                    "Liberation Mono",
                    "monospace",
                ],
            },
            borderRadius: { xl: "1rem", "2xl": "1.25rem" },
            boxShadow: { soft: "0 8px 30px rgba(0,0,0,0.08)" },
        },
    },
    plugins: [],
};
