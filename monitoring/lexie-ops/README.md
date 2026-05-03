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

## Point at production (no CORS change on Lexie)

To poll a **deployed** Lexie host from your laptop without adding `localhost:5173` to **`LEXIE_CORS_ORIGINS`**, keep **`VITE_LEXIE_BASE_URL` unset** and point the dev proxy at HTTPS:

```bash
# in .env (after cp .env.example .env)
VITE_PROXY_TARGET=https://lexie-server.fly.dev
```

Run `npm run dev`, open the app, click **Check health**. The browser calls same-origin `GET /__lexie/health`; Vite forwards to `https://lexie-server.fly.dev/health`. Swap the URL for your own **`BASE_URL`**.

## How requests work

1. **Default (no `VITE_LEXIE_BASE_URL`):** the browser fetches `GET /__lexie/health`. Vite proxies that to `VITE_PROXY_TARGET` (see `vite.config.js`) and strips the `/__lexie` prefix — same-origin, **no CORS** issues while developing.

2. **Direct to deployed host:** in `.env` set `VITE_LEXIE_BASE_URL=https://your-lexie-host.example` and restart Vite. The **Lexie FastAPI** server must list `http://localhost:5173` (and `http://127.0.0.1:5173` if you use that) in CORS (see [SPEC](../../lexie-docs/lexie/committed-to-build/lexie-word-explainer.SPEC.md) `LEXIE_CORS_ORIGINS`). Prefer **proxy mode** (above) if you want to avoid CORS edits.

## What this does *not* do

- It does not show OpenAI spend. Use the [OpenAI usage dashboard](https://platform.openai.com/usage).

**Broader triage** (CORS, device key, admin token, opt-in request logging): [lexie docs — RUNBOOK](../../lexie-docs/lexie/committed-to-build/lexie-word-explainer.RUNBOOK.md).

## Build

`npm run build` emits static files to `dist/`. Serve with any static host, or use `npx serve dist` — CORS to your production Lexie base URL will apply.
