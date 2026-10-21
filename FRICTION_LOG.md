# SPOTLIGHT — Friction Log

Real friction encountered while building. Submitted for the Amazon "Build, Ship, Shape" hackathon
(Fire TV track). Friction logs earn up to a 10% judging bonus — these are honest entries.

## F-01 — Fire TV simulator setup is undocumented for web-first builds
- **Attempted:** Find official docs for running a web-technology app on the Fire TV / Vega OS simulator.
- **Expected:** A single "web apps on Fire TV" guide with simulator download + deploy steps.
- **Actual:** Documentation is fragmented across Fire App Builder (Android), Web App Tester (deprecated path),
  and Vega OS developer previews. No single happy path for "I built a web app, now put it on the Fire TV simulator."
- **Severity:** High — this is the first thing every web-first Fire TV track entrant hits.
- **Workaround:** Built the app as a responsive web app verified in desktop Chrome at TV viewport (1920x1080),
  packaged a WebView wrapper skeleton under `firetv/`, and wrote FIRETV_DEPLOY.md from assembled sources.
- **Suggestion:** One canonical "Web → Fire TV simulator in 10 minutes" guide, linked from the hackathon resources page.

## F-02 — No Fire TV device available for on-device verification
- **Attempted:** Verify the 10-foot UI on a physical Fire TV Stick.
- **Expected:** N/A — no device on hand.
- **Actual:** All verification done in desktop Chrome at 1920x1080. TV-safe overscan margins applied via CSS,
  but remote-control D-pad navigation (arrow-key focus) is implemented and only keyboard-tested.
- **Severity:** Medium.
- **Workaround:** Keyboard arrow-key navigation mapped to the same focus model a D-pad uses; documented as
  "needs on-device confirmation" in FIRETV_DEPLOY.md.
- **Suggestion:** A cloud-based Fire TV simulator with a shareable session URL would unblock device-less builders.

## F-03 — Bedrock credentials not available in the build environment
- **Attempted:** Use AWS Bedrock (Nova/Claude vision + text) as the primary LLM provider.
- **Expected:** Straightforward boto3 call with the standard credential chain.
- **Actual:** No AWS credentials in the sandbox. Built the full provider chain anyway
  (Bedrock → OpenAI → Ollama → curated-only) with graceful degradation, but the Bedrock path is
  code-complete and untested against live AWS.
- **Severity:** Medium.
- **Workaround:** Provider auto-detection at startup logs which provider is active; curated canonical answers
  guarantee the demo works with zero credentials.
- **Suggestion:** Hackathon-provided Bedrock sandbox credits (even tiny) would let entrants demo the AWS path honestly.

## F-04 — Google Fact Check API quota/keys
- **Attempted:** Live fact-checking for the news beat via the Fact Check Explorer API.
- **Expected:** Free-tier key, simple REST lookup.
- **Actual:** API requires a keyed project; built with `FACTCHECK_API_KEY` env support and a clearly-labeled
  curated fallback. Live-verdict UI badge distinguishes LIVE vs CURATED sources.
- **Severity:** Low.
- **Workaround:** Curated canonical answer for the demo question; live path activates when the key is present.
- **Suggestion:** A one-click test key for hackathon entrants would let more teams demo the live
  path instead of shipping curated fallbacks.

## F-05 — Autonomous build-agent quota exhausted mid-build (improvement pass)
- **Attempted:** Run the 10-item improvement pass as an autonomous agent job.
- **Expected:** Agent builds all 10 workstreams.
- **Actual:** `RESOURCE_EXHAUSTED (429): Individual quota reached` — verified real via a trivial
  no-op test job. Reset window fell after the hackathon deadline.
- **Severity:** High (for schedule, not for code).
- **Workaround:** Built all 10 items manually instead — slower, but shippable.
- **Suggestion:** N/A (build-tooling level, not Amazon's).

## F-06 — Web Speech API requires HTTPS or localhost
- **Attempted:** Voice input on the phone remote via the Web Speech API.
- **Expected:** Works wherever the remote page loads.
- **Actual:** `webkitSpeechRecognition` only runs in secure contexts. Fine on localhost/HTTPS, silently absent on
  plain HTTP LAN URLs — which is exactly how you'd demo phone→laptop on a local network.
- **Severity:** Medium.
- **Workaround:** Feature-detects and hides the mic button with an explanatory tooltip when unavailable;
  docs recommend `https://` or localhost for the voice demo.
- **Suggestion:** (Browser-level, not Amazon's.) Noted here because it affects the demo plan.
