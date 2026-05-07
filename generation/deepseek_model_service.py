import os
import re
import logging  # Import the logging module
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential
from base_model_service import BaseModelService
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Set up a logger for your service
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the minimum level to log

# Create handlers (e.g., console handler and file handler)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Set console output level

# Create a file handler specifically for DeepSeek logs
file_handler = logging.FileHandler('deepseek_service.log')
file_handler.setLevel(logging.DEBUG)  # Log all debug info to file

# Create a formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

class DeepSeekModelService(BaseModelService):
    """
    Model service for interacting with Azure AI Inference for DeepSeek R1.
    """

    def __init__(self):
        self.endpoint = os.getenv("AZURE_AI_INFERENCE_ENDPOINT")
        self.api_key = os.getenv("AZURE_AI_INFERENCE_API_KEY")
        self.model_name = os.getenv("DEEPSEEK_MODEL_NAME", "DeepSeek-R1-0528")

        if not self.endpoint or not self.api_key:
            raise ValueError("Set AZURE_AI_INFERENCE_ENDPOINT and AZURE_AI_INFERENCE_API_KEY before running DeepSeek generation.")
        
        self.client = ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key),
            api_version="2024-05-01-preview"
        )
        logger.info("DeepSeekModelService initialized with Azure AI Inference.")

    def _convert_messages_to_azure_format(self, messages):
        """
        Convert messages from OpenAI format to Azure AI Inference format.
        """
        azure_messages = []
        for message in messages:
            role = message.get("role")
            content = message.get("content", "")
            
            if role == "system":
                azure_messages.append(SystemMessage(content=content))
            elif role == "user":
                azure_messages.append(UserMessage(content=content))
            elif role == "assistant":
                azure_messages.append(AssistantMessage(content=content))
            else:
                logger.warning(f"Unknown message role: {role}, treating as user message")
                azure_messages.append(UserMessage(content=content))
        
        return azure_messages

    @retry(wait=wait_random_exponential(min=0.1, max=1), stop=stop_after_attempt(1000))
    def generate_response(self, messages, model=None, temperature=0.6, max_retries=50):
        """
        Generates a response using Azure AI Inference for DeepSeek R1.
        Includes retry logic for incomplete thinking token pairs.
        """
        for attempt in range(max_retries):
            # Convert messages to Azure format
            azure_messages = self._convert_messages_to_azure_format(messages)
            
            # Log the request details (useful for debugging prompt issues)
            logger.debug(f"Sending request to Azure AI Inference with model: {self.model_name} (Attempt {attempt + 1}/{max_retries})")
            logger.debug(f"Messages: {messages}")
            logger.debug(f"Temperature: {temperature}")

            response = self.client.complete(
                messages=azure_messages,
                model=self.model_name,
                temperature=temperature,
                max_tokens=25600
            )
            
            # Add debugging for response metadata
            logger.debug(f"Response object type: {type(response)}")
            logger.debug(f"Response choices length: {len(response.choices) if hasattr(response, 'choices') else 'No choices'}")
            
            # Check if response was truncated
            was_truncated = False
            if hasattr(response, 'choices') and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice, 'finish_reason'):
                    logger.info(f"Finish reason: {choice.finish_reason}")
                    if choice.finish_reason == 'length':
                        logger.warning("Response was truncated due to max_tokens limit!")
                        was_truncated = True
            
            raw_content = response.choices[0].message.content
            logger.debug(f"Raw content length: {len(raw_content)} characters")
            logger.debug(f"Raw content starts with: {raw_content[:100]}...")
            logger.debug(f"Raw content ends with: ...{raw_content[-100:]}")
            logger.debug(f"\n--- FULL RAW CONTENT FROM MODEL ---\n{raw_content}")

            # Check for incomplete thinking token pairs
            think_count = raw_content.count('<think>')
            end_think_count = raw_content.count('</think>')
            
            has_incomplete_thinking = False
            should_retry = False
            
            if think_count != end_think_count:
                if think_count == 0 and end_think_count > 0:
                    # Truncated at beginning - we can parse this, no need to retry
                    logger.warning("Found closing </think> tags without opening <think> tags - likely truncated at beginning, will parse directly")
                    has_incomplete_thinking = True
                    should_retry = False
                elif think_count > 0 and end_think_count == 0:
                    # Truncated at end - should retry to get complete response
                    logger.warning("Found opening <think> tags without closing </think> tags - likely truncated at end")
                    has_incomplete_thinking = True
                    should_retry = True
                else:
                    # Other mismatch cases - should retry
                    logger.warning(f"Incomplete thinking tokens detected: {think_count} <think> tags, {end_think_count} </think> tags")
                    has_incomplete_thinking = True
                    should_retry = True
            
            # If we have incomplete thinking that requires retry and haven't reached max retries, try again
            if should_retry and attempt < max_retries - 1:
                logger.info(f"Retrying due to incomplete thinking tokens (attempt {attempt + 1}/{max_retries})")
                continue
            
            # If we've exhausted retries or have complete thinking, process the response
            content_after_think = raw_content  # Initialize

            # Check if the response contains thinking sections
            if '<think>' in raw_content and '</think>' in raw_content and think_count == end_think_count:
                logger.info("Complete thinking tags detected. Attempting removal.")
                # Remove all thinking sections (everything between <think> and </think> tags)
                content_after_think = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL)
                # Clean up any remaining tags if nested incorrectly
                content_after_think = content_after_think.replace('<think>', '').replace('</think>', '')
                logger.debug(f"\n--- CONTENT AFTER REGEX ATTEMPT ---\n{content_after_think}")
            elif '</think>' in raw_content and '<think>' not in raw_content:
                logger.warning("Found closing </think> tag without opening <think> tag - using content after </think>")
                # Handle case where only </think> is detected - use everything after the </think> tag
                think_end_index = raw_content.find('</think>')
                if think_end_index != -1:
                    content_after_think = raw_content[think_end_index + 8:].strip()  # 8 = len('</think>')
                    logger.info(f"Using response after </think> tag. Content length: {len(content_after_think)} characters")
                    logger.debug(f"Content after </think>: {content_after_think[:200]}...")
                else:
                    content_after_think = raw_content
                    logger.warning("Could not find </think> tag position, using raw content")
            elif '<think>' in raw_content and '</think>' not in raw_content:
                logger.warning("Found opening <think> tag without closing </think> tag - handling truncated response")
                # Handle truncated thinking - remove everything from <think> onwards
                think_start_index = raw_content.find('<think>')
                if think_start_index != -1:
                    content_after_think = raw_content[:think_start_index].strip()
                    logger.info("Removed truncated thinking section from end")
                else:
                    content_after_think = raw_content
            else:
                logger.info("No thinking tags detected or incomplete thinking after retries. Using raw content.")
                content_after_think = raw_content

            # Clean up extra whitespace
            content_after_think = content_after_think.strip()

            # Log final result with retry information
            if attempt > 0:
                logger.info(f"Successfully generated response after {attempt + 1} attempts")
            logger.info(f"\n--- FINAL CLEANED ANSWER ---\n{content_after_think}")

            # Azure AI Inference response structure may differ, so we'll handle token counts carefully
            prompt_tokens = getattr(response.usage, 'prompt_tokens', 0) if hasattr(response, 'usage') else 0
            completion_tokens = getattr(response.usage, 'completion_tokens', 0) if hasattr(response, 'usage') else 0
            reasoning_tokens = 0  # As per your existing logic

            logger.debug(f"Tokens - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Reasoning: {reasoning_tokens}")

            return content_after_think, prompt_tokens, completion_tokens, reasoning_tokens
        
        # If we've exhausted all internal retries, raise an exception so the decorator can retry
        raise Exception(f"Failed to get valid response after {max_retries} internal attempts")
