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
| `/esoul:memory` | Recall what your ExternalSoul memory holds about this project (or any topic), and keep what is worth keeping |
| `memory` | Lifelong recall: "remember that list we made last spring?", "what did I tweet about this years ago?", "who changed the sales sheet this week?" — past work sessions, versioned facts and all dated content in one `recall`, with each thing's status today and a link that opens it |
| `setup` | Connect or repair the connection (a sign-in — never a token) |
| `math-explainer-video` | A narrated manim explainer, rendered in a sandbox and assembled into one mp4 |
| `build-esoul-website` | A site, store or homepage built with the site app and published to your handle |
| `forge-app-builder` | Turn an idea into a full ExternalSoul app in your Forge — events, tools that chat and voice call, server ops and streaming routes, durable tasks, your own tables and roles, realtime, files and Drive, other apps, your own computer — proven with tools in a live workbench before install |
| `research-study` | Run an ML research study on your own repo and GPU from Claude: it interviews you (objective, constraints, success, apps), pairs your machine, gets one approval, and keeps a runs sheet, a hypotheses board and a notebook current while it experiments |
| `training-monitor` | The workspace's TensorBoard: log a training loop with `esoul.track`, read curves and verdicts by tool, and wire a Forge app that trains on your own computer to it |
| `block-notes` | Pages in folders — read, write, append, search, illustrate; the knowledge and documentation surface agents write into |
| `slideshow` | Slides as live TSX on a 1280×720 canvas, edited by find/replace and judged by a vision critic; themes bundled |
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
