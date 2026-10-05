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
| `website` | Make a website people want to stay on — the sequence from story to published domain; starts the five below |
| `website-story` | Who it is for, the chapters, every line of copy in the owner's voice |
| `website-look` | Palette, fonts, one accent, a house style string for every image, motion that does not hurt |
| `website-films` | Real films of the real product — drawn cursor, real timing, cuts, posters, animated WebP; ships the recorder |
| `website-media` | Images and films onto the site: workspace files for a Site app, app assets for a Forge app |
| `website-publish` | Every screen, both themes, contrast, weight, reduced motion (ships the checker); SEO text, homepage, domain |
| `build-esoul-website` | The Site-app block manual: tools, block vocabulary, tested palettes, section rhythm — a site, store or homepage published to your handle |
| `forge-app-builder` | Turn an idea into a full ExternalSoul app in your Forge — events, tools that chat and voice call, server ops and streaming routes, durable tasks, your own tables and roles, realtime, files and Drive, other apps, a service of its own on your computers, and your accounts at Google, Microsoft (Outlook, OneNote) or any OAuth / API-key service without the app ever holding the secret — proven with tools in a live workbench before install. The SDK it builds on: [esoul-sdk on npm](https://www.npmjs.com/package/esoul-sdk) |
| `research-study` | Run an ML research study on your own repo and GPU from Claude: it interviews you (objective, constraints, success, apps), pairs your machine, gets one approval, and keeps a runs sheet, a hypotheses board and a notebook current while it experiments |
| `training-monitor` | The workspace's TensorBoard: log a training loop with `esoul.track`, read curves and verdicts by tool, and wire a Forge app that trains on your own computer to it |
| `agent-builder` | Build and run multi-agent networks in your workspace from the conversation — agents with their own models and tools (your apps, web search, questions to you), hand-offs between them, a trigger that runs them on every new email or event, fan-out over a spreadsheet; then watch runs, answer their questions, stop them |
| `agent-recipes` | Ten complete agent networks to adapt: inbox triage with specialists, a researcher, row-by-row lead enrichment, a report that builds its deck, send-only-on-yes, a planner with specialists, event watchers, images, durable waits, networks calling networks |
| `email-campaign` | Give a list of emails and a goal (and, if you like, the letter's words and images) and say go: real letters to read first, sent paced from your Gmail, an agent in every conversation; ask later how it is going, who replied and what they said |
| `block-notes` | Pages in folders — read, write, append, search, illustrate; the knowledge and documentation surface agents write into |
| `slideshow` | Slides as live TSX on a 1280×720 canvas, edited by find/replace and judged by a vision critic; themes bundled |
| `browser-use` | Drive your cloud browser — logged-in sites, forms, web editors, batch downloads — and know whether it actually worked |
| `cad` | Real parts in the CAD app: bring your existing parts in (Onshape through your cloud browser, or any STEP file), place them by the source mates, design mounts, housings and caps around them with measured fits, an exploded view, and each printable part exported by name |

## Requirements

An ExternalSoul account. Nothing installed locally — the server is hosted, and
Claude Code handles the OAuth flow, token storage and refresh.

One app the skills drive is turned on per account for now: the Gmail app
(`email-campaign`, the mail parts of `agent-recipes`). If `create_app` says the
type is not available to your account, ask ExternalSoul to enable it — every
other app (CAD, notes, slides, the browser, the sandbox, the Forge, agents, the
site, the study, the monitor) is open to every account.

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
