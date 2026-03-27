from __future__ import annotations

import json
import os
import re
from typing import List

import requests

from ..settings import settings


BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = ("todo:", "action:", "next:")


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


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0].lower()
    imperative_starters = {
        "add", "create", "implement", "fix", "update", "write", "check", "verify",
        "refactor", "document", "design", "investigate",
    }
    return first in imperative_starters


def extract_action_items(text: str) -> List[str]:
    """Rule-based (heuristic) action item extractor."""
    lines = (text or "").splitlines()
    extracted: List[str] = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line).strip()
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)

    if not extracted:
        # Fallback: split into sentences, keep imperative-like ones
        sentences = re.split(r"(?<=[.!?])\s+", (text or "").strip())
        for sentence in sentences:
            s = sentence.strip()
            if s and _looks_imperative(s):
                extracted.append(s)

    # Deduplicate (case-insensitive), preserve order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    return unique


def extract_action_items_llm(text: str) -> List[str]:
    """LLM-powered extractor using Ollama HTTP API; returns list[str]."""
    text = (text or "").strip()
    if not text:
        return []

    system_prompt = (
        "You extract action items from notes. "
        "Return ONLY valid JSON: an array of strings. "
        "No markdown, no explanation. "
        "Each string must be a concise action item starting with a verb. "
        "If none, return []."
    )

    prompt = f"SYSTEM:\n{system_prompt}\n\nUSER:\n{text}\n\nOUTPUT:\n"

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }

    try:
        resp = requests.post(
            f"{settings.ollama_host.rstrip('/')}/api/generate",
            json=payload,
            timeout=settings.ollama_timeout_sec,
        )
        resp.raise_for_status()
        raw = (resp.json().get("response") or "").strip()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("[")
            end = raw.rfind("]")
            if start == -1 or end == -1 or end <= start:
                return []
            data = json.loads(raw[start : end + 1])

        if not isinstance(data, list):
            return []

        return [s.strip() for s in data if isinstance(s, str) and s.strip()]
    except Exception:
        return []
