# SPOTLIGHT Alexa Skill — production path

The in-demo voice path is the mic button on `/remote` (Web Speech API, zero setup).
The production path is a proper Alexa Skill. This directory holds the starting point.

## What's here

- `interaction-model.json` — the Alexa interaction model: `AskSpotlightIntent` with a
  `{Question}` slot (AMAZON.SearchQuery), invocation name "spotlight".
- The skill backend is a thin HTTPS wrapper around this repo's `/api/ask`:
  an Alexa Skills Kit SDK handler receives `AskSpotlightIntent`, forwards
  `Question` to `POST /api/ask`, and speaks back `title` + `primary_explanation`.

## What the founder needs to do (Amazon developer account required)

1. https://developer.amazon.com/alexa/console/ask → Create Skill → Custom → Alexa-hosted or self-hosted.
2. Paste `interaction-model.json` into the Build > JSON Editor, then Build Model.
3. Deploy the skill backend (AWS Lambda, Python ASK SDK):
   ```python
   from ask_sdk_core.skill_builder import SkillBuilder
   # on AskSpotlightIntent: POST question to https://<your-host>/api/ask
   # speak: f"{answer['title']}. {answer['primary_explanation']}"
   ```
4. Enable the skill on the Fire TV's linked Alexa account and say:
   "Alexa, ask Spotlight why was that a foul?"

## Why the demo doesn't need it

True Alexa Skills require the founder's Amazon developer account and account linking —
out of scope for an autonomous build. The Web Speech mic button demonstrates the exact
same interaction (speak → question filled → tap Ask) with no account needed.
