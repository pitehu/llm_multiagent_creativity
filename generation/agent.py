# agent.py

from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE
from utils import calculate_tokens
from azure_model_service import AzureModelService
from deepseek_model_service import DeepSeekModelService
from genai_model_service import GeminiModelService

class Agent:
    def __init__(self, name, system_message, model_name, config=None):
        self.name = name
        self.system_message = system_message.strip()
        self.config = config if config else {}
        self.model_name = model_name
        self.history = []
        self.model_service = self._get_model_service(self.model_name)
    
    def _get_model_service(self, model_name):
        """
        Selects the appropriate model service based on the model name.
        """
        if model_name == 'deepseek-ai/DeepSeek-R1':
            return DeepSeekModelService()
        elif model_name in ['gemini-2.0-flash-thinking-exp','gemini-2.5-pro-preview-05-06','gemini-2.5-pro']:
            return GeminiModelService()
        elif model_name in ["o1-mini", "o3-mini","o4-mini", "gpt-4o", "o1",'gpt-4.1','o3']:
            return AzureModelService()
        else:
            raise ValueError(f"Unsupported model: {model_name}")

    def generate_response(self, messages):
        """
        Generate a response using OpenAI API and return the reply along with token counts.
        """
        temperature = self.config.get("temperature", DEFAULT_TEMPERATURE)
        reasoning_effort = self.config.get("reasoning_effort", None)

        args = {
            "messages": messages,
            "model": self.model_name,
            "temperature": temperature
        }
        if reasoning_effort is not None:
            args["reasoning_effort"] = reasoning_effort

        try:
            response, prompt_tokens, completion_tokens, reasoning_tokens = self.model_service.generate_response(**args)

            self.history.append({"role": "assistant", "content": response})

            # Return the reply and token counts
            return response, prompt_tokens, completion_tokens, reasoning_tokens
            
        except Exception as e:
            print(f"Error generating response: {e}")
            # This should now be very rare since retries happen at the service level
            return "(No response due to error)", 0, 0, 0
