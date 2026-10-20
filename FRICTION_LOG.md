# SPOTLIGHT: Hackathon Friction Log

> **Amazon "Build, Ship, Shape" Hackathon — Fire TV Track**  
> *Detailed log of authentic technical friction, platform edge cases, and design trade-offs encountered while building SPOTLIGHT.*

---

## 1. Executive Summary

Building an ambient curiosity remote for television presents unique challenges that differ sharply from traditional web and mobile apps:
1. **The 10-Foot UI Constraint:** Typography and contrast must be immediately legible from across a living room without visual clutter.
2. **Sub-Second Feedback Expectation:** Pausing live TV creates immediate viewer tension; any delay between tap and visual feedback feels broken.
3. **Multi-Screen Synchronization:** Bridging a handheld phone remote to a TV display over disparate local network environments requires resilient, reconnectable event pipelines.

---

## 2. Technical Friction & Discoveries

### Friction Item 1: Starlette 1.9.0 / FastAPI 0.156 `TemplateResponse` Signature Evolution
* **What Happened:** When rendering HTML pages via `templates.TemplateResponse("index.html", {"request": request, ...})`, tests threw `TypeError: unhashable type: 'dict'` inside Jinja2's `_load_template` cache.
* **Root Cause:** In modern Starlette 1.9.0+, `TemplateResponse` changed parameter conventions: the first parameter is `request: Request`. Passing the template name as the first positional argument caused Starlette to treat the dictionary context as the cache key `name`, crashing Jinja2's hashing.
* **Resolution:** Standardized all template responses on explicit keyword arguments:
  ```python
  templates.TemplateResponse(
      request=request,
      name="index.html",
      context={"scenes": config.SCENES, "beats": config.ORDERED_BEATS}
  )
  ```
* **Lesson Learned:** Always pass `request` as an explicit keyword argument when working with Starlette/FastAPI template engines.

---

### Friction Item 2: LLM Latency Mismatch for Television Overlays
* **What Happened:** Initial experiments running local LLMs (`llama3.2:3b` via Ollama) or cloud providers demonstrated typical generation latencies between 1,200ms and 3,500ms. On a paused TV screen, a blank or frozen screen with no immediate state transition makes viewers think the app crashed or the Wi-Fi dropped.
* **Root Cause:** Large language models produce rich text, but live TV viewers require immediate (<200ms) confirmation that their button press registered.
* **Resolution:** Implemented a two-phase state machine:
  1. **Phase 1 (<50ms):** The TV screen freezes instantly, and an "ANALYZING SCENE & QUESTION" telemetry HUD activates.
  2. **Phase 2 (Sub-100ms for Curated Beats / ~1.5s for Fallback):** Curated answers resolve immediately via zero-latency regex matchers, while free-form questions stream into the active overlay container.
* **Takeaway:** Decoupling *acknowledgment of curiosity* from *knowledge resolution* is essential for living room UX.

---

### Friction Item 3: Fire TV 10-Foot UI vs Standard Web Typography
* **What Happened:** Standard web typography (14px–18px body font with multi-card grid layouts) looked fine on a desktop browser, but when viewed on a 55-inch television screen from 10 feet away, it was illegible and cluttered ("card soup").
* **Root Cause:** Web design patterns optimize for close-up mouse/finger interaction. Television requires 10-foot UI standards: high-contrast dark backgrounds, 36px+ titles, 24px+ body explanations, and minimal secondary noise.
* **Resolution:**
  - Removed all card grids and unnecessary buttons from the TV view.
  - Upgraded explanation typography to 1.55rem (25px) with deep black backgrounds (`#08090c`) and vivid contrast accents.
  - Eliminated all emoji in favor of industrial status pills (`[VERIFIED TRUE]`, `[IFAB LAW 12]`, `[ROGUE ASSET ALERT]`).
  - Restricted the answer layout to a bottom-anchored cinematic HUD that leaves the upper broadcast scene visible in a desaturated, frozen state.

---

### Friction Item 4: Multi-Device WebSocket Flakiness & Network Drops
* **What Happened:** In real-world living rooms, smartphones frequently sleep their screens or switch between Wi-Fi bands (2.4 GHz vs 5 GHz), causing WebSockets to disconnect silently.
* **Root Cause:** Relying solely on a persistent WebSocket connection meant that if the phone slept, tapping "Ask" upon wake-up could fail silently or lag.
* **Resolution:**
  - Designed the system with **REST as the source of truth** (`POST /api/ask`) and **WebSockets as the real-time event accelerator** (`/ws`).
  - Added auto-reconnect backoff on both the TV client and Phone Remote.
  - Added background polling synchronization fallback (every 2.5s) on the TV client to ensure state reconciliation even if a WebSocket packet drops.

---

### Friction Item 5: Neutrality & Safety in News Fact-Checking
* **What Happened:** When designing Beat 4 (News Fact-Check), choosing political or current-affairs claims risked introducing bias, hallucination, or controversial friction into the demo.
* **Root Cause:** Broadcast news contains subjective commentary and polarizing debates where algorithmic fact-checks often lack consensus.
* **Resolution:**
  - Explicitly constrained Beat 4 to a neutral, verifiable scientific historical milestone: *"Did the Apollo 11 moon landing happen?"*
  - Curated two unimpeachable primary sources (NASA Lunar Surface Journal and Smithsonian National Air and Space Museum catalog accession data).
  - Built prompt guardrails into the LLM system prompt enforcing non-partisan, neutral objectivity.

---

## 3. Summary of Key Decisions

| Friction Point | Alternative Considered | Final Choice | Outcome |
| :--- | :--- | :--- | :--- |
| **Input Mechanism** | Voice-only remote | One Big Button on Mobile + Editable Text | Zero voice recognition errors; 100% demo reliability. |
| **TV Scene Assets** | Heavy MP4 video files | Pure CSS & SVG simulated scenes | Zero external bandwidth dependencies; instant load; no copyright issues. |
| **Answer Resolution** | Pure LLM generation | Curated Canonical (<100ms) + LLM Fallback | Sub-100ms instant demo speed with free-form AI capability. |
| **Visual Aesthetics** | Generic blue tech theme | Dark carbon cinema palette with beat accents | Premium, broadcast-grade aesthetic fit for Fire TV. |
