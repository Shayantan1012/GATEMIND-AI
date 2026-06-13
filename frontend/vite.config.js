import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: process.env.VITE_BACKEND_URL || "http://43.204.40.4",
        changeOrigin: true,
      },
    },
  },
});
