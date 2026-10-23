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
- **Used for:** Live partial transcript preview on the phone remote while recording.
- **What worked:** Zero-dependency; gives real-time visual feedback ("listening..." with partial text)
  while `MediaRecorder` captures the actual audio for server-side transcription.
- **Needs work:** Secure-context requirement silently kills it on plain-HTTP LAN demos (see F-06); no
  built-in signal for "unavailable due to context" vs "unavailable due to browser." The API is used only
  for preview — the actual transcription is server-side via faster-whisper — so degradation is graceful.
- **Onboarding:** 7/10.
- **Build with it again?** Yes, as a preview layer on top of MediaRecorder.

## faster-whisper (server-side STT)
- **Used for:** Transcribing recorded audio from the phone remote into text for the ask pipeline.
- **What worked:** int8 quantization runs on CPU without GPU; VAD filter eliminates long silences;
  word-level timestamps enable future sub-segment features. Ghost-guard (dropping segments with
  high `no_speech_prob`) prevents silence hallucinations that plague vanilla Whisper.
- **Needs work:** Model load time (~3s on first call) adds latency to the first voice question. The
  `base.en` model occasionally mis-transcribes short, domain-specific words (e.g. "foul" → "goal").
  No streaming mode — the full audio blob is transcribed in one shot.
- **Onboarding:** 8/10.
- **Build with it again?** Yes — the VAD + ghost-guard combination is a real improvement over
  the default Whisper pipeline.

## Piper TTS (server-side, phone reply)
- **Used for:** Synthesizing the answer as spoken audio played on the phone after a voice question.
- **What worked:** Subprocess mode produces clean audio/wav output; the `en_US-lessac-medium` voice
  is natural enough for short answers. Zero GPU required, zero API keys, runs entirely offline.
- **Needs work:** Voice quality drops noticeably on longer sentences (>40 words). No streaming —
  the full WAV is generated before playback starts, adding ~1s latency. Voice model discovery is
  fragile (hardcoded fallback paths that may not match every install). Only English voices tested.
- **Onboarding:** 7/10 — the binary works, but model path discovery required custom fallback logic.
- **Build with it again?** Yes — for a hackathon, offline TTS with no API key is the right call.

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

## Vega SDK + Virtual Device (simulator)
- **Used for:** Attempting on-simulator verification of the SPOTLIGHT TV UI via a React Native WebView wrapper.
- **What worked:** The Vega CLI (`vega virtual-device start --gui`) boots a QEMU-based Fire TV simulator
  quickly. The `.vpkg` packaging flow (`vpt pack`/`vpt unpack`) is straightforward. Backend connectivity
  from inside the VVD to the host (`http://10.0.2.2:8000`) works out of the box.
- **Needs work:** The 0.24 VVD system image omits the Chromium WebView engine, so any WebView-based app
  crashes with SIGABRT. This is the documented dead end in VVD_VERIFICATION.md. The toolchain also
  requires Node 20+, JDK 21, and Python 3 in WSL — a heavy setup for what should be a "launch and test"
  workflow.
- **Onboarding:** 5/10 — the SDK installs fine, but the web-app story hits a wall at the VVD.
- **Build with it again?** Only if the WebView runtime ships in the system image.
