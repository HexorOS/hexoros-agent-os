# HexorOS — Agent OS Dashboard

A single-file React dashboard for coordinating self-hosted AI agents.
Part of the [HexorOS](https://hexoros.com) open agent infrastructure.

## What it shows

- **Agent registry** — live status of every running agent (chat, vault, infra, codegen)
- **Vault browser** — links between project notes, infra docs, and decisions
- **Mindmap view** — graph of agents, infra nodes, and product surfaces
- **Settings** — per-agent model, API key, system context

No build step. Open `index.html` in any modern browser.

## Run locally

```bash
git clone https://github.com/Cyberpunk2026nft/hexoros-agent-os.git
cd hexoros-agent-os
python3 -m http.server 8000
# open http://localhost:8000
```

Or just double-click `index.html`.

## Stack

- React 18 (via CDN)
- Babel standalone for in-browser JSX
- Anthropic / Ollama / HexorOS endpoints — configured per-agent in the Settings panel
- LocalStorage for client-side persistence — no backend required to run the UI

## Project context

This dashboard is the operator surface for HexorOS — a self-hosted, EU-resident
AI operating system. It coordinates streaming chat, tool calls, memory, and
sub-agent delegation across multiple machines.

Learn more at [hexoros.com](https://hexoros.com).

## Status

Public showcase build. The hosted HexorOS stack (inference engine, MCP servers,
mainstore) lives at `api.hexoros.com` and `hexoros.com`. This repo is the
front-end operator dashboard only.

---

© 2026 HexorOS · All rights reserved
