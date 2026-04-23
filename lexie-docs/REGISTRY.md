# Lexie — Feature Registry

Prefix: **LX**

| ID | Name | Status | Document |
|----|------|--------|----------|
| LX-1 | Word Explainer (push-to-talk, age-adaptive) | SPEC in review | PRD: [lexie/prds/lexie-word-explainer.PRD.md](lexie/prds/lexie-word-explainer.PRD.md) · SPEC: [lexie/committed-to-build/lexie-word-explainer.SPEC.md](lexie/committed-to-build/lexie-word-explainer.SPEC.md) |
| LX-2 | Context-Aware Explanation | Future | (extends LX-1 prompt/UX) |
| LX-3 | Age Profile Management | Partial (Phase 1) | (see LX-1 PRD) |
| LX-4 | Physical Device Firmware | Future | — |
| LX-5 | Wake Word Activation | Deferred | — |
| LX-6 | Platform hardening (legacy: “hosted server”) | Optional / future | Public HTTPS is **Phase 1** per PRD; LX-6 reserved for OTA, extra ops, not “first deploy” |

## Relationship to LX-1

| Feature | Relationship |
|---------|--------------|
| **LX-2** — Context-Aware Explanation | Extends LX-1; server API and prompt already accommodate context text. |
| **LX-3** — Age Profile Management | Provides the profile that LX-1 depends on; Phase 1 implements a minimal version. |
| **LX-4** — Physical Device Firmware | Consumes the LX-1 server API. |
| **LX-5** — Wake Word | Deferred; requires always-on microphone. |
| **LX-6** — Platform hardening | “Hosted” is not a separate gate — **deploy in Phase 1**; later hardening TBD. |
