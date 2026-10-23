# SPOTLIGHT on Fire TV — Deploy Guide

How to run the SPOTLIGHT web app on a Fire TV device or the official simulator.

## Path 1 (recommended): Amazon's official web-app submission — works on ALL Fire TV devices

Amazon accepts HTML5 web apps directly into the Appstore — no native code needed.
You submit your app's URL (or a .zip) through the Developer Console and Amazon
wraps it in their Chromium-based Web App Runtime. This is the only path that also
works on the newest Fire TV Sticks running Vega OS (see the Vega OS note below).

1. Host SPOTLIGHT at a public HTTPS URL (the `/tv` page is the entry point).
2. Install **Web App Tester** from the Amazon Appstore onto your Fire TV device —
   it lets you preview your web app in a production-like environment and debug it
   before submitting.
3. In Web App Tester, enter your app name + URL and verify the 10-foot UI,
   D-pad navigation, and spoken answers on the real device.
4. Submit via the Developer Console (developer.amazon.com): guided flow, then
   Amazon reviews (typically 24–72h for TV apps).

**Appstore review requirements that apply to us:**
- Every screen must be navigable with the Fire TV remote's D-pad — no touch/mouse-only flows.
- App must launch within ~5 seconds on a first-run test device.
- Privacy policy URL + data-handling statements are mandatory.
- Amazon expects testing on a physical Fire TV device, not just an emulator.

## Path 1b: Vega Virtual Device — ATTEMPTED AND CLOSED

This path was fully attempted: Vega SDK 0.24 installed, React Native WebView wrapper
built, `.vpkg` packaged and installed on the Virtual Device. It is a dead end — the
0.24 VVD system image omits the Chromium WebView engine (0-byte `icudtl.dat`
placeholder; the webview container crashes with SIGABRT and screenshots come out
pure black). Amazon's own guidance: *"Test your app using a Fire TV Stick instead."*

Full verification logs: `VVD_VERIFICATION.md`. The wrapper source was removed from
this repo; the record above is kept so the attempt stays auditable.

## Path 2: TV Bro (sideloaded — Silk ships as a broken stub on the LDI cloud image and crashes on launch) browser — fastest on-device check, zero packaging

Every Fire TV Stick ships Amazon's Silk browser. Open `http://<host-ip>:8000/tv`
(or your hosted URL) in Silk. Works on Fire OS and Vega OS alike. Good enough to
verify the real 10-foot experience and record B-roll; not a store listing.

## Path 3: WebView wrapper APK sideload — Fire OS (Android) devices ONLY

`firetv/` contains a WebView wrapper skeleton (AndroidManifest.xml + MainActivity.java)
that loads your SPOTLIGHT URL fullscreen.

1. Build the APK in Android Studio.
2. Fire TV Stick → Settings → My Fire TV → Developer Options → enable **ADB debugging**
   and **Apps from Unknown Sources** (unlock Developer Options by clicking the device
   name 7x under My Fire TV → About, if hidden).
3. `adb connect <stick-ip>:5555`, then `adb install` the APK — or install the
   **Downloader** app from the Appstore and fetch the APK by URL.

**Vega OS warning:** Amazon's newest Fire TV Sticks run Vega OS (Linux-based, not
Android). Vega OS devices **cannot sideload APKs at all** — Path 3 does not work on
them; use Path 1 (official web-app submission) or Path 2 (Silk) instead.

## Path 4: Fire TV Simulator (no hardware)

1. Install Android Studio and create a virtual device with the **Fire TV** system image
   (API 28+, `amazon.firetv` tag).
2. On the host machine, run the app:
   ```
   python3 -m uvicorn spotlight.main:app --host 0.0.0.0 --port 8000
   ```
3. In the simulator's Silk browser, open `http://10.0.2.2:8000/tv`
   (`10.0.2.2` is the host loopback from inside the Android emulator).
4. The TV UI is built for 1920x1080 with TV-safe margins (5% overscan padding).
   Arrow keys on your keyboard drive the same focus model as the Fire TV D-pad.

**Verified:** desktop Chrome at 1920x1080, keyboard D-pad navigation.
**Not yet verified:** on the official Fire TV simulator image, or any physical
Fire TV hardware (no device available in this sandbox).

## The phone remote

The `/remote` page is a mobile web app. On the same Wi-Fi network, open
`http://<host-ip>:8000/remote` on your phone. The Ask button talks to the same
backend the TV polls. For the demo video, `/demo` shows TV + remote side by side.

## Notes for judges

- The demo video is recorded from `/demo?demo=1` (deterministic, zero network dependency).
- Voice input (mic button) uses `MediaRecorder` for audio capture and `faster-whisper` for server-side
  transcription. The Web Speech API provides live partial transcript previews when available (requires
  `https://` or `localhost`); it is not required for the main transcription path.
- Voice reply plays on the phone via Piper TTS (`POST /api/voice/speak` → audio/wav) and on the TV via
  the browser's `speechSynthesis` API. Both paths are implemented; on-device verification pending.
- TV self-awareness captures a frame every 5 seconds via canvas and POSTs to `/api/tv/context`. This
  works for same-origin video; cross-origin video without CORS headers produces a tainted canvas
  (the code degrades gracefully to metadata-only context — see F-08).
