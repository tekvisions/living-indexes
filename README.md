# The Living Indexes

A hub for self-updating indexes of the AI-builder ecosystem. Each index is its own site,
recomputed daily from live GitHub signals; this hub aggregates their live counts and links out.

Live: https://the-living-indexes.vercel.app

The fleet:
- [The Skill Index](https://skill.kymatalabs.com) — Claude Code & AI-agent skills
- [The Eval Index](https://eval.kymatalabs.com) — LLM & agent evaluation/benchmark tools
- [The Local LLM Index](https://localllm.kymatalabs.com) — run LLMs locally / on-device
- [The Prompt Index](https://prompt.kymatalabs.com) — prompt-engineering resources

## How it works

`build_data.py` fetches each index's published `data.json` server-side (no CORS) and writes a
combined summary (`data.json`) with live counts + top movers. A daily GitHub Action refreshes it
and redeploys to Vercel. Static HTML/CSS/JS; premium dark hub aesthetic (Instrument Serif +
JetBrains Mono).

## Run locally

```bash
python3 build_data.py && python3 gen_og.py
python3 -m http.server 8080
```
