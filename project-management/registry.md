# Work registry

Single table for **current** work items. IDs are **`WX-*`** (execution). For product features use **`LX-*`** in [`lexie-docs/REGISTRY.md`](../lexie-docs/REGISTRY.md).

| ID | Title | Status | Feature | Area | Updated | Notes |
|----|-------|--------|---------|------|---------|-------|
| WX-001 | Part C (M0) local smoke: `.env`, `uvicorn`, `/health`, `/profile`, `/admin`, `/explain` | planned | LX-1 | release | 2026-04-22 | See checklist Part C |
| WX-002 | Store `LEXIE_DEVICE_KEY` + `LEXIE_ADMIN_TOKEN` in 1Password (A6/A7) | planned | LX-1 | meta | 2026-04-22 | Master checklist |
| WX-003 | Run `pytest` + optional CI on Python 3.11+ against `lexie-server` | planned | LX-1 | lexie-server | 2026-04-22 | Mocked tests exist; verify green |
| WX-004 | Monorepo PM folder: schema, registry, work-log | done | — | meta | 2026-04-22 | `project-management/` |
| WX-005 | Phase 1 FastAPI server in repo + checklist Part B | done | LX-1 | lexie-server | 2026-04-22 | Commit `b1d6a85` |

When adding a row, use the next free `WX-###` number.
