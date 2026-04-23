import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const target = env.VITE_PROXY_TARGET || "http://127.0.0.1:8000";
  return {
    server: {
      port: 5173,
      proxy: {
        "/__lexie": {
          target,
          changeOrigin: true,
          rewrite: (p) => p.replace(/^\/__lexie/, ""),
        },
      },
    },
  };
});
