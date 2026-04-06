# Performance Optimization Guide

This document explains how to optimize the PDF Q&A Assistant for speed.

## Quick Wins

### 1. Use a Faster Model (Biggest Impact)

Your model choice dramatically affects response time:

| Model | Speed | Quality | Cost | Notes |
|-------|-------|---------|------|-------|
| `openai/gpt-4o-mini` | ⚡⚡⚡ Fast | Good | Low | **Recommended** - Best balance |
| `anthropic/claude-3-haiku` | ⚡⚡ Fast | Good | Low | Excellent for Q&A |
| `stepfun/step-3.5-flash:free` | 🐢 Slow | Fair | Free | **Free but slow** - use only for testing |
| `openai/gpt-4o` | ⚡ Fast | Excellent | High | Great quality, decent speed |

**Change your model in `.env`:**
```env
OPENROUTER_MODEL=openai/gpt-4o-mini  # Fast and affordable!
```

### 2. Adjust Chunk Size

Larger chunks = fewer embedding API calls = faster processing.

```env
CHUNK_SIZE=1000  # Default, good balance
# CHUNK_SIZE=1500  # Even faster upload, slightly less precise
# CHUNK_SIZE=800   # More precise, slower upload
```

**Trade-offs:**
- Larger (1000-1500): Faster upload, slightly reduced search precision
- Smaller (300-500): Slower upload, more precise semantic search

### 3. Reduce Top-K Results

Fewer chunks in context = faster chat responses.

```env
TOP_K_RESULTS=3  # Faster responses, slightly less context
# TOP_K_RESULTS=5  # Default - balanced
# TOP_K_RESULTS=7  # More context, slower responses
```

**Impact:** Reducing from 5 → 3 cuts context length by ~40% and speeds up generation.

## Optimizations Already Implemented

✅ **Embedding Cache** - Reuses embeddings for duplicate text chunks
✅ **Smart Chunking** - Splits at sentence boundaries for better context
✅ **Configurable Sizes** - Adjust via `.env` without code changes
✅ **Performance Logging** - Shows timing in backend console
✅ **Client Timeouts** - 30-second timeout prevents hanging
✅ **Parallel-friendly structure** - Easy to add async embedding later

## Troubleshooting Slow Performance

### Check Backend Logs

When you upload a PDF, the backend prints timing:

```
📄 Text extraction: 2.34s, 15000 chars
✂️  Chunking: 0.02s, 15 chunks (avg 1000 chars/chunk)
🔢 Embedding generation: 18.56s (15 embeddings)
✅ Total processing: 20.92s for 15 chunks
```

**What to look for:**
- **Embedding generation** taking >1s per chunk → Model is slow or rate-limited
- **Total processing** high → Many chunks or slow embedding API

### If Upload is Slow

**Cause:** Too many chunks × slow embedding model

**Solutions:**
1. Increase `CHUNK_SIZE` to 1000-1500
2. Use a faster embedding-capable model (OpenRouter supports OpenAI embeddings)
3. Check your OpenRouter credits - low credits may cause rate limiting

### If Chat Response is Slow

**Cause:** Slow chat model or too much context

**Solutions:**
1. Switch to `openai/gpt-4o-mini` or `anthropic/claude-3-haiku` (much faster than free models)
2. Reduce `TOP_K_RESULTS` to 3
3. Check context length: if using TOP_K=5 with large chunks, you might be sending 5000+ characters to the model

### If Rate Limited

**Signs:** "Rate limit exceeded" errors, slow embedding (5-10s per chunk)

**Solutions:**
1. Add credits to your OpenRouter account
2. Reduce `CHUNK_SIZE` to make fewer embedding calls
3. Wait a moment (OpenRouter free tier has limits)

## Expected Performance

With **`openai/gpt-4o-mini`** and recommended settings:

| Operation | Expected Time |
|-----------|---------------|
| Small PDF (5 pages, 2000 chars) | 3-5 seconds total |
| Medium PDF (20 pages, 10000 chars) | 8-15 seconds upload |
| Large PDF (100 pages, 50000 chars) | 30-60 seconds upload |
| Chat response (first token) | 0.5-2 seconds |
| Chat response (full answer) | 2-8 seconds (depends on answer length) |

With **`stepfun/step-3.5-flash:free`**:

| Operation | Expected Time |
|-----------|---------------|
| Small PDF | 10-20 seconds |
| Medium PDF | 30-60 seconds |
| Large PDF | 2-5 minutes |
| Chat response | 5-20 seconds |

**The free model is significantly slower.** Upgrade to a paid model for production use.

## Advanced Optimizations (Not Implemented)

These would require code changes:

1. **Async Embedding Generation** - Generate multiple embeddings in parallel
2. **Database Backend** - Replace in-memory DB with Redis/Postgres for persistence
3. **Embedding Model Caching** - Cache across documents (currently per-document only)
4. **Selective Re-embedding** - For updates, only re-embed changed chunks
5. **Compression** - Compress embeddings (use float16 instead of float64)

## Monitor Performance

Check backend logs for timing info. Each upload shows:
- Text extraction time
- Chunking time
- Embedding generation time (per-chunk average)
- Total processing time

Each chat response shows embedding + generation times in logs.

If you see embedding times >2s per chunk, consider:
- Switching to a faster model
- Adding more credits (rate limits slow you down)
- Reducing chunk count

## Production Recommendations

For production deployment:

1. **Use a fast model**: `openai/gpt-4o-mini` or `anthropic/claude-3-haiku`
2. **Set ENV=production** for better performance
3. **Increase timeout** if needed: `OPENROUTER_TIMEOUT=60` in .env (not yet implemented)
4. **Add monitoring** - Track response times with logging
5. **Use a CDN/edge** - Deploy backend closer to users

---

**Current configuration:** See your `.env` file for active settings.
