import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // Les appels vers /api sont redirigés vers FastAPI
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});