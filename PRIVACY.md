# SPOTLIGHT Privacy Notes

What the TV self-awareness feature collects, and what it does not.

## Frames
- The TV captures a video frame at most every 5 seconds and POSTs it to `/api/tv/context`.
- Frames live in **server memory only**, keyed by session id. Each new post **overwrites** the previous frame for that session — nothing accumulates.
- Frames are **never written to disk**, never logged, and never sent to any third party.
- Rate-limited to 1 post per 2 seconds per session; frames over ~2MB are rejected.

## Audio
- Voice questions are transcribed with faster-whisper and the audio bytes are discarded after transcription. No audio is retained.
- Transcription requests are rate-limited (20/minute per client) and capped at 10MB.

## Person identification
- Identifying people in frames is limited to **curated cast data for known titles** (e.g. "Cary Grant as Peter Joshua" in Charade).
- There is **no open-ended face recognition** and no biometric template storage.

## Sessions
- TV and phone pair via a random per-load code (`SPOT-4821`) shown on the TV screen — there is no guessable default session anymore.
- Session state (context, Q&A history) lives in process memory and is cleared on `/api/reset` or backend restart.
