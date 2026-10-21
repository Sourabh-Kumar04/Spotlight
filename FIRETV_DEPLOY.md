# SPOTLIGHT on Fire TV — Deploy Guide

How to run the SPOTLIGHT web app on a Fire TV device or the official simulator.

## Option A: Fire TV Simulator (no hardware)

1. Install Android Studio and create a virtual device with the **Fire TV** system image
   (API 28+, `amazon.firetv` tag), or use the standalone Amazon Fire TV simulator
   if provided for the hackathon.
2. On the host machine, run the app:
   ```
   python3 -m uvicorn spotlight.main:app --host 0.0.0.0 --port 8000
   ```
3. In the simulator's Silk browser, open `http://10.0.2.2:8000/tv`
   (`10.0.2.2` is the host loopback from inside the Android emulator).
4. The TV UI is built for 1920x1080 with TV-safe margins (5% overscan padding).
   Arrow keys on your keyboard drive the same focus model as the Fire TV D-pad.

**Verified:** desktop Chrome at 1920x1080, keyboard D-pad navigation.
**Not yet verified:** on the official Fire TV simulator image (no image available in this sandbox).

## Option B: Physical Fire TV Stick (4K / 4K Max)

1. Fire TV Stick → Settings → My Fire TV → Developer Options → enable **ADB debugging**
   and **Apps from Unknown Sources**.
2. `adb connect <stick-ip>:5555`, then sideload a WebView wrapper APK
   (see `firetv/` for the wrapper skeleton) that loads your hosted SPOTLIGHT URL.
3. Or simply open the Silk browser on the stick and navigate to your hosted URL —
   zero packaging needed for the demo.

## The phone remote

The `/remote` page is a mobile web app. On the same Wi-Fi network, open
`http://<host-ip>:8000/remote` on your phone. The Ask button talks to the same
backend the TV polls. For the demo video, `/demo` shows TV + remote side by side.

## Notes for judges

- The demo video is recorded from `/demo?demo=1` (deterministic, zero network dependency).
- Voice input (mic button) requires a secure context: `https://` or `localhost`.
  On plain-HTTP LAN it hides itself with an explanatory note.
