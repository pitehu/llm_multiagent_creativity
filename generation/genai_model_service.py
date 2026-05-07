# gemini_model_service.py
from google import genai
from base_model_service import BaseModelService  # Import the base class
import re
import os
from tenacity import retry, wait_random_exponential, stop_after_attempt
import random
class GeminiModelService(BaseModelService):
    """
    Model service for interacting with Google's Gemini API.
    """
    def __init__(self):
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
        if not project:
            raise ValueError("Set GOOGLE_CLOUD_PROJECT before running Gemini generation.")
        self.client = genai.Client(
            vertexai=True, project=project, location=location
        )

    @retry(wait=wait_random_exponential(min=0.5, max=5), stop=stop_after_attempt(1000))
    def generate_response(self, messages, model="gemini-2.0-flash-thinking-exp",temperature=0.7):
        """
        Generates a response using Google's Gemini API.
        """
        # Convert messages into a format Gemini API accepts
        prompt = "\n".join([msg["content"] for msg in messages if "content" in msg])

        # Make API call
        response = self.client.models.generate_content(
            model=model,
            contents=prompt
        )

        # Extract token usage (if available)
        prompt_tokens = response.usage_metadata.prompt_token_count
        completion_tokens = response.usage_metadata.candidates_token_count
        reasoning_tokens = response.usage_metadata.thoughts_token_count

        return response.text, prompt_tokens, completion_tokens, reasoning_tokens
