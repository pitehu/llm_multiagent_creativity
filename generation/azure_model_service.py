# azure_model_service.py
import os
import logging
from openai import AzureOpenAI
from base_model_service import BaseModelService 
from tenacity import retry, wait_random_exponential, stop_after_attempt



class AzureModelService(BaseModelService):
    """
    Model service for interacting with Azure OpenAI.
    """
    def __init__(self):
        default_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        default_key = os.getenv("AZURE_OPENAI_API_KEY")
        reasoning_endpoint = os.getenv("AZURE_OPENAI_O3O4MINI_ENDPOINT", default_endpoint)
        reasoning_key = os.getenv("AZURE_OPENAI_O3O4MINI_API_KEY", default_key)

        if not default_endpoint or not default_key:
            raise ValueError("Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY before running generation.")

        self.default_client = AzureOpenAI(
            azure_endpoint=default_endpoint,
            api_key=default_key,
            api_version="2024-12-01-preview"
        )
        self.o3_o4mini_client = AzureOpenAI(
            azure_endpoint=reasoning_endpoint,
            api_key=reasoning_key,
            api_version="2024-12-01-preview"
        )

    def _get_client_for_model(self, model):
        # Add all o3/o4mini model names as needed
        if model and (model.startswith("o3") or model.startswith("o4mini")):
            return self.o3_o4mini_client
        return self.default_client



    @retry(wait=wait_random_exponential(min=0.1, max=1), stop=stop_after_attempt(1000))
    def generate_response(self, messages, model=None, temperature=1.0, reasoning_effort=None):
        """
        Generates a response using Azure OpenAI.
        """
        # Build the kwargs for the API call
        client = self._get_client_for_model(model)

        api_kwargs = {
            "model": model,
            "messages": messages,
        }
        # Only add temperature for non-reasoning models (if needed)
        if model not in ['o1-mini', 'o3-mini', 'o4-mini', 'o1','o3']:
            api_kwargs["temperature"] = temperature

        # Add reasoning_effort if provided
        if reasoning_effort:
            api_kwargs["reasoning_effort"] = reasoning_effort

        response = client.chat.completions.create(**api_kwargs)

        # Handle reasoning tokens if available
        if model in ['o1-mini', 'o3-mini', 'o4-mini', 'o1','o3']:
            reasoning_tokens = response.usage.completion_tokens_details.reasoning_tokens
        else:
            reasoning_tokens = 0

        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens

        return response.choices[0].message.content.strip(), prompt_tokens, completion_tokens, reasoning_tokens

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(1000))
    def parse_response(self, messages, temperature = 0, model=None, response_model=None):
        """
        Parses a response using Azure OpenAI. This is a conceptual method.
        """
        client = self._get_client_for_model(model)

        response = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format=response_model  # This parameter is hypothetical
        )
        return response
