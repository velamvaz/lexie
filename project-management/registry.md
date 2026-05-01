# Work registry

Single table for **current** work items. IDs are **`WX-*`** (execution). For product features use **`LX-*`** in [`lexie-docs/REGISTRY.md`](../lexie-docs/REGISTRY.md).

**Elaborated narrative** (objectives, steps, acceptance, full milestone tables): **[`work-inventory.md`](work-inventory.md)**. Use this file for **status** and quick scanning; use `work-inventory.md` for detail.

**M0 preflight** is **WX-013** (done: CI + docs) then **WX-014–WX-018**. **WX-014** is **`in_progress`** (manual smoke). Complete **WX-002** (tokens) when you need real device/admin auth for **WX-015**–**WX-017**.

| ID | Title | Status | Feature | Area | Updated | Notes |
|----|-------|--------|---------|------|---------|-------|
| WX-001 | Part C (M0) local smoke (lumped) | cancelled | LX-1 | release | 2026-04-30 | Superseded by **WX-014–WX-018** — use granular rows below. |
| WX-002 | Store `LEXIE_DEVICE_KEY` + `LEXIE_ADMIN_TOKEN` in 1Password (A6/A7) | planned | LX-1 | meta | 2026-04-22 | [§ WX-002](work-inventory.md#wx-002--device-and-admin-tokens-in-1password-a6--a7); do before or with **WX-014**–**WX-017** for real auth. |
| WX-003 | Run `pytest` + optional CI on Python 3.11+ (lumped) | cancelled | LX-1 | lexie-server | 2026-04-30 | Superseded by **WX-013**. |
| WX-004 | Monorepo PM folder: schema, registry, work-log | done | — | meta | 2026-04-22 | [§ Completed — WX-004](work-inventory.md#wx-004--project-management-folder); commit `c93390f` |
| WX-005 | Phase 1 FastAPI server in repo + checklist Part B | done | LX-1 | lexie-server | 2026-04-22 | [§ Completed — WX-005](work-inventory.md#wx-005--phase-1-fastapi-server-part-b); commit `b1d6a85` |
| WX-006 | Part D (M1) — public HTTPS deploy and reachability | backlog | LX-1 | release | 2026-04-22 | [§ Future — Part D](work-inventory.md#part-d-m1--public-https-and-reachability-wx-006) |
| WX-007 | Part E (M2) — child browser path (CORS, mic, device key, journeys) | backlog | LX-1 | release | 2026-04-22 | [§ Future — Part E](work-inventory.md#part-e-m2--child-browser-path-wx-007) |
| WX-008 | Part F (M3) — parent admin on production host | backlog | LX-1 | release | 2026-04-22 | [§ Future — Part F](work-inventory.md#part-f-m3--parent-admin-on-real-host-wx-008) |
| WX-009 | Part G (M4) — E2E shakedown / manual eval set | backlog | LX-1 | release | 2026-04-22 | [§ Future — Part G](work-inventory.md#part-g-m4--e2e-shakedown-wx-009) |
| WX-010 | Part H (M5) — steady operation and cost | backlog | LX-1 | ops | 2026-04-22 | [§ Future — Part H](work-inventory.md#part-h-m5--steady-operation-wx-010) |
| WX-011 | Part I — lexie-ops optional local monitor | backlog | LX-1 | ops | 2026-04-22 | [§ Future — Part I](work-inventory.md#part-i--lexie-ops-optional-wx-011) |
| WX-012 | Part J — SPEC §11 definition-of-done sign-off | backlog | LX-1 | release | 2026-04-22 | [§ Future — Part J](work-inventory.md#part-j--definition-of-done-spec-11-wx-012) |
| WX-013 | **Preflight:** `pytest` passes on Python 3.11+ in `lexie-server` | done | LX-1 | lexie-server | 2026-04-30 | [§ WX-013](work-inventory.md#wx-013--preflight-pytest-on-python-311-or-newer). CI: [`.github/workflows/lexie-server-pytest.yml`](../.github/workflows/lexie-server-pytest.yml) on push/PR. Local: `python3.11 -m venv .venv && pip install -e ".[dev]" && pytest -v`. |
| WX-014 | **M0:** `.env` + `uvicorn` + `GET /health` → 200 (checklist C1–C2) | **in_progress** | LX-1 | lexie-server | 2026-04-30 | [§ WX-014](work-inventory.md#wx-014--m0-dotenv-server-and-health-c1c2) |
| WX-015 | **M0:** `GET`/`PATCH /profile` — 401 without admin, 200 with Bearer (C3) | planned | LX-1 | lexie-server | 2026-04-30 | [§ WX-015](work-inventory.md#wx-015--m0-profile-admin-auth-c3) |
| WX-016 | **M0:** Browser `/admin` — token, load profile, save, refresh (C4) | planned | LX-1 | lexie-server | 2026-04-30 | [§ WX-016](work-inventory.md#wx-016--m0-admin-html-c4) |
| WX-017 | **M0:** `POST /explain` with real or prototype audio — 200 MP3 or 400 JSON (C5) | planned | LX-1 | lexie-server | 2026-04-30 | [§ WX-017](work-inventory.md#wx-017--m0-post-explain-real-pipeline-c5); needs **ffmpeg** on PATH for duration/pipeline. |
| WX-018 | **M0:** No raw audio on disk; `LEXIE_LOG_REQUESTS=0` default (C6) | planned | LX-1 | lexie-server | 2026-04-30 | [§ WX-018](work-inventory.md#wx-018--m0-privacy-no-raw-audio-c6) |

When adding a row, use the next free `WX-###` number.
