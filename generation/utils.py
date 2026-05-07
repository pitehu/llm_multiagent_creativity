# utils.py

import tiktoken
from tiktoken import encoding_for_model
import transformers

def calculate_tokens(messages, model="gpt-4o"):
    """
    Calculate the number of tokens used in a list of messages or parsed content.
    Each input should be a dictionary with 'role' and 'content', or a parsed object.
    """
    if model.startswith("deepseek"):
        tokenizer = transformers.AutoTokenizer.from_pretrained("deepseek-ai/deepseek-tokenizer", trust_remote_code=True)
    elif model in ['o1-mini', 'o3-mini']:
        encoding = tiktoken.get_encoding("cl100k_base")  # Compatible encoding
    else:
        encoding = encoding_for_model(model)
    token_count = 0

    for msg in messages:
        if isinstance(msg, dict) and "content" in msg:
            content = msg["content"]
        elif isinstance(msg, str):
            content = msg
        else:
            from pydantic import BaseModel
            if isinstance(msg, BaseModel):
                content = msg.json()
            elif isinstance(msg, dict):
                import json
                content = json.dumps(msg)
            else:
                raise ValueError("Unsupported message format for token calculation.")

        if model.startswith("deepseek"):
            token_count += len(tokenizer.encode(content))
        else:
            token_count += len(encoding.encode(content))

    return token_count

