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

## F-07 — Vega Virtual Device (VVD) omits WebView engine from system image
- **Attempted:** Verify the SPOTLIGHT TV UI on Amazon's official Vega Virtual Device simulator (SDK 0.24.12112)
  using a React Native WebView wrapper package (`.vpkg`).
- **Expected:** The VVD launches the WebView package and renders the `/tv` page, satisfying the
  "running on simulator" demo-video requirement without physical hardware.
- **Actual:** The VVD 0.24 image omits the Chromium-based WebView runtime
  (`/com.amazon.kepler.webview_4@IWebview_4`). Initial `.vpkg` install fails on the missing module dependency.
  Relaxing the manifest to skip the dependency allows installation, but the webview stem crashes immediately
  with SIGABRT (`stem-init` process). The QEMU framebuffer shows a black screen.
- **Severity:** High — the VVD is the official no-hardware verification path, and it cannot render web apps.
- **Workaround:** Verified the TV UI in desktop Chrome at 1920x1080 instead. Silk browser on a physical
  Fire TV Stick is the remaining on-device path. See `VVD_VERIFICATION.md` for
  full diagnostic logs and `vvd_screenshot.png` for the black-screen evidence.
- **Suggestion:** Ship the WebView runtime module in the VVD system image, or provide a documented
  alternative simulator for web-technology Fire TV apps.

## F-08 — Canvas frame capture fails on cross-origin video (tainted canvas)
- **Attempted:** TV self-awareness: capture a frame from the `<video>` element via `canvas.toDataURL()`
  every 5 seconds and POST it to `/api/tv/context` for auto-attached frame analysis.
- **Expected:** Works for any video source playing on the `/tv` page.
- **Actual:** `canvas.toDataURL()` throws a security exception when the video source is cross-origin
  and not CORS-enabled (tainted canvas). The Charade movie clip and other hosted video assets trigger
  this if served from a different domain without proper CORS headers.
- **Severity:** Medium — the auto-attached frame analysis degrades silently to metadata-only (title +
  timecode + paused state) when canvas capture is blocked. The feature still works for same-origin
  video and for the camera-snap path on the remote.
- **Workaround:** Code catches the exception, logs a warning, and sends `frame_b64: null` so the backend
  still gets title + timecode context. Frame analysis via the camera snap on `/remote` is unaffected
  because the user uploads a photo directly.
- **Suggestion:** (Browser-level security policy, not Amazon's.) Document the CORS requirement for
  video assets, or use a server-side frame proxy for cross-origin content.
