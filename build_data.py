#!/usr/bin/env python3
"""Living Indexes — the hub. Aggregates each sibling index's published data.json (server-side,
at build time → no CORS) into one summary so the hub shows LIVE counts + top movers and links
out to each. Run daily by the GitHub Action so the hub stays in sync with the fleet.

Each index is self-updating on its own cron; this hub just reflects them.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://indexes.kymatalabs.com"   # fixed to the real alias after first deploy
SITE_NAME = "The Living Indexes"

# The fleet. `data` is each index's published data.json (read at build time).
INDEXES = [
    {"key": "skill", "name": "The Skill Index", "tag": "Skills",
     "blurb": "Claude Code & AI-agent skills — skills, subagents, slash-commands, hooks.",
     "url": "https://skill.kymatalabs.com", "accent": "#b3651f"},
    {"key": "eval", "name": "The Eval Index", "tag": "Evals",
     "blurb": "LLM & agent evaluation, benchmark, observability and red-teaming tools.",
     "url": "https://eval.kymatalabs.com", "accent": "#7fae2c"},
    {"key": "local", "name": "The Local LLM Index", "tag": "Local",
     "blurb": "Run LLMs on your own hardware — inference engines, runners, quantization.",
     "url": "https://localllm.kymatalabs.com", "accent": "#1f5bff"},
    {"key": "prompt", "name": "The Prompt Index", "tag": "Prompts",
     "blurb": "Prompt-engineering resources — collections, system prompts, optimizers, guides.",
     "url": "https://prompt.kymatalabs.com", "accent": "#ff3b2f"},
    {"key": "rag", "name": "The RAG Index", "tag": "RAG",
     "blurb": "Retrieval-augmented-generation — RAG frameworks, vector DBs, embeddings, reranking.",
     "url": "https://rag.kymatalabs.com", "accent": "#5b4bff"},
    {"key": "diffusion", "name": "The Diffusion Index", "tag": "Image/Video",
     "blurb": "AI image & video generation — diffusion models, ComfyUI nodes, video gen, editing, training.",
     "url": "https://diffusion.kymatalabs.com", "accent": "#c77dff"},
    {"key": "voice", "name": "The Voice AI Index", "tag": "Voice",
     "blurb": "Voice & speech AI — text-to-speech, speech recognition, voice cloning, realtime voice agents.",
     "url": "https://voice.kymatalabs.com", "accent": "#b6ff2e"},
    {"key": "finetune", "name": "The Fine-Tuning Index", "tag": "Fine-Tuning",
     "blurb": "Make your own model — fine-tuning frameworks, PEFT/LoRA, RLHF/DPO, training data.",
     "url": "https://finetune.kymatalabs.com", "accent": "#ff6a00"},
    # The original four trackers — same self-updating pattern, different data.json shapes
    # (so each carries a `count_key`). They predate the `count`/`items` schema.
    {"key": "stack", "name": "StackTracker", "tag": "Infra",
     "blurb": "The live momentum index for AI-infrastructure repos.",
     "url": "https://stacktracker.kymatalabs.com", "accent": "#00d4a0"},
    {"key": "model", "name": "Model Radar", "tag": "Models",
     "blurb": "What's surging on Hugging Face right now — models ranked by momentum.",
     "url": "https://modelradar.kymatalabs.com", "accent": "#d946ef", "count_key": "model_count"},
    {"key": "mcp", "name": "The MCP Index", "tag": "MCP",
     "blurb": "Every Model Context Protocol server, in one living index.",
     "url": "https://mcp.kymatalabs.com", "accent": "#06b6d4", "count_key": "server_count"},
    {"key": "agentvel", "name": "Agent Velocity", "tag": "Agents",
     "blurb": "The open-source coding-agent race, ranked by velocity.",
     "url": "https://agentvelocity.kymatalabs.com", "accent": "#f59e0b", "count_key": "repo_count"},
]


def fetch_summary(idx: dict) -> dict:
    """Pull the live count + top mover + top categories from an index's data.json. Fail-soft:
    a sibling being momentarily down degrades to nulls, never sinks the hub build. Handles BOTH
    schemas — the new indexes ({count, items, categories:[{name}]}) and the original trackers
    (which carry a `count_key` like repo_count/model_count/server_count and varied shapes)."""
    out = {**idx, "count": None, "top": None, "categories": [], "generated_at": None}
    try:
        req = urllib.request.Request(idx["url"] + "/data.json",
                                     headers={"User-Agent": "living-indexes"})
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read())
        out["count"] = d.get(idx.get("count_key", "count"))
        out["generated_at"] = d.get("generated_at")
        # categories may be [{name}], [str], or a {name:count} dict — normalize to up-to-4 names
        cats = d.get("categories")
        if isinstance(cats, dict):
            names = list(cats.keys())
        elif isinstance(cats, list):
            names = [c.get("name") if isinstance(c, dict) else c for c in cats]
        else:
            names = []
        out["categories"] = [n for n in names if n][:4]
        # top mover: new schema uses `items`; trackers use `repos`/`trending`/`movers`
        items = d.get("items") or d.get("repos") or d.get("trending") or d.get("movers") or []
        if items and isinstance(items[0], dict):
            it = items[0]
            out["top"] = {"name": it.get("full_name") or it.get("name") or it.get("repo"),
                          "momentum": it.get("momentum") or it.get("score")}
    except Exception as e:
        print(f"  {idx['key']} summary failed: {e}", file=sys.stderr)
    return out


def main() -> int:
    summaries = [fetch_summary(i) for i in INDEXES]
    total = sum(s["count"] or 0 for s in summaries)
    data = {"generated_at": datetime.now(timezone.utc).isoformat(),
            "total_indexed": total, "indexes": summaries}
    with open(os.path.join(HERE, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    # SEO: sitemap + robots + llms.txt (the hub is a single page + the 4 outbound links)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    open(os.path.join(HERE, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'  <url><loc>{SITE_URL}/</loc><lastmod>{now}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>\n'
        '</urlset>\n')
    open(os.path.join(HERE, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    lines = [f"# {SITE_NAME}", "",
             "> A hub for self-updating indexes of the AI-builder ecosystem. Each index is",
             "> recomputed daily from live GitHub signals.", "",
             f"Updated: {data['generated_at']}  ·  {total} entries across {len(summaries)} indexes", ""]
    for s in summaries:
        lines.append(f"- [{s['name']}]({s['url']}) — {s['count']} entries — {s['blurb']}")
    open(os.path.join(HERE, "llms.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

    print(f"hub data: {total} total across {len(summaries)} indexes")
    for s in summaries:
        print(f"  {s['name']}: {s['count']} (top {s['top']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
