"""Intent router for SPOTLIGHT: Curiosity Remote for Fire TV.

Classifies transcribed or entered text into either:
1. Device commands: pause, play/resume, rewind/forward (with duration), volume up/down/mute, go-back.
2. Questions: routed to the canonical / LLM fallback knowledge engine pipeline.
"""

import re
from typing import Any, Dict, Optional

WORD_TO_NUM = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "fifteen": 15,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "forty-five": 45,
    "fifty": 50,
    "sixty": 60,
    "a": 1,
    "an": 1,
}

QUESTION_STARTERS = (
    "who", "what", "where", "when", "why", "how", "which",
    "is", "are", "was", "were", "does", "do", "did",
    "can you", "could you", "would you", "will you",
    "tell me", "explain", "describe",
)


def parse_duration(text: str, default: int = 10) -> int:
    """Parse duration in seconds from text like '30 seconds', '10s', '1 minute'."""
    clean = text.lower().strip()

    if "half a minute" in clean or "half minute" in clean:
        return 30
    if "a minute" in clean or "one minute" in clean:
        return 60

    # Digits + unit: e.g. "30 seconds", "10s", "1 minute", "2.5 mins"
    m = re.search(r'(\d+(?:\.\d+)?)\s*(seconds?|secs?|s\b|minutes?|mins?|m\b)', clean)
    if m:
        val = float(m.group(1))
        unit = m.group(2)
        if unit.startswith("m"):
            return int(val * 60)
        return int(val)

    # Word numbers + unit: e.g. "thirty seconds", "two minutes", "ten secs"
    for word, num in WORD_TO_NUM.items():
        pattern = rf'\b{re.escape(word)}\s*(seconds?|secs?|s\b|minutes?|mins?|m\b)'
        m_word = re.search(pattern, clean)
        if m_word:
            unit = m_word.group(1)
            if unit.startswith("m"):
                return num * 60
            return num

    # Trailing or embedded standalone integer: e.g. "rewind 30", "back 10"
    m_num = re.search(r'\b(\d+)\b', clean)
    if m_num:
        return int(m_num.group(1))

    return default


def classify_intent(text: str) -> Dict[str, Any]:
    """Classify input text into a device command or a curiosity question.

    Returns:
        {"type": "command", "action": str, "seconds": Optional[int]}
        or
        {"type": "question", "question": str}
    """
    raw = (text or "").strip()
    if not raw:
        return {"type": "question", "question": ""}

    normalized = raw.lower().strip().rstrip(".!?,")

    # If it clearly starts with question phrasing or ends with '?', treat as question
    if raw.endswith("?"):
        return {"type": "question", "question": raw}

    for starter in QUESTION_STARTERS:
        if normalized == starter or normalized.startswith(starter + " "):
            return {"type": "question", "question": raw}

    # 1. Pause
    if re.match(r'^(pause|freeze)(\s+(the\s+)?(video|playback|movie|tv))?$', normalized) or normalized in ("pause", "freeze", "stop playback"):
        return {"type": "command", "action": "pause"}

    # 2. Play / Resume
    if re.match(r'^(resume)(\s+(the\s+)?(video|playback|movie|tv))?$', normalized) or normalized == "resume":
        return {"type": "command", "action": "resume"}
    if re.match(r'^(play|unpause|continue)(\s+(the\s+)?(video|playback|movie|tv))?$', normalized) or normalized in ("play", "unpause", "continue"):
        return {"type": "command", "action": "play"}

    # 3. Rewind / Back with duration
    # Notice: "back 10 seconds", "rewind 30 seconds", "go back 15 seconds"
    if re.search(r'\b(rewind|skip back|step back|jump back)\b', normalized) or (
        re.search(r'\b(back|go back)\b', normalized) and re.search(r'\d+|minute|second|sec|min', normalized)
    ):
        sec = parse_duration(normalized, default=10)
        return {"type": "command", "action": "rewind", "seconds": sec}

    # 4. Forward with duration
    if re.search(r'\b(forward|fast forward|fast-forward|skip ahead|skip forward|jump forward)\b', normalized):
        sec = parse_duration(normalized, default=10)
        return {"type": "command", "action": "forward", "seconds": sec}

    # 5. Volume up / down / mute
    if re.search(r'\b(volume up|turn (it )?up|louder|raise (the )?volume)\b', normalized) or normalized == "volume up":
        return {"type": "command", "action": "volume_up"}

    if re.search(r'\b(volume down|turn (it )?down|quieter|lower (the )?volume)\b', normalized) or normalized == "volume down":
        return {"type": "command", "action": "volume_down"}

    if re.match(r'^(mute|unmute|silence)(\s+(the\s+)?(audio|tv|sound|volume))?$', normalized) or normalized in ("mute", "unmute", "silence"):
        return {"type": "command", "action": "mute"}

    # 6. Go-back (navigation/overlay dismissal)
    if normalized in ("go back", "go-back", "back", "dismiss", "dismiss overlay", "close overlay", "return"):
        return {"type": "command", "action": "go-back"}

    # Fallback to question
    return {"type": "question", "question": raw}


# Alias for flexibility
route_intent = classify_intent
