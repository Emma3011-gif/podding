# Migration from OpenAI to OpenRouter

This project has been migrated from OpenAI API to OpenRouter, which provides access to multiple AI models through a unified API.

## What Changed

- **API Provider**: OpenAI → OpenRouter
- **Environment Variables**:
  - `OPENAI_API_KEY` → `OPENROUTER_API_KEY`
  - Added `OPENROUTER_MODEL` (optional, defaults to `openai/gpt-4o-mini`)
- **Base URL**: Direct OpenAI API → `https://openrouter.ai/api/v1`
- **Headers**: Added `HTTP-Referer` and `X-Title` for OpenRouter attribution

## Getting Started with OpenRouter

### 1. Get Your OpenRouter API Key

1. Go to [OpenRouter.ai](https://openrouter.ai)
2. Sign up or log in
3. Navigate to **[API Keys](https://openrouter.ai/api-keys)**
4. Click "Create Key"
5. Copy your key (starts with `sk-or-`)

### 2. Configure Your `.env` File

Edit the `.env` file:

```bash
OPENROUTER_API_KEY=sk-or-your-actual-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini
```

### 3. Choose a Model (Optional)

Popular models available on OpenRouter:

| Model ID | Description |
|----------|-------------|
| `openai/gpt-4o-mini` | Fast, affordable (default) |
| `openai/gpt-4o` | Most capable OpenAI model |
| `anthropic/claude-3-haiku` | Fast, accurate |
| `anthropic/claude-3-sonnet` | Balanced performance |
| `google/gemini-pro-1.5` | Google's flagship model |
| `meta-llama/llama-3.1-70b-instruct` | Open source powerhouse |

See all models: https://openrouter.ai/models

### 4. Install Updated Dependencies

```bash
pip install -r requirements.txt
```

### 5. Restart Your Servers

```bash
# Backend (Terminal 1)
python backend.py

# Frontend (Terminal 2)
python app.py
```

## Benefits of OpenRouter

- **Lower costs**: Often cheaper than direct OpenAI API
- **Model choice**: Access to OpenAI, Anthropic, Google, Meta, and more
- **Unified API**: Same interface for all providers
- **Fallback options**: Easy to switch models if one is unavailable

## Troubleshooting

### "Invalid API key"
Double-check your `OPENROUTER_API_KEY` in `.env`. OpenRouter keys start with `sk-or-`.

### "Model not found"
Check that your model ID is correct. Update `OPENROUTER_MODEL` in `.env` with a valid model.

### "Insufficient quota"
Add credits to your OpenRouter account at https://openrouter.ai/account/billing

### API Errors
Check the backend terminal for detailed error messages. OpenRouter returns clear error descriptions.
