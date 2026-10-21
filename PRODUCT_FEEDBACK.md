# SPOTLIGHT — Product Feedback

Feedback on every tool, API, and SDK used. Submitted for the Amazon "Build, Ship, Shape"
hackathon (Fire TV track). Sent to the teams building these tools.

## Fire TV developer documentation & simulator
- **Used for:** Targeting the Fire TV track; 10-foot UI design; deploy path.
- **What worked:** The track rules were unusually clear — "any framework works, demo must show it running
  on a device or simulator" removed a whole class of uncertainty. Priority categories (AI-enhanced viewing,
  sports, family entertainment, multi-modal UX, computer vision) gave the idea a concrete shape.
- **Needs work:** No single happy path for web-technology apps → simulator (see F-01). Fire App Builder assumes
  Android; the web story feels like a second-class citizen despite being explicitly allowed.
- **Onboarding:** 6/10 — clear on *what* to build, murky on *how to run it* without a physical device.
- **Build with it again?** Yes — the track design itself is excellent; the docs need the web path.

## AWS Bedrock (planned provider)
- **Used for:** Primary LLM provider (text + vision) with graceful fallback chain.
- **What worked:** The boto3 credential-chain convention made the integration code clean; model IDs are
  well documented.
- **Needs work:** Could not test live without credentials in the sandbox (see F-03).
- **Onboarding:** 7/10 for the docs; 4/10 for the sandbox experience.
- **Build with it again?** Yes — Nova's price/performance for vision tasks is the reason it's first in the chain.

## Google Fact Check Explorer API
- **Used for:** Live verdicts on the news beat.
- **What worked:** Simple REST shape; claim-review structured data is exactly what a fact-check overlay needs.
- **Needs work:** Key provisioning is a multi-step Cloud Console flow for what is essentially a read-only lookup.
- **Onboarding:** 6/10.
- **Build with it again?** Yes.

## Web Speech API (browser)
- **Used for:** Voice input on the phone remote.
- **What worked:** Zero-dependency voice input; surprisingly good accuracy for short questions.
- **Needs work:** Secure-context requirement silently kills it on plain-HTTP LAN demos (see F-06); no
  built-in signal for "unavailable due to context" vs "unavailable due to browser."
- **Onboarding:** 7/10.
- **Build with it again?** Yes, with the feature-detection guard we shipped.

## Ollama (local LLM runtime)
- **Used for:** Offline LLM fallback (llama3.2:3b) for free-form questions.
- **What worked:** `ollama run` simplicity; good enough for short explanatory answers; zero cost, zero keys.
- **Needs work:** First-token latency on CPU-only machines makes it a poor *demo* path — fine as a fallback,
  not as the hero.
- **Onboarding:** 9/10.
- **Build with it again?** Absolutely — the reason the demo works on a plane.

## FastAPI + vanilla JS
- **Used for:** Backend and the TV/remote frontends.
- **What worked:** FastAPI's Pydantic validation caught three API contract bugs before they reached the UI.
  Vanilla JS kept the TV frontend under control with zero build step — a real advantage when iterating on
  a 10-foot UI via screenshots.
- **Onboarding:** 9/10.
- **Build with it again?** Yes.
