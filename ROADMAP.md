# Roadmap

This roadmap mirrors the public stretch goals of the HexorOS Indiegogo
campaign. The dashboard is the visible operator surface — each milestone
below adds new panels, new MCP integrations, or new orchestration views to it.

## v0.1 — Operator MVP *(shipped)*

- Agent registry with live status, model, and host columns
- Streaming chat panel against `api.hexoros.com`
- Vault browser scaffold (read-only)
- Mindmap view of agents and infrastructure nodes
- Per-agent settings: model, system prompt, API endpoint
- `localStorage` persistence — no backend required to run the UI

## v0.2 — Multi-tenant Hardening *(in progress)*

- Role-based access: operator, viewer, admin
- Per-agent token-usage meters from `customer_dashboard_api`
- Vault write-back via MCP brain
- Mobile-responsive layout

## v0.3 — HexorSwarm Panel *(stretch goal at €60k campaign milestone)*

- Cross-machine agent orchestration view
- Drag-and-drop task delegation between agents on different servers
- Health monitoring per node (CPU, GPU, model RAM, queue depth)

## v0.4 — HexorMemory Panel *(stretch goal at €80k)*

- Encrypted vector store browser
- Episodic memory timeline per agent
- Memory eviction policies, audit trail
- Cross-agent memory sharing controls

## v0.5 — HexorHub Marketplace *(stretch goal at €120k)*

- One-click install of community MCP tools
- Agent template gallery
- Reputation and signature verification for shared agents

## v1.0 — Open-Source Kernel *(stretch goal at €180k)*

- HexorOS kernel released under AGPLv3
- Reference deployments for Hetzner, Scaleway, OVH, self-hosted
- Public SBOM and signed release artifacts
- Compliance documentation pack for the EU AI Act

## How to Influence the Roadmap

- **File an issue** in this repo for feature requests
- **Back the [Indiegogo campaign](https://hexoros.com)** — campaign milestones
  directly unlock the stretch goals above
- **Join the Discord** (link in README) to discuss priorities with the team

This roadmap is intentionally honest: dates depend on funding velocity. We
ship every day; the order shifts based on backer signal and operator demand.
