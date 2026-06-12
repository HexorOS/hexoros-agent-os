# HexorOS Chat Widget

Embeddable, dependency-free chat widget for any website. One `<script>` tag, zero build steps — the same hackability-first philosophy as the Agent OS Dashboard.

## Quick Start

```html
<script src="hexor-widget.js"
        data-business-name="Your Company"
        data-context="You are a helpful support agent for Your Company."
        data-api-endpoint="https://your-backend.example.com/api/widget/chat"
        data-color="#00f2ff"></script>
```

That's it. The widget renders a floating chat button (bottom right) that opens a streaming chat window.

## Configuration

| Attribute | Default | Description |
|-----------|---------|-------------|
| `data-business-name` | `HexorOS Agent` | Display name in the chat header |
| `data-context` | *(empty)* | System prompt / business context sent with every message |
| `data-api-endpoint` | `http://localhost:8000/api/widget/chat` | Your chat backend endpoint |
| `data-color` | `#00f2ff` | Accent color (any CSS color) |

## Backend Contract

The widget POSTs JSON to your endpoint and renders the streamed response:

```json
{ "message": "user text", "business_name": "Your Company", "context": "your data-context" }
```

Any backend works — a few lines of FastAPI in front of Ollama is enough. Chat history is kept in `sessionStorage` (per tab, no tracking, no cookies).

## Hosted Backend

Don't want to run your own inference? The HexorOS Engine provides a managed, GDPR-compliant widget backend on EU infrastructure — see [hexoros.com](https://hexoros.com).

## License

AGPL-3.0, same as the rest of this repository.
