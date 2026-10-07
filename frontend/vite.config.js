import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// DEVELOPMENT ONLY: forwards /api/student, /api/question, /api/result to the right service.
// In Docker/Kubernetes the nginx server (nginx.conf) does the same job.
const proxy = (port, name) => ({
  target: `http://localhost:${port}`,
  changeOrigin: true,
  rewrite: (path) => path.replace(new RegExp(`^/api/${name}`), ""),
});

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api/student": proxy(8001, "student"),
      "/api/question": proxy(8002, "question"),
      "/api/result": proxy(8003, "result"),
    },
  },
});
