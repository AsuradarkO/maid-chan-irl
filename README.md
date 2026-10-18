# Maid-chan IRL — a real offline AI companion

A fully offline AI assistant running on a regular laptop: chat plus voice notes with spoken replies, no cloud, no API keys, no accounts. Built around an Ollama-hosted language model with a custom personality, a phone web app served over a private tunnel, and a local speech pipeline.

## How it works

| Piece | Role |
|---|---|
| Ollama + `qwen3:4b` (custom `Modelfile`) | The brain — Maid-chan's personality, tuned for an 8 GB machine |
| Flask server + installable phone web app (PWA) | Chat UI, served over a Tailscale private tunnel |
| Piper TTS (`en_US-amy-medium`) | Her voice |
| faster-whisper (`base.en`) + ffmpeg | Her ears (speech → text) |

The pipeline runs sequentially (listen → think → speak), never overlapping — a deliberate RAM-budgeting decision for machines without a GPU.

## What's here

- `Modelfile` — the Ollama model definition: personality system prompt, context window and sampling tuned for low RAM
- `personality.md` — Maid-chan's character spec (cheerful, teasing AI assistant with a defined voice)
- `app/server.py` + `app/static/` — Flask server and the installable phone UI
- `SETUP.md`, `SETUP-PART2.md` — step-by-step install guides for the laptop brain and the phone app
- `SMOKE-TEST.md` — verification checklist for each stage

## Status

In progress — guides and code complete; laptop install is the next step.

## Why it matters

Designing an AI system under hard constraints (8 GB RAM, no GPU, fully offline) forces real tradeoffs: model quantization choices, sequential vs. parallel pipelines, context-window budgeting. This project is those tradeoffs, documented.

---
*Built with Muse (Meta's AI assistant) — architecture, code, and docs directed and specified by Vince Pham.*
