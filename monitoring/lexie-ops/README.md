# Lexie Ops (local parent monitoring UI)

Minimal **Vite** static app to poll `GET /health` against a Lexie server. Not part of the child UX.

## Setup

```bash
cd monitoring/lexie-ops
npm install
cp .env.example .env
npm run dev
```

Open the URL Vite prints (default `http://localhost:5173`).

## How requests work

1. **Default (no `VITE_LEXIE_BASE_URL`):** the browser fetches `GET /__lexie/health`. Vite proxies that to `VITE_PROXY_TARGET` (see `vite.config.js`) and strips the `/__lexie` prefix — same-origin, **no CORS** issues while developing.

2. **Direct to deployed host:** in `.env` set `VITE_LEXIE_BASE_URL=https://your-lexie-host.example` and restart Vite. The **Lexie FastAPI** server must list `http://localhost:5173` in CORS (see [SPEC](../../lexie-docs/lexie/committed-to-build/lexie-word-explainer.SPEC.md) `LEXIE_CORS_ORIGINS`).

## What this does *not* do

- It does not show OpenAI spend. Use the [OpenAI usage dashboard](https://platform.openai.com/usage).

**Broader triage** (CORS, device key, admin token, opt-in request logging): [lexie docs — RUNBOOK](../../lexie-docs/lexie/committed-to-build/lexie-word-explainer.RUNBOOK.md).

## Build

`npm run build` emits static files to `dist/`. Serve with any static host, or use `npx serve dist` — CORS to your production Lexie base URL will apply.
