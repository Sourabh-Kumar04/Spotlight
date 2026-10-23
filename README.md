# SPOTLIGHT — The Curiosity Remote for Fire TV

> **Amazon "Build, Ship, Shape" Hackathon — Fire TV Track**  
> *One tap. Any screen. Any question.*

---

## Concept

You're watching TV. Something happens on screen that confuses you:
- A soccer player gets booked, and nobody at home knows the rule.
- A character re-appears after 40 minutes, and you can't remember their name.
- Your kid asks why the sky is blue during a nature documentary.
- A broadcast makes an astonishing historical claim.
- The chef adds a mystery spice — and the recipe builds itself.
- Your team loses the fight and you need the coach's breakdown.
- The lead's sneakers get a 3-second close-up — what are they?
- The drama switches to Spanish mid-scene — what did she just say?

You don't want to type a query into a sluggish TV keyboard or open a mobile browser and search through search engine clutter.

**With SPOTLIGHT, you tap ONE button on your phone remote:**
1. **Instant Frame Freeze:** The TV freezes the broadcast moment.
2. **Telemetry & Visual Analysis:** The backend analyzes the broadcast metadata, frame timecode, and question.
3. **High-Contrast 10-Foot Overlay:** A big-type, high-contrast overlay explains the answer in seconds on the TV screen.
4. **Learning Companion Seed:** The system captures your curiosity query into a persistent profile (*"You've asked about fouls twice this week"*).

---

## Feature Map (8 beats)

| # | Beat | Question | Engine |
|---|------|----------|--------|
| 1 | Kids documentary | Why is the sky blue? | Rayleigh scattering explainer, read-aloud |
| 2 | Movies | Who is that guy...? | Character catch-up card |
| 3 | Sports (soccer) | Why was that a foul? | IFAB Law 12 ruling |
| 4 | News | Is that claim true? | Fact-check (live API or curated) |
| 5 | Cooking | What spice did they just add? | Recipe auto-builder |
| 6 | Esports | Why did they lose that fight? | Coach's breakdown |
| 7 | Shopping | What shoes is he wearing? | Real product identification (e.g. Forrest Gump's Nike Cortez) |
| 8 | Language | What did they just say? | ES→EN translation + context |

Plus: **voice Q&A** (push-to-talk on phone → faster-whisper STT → Piper TTS voice reply on phone + speechSynthesis spoken answer on TV), **voice commands** (pause/play/rewind/volume via intent router + WebSocket hub), **TV self-awareness** (/tv pushes title + frame every 5s to /api/tv/context, auto-attached to /api/ask when no explicit context given), **3 languages** (EN/ES/HI for the 4 demo-tour beats; remaining 4 beats fall back to English), **frame analysis** (`POST /api/analyze-frame`), **learning companion** (60-second explainers after 2+ asks in a topic), **Bedrock → OpenAI → Ollama → curated** LLM fallback chain.

---

## Live Interfaces

| Interface | URL | Purpose |
| :--- | :--- | :--- |
| **Fire TV App** | [`/tv`](http://localhost:8000/tv) | Full-screen 10-foot UI with frame freeze, analysis HUD, and big-type overlay. |
| **Phone Remote** | [`/remote`](http://localhost:8000/remote) | Mobile web UI with the single big **ASK** button, beat switcher, and editable query. |
| **Side-by-Side Simulator** | [`/demo`](http://localhost:8000/demo) | Dual-screen view of TV + Phone Remote side-by-side with 1-click automated tour. |
| **Portal Gateway** | [`/`](http://localhost:8000/) | Central launcher and beat reference table. |
| **REST & WebSocket API** | [`/docs`](http://localhost:8000/docs) | Interactive Swagger OpenAPI documentation. |

---

## The 4 Demo-Tour Beats

Spotlight ships 8 knowledge engines (one per beat in the Feature Map above). The first 4 have canonical answers translated into EN/ES/HI and are the scripted demo tour:

| Beat | Category | Channel & Scene | Canonical Question | Engine Output |
| :--- | :--- | :--- | :--- | :--- |
| **Beat 1** | **Kids Documentary** | Nature documentary scene | *"Why is the sky blue?"* | Warm 3-sentence parent read-aloud explanation of Rayleigh scattering; high-contrast; child-friendly. |
| **Beat 2** | **Cinema Thriller** | *Charade* (1963, public domain) playing full-bleed | *"Who is that man?"* | Cary Grant, as Peter Joshua — character catch-up from live frame + title context. |
| **Beat 3** | **Sports (Soccer)** | Soccer match scene | *"Why was that a foul?"* | Replay breakdown + IFAB Law 12 reckless-challenge ruling. |
| **Beat 4** | **News Fact-Check** | News segment | *"Is that claim true?"* | Non-partisan scientific audit: Apollo 11 moon landing **VERIFIED TRUE** with 2 independent citations. |

> **Hybrid Intelligence Guarantee:** Canonical questions resolve instantly (**<100ms**) via curated rule engines. Free-form questions route to the LLM fallback chain (Bedrock → OpenAI → Ollama `llama3.2:3b` → deterministic contextual synthesis), falling back gracefully to context-aware synthesis when all LLMs are offline.

---

## How to Run

### Requirements
- **Python 3.12+**
- **uv** (or standard pip)

### 1. Install Dependencies
```bash
uv pip install -e ".[dev]"
# Or: pip install fastapi "uvicorn[standard]" httpx jinja2 websockets pytest pytest-asyncio
```

### 2. Start the Server
```bash
python3 -m uvicorn spotlight.main:app --host 0.0.0.0 --port 8000
```

### 3. Open the Experience
- **Evaluating side-by-side?** Open [`http://localhost:8000/demo`](http://localhost:8000/demo) to see the TV and Phone Remote operating in real time together.
- **Testing multi-device?** Open `/tv` on your TV / monitor and `/remote` on your smartphone (connected to the same local network).

---

## Demo Mode (`?demo=1`) & Deterministic Tour

To record a demo video or run deterministic tests without any network dependency:
1. Navigate to [`http://localhost:8000/demo?demo=1`](http://localhost:8000/demo?demo=1).
2. Click **RUN FULL 4-BEAT TOUR** in the top navigation bar.
3. The simulator steps through all 4 beats with scripted timings:
   - Switches scene
   - Triggers freeze & analysis HUD
   - Displays canonical answer overlay
   - Logs query to session history & advances to the next beat.

---

## Testing

Run the full pytest suite (87 automated tests covering engines, fallback, state machine, API, and WebSockets):

```bash
python3 -m pytest -v
```

All 87 tests pass green.

---

## Fire TV Keyboard Shortcuts (for 10-Foot UI Testing)

When viewing `/tv` in a browser or Fire TV test browser:
- `1` : Switch to Beat 1 (Kids Nature Documentary)
- `2` : Switch to Beat 2 (Movie Espionage Thriller)
- `3` : Switch to Beat 3 (Soccer Match)
- `4` : Switch to Beat 4 (News Fact-Check)
- `Space` / `Enter` : Dismiss overlay / resume video playback

---

## License

MIT License. Open-source for the Amazon "Build, Ship, Shape" Hackathon.
