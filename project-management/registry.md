# Work registry

Single table for **current** work items. IDs are **`WX-*`** (execution). For product features use **`LX-*`** in [`lexie-docs/REGISTRY.md`](../lexie-docs/REGISTRY.md).

**Elaborated narrative** (objectives, steps, acceptance, full milestone tables): **[`work-inventory.md`](work-inventory.md)**. Use this file for **status** and quick scanning; use `work-inventory.md` for detail.

| ID | Title | Status | Feature | Area | Updated | Notes |
|----|-------|--------|---------|------|---------|-------|
| WX-001 | Part C (M0) local smoke: `.env`, `uvicorn`, `/health`, `/profile`, `/admin`, `/explain` | planned | LX-1 | release | 2026-04-22 | [§ Planned — WX-001](work-inventory.md#wx-001--part-c-m0-local-smoke) |
| WX-002 | Store `LEXIE_DEVICE_KEY` + `LEXIE_ADMIN_TOKEN` in 1Password (A6/A7) | planned | LX-1 | meta | 2026-04-22 | [§ Planned — WX-002](work-inventory.md#wx-002--device-and-admin-tokens-in-1password-a6--a7) |
| WX-003 | Run `pytest` + optional CI on Python 3.11+ against `lexie-server` | planned | LX-1 | lexie-server | 2026-04-22 | [§ Planned — WX-003](work-inventory.md#wx-003--verify-tests-on-python-311-or-newer) |
| WX-004 | Monorepo PM folder: schema, registry, work-log | done | — | meta | 2026-04-22 | [§ Completed — WX-004](work-inventory.md#wx-004--project-management-folder); commit `c93390f` |
| WX-005 | Phase 1 FastAPI server in repo + checklist Part B | done | LX-1 | lexie-server | 2026-04-22 | [§ Completed — WX-005](work-inventory.md#wx-005--phase-1-fastapi-server-part-b); commit `b1d6a85` |
| WX-006 | Part D (M1) — public HTTPS deploy and reachability | backlog | LX-1 | release | 2026-04-22 | [§ Future — Part D](work-inventory.md#part-d-m1--public-https-and-reachability-wx-006) |
| WX-007 | Part E (M2) — child browser path (CORS, mic, device key, journeys) | backlog | LX-1 | release | 2026-04-22 | [§ Future — Part E](work-inventory.md#part-e-m2--child-browser-path-wx-007) |
| WX-008 | Part F (M3) — parent admin on production host | backlog | LX-1 | release | 2026-04-22 | [§ Future — Part F](work-inventory.md#part-f-m3--parent-admin-on-real-host-wx-008) |
| WX-009 | Part G (M4) — E2E shakedown / manual eval set | backlog | LX-1 | release | 2026-04-22 | [§ Future — Part G](work-inventory.md#part-g-m4--e2e-shakedown-wx-009) |
| WX-010 | Part H (M5) — steady operation and cost | backlog | LX-1 | ops | 2026-04-22 | [§ Future — Part H](work-inventory.md#part-h-m5--steady-operation-wx-010) |
| WX-011 | Part I — lexie-ops optional local monitor | backlog | LX-1 | ops | 2026-04-22 | [§ Future — Part I](work-inventory.md#part-i--lexie-ops-optional-wx-011) |
| WX-012 | Part J — SPEC §11 definition-of-done sign-off | backlog | LX-1 | release | 2026-04-22 | [§ Future — Part J](work-inventory.md#part-j--definition-of-done-spec-11-wx-012) |

When adding a row, use the next free `WX-###` number.
