# SPOTLIGHT Alexa Skill — Stub (Not Shipped)

This directory contains a starting point for an Alexa Skill integration. It is **not a shipped
feature** — no skill is deployed, no Lambda function exists, and no Amazon developer account
is linked. The in-demo voice path uses the phone remote's push-to-talk button (MediaRecorder +
faster-whisper STT), not Alexa.

## What is here

- `interaction-model.json (removed — skill is a design stub, see doc header)` — the Alexa interaction model: `AskSpotlightIntent` with a
  `{Question}` slot (AMAZON.SearchQuery), invocation name "spotlight".

That is the only file. There is no skill backend, no Lambda handler, no ASK SDK code.

## What it would take to ship

An Amazon developer account is required to deploy an Alexa Skill. The steps would be:

1. https://developer.amazon.com/alexa/console/ask → Create Skill → Custom → Alexa-hosted or self-hosted.
2. Paste `interaction-model.json (removed — skill is a design stub, see doc header)` into the Build > JSON Editor, then Build Model.
3. Deploy a skill backend (AWS Lambda, Python ASK SDK):
   ```python
   from ask_sdk_core.skill_builder import SkillBuilder
   # on AskSpotlightIntent: POST question to https://<your-host>/api/ask
   # speak: f"{answer['title']}. {answer['primary_explanation']}"
   ```
4. Enable the skill on the Fire TV's linked Alexa account and say:
   "Alexa, ask Spotlight why was that a foul?"

## Why the demo does not need it

The phone remote's push-to-talk button demonstrates the same voice interaction (speak →
transcribe → answer → voice reply) without an Amazon developer account. The Alexa Skill is a
future production path, not part of the hackathon demo.
