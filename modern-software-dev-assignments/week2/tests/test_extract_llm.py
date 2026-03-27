import os
import pytest
from unittest.mock import patch

from ..app.services.extract import extract_action_items, extract_action_items_llm


class DummyResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


# Test 1: Bullet list input (LLM)
def test_extract_llm_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    fake_llm_output = {
        "response": '["Set up database", "implement API extract endpoint", "Write tests"]'
    }

    with patch("requests.post", return_value=DummyResponse(fake_llm_output)):
        items = extract_action_items_llm(text)

    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


# Test 2: Keyword-prefixed lines (LLM)
def test_extract_llm_keyword_prefixed_lines():
    text = """
    TODO: email John about contract
    Action: book meeting room for Friday
    FYI: next week is holiday
    """.strip()

    fake_llm_output = {
        "response": '["Email John about contract", "Book meeting room for Friday"]'
    }

    with patch("requests.post", return_value=DummyResponse(fake_llm_output)):
        items = extract_action_items_llm(text)

    assert "Email John about contract" in items
    assert "Book meeting room for Friday" in items
    # ensure it doesn't invent FYI line
    assert all("holiday" not in x.lower() for x in items)


# Test 3: Empty input (LLM) — không được gọi HTTP
def test_extract_llm_empty_input_returns_empty_and_no_http_call():
    with patch("requests.post") as mocked_post:
        items = extract_action_items_llm("   ")

    assert items == []
    mocked_post.assert_not_called()


# (Rất nên) Test 4: LLM trả về kèm chữ, hàm vẫn recover JSON
def test_extract_llm_recovers_json_array_from_text():
    text = "Remember to do A and B."

    fake_llm_output = {
        "response": 'Sure! Here you go:\n["Do A", "Do B"]\nThanks!'
    }

    with patch("requests.post", return_value=DummyResponse(fake_llm_output)):
        items = extract_action_items_llm(text)

    assert items == ["Do A", "Do B"]


# (Tuỳ chọn) Test 5: Ollama lỗi HTTP → trả []
def test_extract_llm_http_error_returns_empty():
    text = "Do something"

    with patch("requests.post", return_value=DummyResponse({"response": ""}, status_code=500)):
        items = extract_action_items_llm(text)

    assert items == []
