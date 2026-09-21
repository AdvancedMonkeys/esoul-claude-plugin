# ExternalSoul — Claude plugin

Gives Claude a persistent memory and a workspace it can operate: spreadsheets,
notes, email, calendar, contacts, drawings and multi-agent networks, all on one
event-sourced timeline. Every change Claude makes is a typed event you can
replay, scrub and audit.

## Install

```
/plugin marketplace add AdvancedMonkeys/esoul-claude-plugin
/plugin install esoul@externalsoul
```

Then run `/mcp`, pick **esoul**, and sign in. A browser opens, you approve, and
that is the whole setup — no token to paste, nothing to configure. The
connection reaches every project and workspace on your account.

## What's in it

| Component | What it does |
|---|---|
| `esoul` connection | Your own account over OAuth — list, read, search, create apps and workspaces, and drive any app through its own tools |
| `/esoul:memory` | Recall what you already know about this project from your workspace, and write back what is worth keeping |
| `setup` | Connect or repair the connection (a sign-in — never a token) |
| `math-explainer-video` | A narrated manim explainer, rendered in a sandbox and assembled into one mp4 |
| `build-esoul-website` | A site, store or homepage built with the site app and published to your handle |
| `forge-app-builder` | Build a new ExternalSoul app in your Forge, with a live workbench |
| `browser-use` | Drive your cloud browser — logged-in sites, forms, web editors, batch downloads — and know whether it actually worked |

## Requirements

An ExternalSoul account. Nothing installed locally — the server is hosted, and
Claude Code handles the OAuth flow, token storage and refresh.

Prefer to run it yourself, or using another client? The same tools ship as a
local server in the [`esoul` Python SDK](https://pypi.org/project/esoul/):
`pip install "esoul[mcp]"`, then `esoul-mcp`.

## Finding capabilities

The connection exposes a handful of general tools rather than one per feature.
Every app's own tools are reached through `get_app_tools` → `call_app_tool`, so
the tool list stays small while nothing is out of reach — just ask for what you
want rather than assuming it is missing.

## Links

- [ExternalSoul](https://externalsoul.com)
- [SDK on PyPI](https://pypi.org/project/esoul/)
- [SDK on npm](https://www.npmjs.com/package/esoul-sdk)

MIT licensed.
