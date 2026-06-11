# Lexie — Feature Registry

Prefix: **LX**

| ID | Name | Status | Document |
|----|------|--------|----------|
| LX-1 | Word Explainer (push-to-talk, age-adaptive) | Phase 1 shipped (2026-05-03) | PRD: [lexie/prds/lexie-word-explainer.PRD.md](lexie/prds/lexie-word-explainer.PRD.md) · SPEC: [lexie/committed-to-build/lexie-word-explainer.SPEC.md](lexie/committed-to-build/lexie-word-explainer.SPEC.md) |
| LX-2 | Context-Aware Explanation | Future | (extends LX-1 prompt/UX) |
| LX-3 | Age Profile Management | Partial (Phase 1) | (see LX-1 PRD) |
| LX-4 | Physical Device Firmware (**Lexie Card**) | Phase 2 / **bench execution** | Mechanical v1: [../hardware/lexie-plaud-form-factor.html](../hardware/lexie-plaud-form-factor.html) · Firmware contract: [DEVICE-INTEGRATION.md](lexie/committed-to-build/lexie-word-explainer.DEVICE-INTEGRATION.md) (WX-023) · **Path B PRDs v1.1:** [lx-4-waveshare-device.PRD.md](lexie/prds/lx-4-waveshare-device.PRD.md), [lx-4-device-firmware.PRD.md](lexie/prds/lx-4-device-firmware.PRD.md), [lx-4-device-ux-sla.PRD.md](lexie/prds/lx-4-device-ux-sla.PRD.md) · PINMAP: [PINMAP-WAVESHARE-AUDIO.md](lexie/committed-to-build/lexie-word-explainer.PINMAP-WAVESHARE-AUDIO.md) · **WX-035** in progress (board delivered) · [work-inventory § D3](../project-management/work-inventory.md#section-d3--lx-4-bench-execution-path-b-waveshare) |
| LX-5 | Wake Word Activation | Deferred | — |
| LX-6 | Platform hardening (legacy: “hosted server”) | Optional / future | Public HTTPS is **Phase 1** per PRD; LX-6 reserved for OTA, extra ops, not “first deploy” |

## Relationship to LX-1

| Feature | Relationship |
|---------|--------------|
| **LX-2** — Context-Aware Explanation | Extends LX-1; server API and prompt already accommodate context text. |
| **LX-3** — Age Profile Management | Provides the profile that LX-1 depends on; Phase 1 implements a minimal version. |
| **LX-4** — Physical Device Firmware (**Lexie Card**) | Consumes the LX-1 server API; WiFi client to same `BASE_URL` as Phase 1 browser. |
| **LX-5** — Wake Word | Deferred; requires always-on microphone. |
| **LX-6** — Platform hardening | “Hosted” is not a separate gate — **deploy in Phase 1**; later hardening TBD. |

## Execution work (WX-*)

Engineering tasks (deploy, tests, secrets) use **`WX-*`** ids in the monorepo **[`project-management/registry.md`](../project-management/registry.md)** and are **not** listed in this LX table.
