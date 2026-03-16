import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
    plugins: [react()],
    base: "/",
    server: {
        fs: {
            // Allow imports from catalog/ at repo root (e.g. mouth_coordinates.json)
            allow: ["../.."],
        },
    },
    build: {
        outDir: "dist",
        rollupOptions: {
            output: {
                manualChunks: {
                    vendor: ["react", "react-dom", "react-router-dom"],
                    icons: ["lucide-react"],
                },
            },
        },
    },
});
