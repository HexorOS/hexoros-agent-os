# HexorOS — Agent OS Dashboard

[![Live Demo](https://img.shields.io/badge/live-demo-00f2ff?style=flat-square)](https://hexoros.github.io/hexoros-agent-os/)
[![Made for HexorOS](https://img.shields.io/badge/made_for-HexorOS-00f2ff?style=flat-square)](https://hexoros.com)
[![EU AI Act ready](https://img.shields.io/badge/EU_AI_Act-ready-22c55e?style=flat-square)](https://hexoros.com)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg?style=flat-square)](https://www.gnu.org/licenses/agpl-3.0.html)

**The sovereign, zero-telemetry operator surface for self-hosted AI agents.**  
*Single-file React app. Zero build steps. 100% auditable directly in your browser.*

---

## 🇩🇪 Deutsche Version / German Overview

### Souveräne KI-Infrastruktur für europäische Unternehmen

Die meisten modernen KI-Tools vermieten Ihnen nur den Zugriff — ein Interface, eine monatliche Kreditkartenabrechnung pro Nutzer und die Gewissheit, dass Ihre sensiblen Unternehmensdaten im Hintergrund zum Training von US-Modellen verwendet werden.

**HexorOS ist die souveräne Alternative:** Ein datenschutzkonformes, selbst-gehostetes KI-Betriebssystem, das vollständig auf Ihrer eigenen Hardware oder auf EU-basierten GPU-Servern läuft. Dieses Repository enthält das **Agent OS Dashboard** — die visuelle Kommandozentrale für Ihre digitale Belegschaft.

#### Warum HexorOS anders ist:
* **🔒 100% DSGVO-konform:** Keine Daten verlassen Ihr System. Logs, Memory und Inferenz bleiben auf Ihren Servern.
* **🚫 Kein OpenAI-Zwist:** Volle Unabhängigkeit von Drittanbietern durch den Einsatz lokaler, hochoptimierter Open-Source-Modelle (wie Qwen3:27b).
* **🖥️ Zero-Telemetry Auditing:** Die Benutzeroberfläche besteht aus einer einzigen HTML-Datei. Sie können jede Zeile Code in Sekundenschnelle einsehen und auditieren, bevor Sie das System starten.

---

## 🇬🇧 English Version / English Overview

### Sovereign AI Infrastructure for Privacy-First Enterprises

Most commercial AI tools sell you a lease on a closed black box — charging you per-seat, per-token, and per-call while exfiltrating your prompts to foreign cloud providers.

**HexorOS is the private alternative:** A self-hosted AI agent operating system running entirely on hardware you control or secure EU GPU nodes. This repository hosts the **Agent OS Dashboard** — the stateless, transparent operator interface that sits in front of your private agent fleet.

---

## 📊 Core Features / Hauptfunktionen

* **Registry (Live-Register):** Real-time monitoring of all active agent runtimes, model loads, token usage, and execution queues.
* **Streaming Chat (Interaktiver Chat):** Token-by-token streaming, tool-use visualization, and child-agent delegation tracing.
* **Vault Browser (Wissensdatenbank):** Search, browse, and link local markdown documents (e.g., Obsidian vaults) directly to agent memory contexts.
* **Mindmap Swarm View (Netzwerk-Visualisierung):** Interactive topology map showing agent swarms, infrastructure nodes, and active tool pipelines.
* **Sovereign State (Lokale Speicherung):** All configuration, API endpoints, and system prompts are saved strictly in your browser's local storage (`localStorage`). No remote database tracking.

---

## ⚡ Quick Start / Schnellstart

### 1. Run Locally (Lokal ausführen)
Because the dashboard is built as a single-file React application with no build steps, you can run it instantly using any static web server:

```bash
# Clone the repository
git clone https://github.com/HexorOS/hexoros-agent-os.git
cd hexoros-agent-os

# Start a simple local server
python3 -m http.server 8000
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser or simply double-click `index.html`.

### 2. Live Demo
A public, read-only build is auto-deployed directly to GitHub Pages on every main branch commit:  
👉 **[https://hexoros.github.io/hexoros-agent-os/](https://hexoros.github.io/hexoros-agent-os/)**

*Note: The demo runs in sandbox mode. While all panels render for visual auditing, chat API calls will return `401 Unauthorized` until connected to your private HexorOS Engine.*

---

## 🏗️ System Architecture / Systemarchitektur

The dashboard is completely stateless and interacts with your secure backend gateway via JSON Web Tokens (JWT RS256):

```
+-------------------------------------------------------+
|                 🖥️  OPERATOR BROWSER                  |
|  Agent OS Dashboard (Stateless Single-File React)    |
+-------------------------------------------------------+
                           | (Bearer JWT)
                           v
+-------------------------------------------------------+
|               🇪🇺  SECURE GATEWAY / VPS                |
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

## 📂 Repository Layout / Dateistruktur

```
.
├── index.html          # Single-file React application (Babel-in-browser)
├── ARCHITECTURE.md     # In-depth architectural design, endpoints, and data boundaries
├── ROADMAP.md          # Public roadmap, tracking Indiegogo milestones
├── CHANGELOG.md        # Documented version history
├── docs/
│   ├── SETUP.md        # Deployment instructions (local, static hosting, Nginx proxy)
│   └── CUSTOMIZATION.md # Guide to adding custom agents, panel modules, and styling themes
├── examples/
│   ├── agent.json      # Sample configuration file for custom agents
│   └── vault-note.md   # Structure specifications for knowledge base documents
└── screenshots/        # Assets, diagrams, and preview screenshots
```

---

## 🤝 Contributing / Mitwirken

We embrace open source. If you want to contribute features, improve the UI, or add integration connectors, we welcome your pull requests!

* **Hackability First:** Since the app requires no webpack or compilation steps, you can edit `index.html` directly, reload your browser, and instantly see your changes.
* **Enterprise Focus:** Features prioritizing offline capabilities, air-gapped security, or GDPR alignment are highly prioritized.

---

## ⚖️ License / Lizenz

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. 
Verify the full license text in the [LICENSE](https://www.gnu.org/licenses/agpl-3.0.html) file.

---

*Part of the **HexorOS** sovereign AI workforce.*  
*Handgefertigt in Deutschland 🇩🇪 · [hexoros.com](https://hexoros.com)*
