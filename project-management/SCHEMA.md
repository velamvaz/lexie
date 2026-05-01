# Work item schema (minimal)

**Elaboration:** Long-form objectives, steps, and roadmap tables live in [`work-inventory.md`](work-inventory.md). **`registry.md`** remains the canonical place for **current status** per `WX-*` row.

## Identity

| Field | Required | Description |
|-------|----------|-------------|
| **ID** | yes | `WX-###` — unique in this monorepo (execution work). Not the same as product `LX-*` in `lexie-docs/REGISTRY.md`. |
| **Title** | yes | One line; imperative or outcome (“Run M0 smoke tests”). |
| **Status** | yes | One of: `backlog`, `planned`, `in_progress`, `blocked`, `done`, `cancelled`. |
| **Feature** | no | Optional `LX-*` link when the work serves a named product line. |
| **Area** | no | Rough scope: `lexie-server`, `lexie-docs`, `device`, `ops`, `meta`, `release`, … |
| **Updated** | yes | Last change to this row, `YYYY-MM-DD` (ISO). |
| **Notes** | no | Short pointer: commit, PR URL, path to `items/WX-###.md`, or blocker text. |

## Status meanings

| Status | Meaning |
|--------|---------|
| `backlog` | Acknowledged; not scheduled. |
| `planned` | Intention to do soon; may have no owner yet. |
| `in_progress` | Active. |
| `blocked` | Waiting on external input; say what in **Notes**. |
| `done` | Completed (leave row for history or archive later if the table grows). |
| `cancelled` | Will not do; one-line reason in **Notes**. |

## Work log entries (monthly files)

Each `work-log/YYYY-MM.md` is **append-only** (newest entries at the **bottom** of the month file, or top—pick one; this repo uses **bottom** for chronological flow).

Suggested line shape:

```text
YYYY-MM-DD — WX-### — What happened (optional: commit abc1234, PR #n).
```

No rigid parser: keep it human-readable.
