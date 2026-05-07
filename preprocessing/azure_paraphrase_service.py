#!/usr/bin/env python3
# azure_paraphrase_service.py
import os
import json
import time
import logging
from openai import AzureOpenAI
from typing import Optional, Tuple

class AzureParaphraseService:
    """
    Azure OpenAI service specifically designed for paraphrasing tasks.
    Handles content filtering gracefully by returning None for filtered content.
    """
    
    def __init__(self):
        # Load configuration from environment variables
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not endpoint or not api_key:
            raise ValueError("Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY before running paraphrasing.")

        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2024-12-01-preview"
        )


        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def paraphrase_idea(self, idea: str, max_words: int = 100, max_retries: int = 3) -> Optional[str]:
        """
        Paraphrase a single idea using GPT-4.1.
        Returns None if content is filtered or other errors occur.
        
        Args:
            idea (str): The original idea to paraphrase
            max_words (int): Maximum word count for the paraphrased idea
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            Optional[str]: Paraphrased text or None if filtered/failed
        """
#         messages = [
#             {
#                 "role": "system",
#                 "content": f"""You are an AI assistant that rephrases ideas. Your main goal is to accurately convey the core meaning of the provided text.
#
# A key aspect of your task is to use a **clear, neutral, and consistent writing style for all your paraphrases,** regardless of the style of the original idea. This helps ensure uniformity.
#
# - Be concise: If the original idea is lengthy, shorten it. If it's already brief, simply rewrite the idea while preserving its essence and approximate length.
# - Stick to the original meaning: Do not add any new information, context, or your own opinions.
# - Direct output: Provide only the rephrased idea, without any introductory or concluding phrases.
# - Use THIRD-PERSON perspective only. Never use "we", "I", "you", "us", or "our" but maintain natural language use.
# - Use active voice when possible and replace informal language with professional but broadly accessible alternatives
# - Start the paraphrase with a verb - select verbs that reflect the specific nature of each idea. Crucially, do not use instructional verbs that issue a command to the reader (like "describe," "show," or "list").
# """
#             },
#             {
#                 "role": "user",
#                 "content": f"Paraphrase this idea in under {max_words} words, following all system guidelines: {idea}"
#             }
#         ]
#
        # messages = [
        #     {
        #         "role": "system",
        #         "content": f"""You are an AI assistant that rephrases ideas. Your main goal is to accurately convey the core meaning of the provided text.
        #
        # **Text Processing Instructions:**
        # - If the text contains "evolve [X] into [Y]" or similar transformation language, focus only on the final concept (Y) and ignore the initial concept (X).
        # - If the text contains multiple ideas with clear section headers (like "---Final Idea---" or "---One Creative Idea---"), focus only on the content under the final/main idea section.
        # - If the text contains multiple ideas without clear hierarchy, treat the entire content as one comprehensive idea.
        # - Remove any brainstorming artifacts, transitional phrases, or development language that doesn't contribute to the core concept.
        #
        # **Writing Style Requirements:**
        # - Use a **clear, neutral, and consistent writing style** regardless of the original text's style.
        # - Be concise: If the original idea is lengthy, shorten it. If it's already brief, rewrite while preserving its essence and approximate length.
        # - Stick to the original meaning: Do not add new information, context, or opinions.
        # - Direct output: Provide only the rephrased idea, without introductory or concluding phrases.
        # - Use THIRD-PERSON perspective only. Never use "we", "I", "you", "us", or "our" but maintain natural language.
        # - Use active voice when possible and replace informal language with professional but accessible alternatives.
        # - Start the paraphrase with a verb that reflects the specific nature of the idea. Do not use instructional verbs that command the reader (like "describe," "show," or "list").
        # """
        #     },
        #     {
        #         "role": "user",
        #         "content": f"Paraphrase this idea in under {max_words} words, following all system guidelines: {idea}"
        #     }
        # ]

        messages = [
            {
                "role": "system",
                "content": f"""You are an AI assistant that rephrases ideas. Your main goal is to accurately convey the core meaning of the provided text in a natural, accessible way.

        **Text Processing Instructions:**
        - If the text contains "evolve [X] into [Y]" or similar transformation language, focus only on the final concept (Y) and ignore the initial concept (X).
        - If the text contains multiple ideas with clear section headers (like "---Final Idea---" or "---One Creative Idea---"), focus only on the content under the final/main idea section.
        - If the text contains multiple ideas without clear hierarchy, treat the entire content as one comprehensive idea.
        - Remove any brainstorming artifacts, transitional phrases, or development language that doesn't contribute to the core concept.

        **Writing Style Requirements:**
        - Use a **clear, neutral, and straightforward writing style** regardless of the original text's style.
        - Simplify complex or technical language while preserving core meaning - choose everyday words over specialized terminology when possible.
        - Remove branded terms, metaphorical names in quotes, and elaborate descriptive phrases that don't add essential information.
        - Break down dense technical concepts into simpler, more digestible explanations.
        - Be concise: If the original idea is lengthy, shorten it. If it's already brief, rewrite while preserving its essence and approximate length.
        - Stick to the original meaning: Do not add new information, context, or opinions.
        - Direct output: Provide only the rephrased idea, without introductory or concluding phrases.
        - Use THIRD-PERSON perspective only. Never use "we", "I", "you", "us", or "our" but maintain natural language.
        - Use active voice when possible and replace overly formal or technical language with clear, accessible alternatives.
        - Reduce technical density: If the original lists many technical specifications or components, focus on the main mechanism and primary benefits.
        - Use conversational sentence structure rather than academic or highly technical phrasing.
        """
            },
            {
                "role": "user",
                "content": f"Paraphrase this idea in under {max_words} words using simple, clear language that anyone can understand: {idea}"
            }
        ]


        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4.1",
                    messages=messages,
                    temperature=0.0,
                    max_tokens=200,
                    timeout=30
                )
                
                paraphrased_text = response.choices[0].message.content.strip()
                self.logger.debug(f"Successfully paraphrased idea (attempt {attempt + 1})")
                return paraphrased_text
                
            except Exception as e:
                error_message = str(e).lower()
                
                # Check if this is a content filtering error
                if any(keyword in error_message for keyword in [
                    'content_filter', 'content management policy', 
                    'responsibleaipolicyviolation', 'filtered'
                ]):
                    self.logger.warning(f"Content filtered for idea: {idea[:50]}...")
                    return None  # Return None for filtered content
                
                # Check if this is a rate limiting error
                elif any(keyword in error_message for keyword in [
                    'rate limit', 'quota', 'too many requests'
                ]):
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    self.logger.warning(f"Rate limited, waiting {wait_time} seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                
                # For other errors, log and retry
                else:
                    self.logger.warning(f"API error on attempt {attempt + 1}/{max_retries}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Brief pause before retry
                        continue
        
        # If all retries failed
        self.logger.error(f"Failed to paraphrase after {max_retries} attempts: {idea[:50]}...")
        return None
    
    def batch_paraphrase(self, ideas: list, max_words: int = 100, progress_callback=None) -> list:
        """
        Paraphrase a batch of ideas.
        
        Args:
            ideas (list): List of ideas to paraphrase
            max_words (int): Maximum word count for each paraphrased idea
            progress_callback (callable): Optional callback function for progress updates
            
        Returns:
            list: List of paraphrased ideas (None for filtered/failed items)
        """
        results = []
        
        for i, idea in enumerate(ideas):
            result = self.paraphrase_idea(idea, max_words)
            results.append(result)
            
            if progress_callback:
                progress_callback(i + 1, len(ideas), result is not None)
        
        return results
    
    def get_model_info(self) -> dict:
        """Get information about the service configuration."""
        return {
            "endpoint": self.endpoint,
            "api_version": self.api_version,
            "model": "gpt-4.1"
        } 
