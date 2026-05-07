# Multi-Agent Chatlog Generation Code

This folder contains the code used to generate the LLM multi-agent chat logs.

The manuscript uses the label `progressive` for a discussion method that appears in the original generation code and raw filenames as `creative`. The labels refer to the same experimental condition; the manuscript label was updated after the generation runs.

## Files

- `batch_run.py`: batch configuration grid used for multi-agent LLM runs.
- `main.py`: single-run entry point.
- `agent.py`, `conversation.py`, `discussion_modes.py`, `data_strategies.py`, `message_strategies.py`: multi-agent orchestration and logging.
- `prompts.py`, `roles.py`: task prompts and agent role/persona definitions.
- `*_model_service.py`: provider-specific model adapters.
- `config.py` and `config.example.py`: minimal default model/temperature configuration.

## Credentials

No API keys are included. Set provider credentials in environment variables before running:

```bash
export AZURE_OPENAI_ENDPOINT="..."
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_O3O4MINI_ENDPOINT="..."      # optional separate endpoint
export AZURE_OPENAI_O3O4MINI_API_KEY="..."       # optional separate key
export AZURE_AI_INFERENCE_ENDPOINT="..."         # for DeepSeek via Azure AI Inference
export AZURE_AI_INFERENCE_API_KEY="..."
export GOOGLE_CLOUD_PROJECT="..."                # for Gemini/Vertex AI
export GOOGLE_CLOUD_LOCATION="global"
```

## Running

Run one configuration through `main.py`, or edit/run `batch_run.py` for a batch. Outputs are written to `results/<question_id>/`.

Warning: regenerating the full LLM chatlog corpus can take a long time and use a substantial amount of paid API credits. The batch grid includes many multi-agent, multi-round conversations, and some conditions call multiple hosted models. Start with a small subset or a single configuration before running the full batch.

Generation depends on external hosted model APIs. Re-running the generation code documents the original workflow, but exact text outputs are not expected to be bitwise reproducible because provider models and serving systems can change over time.
