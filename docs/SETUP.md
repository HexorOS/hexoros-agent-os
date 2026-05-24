# Setup

The dashboard runs in any modern browser. It needs no build step, no server-side
runtime, and no package manager to start. Below are the three supported modes
of running it.

## 1. Open the file directly

The simplest possible setup:

```bash
git clone https://github.com/HexorOS/hexoros-agent-os.git
cd hexoros-agent-os
open index.html       # macOS
xdg-open index.html   # Linux
start index.html      # Windows
```

That's it. The page loads React and Babel from a CDN and runs entirely
client-side. Settings persist via the browser's `localStorage`.

## 2. Serve locally over HTTP

Some browser features (Service Workers, secure-context APIs) only work over
HTTP, not `file://`. A two-line static server fixes that:

```bash
cd hexoros-agent-os
python3 -m http.server 8000
# then visit http://localhost:8000
```

Or with Node:

```bash
npx serve .
```

## 3. Deploy to GitHub Pages

This repo ships a GitHub Actions workflow at `.github/workflows/pages.yml`
that auto-deploys `index.html` to GitHub Pages on every push to `main`.

To enable it on a fork:

1. Go to your fork's **Settings → Pages**
2. Under **Build and deployment → Source**, choose **GitHub Actions**
3. Push to `main` — the workflow runs and your dashboard appears at
   `https://<your-user>.github.io/hexoros-agent-os/`

The official deploy lives at:
👉 https://hexoros.github.io/hexoros-agent-os/

## Connecting to a HexorOS Engine

Once the dashboard is loaded, open the **Settings** panel and configure:

| Field | What to enter |
|---|---|
| API host | `https://api.hexoros.com` (or your own self-hosted endpoint) |
| Model | `hexoros:latest` (default) or any model your engine exposes |
| Bearer token | JWT issued by your HexorOS Engine login flow |

Without a valid bearer token, the dashboard still renders — but chat and
vault calls return `401 Unauthorized`. This is expected and intentional;
the dashboard is read-only against unauthenticated endpoints.

## Self-Hosted HexorOS Engine

This repo is the **dashboard only**. The HexorOS Engine (inference proxy,
auth, MCP servers, model weights) is a separate distribution available in
three tiers — see [hexoros.com](https://hexoros.com) for licensing.

If you already have an Engine running, point the dashboard at it via
**Settings → API host**.

## Troubleshooting

**The page loads but nothing renders.** Open the browser console. If you see
a Babel parse error, your browser is likely an outdated build that doesn't
support modern ES syntax. The dashboard targets Chrome 120+, Firefox 120+,
Safari 17+, and recent Edge.

**Chat calls return CORS errors.** Your HexorOS Engine needs an
`Access-Control-Allow-Origin` header that includes wherever you serve the
dashboard from. The default `api.hexoros.com` config already allows
`https://hexoros.com` and `https://*.hexoros.com`.

**Settings don't persist.** Verify your browser is not in private/incognito
mode — `localStorage` is wiped at session end in those modes.
