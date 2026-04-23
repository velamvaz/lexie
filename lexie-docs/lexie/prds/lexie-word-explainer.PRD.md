# Product PRD: Lexie Word Explainer

**Feature:** Lexie Smart Bookmark — Push-to-Talk AI Word Explanation with Age-Adaptive Responses

**Status:** Draft

**Date:** 2026-04-08

**Last updated:** 2026-04-22 (admin one-pager, first-run, **error tone**, Phase 1 **acceptance**; Journey 5; locked defaults; see decision log)

**Registry ID:** LX-1

**Author:** Vignesh

**Source:** Personal need — 6-year-old accelerated reader encountering advanced vocabulary in books like Harry Potter

**Deployment intent (2026):** This PRD targets a **single child in one family** — not a multi-tenant product, school deployment, or commercial service. The system should stay **as simple as possible** (one age profile, one device, minimal operational burden). Multi-child or hosted “for many users” features are **explicitly not goals** for this project unless plans change.

---

## 1. Problem Statement

1. A young child reading advanced books encounters multiple unfamiliar words per page. Stopping to look up words in a printed dictionary destroys reading flow, requires adult assistance, and often provides definitions that are themselves incomprehensible to a 6-year-old.

2. Asking a parent is the current workaround — but parents are not always present in the room, and the interruption pulls both the child and the parent out of what they were doing.

3. General-purpose voice assistants (Alexa, Siri, Google) answer the question but do so in adult language, expose the child to an unconstrained internet-connected AI, and create a habit of asking about anything — not just words they encounter while reading.

4. As the child grows, the explanation style needs to evolve. A definition appropriate for age 6 is condescending at age 9, and a word that needs explanation at 6 may be obvious by 8. Static tools cannot adapt.

### What Success Looks Like

A child clips Lexie onto whatever book she is reading. When she hits a word she does not understand, she presses the button on the bookmark, says the word (and optionally a short sentence of context), and hears a clear, warm, simple explanation spoken back to her in a few seconds — using words she already knows, often referencing something familiar from the book or her own life. She gets back to reading immediately. Over months and years, the explanations grow richer and more nuanced as her age profile is updated, without any change to the device itself.

### Key Design Principles

> "It should feel like asking a very patient older sibling who always knows the right way to explain things to you."

> "The device should do one thing. It should never be a distraction, a toy, or a general assistant."

> **Patient with developing readers:** A child may not know how to *pronounce* a word that is new on the page. She will approximate, spell phonetically, mix up **c/k** (or similar), skip silent letters, or chunk syllables oddly — and the microphone + STT will not always return a “dictionary clean” string. The product’s job is the **meaning** of the **word she intends**, not a perfect first utterance. Treat that as **success-seeking behavior**, not user error. See **Journey 5** for messy input and **cascading** recovery when the target is still unclear.

---

## 2. Current State

- **What works today:** Parents explain words verbally on request. General-purpose voice assistants can define words but use adult language and are unconstrained in what they respond to.
- **What's missing:** A device purpose-built for in-the-moment word explanation that is age-appropriate, voice-native, constrained to vocabulary only, and grows with the child.
- **Workarounds users rely on:** Child asks parent or skips the word entirely; parent looks up a dictionary or paraphrases; child forgets the word by the next day.

---

## 3. Proposed Solution

### Overview

Lexie is a small, clip-on physical bookmark that uses **WiFi** (it has no cellular radio). The child presses a single button, speaks a word or short phrase, and receives a spoken explanation within a few seconds. The bookmark is **single-purpose and low-ops** (and should stay physically **thin enough** to live on a book — not a claim that every BOM choice is “cheap”): it does not call OpenAI or the public internet by itself. It only talks to a **single configured Lexie backend** over **HTTPS** (the **orchestration** service you operate).

**Where “AI” runs:** The Lexie **server** (FastAPI) runs the pipeline: **OpenAI Whisper** (speech-to-text), **GPT-4o** (age-appropriate explanation, constraint guard), and **OpenAI TTS** (spoken response). Those are **cloud model APIs** — the important privacy/shape distinction is: the **device** is constrained to vocabulary requests only; the **orchestration host** holds credentials and enforces the contract. *This is not “all-local ML inference”* unless you later swap in self-hosted models.

**Connectivity (decided):**

- **At home:** The bookmark joins **home Wi‑Fi** and sends audio to the same **public base URL** as elsewhere (e.g. `https://lexie.example.com` on Fly.io, Railway, Render, or a small VPS). A **parent laptop** is for **development** (`uvicorn` locally), not the long-term way the family depends on the product being “on.”
- **Away (e.g. in the car, travel):** The child uses a **parent phone’s mobile hotspot**; the bookmark is again a WiFi client with a path to the internet, and still calls the **same HTTPS `POST /explain`**. No BLE on the data path for v1.

**Profiles:** The server stores **one `age_profile`** for this child. The parent updates it as the child grows. The system prompt is strictly scoped: refuse non–word-meaning requests, and the device firmware is hardcoded to call only the `/explain` endpoint.

### User Experience

The interaction has three surfaces:

- **The bookmark device** — the child's interface: one button, a speaker, an LED status light
- **The Lexie server** — FastAPI (and optional SQLite) deployed to a **small public host** you control; the parent edits the age profile through a **web admin** (authenticated). Local laptop only for **dev and testing** before deploy.
- **Phase 1 prototype** — a browser (or phone browser) that simulates push-to‑talk: record → `POST /explain` → play audio, to validate the pipeline and prompts before hardware

```
[Lexie Bookmark]
  ├── Button (press and hold to speak, release to send)
  ├── LED ring
  │     ├── Pulsing blue     — listening
  │     ├── Spinning teal    — thinking
  │     └── Solid teal-green — speaking (per decision log; match hardware / device design doc; avoid toy-like random colors)
  └── Speaker (small amplified output)
```

**Primary flow — word-only ask:**

1. Child encounters "sorcerer" in Harry Potter.
2. Child presses and holds the button. LED pulses blue.
3. Child says "sorcerer." Releases button.
4. LED spins teal while server processes.
5. Lexie speaks: *"A sorcerer is someone who can do magic — like Harry Potter! They learn spells and can make amazing things happen."*
6. LED returns to off. Child continues reading.

**Secondary flow — context-augmented ask:**

1. Child encounters "reluctant" in a sentence about Hermione.
2. Child presses and holds, says: "What does 'reluctant' mean when Hermione doesn't want to break the rules?"
3. Lexie speaks: *"Reluctant means you really don't want to do something, even if you might have to. Like when Hermione feels nervous about breaking rules — she's reluctant, which means she holds back because it doesn't feel right to her."*

> **Note:** The primary and secondary flows above use “clean” speech in documentation for readability. In real use, a **young reader** often does **not** know how to pronounce the new word first try; speech may be **messy** or **letter-by-letter**. That is **expected** — see **Journey 5** (approximate speech and **cascading** recovery).

### Scope

**In scope:**

- Single-word and short-phrase vocabulary explanations
- Optional context sentence from the child
- Age-adaptive explanation framing (controlled by server-side age profile)
- Push-to-talk button activation (Phase 1 and Phase 2)
- Audio response played back on device speaker
- Browser/phone prototype for Phase 1 validation
- Tolerate **noisy, approximate, or letter-by-letter** speech: the success metric is the **right explanation** of the child’s **intended** vocabulary target, not a perfect pronunciation or a spelling score on the first try
- **Cascading recovery** when the target headword is still **ambiguous** after the first utterance: **escalate** in order (see **Journey 5**) — infer and explain when confident; else a **brief** oral “A or B” meaning fork; else (only if still stuck) an **ask to spell letter-by-letter** for **disambiguation** (recovery, not the default path); then a **kind, bounded** exit with **no** endless reprompt loop. **Multi-PTT** parts are **Phase 1b**; **Phase 1** is **single-PTT** / **Level 0** (see **§6**, **Open Q9**). (Mechanism: **short-lived server session** or equivalent — **SPEC** / implementation.)
- **Parent web admin (one-pager):** one authenticated page to edit the **single** `age_profile`; **mobile-friendly** when possible (see **§5**)
- **First run (Phase 1):** documented path from **deploy** + **env** + **first successful** browser explain (see **§5**)
- **Error tone (technical):** child-facing **calm, non-technical** handling for transport/server/editing errors — **not** the same as Journey 5 recovery, but same **sibling** voice (see **§5**)

**Explicitly out of scope:**

- General question answering ("what is the biggest planet?") — Lexie is not a trivia assistant
- Storytelling, games, or entertainment — scope creep risk
- Wake word ("Hey Lexie") — deferred; always-on mic adds hardware and privacy complexity
- **Multiple child profiles** — **out of scope for this product** (single child, one `age_profile`). A generic “Phase 3+ multi-profile” idea may exist in the registry for other hypothetical products; it is not a commitment for Lexie as scoped here
- Parental content controls beyond the age profile — the constraint is architectural (system prompt)
- Reading aloud or page-scanning — Lexie responds to spoken queries only
- A full **phonics** or **structured reading-instruction** program as the **primary** product (optional headword TTS after meaning is **opt-in** via `LEXIE_HEADWORD_TTS=1`; default is **off**; still a **word-meaning** product, not a literacy curriculum)

---

## 4. User Journeys

### Journey 1: Simple Word Lookup

**Actor:** Child, reading alone

**Trigger:** Encounters an unknown word while reading

```
  ┌──────────────────────────────────────┐
  │  LEXIE BOOKMARK (clipped to page)    │
  │                                      │
  │   ●  [LED: OFF]                      │
  │                                      │
  │   ╔══════════╗                       │
  │   ║  BUTTON  ║  ← press and hold     │
  │   ╚══════════╝                       │
  │                                      │
  │   ▶  Speaker                         │
  └──────────────────────────────────────┘

  Child presses button → LED pulses blue
  Child speaks: "sorcerer"
  Child releases button
  LED spins teal (thinking)
  Speaker plays response
  LED off — done
```

**Step-by-step:**

1. Child spots "sorcerer" on the page.
2. Presses and holds the Lexie button. LED ring pulses blue — device is listening.
3. Says "sorcerer" clearly.
4. Releases the button. Audio recording is sent to the server over WiFi.
5. Server runs Whisper (speech-to-text), passes the word and age profile to GPT-4o.
6. GPT-4o returns an age-appropriate explanation. Server runs TTS and sends audio back.
7. Lexie plays the spoken explanation through its speaker.
8. LED returns to off. Total round-trip: approximately 3–5 seconds.

**Outcome:** Child hears a friendly, simple explanation and returns to reading immediately.

> **Design rationale:** Release-to-send (not press-to-send) is deliberate — it matches the natural rhythm of speaking and avoids cutting off the child mid-word.

---

### Journey 2: Context-Augmented Word Ask

**Actor:** Child, reading alone

**Trigger:** Encounters a word and wants to give context for a better explanation

**Step-by-step:**

1. Child encounters "reluctant" in a sentence about Hermione hesitating.
2. Presses and holds the button. Speaks: *"What does reluctant mean when Hermione doesn't want to break the rules?"*
3. Releases the button.
4. Server receives the transcript. GPT-4o uses the context (Hermione, rules) to anchor the explanation in something familiar.
5. Lexie responds with an explanation that references the exact scene or character.

**Outcome:** Child gets a richer, more memorable explanation because it is tied to the story she is already in.

---

### Journey 3: Out-of-Scope Request (Constraint Guard)

**Actor:** Child, curious about something beyond vocabulary

**Trigger:** Child asks a general question ("Lexie, what is Hogwarts?")

**Step-by-step:**

1. Child presses button and asks: *"What is Hogwarts?"*
2. Server receives transcript. GPT-4o system prompt detects this is not a vocabulary request.
3. Lexie responds gently: *"I'm your word helper! I can explain what words mean. Ask me what a word means and I'll tell you."*
4. Child is redirected without frustration.

**Outcome:** The constraint is enforced gracefully. The child is not scolded; Lexie simply redirects.

> **Design rationale:** The redirect response must be warm and non-dismissive. A cold "I can't answer that" risks the child losing trust in the device.

---

### Journey 4: Parent Updates Age Profile

**Actor:** Parent

**Trigger:** Child's birthday, or parent notices explanations are too simple

**UI:** The **one-pager** admin (see **§5 — Parent web admin**): one form, token auth, **mobile-friendly** when possible.

**Step-by-step:**

1. Parent navigates to the Lexie **admin** page on the **deployed** service (HTTPS), or `localhost` when developing locally.
2. Updates the age field (e.g., from 6 to 7) and optionally adjusts reading level descriptor ("advanced reader").
3. Saves. Server reloads the profile — no device restart needed.
4. Next explanation Lexie gives uses the updated framing.

**Outcome:** Lexie's explanations gradually grow with the child with zero hardware changes.

---

### Journey 5: Unfamiliar Pronunciation, Approximate Speech, and Cascading Disambiguation

**Actor:** Child, reading alone (often **early elementary**, including strong readers who still **decode out loud** poorly on first sight of a multisyllabic word)

**Trigger:** She sees a word on the page she **does not know how to say**, not only what it **means**. She still uses Lexie as her **word helper**: press-and-hold, speak **something** about that word, release.

**What actually happens (real speech):**

- She may **guess** pronunciation and **stress the wrong syllable**, so Whisper writes a **different string** than the printed word.
- She may **spell it phonetically** (“s-o-r-c…” / “sor-ser-er”) with **c/k** swaps, **silent letters** omitted or voiced oddly, or **chunks** in the wrong place.
- She may combine this with **Journey 2**-style context in the **same** hold (“the boy who does magic in the book — what does that word mean?”) while **mispronouncing** the headword — context should be used to **skip** unnecessary recovery turns when possible.

**Phase 1 vs full cascade (decided):** The **first shipped** server + browser prototype implements **one** `POST /explain` per button press: **Level 0** only — **infer** the best vocabulary target from a **noisy** transcript (and **same-utterance** context when the child provides it) and return **one** explanation audio, plus the **constraint guard** and error handling in the **SPEC**. **Levels 1–3** (oral fork, spell-for-disambiguation, kind stop across **multiple** PTTs) require **session** (or equivalent) and **clarification** TTS; they are **Phase 1b** (follow-on), not blocking the Phase 1 MVP. **Journey 5** remains **must-have** for the **product**; it is **phased**, not removed.

**Cascading recovery (product-owned order — escalate only if the previous step did not yield a confident target):**

| Level | When | What Lexie does |
|-------|------|------------------|
| **0 — Infer first** | Transcript + optional **same-utterance** story context + age profile support **one** likely vocabulary target | **Explain** that word. **Do not** open with “spell it” when a reasonable inference exists (including common typos / near-miss spellings of one lemma). |
| **1 — Light oral fork** | Model is stuck between a **small** set of **different words** (often **homophones** or clear alternates) | One **short, warm** meaning fork: e.g. “Do you mean the **night**-time word, or the **knight** with a sword?” **Not** a spelling quiz. |
| **2 — Spell for disambiguation (recovery)** | Level 1 **does not apply** (e.g. muddled audio, or two heads still plausible) **or** Level 1 did not resolve | Ask her to say the **letters** **one by one** (or “the letters you see on the page”) so Lexie can match the **printed** headword. Frame it as **helping you see the same word** — *“That helps me know which word you mean.”* **No** shaming for c/k or silent letters. |
| **3 — Kind stop** | After the **locked recovery cap** (below) is reached without a confident target | Fixed, short encouragement: try again in a moment, or **ask a grown-up to say the word once** — **no** infinite reprompt loop. |

**Locked recovery cap (product — Phase 1b):** In one **recovery session**, the child may receive **at most** **one** Level **1** clarification (the oral A/B fork **and** the **single** PTT in which they answer it) and **at most** **one** Level **2** clarification (the spell request **and** the **single** PTT in which they say letters). There is **no** third recovery prompt: if the word is still not identified, go straight to **Level 3** (kind stop). **Worst-case PTTs:** **1** initial + **1** (fork path) + **1** (spell path) = **3** PTTs before a mandatory **Level 3** exit; many flows end earlier (e.g. **2** PTTs when the fork or spell alone succeeds).

**Multi-turn expectation:** A cascade is usually **more than one** button press: first PTT (messy ask) → optional second PTT (answer to fork **or** letter string) → explanation or exit. Whether the server uses a **short-lived session**, a **turn counter**, or **client hints** is **implementation** (see **SPEC**); the PRD now **locks** the **maximum** depth above.

**Concrete example (homophone fork → meaning):**

- Printed: **knight**. She says something closer to “night.” Whisper may transcribe **“night.”** Level 0 is **not** confident between two real words.
- Level 1: Lexie asks the **night / knight** fork; she answers the second.
- Lexie gives the **knight** explanation in age-appropriate language.

**Concrete example (spell step for headword lock):**

- Printed: **knight** again, but she is **too unsure** to pick the fork confidently, or audio is noisy. After Level 1 **fails** or is **skipped** as not applicable, Level 2: *“Can you tell me the letters one by one, like you see in the book?”* She says *“K — N — I — G — H — T.”* That **spelling** signal locks the lemma; Lexie explains **knight** (and does not treat her as “wrong” for how she said it out loud first).

**Outcome:** She gets **meaning** for the word on the page even when her **first** utterance is not dictionary-perfect — with **at most** a few clear recovery steps, never a **classroom test** tone.

> **Design rationale:** Asking a six-year-old to “say it clearly first” is the wrong default; she is already doing the right thing by **engaging** with a hard word. **Spelling** is a **recovery tool** for **disambiguation**, not the opening move. **Journey 2** context in the first hold reduces how often Level 1–2 are needed.

### Journey Priority Summary

| # | Journey | Priority |
|---|---------|----------|
| 1 | Simple word lookup | Must-have |
| 2 | Context-augmented ask | Must-have |
| 3 | Out-of-scope constraint guard | Must-have |
| 4 | Parent updates age profile | Must-have |
| 5 | Unfamiliar pronunciation, approximate speech, cascading disambiguation | Must-have |

---

## 5. Technical Considerations

### Entity Shape

```
age_profile
  id                    UUID          PK
  child_name            TEXT          NOT NULL
  age_years             INTEGER       NOT NULL — drives explanation framing
  reading_level         TEXT          NOT NULL — e.g., "advanced for age", "grade-level"
  explanation_style     TEXT          NULLABLE — override hints for system prompt
  created_at            TIMESTAMPTZ   NOT NULL
  updated_at            TIMESTAMPTZ   NOT NULL

explain_request (log, not queried in real-time)
  id                    UUID          PK
  profile_id            UUID          FK → age_profile
  raw_transcript        TEXT          NOT NULL — what Whisper heard
  word_or_phrase        TEXT          NOT NULL — extracted target
  context_text          TEXT          NULLABLE — additional context child provided
  response_text         TEXT          NOT NULL — GPT-4o explanation
  latency_ms            INTEGER       NOT NULL — end-to-end round trip
  created_at            TIMESTAMPTZ   NOT NULL
```

### API Shape

```
POST   /explain           — receive audio (multipart) → return audio (MP3/WAV)
GET    /profile           — get current age profile
PATCH  /profile           — update age profile (parent only; auth TBD in SPEC, e.g. token or password on HTTPS)
GET    /health            — liveness check for device on startup
```

The device calls only `POST /explain` and `GET /health`. The profile endpoints are for the **parent admin** (browser) only, not exposed through device firmware. **Optional (SPEC):** `GET /admin/usage` for rough monthly explain count and cost **estimate** (OpenAI is the billing source of truth).

### Parent web admin (one-pager)

A **single** parent-facing page served by the same FastAPI app (no separate “portal” product in v1). **Purpose:** edit the one **`age_profile`**; **not** a dashboard for the child.

| Property | PRD rule |
|----------|----------|
| **Auth** | `LEXIE_ADMIN_TOKEN` (bearer or header as in **SPEC**) — not shared with the child or the bookmark **device** key. |
| **Content** | One form: **child’s first name or nickname** (`child_name`), **age in years** (`age_years`), **reading level** (short free text, e.g. “advanced for age”, “grade-level”), **optional** `explanation_style` (hints for the system prompt). All fields map to the `age_profile` **entity shape** in this PRD. |
| **Layout** | **Single column**, minimal chrome — engineering UI is fine. **Mobile-friendly (should):** usable on a **phone browser** (parent on the couch); tap targets and text large enough to read without zoom. No multi-step wizard required for v1. |
| **Save** | **PATCH**-style update (partial OK); show **clear success** (“Saved” / “Profile updated”) and surface **auth errors** plainly to the parent only. |
| **Out of scope for v1** | Per-child analytics charts, log viewers, or billing (parent uses **OpenAI** dashboard + optional **lexie-ops** for `GET /health`). |

Journey 4 (parent updates age profile) **uses** this page after deploy; the **order of operations** for a brand-new install is in **First run (Phase 1 — family / builder)** above.

### First run (Phase 1 — family / builder)

**Goal:** A **repeatable** sequence from “empty repo / fresh host” to **first successful** explain in the **browser** prototype, without the child in the loop until the parent is ready.

1. **Provision host** — public **HTTPS** `BASE_URL` (PaaS or small VPS) with TLS; **min machines = 1** (or equivalent) to avoid cold-start surprises (**SPEC**).  
2. **Secrets** — set server env: **`OPENAI_API_KEY`**, **`LEXIE_DEVICE_KEY`**, **`LEXIE_ADMIN_TOKEN`**, and defaults for **`LEXIE_LOG_REQUESTS=0`**, **`LEXIE_HEADWORD_TTS=0`** (and **CORS** for local prototype if needed) per **SPEC**. **Never** commit keys to git.  
3. **Age profile** — **seed** one `age_profile` row (migration or one-off script) **or** complete the **admin** form once deploy is up, so `GET /profile` returns data before the first child test.  
4. **Verify** — `GET /health` returns **200** from the public URL (and, if possible, from a **phone on cellular** or **laptop on hotspot** to approximate “not only home WiFi” later).  
5. **Browser prototype** — point the Phase 1 page at `BASE_URL`; configure the **device key** the app sends on `POST /explain` to match `LEXIE_DEVICE_KEY`.  
6. **First explain** — parent (or child, when ready) does **one** PTT: single word + hear explanation → **“done”** for first-run.

**Optional but valuable:** one successful `POST /explain` on **parent hotspot** (same `BASE_URL`) to match the “away” story in the connectivity section — can be a **checklist** item, not a gate to calling Phase 1 complete.

### Child-facing error tone (technical / transport failures, not Journey 5 recovery)

Separate from **Journey 5** (ambiguous word / spell recovery). This covers: **no network**, **server 5xx**, **timeout**, **rate limit**, **empty or too-short** audio, **unauthorized** device key, etc.

| Principle | PRD rule |
|----------|----------|
| **Voice** | **Same** family as Lexie: **calm, short, one idea** — a patient **older sibling**, not a sysadmin. **No** HTTP status codes, **no** “stack trace” language, **no** scary or blaming tone toward the child. |
| **Channel** | Where the product speaks: **TTS** or fixed spoken line when the stack supports it; otherwise the **browser prototype** may use on-screen text **in addition to** a simple spoken line. Exact strings and JSON bodies are **SPEC**; the PRD only locks **tone** and that errors must **not** be a wall of raw JSON to the child. |
| **What to say** | Prefer **one** line: e.g. try again in a moment, check the WiFi, or ask a grown-up — **parallel spirit** to Level 3 in Journey 5 (kind stop), but triggered by **infrastructure** failure, not “we don’t know the word yet.” |
| **Parent** | The **ops** / admin path can show more detail to the **adult** (health check, deploy logs) — not read aloud to the child. |

### Integration Notes

- **Speech-to-text:** OpenAI Whisper API — accepts raw audio bytes, returns transcript
- **Word explanation:** OpenAI GPT-4o — system prompt enforces: explain like the child's age, use familiar examples, refuse non-vocabulary requests
- **Text-to-speech:** OpenAI TTS API — returns MP3 audio streamed back to device
- **Server framework:** Python FastAPI — lightweight, async; **deployed** to a small PaaS/VPS with TLS
- **Device transport:** **HTTPS** to the configured `BASE_URL` from **any** WiFi that provides internet (home AP or parent **mobile hotspot**). The bookmark has no direct route to OpenAI; only the Lexie server does.
- **Auth:** Device uses a pre-shared API key in firmware; server key in **host environment** (never in repo). Admin UI uses separate auth in SPEC.

### Cost, usage, and monitoring (single family)

- **Cost drivers:** For realistic single-child use, **OpenAI API** (Whisper + chat + TTS) usually **dominates**; hosting is a **small fixed** monthly (e.g. a single small Fly/Railway/Render instance or tiny VPS) until you resize for CPU/RAM.
- **Assumptions to validate with logs:** Onboarding may see **tens of explains on heavy days**; steady use might be on the order of **~10–35 explains per day** with **bursts** higher; the SPEC can define **soft caps** and **rate limits** to protect budget and API tiers.
- **Default logging (locked):** **Off** on fresh deploy — **no** server-side persistence of **transcript** or **explanation text** for tuning until the parent **opts in** (e.g. `LEXIE_LOG_REQUESTS=1`; see **SPEC**). Rationale: **privacy-first** for a child’s voice path; logging is for **adult tuning**, not the default. **No raw audio** in either mode. **OpenAI billing alerts**; optional host CPU/RAM metrics. **No** multi-tenant or “scale to many customers” monitoring — this deployment is for **one child**. When enabled, per-request `latency_ms` and success/fail in logs per **SPEC** retention.

**Local parent “ops” app (optional, in product scope for the parent only):** A small **separate** application that runs on the **parent’s computer** (e.g. a local Vite page, a Tauri window, or a short script) and **polls** the deployed Lexie **HTTP** APIs for status. It is **not** part of the child’s reading flow. Intended use:

- **What it calls at minimum:** `GET /health` (liveness, optional build/version). **Later:** `GET /admin/usage` or a compact JSON **metrics** route if the SPEC adds one (e.g. rolling explain count, last error).
- **Configuration:** `BASE_URL` and **admin** credentials (token or session) via environment or local config — **never** committed to git.
- **CORS / browser:** A dev UI on `http://localhost` calling `https://…` may require **CORS allowlist** for local origin on the FastAPI app and/or a **dev proxy**; the SPEC will define the supported pattern.
- **What it does *not* replace:** **OpenAI** usage and billing remain the **authoritative** view of model cost; the ops app is a **convenience** for “is the service up?” and quick **server-side** rollups, not a second billing system.
- **Priority:** **After** the core server is deployed and `/health` is real; does **not** block Phase 1 delivery of the explain pipeline or the browser PTT prototype.

### System Prompt Design (AI Constraint Layer)

The GPT-4o system prompt encodes the following **base** constraints. Full wording and tool-specific parameters live in implementation; these **intents** must be reflected in the live prompt and in any **recovery** or **clarification** TTS the server emits on follow-up turns.

```
You are Lexie, a friendly word helper for a child.
Your ONLY job is to explain what a word or short phrase means.
The child is currently {age_years} years old and is a {reading_level} reader.
Always use simple, warm, friendly language.
Use one or two examples from things a child this age would know.
If the child gives you context (a sentence or scene), use it in your explanation.
If the request is NOT asking for a word meaning, respond ONLY with:
  "I'm your word helper! I can explain what words mean. Ask me what a word means and I'll tell you."
Never answer general knowledge questions, tell stories, or do anything except explain words.
Keep your explanation to 2–4 sentences.
```

**Additional prompt intents (noisy input, disambiguation, cascade):**

- Treat the Whisper **transcript** as a **noisy hint** at the word on the page. Prefer **vocabulary** interpretation. When the same utterance includes **story context** (Journey 2), use it to **disambiguate** and to **reduce** extra turns.
- If one **clear** best candidate exists (including common misspellings or near-misses of a single word), **explain** it — do **not** ask the child to spell or “say it again” as a default.
- **Cascading recovery (escalation on low confidence or true ambiguity):** follow the **order in Journey 5** — (0) explain when confident; (1) **one** short **oral** “A or B” **meaning** fork for two plausible **different** words; (2) only if still stuck, a **request to spell letter-by-letter** to lock the **printed** headword (*never* a school-test tone); (3) after a **capped** number of steps, a **brief, kind** exit. **Orchestrated** recovery may require **separate** clarification audio on a **subsequent** `POST /explain` (or equivalent) — see **SPEC** for session / turn handling.
- **Headword TTS (optional, default off):** **Default (locked):** the spoken response is **explanation (meaning) only** — no separate pronunciation pass — to keep **TTS cost** and **latency** down. The parent may **opt in** via server config (`LEXIE_HEADWORD_TTS=1` in the **SPEC**) to append a short TTS of the **target headword** after the meaning, as a light pronunciation anchor (still not a **phonics** tutor). See **decision log** and **§8**.
- **Tone:** Never shame. Missed c/k or silent letters are **normal**; recovery language should sound like a **helpful older sibling**, not a correction.

---

## 6. Phases

### Phase 1: Server + Prototype (Target: April–May 2026)

- FastAPI server: **Whisper + GPT-4o + TTS** pipeline, age profile in **SQLite** (or similar), **web admin** for the parent
- **Deploy** to a small **public HTTPS** host (e.g. Fly.io, Railway, Render, or a tiny VPS) so the **same** backend works on **home WiFi** and on a **parent hotspot** — *not* “laptop must be on” for the family
- **Develop** on a laptop with `uvicorn` / `.env` locally; **production** is the deployed URL
- Browser (or phone browser) **prototype** UI: press / hold / release → record → play response
- Validate prompt quality, **constraint** guard, latency, and **budget-friendly** limits (max audio length, optional rate limits)
- **Journey 5 (Phase 1 slice):** **Single-turn** path only — **Level 0** “infer and explain” from **messy** audio; **no** server-side **multi-PTT** recovery **session** in this ship (see **Open Q9**, **decision log**)

**Explicitly not in the Phase 1 MVP cut** (deferred to **Phase 1b**): **Journey 5** **Levels 1–3** — oral disambiguation fork, letter-by-letter spell recovery, and bounded “try again / ask a grown-up” **across** multiple `POST /explain` calls, which need **short-lived session** (or turn tracking) in the **SPEC**.

**Phase 1 acceptance (ship bar for the family, before Phase 1b or hardware):** All should be true on the **deployed** public host (not only on a dev laptop that must stay on):

- [ ] **`GET /health`:** **200** from the internet-facing `BASE_URL` (and documented how a parent re-checks).  
- [ ] **Secrets:** `OPENAI_API_KEY`, `LEXIE_DEVICE_KEY`, `LEXIE_ADMIN_TOKEN` set on the host; **defaults** `LEXIE_LOG_REQUESTS=0`, `LEXIE_HEADWORD_TTS=0` (see **SPEC** / decision log).  
- [ ] **One `age_profile`:** Present and editable via the **parent admin** one-pager; **GET/PATCH** behavior matches **SPEC**.  
- [ ] **Browser PTT:** Press/hold/release → `POST /explain` → **audible** explanation; **one** end-to-end success with a real OpenAI path (not only mocked).  
- [ ] **Journeys 1–2** (happy: word + context) and **Journey 3** (out-of-scope redirect) **exercise** the pipeline; **Journey 5** **Level 0** in behavior (messy/approximate utterance still yields a **reasonable** explanation in **one** turn) — not yet multi-turn recovery.  
- [ ] **Child-facing error tone (§5):** When something fails, the experience matches the **error tone** principles (calm, non-technical, no “debug dump” to the child) — even if the prototype uses on-screen text until TTS of errors is implemented.  
- [ ] **First run:** A **new** follow can repeat **First run (Phase 1)** steps 1–6 and get to a **first successful** explain.  
- [ ] **(Optional / stretch):** `GET /health` or one explain path verified from a **parent hotspot** (same `BASE_URL`) to align with the **connectivity** story.  
- [ ] **SPEC definition of done** (tests, CORS, **lexie-ops** if in scope) — see [lexie-word-explainer.SPEC.md](../committed-to-build/lexie-word-explainer.SPEC.md) §11.

### Phase 1b: Journey 5 multi-turn recovery (follow-on to Phase 1 MVP)

- **Target:** Full **Journey 5** **cascade** after Phase 1 is stable: **Levels 1–3** as in §4, with **clarification** TTS and a **next** PTT carrying the child’s answer or spelling
- **Mechanism:** **Short-lived session**, turn counter, or equivalent — **defined in** [lexie-word-explainer.SPEC.md](../committed-to-build/lexie-word-explainer.SPEC.md) (and API changes if any); not a second product, the same `BASE_URL` and family deployment

### Phase 2: Physical Device (Target: TBD)

> Hardware platform decision needed first — see Open Questions.

- Device firmware (MicroPython on ESP32-S3 or Python on Pi Zero 2W)
- I2S MEMS microphone integration
- I2S amplified speaker integration
- Single button with LED ring
- Battery + USB-C charging
- Pre-shared API key flashed to device at setup
- Physical bookmark enclosure design

### Phase 3: Hardening + Extras (Future, optional)

> The **orchestration server** is **already** hosted in Phase 1; Phase 3 is not “first time on the internet.”

- OTA (over-the-air) **firmware** update support
- Wake word ("Hey Lexie") as an alternative to push-to‑talk (hardware and privacy implications)
- Deeper **observability** (e.g. error tracking) if needed
- **Multi-child profiles** and **commercial multi-tenancy** remain **out of scope** for the single-family product described in this PRD

---

## 7. Relationship to Other Features

| Feature | Relationship |
|---------|----------------|
| **LX-2 — Context-Aware Explanation** | Extends LX-1; the server API and prompt already accommodate context text, so LX-2 is a refinement of the prompt and UX guidance, not a new system |
| **LX-3 — Age Profile Management** | Provides the profile that LX-1 depends on; Phase 1 implements a minimal version of LX-3 as part of this feature |
| **LX-4 — Physical Device Firmware** | Consumes the LX-1 server API; device and server are developed in parallel in Phase 2 |
| **LX-5 — Wake Word Activation** | Deferred to Phase 2; requires always-on microphone which has hardware and privacy implications |
| **LX-6 — Hosted Server** | **Superseded in practice** — the production server is **public HTTPS from Phase 1**; any “LX-6” doc is legacy naming for optional future platform hardening, not a separate migration step |

---

## 8. Open Questions

| # | Question | Options | Recommendation |
|---|----------|---------|----------------|
| 1 | **Hardware platform for device firmware** | (A) ESP32-S3: smaller, cheaper (~$5–10 BOM), I2S native, MicroPython or C++, tight memory constraints for audio buffering. (B) Raspberry Pi Zero 2W: runs Linux, easier to develop and debug, supports Python natively, ~$15 + USB audio hat, slightly bulkier. | Start with Pi Zero 2W for Phase 2 development (easier iteration); consider ESP32-S3 for a final production-style build if size matters. |
| 2 | **Audio format between device and server** | (A) Raw PCM streamed over HTTP. (B) Opus or MP3 compressed audio to reduce WiFi payload. | Start with raw PCM / WAV for simplicity in Phase 1 prototype; evaluate compression in Phase 2 if latency is an issue. |
| 3 | **Age profile update mechanism** | (A) Parent edits a JSON file manually. (B) Simple web admin page served by FastAPI. | Build the web admin page — editing JSON is error-prone and not parent-friendly. |
| 4 | **Latency target** | What is an acceptable round-trip from button release to first audio byte? | Target **≤ 5 s p95** end-to-end for the **deployed** service + OpenAI path; **avoid cold starts** on the host (one warm small instance for a single family is usually enough). |
| 5 | **Logging and privacy** (decided) | Off by default vs opt-in | **Default off (locked):** no transcript/response persistence. Parent **opts in** (`LEXIE_LOG_REQUESTS=1`, **SPEC**) for tuning. **No raw audio** in either case. Retention in **SPEC**. |
| 6 | **PaaS choice** | Fly vs Railway vs Render vs small VPS? | Pick by **TTL ops comfort**: trial deploy with Dockerfile; set **monthly** OpenAI and host **budget** alerts. |
| 7 | **WiFi provisioning (Phase 2 device)** | How are home + hotspot SSIDs and `BASE_URL` stored on the bookmark? | **TBD in hardware SPEC** (e.g. SoftAP, companion BLE for setup, USB); at least **two** saved networks are a likely requirement. |
| 8 | **Headword TTS?** (speak the target word once after the meaning) (decided) | **Off** default, opt-in to on / always on | **Off (locked).** `LEXIE_HEADWORD_TTS=1` enables append headword TTS (see **SPEC**). |
| 9 | **Cascading recovery and transport** (decided) | (A) **Phase 1** = stateless **single** `POST /explain` per PTT; **Level 0** inference only. (B) **Multi-turn** cascade = **short-lived session** (or turn counter) for Levels 1–3. | **Option A** for **Phase 1** MVP; **Option B** in **Phase 1b**. **Journey 5** is **phased** — see **§6** and **decision log**. **SPEC** will define session shape for **1b**. |

---

## 9. Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-08 | Project name: Lexie | Short, friendly, memorable for a child; derived from "lexicon" |
| 2026-04-08 | Primary activation: push-to-talk button; wake word deferred to Phase 2 | Push-to-talk avoids always-on microphone (simpler hardware, better privacy); wake word added once physical form factor is validated |
| 2026-04-08 | Server stack: Python FastAPI | Lightweight, async, easy to run locally, good OpenAI SDK support |
| 2026-04-08 | AI stack: OpenAI Whisper + GPT-4o + TTS | End-to-end OpenAI keeps the integration simple for Phase 1; can swap individual components later |
| 2026-04-08 | Scope constraint: device firmware hardcoded to /explain only | Prevents device from being repurposed; architectural enforcement is stronger than policy enforcement |
| 2026-04-22 | **Production backend = public HTTPS host** (e.g. Fly, Railway, Render, VPS) | Home + **parent mobile hotspot** both use the same `BASE_URL`; laptop is dev-only, not the reliability model |
| 2026-04-22 | **Orchestration vs inference** | Lexie **server** orchestrates; **OpenAI** runs STT/LLM/TTS — not “all local AI on a home PC” for this product |
| 2026-04-22 | **Scope: one child, one family** | Single `age_profile`; no multi-tenant or multi-child requirement for this project |
| 2026-04-22 | **Cost / monitoring** | Single-family: OpenAI **billing alerts**, optional per-request and daily **metrics** in app; no horizontal “scale to many customers” work |
| 2026-04-22 | **LED “speaking”** | Prefer **solid teal-green**; align with hardware / UX spec (avoid mixed green vs teal in docs) |
| 2026-04-22 | **Local parent ops app** | Optional local **only** app (not child-facing) that **polls** Lexie `GET /health` and future admin/metrics endpoints; CORS/proxy in SPEC; OpenAI billing remains cost source of truth |
| 2026-04-22 | **Unfamiliar pronunciation & cascading recovery (Journey 5)** | Young readers may mispronounce or spell phonetically; product **infers** meaning first, then **escalates**: brief oral fork → **spell letter-by-letter** for disambiguation (recovery, not default) → **bounded** kind exit. Optional **headword TTS** after meaning remains a separate gate. |
| 2026-04-22 | **Open Q9 — Phase 1 vs full Journey 5 (Option A)** | **Phase 1 MVP** ships **single-turn** `POST /explain` only: **Level 0** best-effort inference + **one** explanation audio, **constraint guard**, and SPEC error paths — **no** server **session** for multi-PTT recovery. **Journey 5** **Levels 1–3** (oral fork, spell step, kind stop) ship in **Phase 1b** with **session** (or equivalent) in the **SPEC**. The full **Journey 5** design stays **must-have** for the product; delivery is **phased** to unblock the core pipeline first. |
| 2026-04-22 | **Recovery cap (Journey 5, Phase 1b)** | **At most one** Level 1 oral-fork **episode** and **at most one** Level 2 spell **episode** per session after the **initial** ask; then **Level 3** is mandatory. **No** third recovery round. **Worst case:** **3** child PTTs on the bookmark/browser before a forced **kind** exit. |
| 2026-04-22 | **Default logging = off (opt-in)** | `LEXIE_LOG_REQUESTS` defaults to **0**: no **transcript** or **explanation** persistence. Parent **opts in** to `1` for tuning. **Privacy-first** for a child. **No raw audio** in either case. |
| 2026-04-22 | **Headword TTS = off (opt-in)** | `LEXIE_HEADWORD_TTS` defaults to **0**: TTS is **explanation (meaning) only**. Parent may set `1` to add a short pronunciation pass after the meaning. **Cost and latency** favor default off. |
| 2026-04-22 | **Admin one-pager, first-run, error tone, Phase 1 acceptance** | **Admin:** single FastAPI-served form for `age_profile`, **mobile-friendly** when possible, no child analytics in v1. **First run:** ordered steps from host + secrets + profile + `GET /health` + browser PTT to **first** explain. **Error tone:** technical failures use **calm, one-idea** lines — no stack-speak to the child. **Acceptance:** checklist in **§6** (deployed `BASE_URL`, journeys 1–3 + Level 0, error tone, repeatable first run, **SPEC** §11). |
