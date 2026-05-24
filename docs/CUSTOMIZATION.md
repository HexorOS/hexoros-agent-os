# Customization

The dashboard is intentionally hackable. Open `index.html` in any editor and
search for the marker comments — every customization point is annotated.

## Add Your Own Agent

Agents are defined as a JavaScript array near the top of the React tree.
Find the line:

```js
// ── Agent Registry ───────────────────────────────────────
```

Append a new object:

```js
{
  id:    'my-agent',
  label: 'Marketing Bot',
  model: 'hexoros:latest',
  host:  'https://api.hexoros.com',
  ctx:   'You write short Twitter posts about indie SaaS launches.',
  tag:   'ops',
  pri:   'med'
}
```

See `examples/agent.json` for the full shape and every supported field.

## Change the Color Theme

The dashboard uses cyan `#00f2ff` as the primary accent. To rebrand:

1. Search `index.html` for `#00f2ff`
2. Replace every occurrence with your hex of choice
3. Reload the page

The dark background, glow effects, and chrome panels are tied to the accent
via CSS custom properties — a single hex change cascades everywhere.

## Add a New Panel

Panels are React components registered in the navigation strip. Steps:

1. Find `const NAV = [`
2. Add your tab: `{id:'mypanel', lbl:'My Panel', ico:'★'}`
3. In the route switch (`switch(active)`), add a case:
   ```js
   case 'mypanel':
     return <div className="panel"><MyPanel/></div>;
   ```
4. Define `function MyPanel(){ return <h2>Hello</h2>; }` anywhere below.

The panel inherits the standard chrome (header, padding, scroll behavior)
for free.

## Wire Up a Custom Backend

The dashboard makes one fetch per outbound call. Search for `fetch(` in
`index.html` — each call is short and self-contained.

Replace the URL with your own backend, but keep the shape the same:

- Streaming chat: `POST /api/chat`, body `{model, messages, stream:true}`,
  response is NDJSON with `{message:{content:string}}` chunks
- Vault read: `GET /mcp/brain/notes` returning `[{id, title, body, tags}]`
- Dashboard stats: `GET /api/dashboard/summary` returning `{agents, tokens, queue}`

## Embed in Another App

The dashboard works as an iframe:

```html
<iframe
  src="https://hexoros.github.io/hexoros-agent-os/"
  width="100%"
  height="900"
  style="border:0;border-radius:12px;"
></iframe>
```

For deeper integration, copy the React components out of `index.html` into
your own build. The dashboard has no external dependencies beyond React,
ReactDOM, and Babel — all CDN-loaded.

## Persist Settings to a Backend

By default settings live in `localStorage`. To sync them across devices, wrap
the `useState` calls in a custom hook that POSTs to your own endpoint:

```js
function useSyncedState(key, initial){
  const [v, setV] = useState(() => {
    const local = localStorage.getItem(key);
    return local ? JSON.parse(local) : initial;
  });
  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(v));
    fetch('/api/settings/'+key, {method:'PUT', body:JSON.stringify(v)});
  }, [key, v]);
  return [v, setV];
}
```

Replace every `useState` for persistent config with `useSyncedState` and you
get cross-device sync without rewriting the UI.
