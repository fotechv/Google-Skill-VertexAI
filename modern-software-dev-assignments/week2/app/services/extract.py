from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def extract_action_items_llm(text: str) -> list[str]:
    """
    Extract action items from free-form notes using an LLM via Ollama.

    Returns:
        List of action item strings.
    """
    import json
    import requests

    text = (text or "").strip()
    if not text:
        return []

    OLLAMA_URL = "http://localhost:11434/api/generate"
    MODEL = "llama3.1:8b"  # model nhỏ, chạy nhẹ – đổi nếu bạn muốn llama3.2:1b

    system_prompt = (
        "You are an assistant that extracts action items from notes.\n"
        "Return ONLY valid JSON.\n"
        "The output must be a JSON array of strings.\n"
        "Each string is a concise action item starting with a verb.\n"
        "If there are no action items, return an empty JSON array: [].\n"
        "Do not include explanations or markdown."
    )

    prompt = f"""SYSTEM:
            {system_prompt}
            
            USER:
            {text}
            
            OUTPUT:
        """

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()

        raw = (result.get("response") or "").strip()

        # Expect raw to be JSON, but be defensive
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Try to recover JSON array inside the text
            start = raw.find("[")
            end = raw.rfind("]")
            if start == -1 or end == -1 or end <= start:
                return []
            data = json.loads(raw[start:end + 1])

        if not isinstance(data, list):
            return []

        # Clean result
        return [item.strip() for item in data if isinstance(item, str) and item.strip()]

    except Exception as e:
        # In production you might log this
        return []


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
