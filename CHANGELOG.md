# Changelog

All notable changes to the HexorOS Agent OS Dashboard are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Role-based access (operator / viewer / admin)
- Per-agent token-usage meters
- Mobile-responsive layout

## [0.1.0] — 2026-05-24

### Added
- Initial public release of the single-file React operator dashboard
- Agent registry with status, model, and host columns
- Streaming chat panel against `api.hexoros.com`
- Vault browser scaffold (read-only)
- Mindmap view of agents and infra nodes
- Per-agent settings persisted in `localStorage`
- `ARCHITECTURE.md`, `ROADMAP.md`, `CHANGELOG.md`
- `docs/SETUP.md` and `docs/CUSTOMIZATION.md`
- Example agent and vault-note configurations under `examples/`
- GitHub Pages auto-deploy via `.github/workflows/pages.yml`

### Security
- All real production IPs sanitized before public release; the dashboard
  references domains (`api.hexoros.com`, `hexoros.com`) and never raw addresses
- No secrets stored in repository — operator API keys live in the operator's
  own browser `localStorage` only
