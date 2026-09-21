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
| `esoul` MCP server | Drives the workspace: read state, dispatch typed events, run agents, search |
| `/esoul:memory` | Opens this folder's memory space and recalls what was learned here before |
| `setup` skill | Guides Claude through connecting and repairing the connection |

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
- [SDK reference](https://externalsoul.com/sdk-docs/llm-reference.md)

MIT licensed.
