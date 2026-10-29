"""
services/llm_client.py
───────────────────────
Pluggable LLM client supporting Google Gemini (default), OpenAI, and HuggingFace providers.
Includes retry logic with exponential backoff.
"""

import time
from config.settings import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    GOOGLE_API_KEY,
    HUGGINGFACE_TOKEN,
    GEMINI_MODEL,
    OPENAI_MODEL,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Wrapper around LLM providers with automatic retry and backoff."""

    def __init__(self, provider: str = LLM_PROVIDER):
        self.provider = provider.lower().strip()
        self._init_client()

    def _init_client(self) -> None:
        if self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            self.client = genai.GenerativeModel(GEMINI_MODEL)
            logger.info(f"Initialized Gemini client using model: {GEMINI_MODEL}")
        elif self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info(f"Initialized OpenAI client using model: {OPENAI_MODEL}")
        elif self.provider == "huggingface":
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(token=HUGGINGFACE_TOKEN)
            logger.info("Initialized HuggingFace Inference client")
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    def complete(self, system_prompt: str, user_prompt: str, retries: int = 3) -> str:
        """
        Execute completion with exponential backoff on transient errors.

        Args:
            system_prompt: System prompt / persona and rules.
            user_prompt: User query containing criteria and candidates.
            retries: Number of retry attempts.

        Returns:
            str: Raw textual response from the model.

        Raises:
            RuntimeError: If all retry attempts fail.
        """
        for attempt in range(1, retries + 1):
            try:
                logger.info(f"LLM call attempt {attempt}/{retries} via {self.provider}")
                return self._call(system_prompt, user_prompt)
            except Exception as e:
                logger.warning(f"LLM call failed (attempt {attempt}/{retries}): {e}")
                if attempt < retries:
                    sleep_time = 2 ** attempt
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
        raise RuntimeError(f"LLM API ({self.provider}) failed after all {retries} retries.")

    def _call(self, system_prompt: str, user_prompt: str) -> str:
        if self.provider == "gemini":
            # Gemini models accept system instruction or combined prompt
            combined = f"{system_prompt}\n\n{user_prompt}"
            response = self.client.generate_content(combined)
            return response.text

        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content

        elif self.provider == "huggingface":
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ]
            response = self.client.chat_completion(
                messages=messages,
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                max_tokens=1000
            )
            return response.choices[0].message.content
