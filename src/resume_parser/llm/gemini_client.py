"""
GeminiClient — Thin wrapper around Google's Generative AI SDK.

Manages API key loading and provides a simple interface for
sending prompts to the Gemini model. Designed to be easily
removable when sharing code without API credentials.
"""

import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file if present
load_dotenv()


class GeminiClient:
    """Client for interacting with the Google Gemini API.

    Loads the API key from the GEMINI_API_KEY environment variable
    and provides a simple `generate()` method for text generation.

    Args:
        model_name: The Gemini model to use. Defaults to "gemini-2.0-flash".
        api_key: Optional API key override. If not provided, reads from
                 the GEMINI_API_KEY environment variable.

    Raises:
        ValueError: If no API key is available.
    """

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash",
        api_key: str | None = None,
    ):
        self._api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self._api_key:
            raise ValueError(
                "Gemini API key is required. Set the GEMINI_API_KEY "
                "environment variable or pass it directly."
            )

        self._model_name = model_name
        self._model = None  # Lazily initialized on first use
        logger.info("GeminiClient configured with model: %s", model_name)

    def _get_model(self):
        """Lazily initialize the Gemini model on first use."""
        if self._model is None:
            import google.generativeai as genai

            genai.configure(api_key=self._api_key)
            self._model = genai.GenerativeModel(self._model_name)
            logger.debug("Gemini model initialized: %s", self._model_name)
        return self._model

    def generate(self, prompt: str) -> str:
        """Send a prompt to the Gemini model and return the response text.

        Args:
            prompt: The text prompt to send to the model.

        Returns:
            The generated text response.

        Raises:
            RuntimeError: If the API call fails.
        """
        try:
            model = self._get_model()
            response = model.generate_content(prompt)
            result = response.text.strip()
            logger.debug("Gemini response length: %d characters", len(result))
            return result
        except Exception as exc:
            raise RuntimeError(
                f"Gemini API call failed: {exc}"
            ) from exc
