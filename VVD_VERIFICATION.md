# Vega Virtual Device (VVD) Rendering Verification Report

**Date**: 2026-10-21  
**Target Package**: `spotlight/vega-wrapper/build/x86_64-release/spotlighttv_x86_64.vpkg`  
**Device**: Vega Virtual Device (qemu x86_64, OS 1.2, SDK 0.24.12112)  
**Backend**: FastAPI / Uvicorn running on `0.0.0.0:8000` (accessible from VVD via `http://10.0.2.2:8000/tv`)

---

## 1. Summary of Results

| Step | Action | Status | Notes |
|------|--------|--------|-------|
| 1 | VVD Status Check | **SUCCESS** | QEMU process running (PID 238010) |
| 2 | Backend Verification | **SUCCESS** | Uvicorn running on `0.0.0.0:8000`; `http://10.0.2.2:8000/tv` returns HTTP 200 |
| 3 | Package Installation | **SUCCESS (with manifest module relaxation)** | Initial `.vpkg` failed on missing `/com.amazon.kepler.webview_4@IWebview_4`. Repacked with manifest relaxed installs cleanly via `vega run-app` |
| 4 | Rendering Verification | **OBSERVED (Black Screen / SIGABRT)** | QEMU QMP framebuffer dump shows black screen (1920x1080 RGB zeros). System logs confirm webview stem crashed |

---

## 2. Step-by-Step Observations

### Step 1: Virtual Device Status
- Command: `vega virtual-device status`
- Result:
  ```json
  {"running":true,"process_ids":{"qemu":238010}}
  ```
- Device identifier: `VirtualDevice : tv - x86_64 - OS - amazon-cdb6a24cc5064b7a`

### Step 2: SPOTLIGHT Backend Connectivity
- Backend running on `0.0.0.0:8000`.
- Verified on host: `curl -s http://localhost:8000/tv` returns full HTML for `SPOTLIGHT — Fire TV Experience`.
- Verified from within the Vega Virtual Device via `vda shell`:
  ```bash
  vega device run-cmd -c 'curl -s -o /dev/null -w "%{http_code}\n" http://10.0.2.2:8000/tv'
  # Output: 200
  ```

### Step 3: Package Installation (`vega run-app`)
When installing the original release build `spotlight/vega-wrapper/build/x86_64-release/spotlighttv_x86_64.vpkg`:
```
Installing/Updating '/tmp/spotlighttv_x86_64.vpkg' ...error (Module dependency not found):
error: Unable to install '/tmp/spotlighttv_x86_64.vpkg' as the required dependencies are not found on the device.
The Vega Virtual Device is missing modules that are available on a physical device. Test your app using a Fire TV Stick instead.
The following module dependencies declared in the application manifest are not found:
  - /com.amazon.kepler.webview_4@IWebview_4
```

To test whether the package can install and execute without strict module declaration:
1. Extracted `.vpkg` via `vpt unpack`.
2. Relaxed `manifest.toml` to omit the `/com.amazon.kepler.webview_4@IWebview_4` module constraint.
3. Repacked via `vpt pack`.
4. Installed via `vega run-app spotlighttv_x86_64.vpkg com.spotlight.tv.main`:
   ```
   Installed spotlighttv_x86_64.vpkg on 
   Successfully launched the app
   ```
5. Verified installation via `vpm info com.spotlight.tv`:
   - Package ID: `com.spotlight.tv`
   - Installed at: `/var/lib/pkgmgrd/packages/com.spotlight.tv`
   - Component: `com.spotlight.tv.main`

### Step 4: Rendering & Screenshot Verification
- Took screen capture directly from the virtual device display using QEMU's Machine Protocol (QMP) `screendump` over `/tmp/qmp-socket-5554.sock`, converted to PNG:
  - Output file: `spotlight/vega-wrapper/vvd_screenshot.png` (1920x1080)
- The display shows a black screen (`RGB (0,0,0)`).
- Inspection of runtime device diagnostics (`loggingctl log` and `vlcm crash-history`) revealed:
  ```
  acr_core_dump: Process '!usr!bin!stem-init' (PID=19796) crashed with signal 6
  stemd: prewarming new stem, prewarm_request="com.amazon.family.webview"
  stemd: connection with stem was dropped
  stemd: stem was killed: sig=SIGKILL
  ```
- **Root Cause**: The official Vega Virtual Device (0.24 image) omits the Chromium-based WebView rendering engine. The filesystem contains only a 0-byte stub for `/usr/share/webview/icudtl.dat`, and attempting to initialize the webview sandbox (`com.amazon.family.webview`) triggers an immediate SIGABRT in `stem-init`.

---

## 3. Conclusion & Recommendation

As Amazon's error message states:
> *"The Vega Virtual Device is missing modules that are available on a physical device. Test your app using a Fire TV Stick instead."*

- **Root cause:** The Vega Virtual Device (0.24 image) omits the Chromium-based WebView rendering engine. The filesystem contains only a 0-byte stub for `/usr/share/webview/icudtl.dat`, and attempting to initialize the webview sandbox (`com.amazon.family.webview`) triggers an immediate SIGABRT in `stem-init`.
- **Impact:** This is a VVD-only limitation. The SPOTLIGHT TV UI itself is fully functional in a browser at 1920x1080; only the VVD rendering path is a dead end.
- **See also:** F-07 in FRICTION_LOG.md for the friction-log entry on this issue.
- For demonstration and verification of the SPOTLIGHT TV UI, recommended paths remain:
  1. **Physical Fire TV Stick (Vega OS / Fire OS)**: Running via Silk browser (`http://<host-ip>:8000/tv`) or installed web app.
  2. **Fire OS Sideload**: Android WebView wrapper APK in `firetv/`.
  3. **Browser 10-foot emulation**: Fullscreen Chrome/Firefox at 1080p pointing to `/tv` (used for the demo video).
