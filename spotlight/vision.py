"""Frame analysis pipeline for SPOTLIGHT.

POST /api/analyze-frame accepts an uploaded image and returns a structured
scene understanding result. Provider chain:
  1. AWS Bedrock (Nova/Claude vision) — if credentials + boto3 available
  2. Ollama vision model (llava) — if reachable
  3. PIL heuristic fallback — dominant colors, brightness, simple scene-type guess

Always returns a well-formed result; never raises on provider failure.
"""

import io
import os
from typing import Any, Dict, List, Optional

try:
    from PIL import Image, ImageStat
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def _pil_heuristic(image_bytes: bytes, question: Optional[str] = None) -> Dict[str, Any]:
    """Cheap local analysis: colors, brightness, aspect, naive scene guess."""
    if not PIL_AVAILABLE:
        return {
            "scene_type": "unknown",
            "notable_elements": [],
            "suggested_question": question or "What is happening in this scene?",
            "provider": "none",
            "note": "PIL not installed; install pillow for local heuristics.",
        }
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        return {
            "scene_type": "unknown image format",
            "notable_elements": ["unidentified image bytes"],
            "suggested_question": question or "What is happening in this scene?",
            "provider": "pil-heuristic",
            "note": f"Failed to parse image: {e}",
        }

    w, h = img.size
    stat = ImageStat.Stat(img)
    r, g, b = [int(v) for v in stat.mean]
    brightness = sum(stat.mean) / 3 / 255.0

    # dominant hue guess
    if b > r + 20 and b > g + 10:
        hue, scene_guess = "blue-dominant", "outdoor or sky-heavy scene"
    elif g > r + 15 and g > b:
        hue, scene_guess = "green-dominant", "possible sports field or nature scene"
    elif r > g + 25 and r > b + 25:
        hue, scene_guess = "warm/red-dominant", "possible indoor, stage, or sunset scene"
    else:
        hue, scene_guess = "balanced", "mixed indoor/outdoor scene"

    elements = [
        f"{hue} palette (avg RGB {r},{g},{b})",
        f"{'bright' if brightness > 0.6 else 'dim' if brightness < 0.35 else 'mid-tone'} exposure",
        f"{w}x{h} frame",
    ]
    return {
        "scene_type": scene_guess,
        "notable_elements": elements,
        "suggested_question": question or "What just happened in this scene?",
        "provider": "pil-heuristic",
        "note": "Local heuristic only — connect Bedrock or Ollama vision for real understanding.",
    }


def _bedrock_vision(image_bytes: bytes, question: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Try AWS Bedrock vision. Returns None on any failure."""
    try:
        import boto3
        import base64
    except ImportError:
        return None
    try:
        region = os.getenv("AWS_REGION", "us-east-1")
        model = os.getenv("BEDROCK_VISION_MODEL", "amazon.nova-lite-v1:0")
        client = boto3.client("bedrock-runtime", region_name=region)
        prompt_text = (
            f"The viewer is watching TV and asks: '{question}'. Answer what is visible on this TV frame. "
            "Describe what is visible; identify people/objects only when confident; say so when unsure. "
            'Reply as JSON: {"scene": "...", "elements": ["..."], "answer": "...", "question": "..."}'
        ) if question else (
            "Describe this TV frame in one sentence. Then suggest the single most "
            "interesting question a viewer would ask about it. Reply as JSON: "
            '{"scene": "...", "question": "...", "elements": ["..."]}'
        )
        body = {
            "messages": [{
                "role": "user",
                "content": [
                    {"image": {"format": "png", "source": {"bytes": base64.b64encode(image_bytes).decode()}}},
                    {"text": prompt_text},
                ],
            }],
            "inferenceConfig": {"maxTokens": 300},
        }
        import json as _json
        resp = client.invoke_model(modelId=model, body=_json.dumps(body))
        out = _json.loads(resp["body"].read())
        text = out["output"]["message"]["content"][0]["text"]
        # try to parse JSON out of the text
        start, end = text.find("{"), text.rfind("}") + 1
        parsed = _json.loads(text[start:end]) if start != -1 and end > start else {}
        return {
            "scene_type": parsed.get("scene", "live TV frame"),
            "notable_elements": parsed.get("elements", []),
            "suggested_question": parsed.get("question", question or "What just happened in this scene?"),
            "answer": parsed.get("answer"),
            "provider": "bedrock-vision",
            "note": "",
        }
    except Exception:
        return None


def _ollama_vision(image_bytes: bytes, question: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Try Ollama llava. Returns None on any failure."""
    try:
        import base64
        import urllib.request
        import json as _json
    except ImportError:
        return None
    try:
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        model = os.getenv("OLLAMA_VISION_MODEL", "llava")
        prompt_text = (
            f'The TV viewer asks: "{question}". Describe what is visible in this frame; identify people/objects only when confident; say so when unsure. Reply as JSON: {{"scene": "...", "elements": ["..."], "answer": "..."}}'
        ) if question else (
            'Describe this TV frame in one sentence and suggest one interesting viewer question. Reply as JSON: {"scene": "...", "question": "...", "elements": ["..."]}'
        )
        payload = _json.dumps({
            "model": model,
            "prompt": prompt_text,
            "images": [base64.b64encode(image_bytes).decode()],
            "stream": False,
        }).encode()
        req = urllib.request.Request(host + "/api/generate", data=payload,
                                     headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=60)
        text = _json.loads(resp.read().decode()).get("response", "")
        start, end = text.find("{"), text.rfind("}") + 1
        parsed = _json.loads(text[start:end]) if start != -1 and end > start else {}
        elements = parsed.get("elements") or _pil_heuristic(image_bytes).get("notable_elements", [])
        return {
            "scene_type": parsed.get("scene", "live TV frame"),
            "notable_elements": elements,
            "suggested_question": parsed.get("question", question or "What just happened in this scene?"),
            "answer": parsed.get("answer"),
            "provider": "ollama-vision",
            "note": "",
        }
    except Exception:
        return None


def analyze_frame(image_bytes: bytes, question: Optional[str] = None) -> Dict[str, Any]:
    """Run the provider chain and return the first successful analysis."""
    for provider in (_bedrock_vision, _ollama_vision):
        try:
            result = provider(image_bytes, question=question)
        except Exception:
            result = None
        if result:
            return result
    return _pil_heuristic(image_bytes, question=question)
