---
name: forge-app-builder
description: Turn an idea into a real ExternalSoul app over MCP — a native app with its own events, UI, agent tools, server ops, durable tasks, tables, realtime, files, other apps and the user's own computer — built and PROVEN in the user's Forge workbench with tools (look, drive, call its tools, run its tests) before anyone installs it. Use whenever the user says "make me an app", "I want an app that…", "build this in the Forge", asks for a research tool, a store, a dashboard, a labeller, a data pipeline on their machine, or asks to change an app still being built. For a marketing site or homepage use build-esoul-website instead.
---

# Build an ExternalSoul app in the Forge

You are writing a **native app** for a person's ExternalSoul workspace — not a widget, not a
page. It sits beside their spreadsheets and mail, holds its state as typed events on the
shared timeline (scrubbable, replayable), exposes tools that chat, voice, agents and MCP call,
can bring its own server (ops, streaming routes, webhooks), durable background tasks, its own
database tables, realtime channels, the workspace's files and Google Drive, other apps' tools,
and the person's own computer. The Forge gives you a cloud machine holding the platform with
your app on its own branch; you see it running in the person's frame within seconds and prove
every arm with tools before a human reads the diff and installs it.

**You are the only model in this loop.** Nothing writes the app but you; nothing is installed
until a person has read it. Write as if they are reading over your shoulder — they are (the
board shows every file, diff, checkpoint and tool call).

Read `reference/what-you-work-with.md` FIRST — the surfaces you have, what a preview can and
cannot do, every cap, and what things cost. Then `reference/idea-to-app.md` for the flow.
The rest is the contract, read as the app needs it:

| Reference | Read it for |
|---|---|
| `what-you-work-with.md` | the 15 hosted tools, the 28 board tools, the box, the preview's powers and LIMITS, caps, costs, personas |
| `idea-to-app.md` | the interview, the shape decision (fold / tables / machine / external / site), the write order, worked shapes |
| `app-anatomy.md` | the code contract: manifest, schema, events, ops declared once, UI, server, tests |
| `tools-chat-and-voice.md` | how defining tools lets chat, voice, agents and MCP drive the app; honest results; **test tools** |
| `talking-to-other-apps.md` | calling other apps (UI + server), reading them, bindings, events other apps and agents can wake on |
| `my-computer.md` | using the person's paired computer from an app — in the Forge and after install |
| `server-and-tasks.md` | ops, routes (SSE, a token door for machines), webhooks, Inngest tasks and the replay model, realtime |
| `data-people-files.md` | your own tables and rules, roles and access levels, connections, files and Drive, public viewers |
| `telling-people-later.md` | notifying a person AFTER the request: a status change, a cadence, a first visit — the recipient table, the task, the email app on the workspace |
| `design-rules.md` | what "native" and "responsive" mean here; the pre-ship checklist |
| `test-and-ship.md` | proving every arm with tools, the problem journal, removing test tools, shipping and installing |

## Where the tools are

Over the hosted connection you have fifteen general tools (`list_workspaces`, `search_workspace`,
`read_app_state`, `get_app_tools`, `call_app_tool`, `create_app`, …). **The Forge is an app** on
the person's workspace (type `forge`, usually named "Forge"); its 30 workbench tools are minted
as `<verb>_<board name>` and reached like any app's:

```
list_workspaces                                          → find the board's app id
get_app_tools(<board id>)                                → open_workbench_Forge, write_app_file_Forge, …
call_app_tool(<board id>, "open_workbench_Forge", {pluginId, name, description, icon})
```

**Two doors, one handler.** The hosted connection (`/mcp/me`, OAuth, the account OWNER) drives
the board's tools through `call_app_tool` as above. The local `esoul-mcp` server (`pip install
esoul[mcp]`, a Personal Access Token) has the same verbs as `forge_*` tools — `forge_open`,
`forge_write`, `forge_edit`, `forge_test`, `forge_check`, `forge_look`, `forge_drive`, `forge_tool`,
`forge_put_asset`, `forge_commit`, `forge_ship`, `forge_merge`, `forge_close`, … — and, because it
runs on the person's machine, it can read their disk: a film on their laptop reaches the app
through `forge_put_asset(file=…)` and a whole local folder through `forge_sync`. Prefer it when
the person has files to bring; either door is complete for everything else.

Below, board tools are written without the suffix. No board? `create_app(application_type=
"forge", name="Forge")`, then the person connects GitHub in Account settings → GitHub; a board
without it refuses to open a workbench and says so — relay that, never work around it. Only the
**workspace owner** may author on a board; a collaborator's chat is refused and told so.

## Reading the SDK's own docs

These references are the distilled rules. The SDK ships its full CONTRACT as text, and when a
reference and the contract disagree, the contract wins — read it, and say which you used.

**In a box, read the INSTALLED version** — it is what this app compiles against.
`read_platform_file {path}` opens:
- `packages/esoul-sdk/docs/<nn>-<chapter>.md` — 01 getting-started · 02 manifest · 03 events-and-state ·
  04 tools · 05 ui · 06 server · 07 background-tasks · 08 connections · 09 files · 10 testing ·
  11 shipping · 12 rules · 13 people-and-access · 14 database · 15 realtime · 16 bindings ·
  17 editing-and-merging;
- `packages/esoul-sdk/api-reference.md` — every export with its signature and doc comment; the
  place to look ONE name up (`search_app_files {scope:"sdk", query:"<name>"}` finds it, and greps
  the SDK's source too);
- `packages/esoul-sdk/README.md`.

**With no box open**, the published package: [npmjs.com/package/esoul-sdk](https://www.npmjs.com/package/esoul-sdk).
Fetch `https://unpkg.com/esoul-sdk/llms.txt` (the index), then
`https://cdn.jsdelivr.net/npm/esoul-sdk/llms-full.txt` (the whole contract in one file) or one
chapter at `https://unpkg.com/esoul-sdk/docs/<nn>-<chapter>.md`. Published and installed can
differ by a version — for an app that is open in a box, the box's copy is the truth.

## The flow: idea → app (details in `idea-to-app.md`)

1. **Understand** — five questions, one message: who uses it (only them / invited people /
   the public), what it remembers, what must be true *now* (server truth), what runs while
   nobody is looking, what it touches outside (Drive, their computer, an API, another app).
2. **Shape** — decide where each thing lives: shared-and-small → **the fold** (events);
   per-person / unbounded / must-not-scrub → **tables** (`db`); heavy compute → **their
   computer**; live view → **route**; durable work → **task**. Write the manifest first: it IS
   the design, and the person reads it at install.
3. **Open** the workbench, read the scaffold, then write in this order: `plugin.json` +
   `ops.ts` + `server.ts` in ONE round (a manifest naming ops the server lacks is refused),
   `app.tsx` (events → tools → describer), `ui/`, tests. Every write answers with the
   preview's health and the **⚠ problem paragraph** — fix those before anything else.
4. **Prove with tools** — `look_at_app` (three viewports, as each persona), `drive_app` (a
   flow, reading the page's console), `call_app_tool` on the app's own tools then
   `read_app_state`, `test_app`, `check_app`. Add **test tools** where a probe needs a door
   the product does not have; remove them before shipping (`tools-chat-and-voice.md` §5).
5. **Iterate with the person** — they play with the build in their frame and tell you what is
   wrong; keep rounds small; `look_at_app` after a visual change, a drive after a behaviour
   change. Resolve the journal rows you fixed (`resolve_problem`), honestly.
6. **Ship** — `check_app` green (no `skipped`), test tools gone, version bumped, `ship_app`.
   Give the PR URL. After review and release: `create_app(application_type="plugin_<id>",
   name=…)` puts it on a workspace — its tools are live in chat, voice, agents and MCP.

## The loop, tool by tool

1. `open_workbench {pluginId, name, description, icon}` — `pluginId` lower-case with dashes;
   `icon` a lucide name (the tool lists the allowed ones when yours is wrong). First open on a
   board: minutes (clone + install); later apps: seconds. Reopening resumes and merges the
   platform's `main` into the box. Answers with what the box can do (`tasks, ops, routes,
   realtime, viewer, db`) — if that line is missing, `close_workbench` and open again.
2. `orient_app` (an app you did not write this conversation) or `list_app_files` +
   `read_app_file {pluginId, path, from?, lines?}`. `search_app_files {query, glob?, regex?,
   scope:"app"|"sdk"}` greps the app, or the SDK's source and docs; `read_platform_file` opens
   an allow-listed SDK file when an answer surprises you.
3. `write_app_file {pluginId, path, content}` / `edit_app_file {pluginId, path, edits:[{find,
   replace}]}` (each `find` matches exactly once or nothing is written) / `delete_app_file`.
   Files `.ts .tsx .json .css .md .txt .svg`, ≤ 512 KB each, ≤ 200 per app, paths ≤ 6 deep.
   The answer's `Preview: live (answered 200 in 0.9 s)` means that build is on screen;
   `Preview: DOWN — …` carries the compiler's own lines. Fix it first.
   Images, films, fonts, PDFs are **assets**, not files: `put_app_asset {pluginId, name,
   fileId | contentBase64 | sourceUrl}` (`fileId`: a workspace file, e.g. what `generate_image` /
   `generate_video` made; over esoul-mcp `forge_put_asset(file=…)` for anything on the
   person's disk, up to 64 MB) stores the bytes content-addressed and writes `assets.json` for
   you; the app renders `assetUrl(assets, "hero.mp4")` from `esoul-sdk` — one URL, the same in
   the preview and installed. `assets.md` has the whole contract.
4. `preview_app {pluginId, viewer?}` — starts the dev server (a minute cold, seconds warm) and
   puts the URL on the frame. Every later write hot-reloads.
5. `look_at_app {pluginId, intent, viewer?}` — screenshots desktop-light, desktop-dark,
   phone-light; returns image URLs plus what is on screen, errors, anything clipped. **Open the
   images and judge them.** Leave `critique` off unless you want a second opinion.
6. `drive_app {pluginId, steps, viewer?}` — use it like a person (≤ 40 steps: `{click}`,
   `{type:[selector,text]}`, `{keys:[selector,key,times]}`, `{select:[selector,value]}`,
   `{wait:ms}`, `{say:selector}`) and read what the PAGE said: console errors, throws, failed
   calls, what each `say` read, a final screenshot. A look proves layout; a drive proves health.
   Steps run against the real preview — a click that starts something starts it.
7. `call_app_tool {pluginId, tool, args}` — runs one of the APP's own tools inside the box; the
   events land in the frame. `read_app_state {pluginId}` reads the fold. This is how an agent
   will drive the app after install — drive it that way now. Ops run over the preview's
   in-memory tables (`pluginDb`) with your real rules, and **VIEW AS** (`viewer:` on
   `look_at_app` / `drive_app` / `preview_app`) shows each persona exactly what those rules let
   them see — visitor-b must see nothing of visitor-a's.
8. `test_app` (the app's own jest, seconds) after any change to schema/events/ops;
   `check_app` (registry sync, the import wall, the app's tests + the platform suites, types)
   before "ready". Read every red gate's detail. `skipped` is not a pass.
9. `app_problems` / `resolve_problem {id, note}` — the journal (§ what-you-work-with).
10. `commit_app {message}` at milestones; `app_history`, `diff_app {sha}`, `restore_app {sha}`
    (a restore is itself a checkpoint). `run_in_app {cmd}` runs one shell command in the app's
    directory (≤ 120 s; `npx jest x.test.ts`, `curl` the preview).
11. `ship_app {message}` → the PR URL. The branch is rebuilt on the base first, so the pull
    request is exactly this app's files against the base as it stands — an app shipped, merged
    and improved ships again cleanly. `merge_app {prNumber}` after approval when the app
    belongs in the platform repo. `close_workbench` when done — a running box costs money; it
    idles out after 10 minutes anyway and reopening resumes.

`build_app {brief}` hands a brief to an unattended agent. Use it only when the person wants to
walk away; when they are present the workbench is the honest choice.

## The non-negotiables (each earned by a real failure — `app-anatomy.md`, `design-rules.md`)

- **Events are the truth.** Processors pure, idempotent, bounded, refusing bad payloads; ids
  and timestamps minted in `dataCreator`; bursts carry a collapse key per entity and field;
  `reconstructStateFromEventLog: true`.
- **Every UI action has a tool twin**, and every tool has a real `onClient` (`= execute`).
  A tool result says what was DONE and refuses what was not.
- **Ops declared once** (`defineOps` → `handleOp` → `opTool`); the op owns the timeline
  (`ctx.emit`); server truth through an op, never a self-fetch of `/api/v1`.
- **The import wall**: server code reaches the platform only through `esoul-sdk/server`;
  `app.tsx` is never `"use client"`; the UI imports only `esoul-sdk/react`.
- **Every task side effect lives in a `step.run`**; never `void` a promise inside a step.
- **Nothing opens by default**: every op, route and task is `write` unless declared; `read`
  means workspace members, `public` means share-link holders; `requires:"account"` is the
  sign-in wall.
- **Different people see different rows** — never one screen for everyone. `roles` are your
  vocabulary, `db.rules` decide per row (`creator`, a role, a scoped role `{role, where}`),
  `sealed` hides a field from everyone but its owner, and a `customer` sees only their own
  rows while `staff` see all and never an address. Proved as five people (`data-people-files.md` §2).
- **Telling someone later is a task plus your own table.** No send primitive exists and a task
  cannot look a person up: capture the address while there IS a viewer, put what the task will
  need on the row it will act on, send through the workspace's email app under a `workspaceTools`
  grant, and record the send as an event (`telling-people-later.md`).
- **Missing ≠ empty**: `getStateDescription` uses `incompleteStateNotice`.
- **Native and responsive**: root fills the frame, warm-sepia light / translucent dark,
  opaque popovers in dark, tap-to-act, a 390 px phone shot with no horizontal scroll.
- **Never break the box a person is using**: destructive probes on a throwaway app or when the
  board is idle; a reboot is announced first.

## Honest reporting

Never "shipped" without the PR URL, "merged" without the merge result, "installed" without the
new app's node id, "works" without the drive that proved it. A red or `skipped` gate is
reported with its name and detail. A preview that will not come up is quoted in the compiler's
words. Say which `workspaceTools` grants, public doors, connections and file sources the app
declares and why — the person reads them at install. When the app needs something the SDK
does not have, say so and ask for it in the SDK; do not reach around the wall.
