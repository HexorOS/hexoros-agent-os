# HexorOS — Agent OS Dashboard

[![Live Demo](https://img.shields.io/badge/live-demo-00f2ff?style=flat-square)](https://hexoros.github.io/hexoros-agent-os/)
[![Made for HexorOS](https://img.shields.io/badge/made_for-HexorOS-00f2ff?style=flat-square)](https://hexoros.com)
[![EU AI Act ready](https://img.shields.io/badge/EU_AI_Act-ready-22c55e?style=flat-square)](https://hexoros.com)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg?style=flat-square)](LICENSE)

**The sovereign, zero-telemetry operator surface for self-hosted AI agents.**
*Single-file React app. Zero build steps. 100% auditable directly in your browser.*

---

## Why HexorOS

Most commercial AI tools sell you a lease on a closed black box — charging you per-seat, per-token, and per-call while exfiltrating your prompts to foreign cloud providers.

**HexorOS is the private alternative:** a self-hosted AI agent operating system running entirely on hardware you control or secure EU GPU nodes. This repository hosts the **Agent OS Dashboard** — the stateless, transparent operator interface that sits in front of your private agent fleet.

- **🔒 Privacy by architecture:** No data leaves your system. Logs, memory, and inference stay on your servers. GDPR-compliant by design.
- **🚫 No vendor lock-in:** Full independence from third-party APIs through local, highly optimized open-source models (such as Qwen3:27b).
- **🖥️ Zero-telemetry auditing:** The entire UI is a single HTML file. Audit every line of code in your browser before you run it.

---

## 📊 Core Features

- **Registry:** Real-time monitoring of all active agent runtimes, model loads, token usage, and execution queues.
- **Streaming Chat:** Token-by-token streaming, tool-use visualization, and child-agent delegation tracing.
- **Vault Browser:** Search, browse, and link local markdown documents (e.g., Obsidian vaults) directly to agent memory contexts.
- **Mindmap Swarm View:** Interactive topology map showing agent swarms, infrastructure nodes, and active tool pipelines.
- **Sovereign State:** All configuration, API endpoints, and system prompts are saved strictly in your browser's `localStorage`. No remote database tracking.

---

## ⚡ Quick Start

### 1. Run Locally

The dashboard is a single-file React application with no build steps — run it instantly with any static web server:

```bash
# Clone the repository
git clone https://github.com/HexorOS/hexoros-agent-os.git
cd hexoros-agent-os

# Start a simple local server
python3 -m http.server 8000
```

Open **[http://localhost:8000](http://localhost:8000)** in your browser, or simply double-click `index.html`.

### 2. Live Demo

A public, read-only build is auto-deployed to GitHub Pages on every main branch commit:
👉 **[https://hexoros.github.io/hexoros-agent-os/](https://hexoros.github.io/hexoros-agent-os/)**

*Note: The demo runs in sandbox mode. All panels render for visual auditing, but chat API calls return `401 Unauthorized` until connected to your private HexorOS Engine.*

---

## 🏗️ System Architecture

The dashboard is completely stateless and talks to your secure backend gateway via JSON Web Tokens (JWT RS256):

```
+-------------------------------------------------------+
|                 🖥️  OPERATOR BROWSER                  |
|  Agent OS Dashboard (Stateless Single-File React)    |
+-------------------------------------------------------+
                           | (Bearer JWT)
                           v
+-------------------------------------------------------+
|                 SECURE GATEWAY / VPS                  |
|             api.hexoros.com (Nginx + TLS)            |
+-------------------------------------------------------+
         |                                     |
         v                                     v
+------------------+                 +------------------+
| INFERENCE LAYER  |                 |    MCP LAYER     |
|  Ollama Runtime  |                 |  hexoros-brain   |
|   (Qwen3 27B)    |                 | (Memory & Vault) |
+------------------+                 +------------------+
```

For a detailed technical breakdown, configurations, and boundaries, see [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## 📂 Repository Layout

```
.
├── index.html          # Single-file React application (Babel-in-browser)
├── ARCHITECTURE.md     # In-depth architectural design, endpoints, and data boundaries
├── ROADMAP.md          # Public roadmap, tracking Indiegogo milestones
├── CHANGELOG.md        # Documented version history
├── LICENSE             # AGPL-3.0 license text
├── docs/
│   ├── SETUP.md        # Deployment instructions (local, static hosting, Nginx proxy)
│   └── CUSTOMIZATION.md # Guide to adding custom agents, panel modules, and styling themes
├── examples/
│   ├── agent.json      # Sample configuration file for custom agents
│   └── vault-note.md   # Structure specifications for knowledge base documents
└── screenshots/        # Assets, diagrams, and preview screenshots
```

---

## 🤝 Contributing

We embrace open source. If you want to contribute features, improve the UI, or add integration connectors, we welcome your pull requests!

- **Hackability first:** No webpack, no compilation — edit `index.html`, reload your browser, see your changes instantly.
- **Enterprise focus:** Features prioritizing offline capability, air-gapped security, or GDPR alignment are highly prioritized.

---

## ⚖️ License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
See the full license text in [LICENSE](LICENSE).

---

*Part of the **HexorOS** sovereign AI workforce · [hexoros.com](https://hexoros.com)*
