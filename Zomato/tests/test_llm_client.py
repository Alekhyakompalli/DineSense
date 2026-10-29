"""
tests/test_llm_client.py
─────────────────────────
Unit tests for services/llm_client.py.
Tests client initializations, retry backoff logic, and exception handling.
"""

from unittest.mock import patch, MagicMock
import pytest
from services.llm_client import LLMClient


def test_init_gemini_client():
    """Verify Gemini client initializes using google.generativeai."""
    with patch("google.generativeai.configure") as mock_conf, \
         patch("google.generativeai.GenerativeModel") as mock_model:
        client = LLMClient(provider="gemini")
        assert client.provider == "gemini"
        mock_conf.assert_called_once()
        mock_model.assert_called_once()


def test_init_openai_client():
    """Verify OpenAI client initializes using openai.OpenAI."""
    with patch("openai.OpenAI") as mock_openai:
        client = LLMClient(provider="openai")
        assert client.provider == "openai"
        mock_openai.assert_called_once()


def test_init_unknown_provider_raises():
    """Unknown provider string must raise ValueError."""
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        LLMClient(provider="unknown_ai")


def test_complete_retries_and_succeeds():
    """complete() must retry on failure with backoff and return when successful."""
    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel"):
        client = LLMClient(provider="gemini")

    # Mock _call to fail once then succeed
    client._call = MagicMock(side_effect=[Exception("Transient network glitch"), "Success response"])

    with patch("time.sleep") as mock_sleep:
        res = client.complete("system prompt", "user prompt", retries=2)
        assert res == "Success response"
        assert client._call.call_count == 2
        mock_sleep.assert_called_once_with(2)


def test_complete_raises_runtime_error_when_all_retries_fail():
    """complete() must raise RuntimeError after exhausting all retries."""
    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel"):
        client = LLMClient(provider="gemini")

    client._call = MagicMock(side_effect=Exception("API Down"))

    with patch("time.sleep"):
        with pytest.raises(RuntimeError, match="failed after all 3 retries"):
            client.complete("sys", "user", retries=3)
        assert client._call.call_count == 3

