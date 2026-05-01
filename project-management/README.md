# Project management (Lexie monorepo)

This folder tracks **execution work**: what is planned, in flight, blocked, or done. It complements product documentation under `lexie-docs/`.

| Artifact | Purpose |
|----------|---------|
| [SCHEMA.md](SCHEMA.md) | Field definitions and status rules |
| [registry.md](registry.md) | **Current** work items (single table; update in place) |
| [work-log/](work-log/) | **Append-only** narrative log by month (decisions, progress, links to commits/PRs) |
| [items/TEMPLATE.md](items/TEMPLATE.md) | Optional long-form notes for a work item (link from registry) |

## Relationship to `lexie-docs/REGISTRY.md`

- **`LX-*`** — Product / feature registry (what Lexie *is*: Word Explainer, firmware, etc.).
- **`WX-*`** — Work execution items (what we *do* next: deploy, tests, secrets, milestones).

Link them with the **Feature** column in `registry.md` (e.g. `LX-1`) when a task serves a specific feature.

## Conventions

1. **New work** — Add a row to `registry.md` with the next `WX-###` id; set `Status` to `planned` or `backlog`.
2. **Start work** — Set `Status` to `in_progress`, bump **Updated** (ISO date).
3. **Finish** — Set `Status` to `done` (or `cancelled` with a short note); add a line to the current month in `work-log/` pointing to commits or outcomes.
4. **Heavy context** — Add `items/WX-###.md` and put the path in **Notes**.

Keep the registry **scannable**: titles short; defer detail to work-log or `items/`.
