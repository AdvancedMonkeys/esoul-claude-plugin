# What you are working with — surfaces, powers, limits, costs

Read this before your first call. Most wasted rounds come from asking a surface for something
it does not have, or from believing a preview about something only an install can prove.

## 1. Three surfaces, one app

| Surface | What it is | You reach it with |
|---|---|---|
| **The hosted connection** (`esoul`, OAuth) | the person's whole account: every project, workspace, app | 15 general tools (below) |
| **The Forge board** | an app on one workspace; opens a **box** per app being built | `get_app_tools(<board>)` → 28 `<verb>_<board>` tools via `call_app_tool` |
| **The box** (workbench) | a cloud machine (4 vCPU, 8 GB) holding the platform's source at the board's base branch, your app on branch `forge-app/<board>__<id>`, running `next dev` for the preview | only through the board's tools; you have no shell except `run_in_app` |

The **fifteen hosted tools**: `list_workspaces`, `search_workspace`, `read_app_state`,
`list_app_entries`, `read_app_entry`, `get_app_tools`, `call_app_tool`, `create_app`,
`create_workspace`, `list_files`, `upload_file`, `view_image`, `get_run_status`,
`describe_profile`, `publish_homepage`. Everything an app can do is behind `get_app_tools` →
`call_app_tool` on that app — the list stays small, nothing is out of reach. **Two names
collide**: the hosted `call_app_tool`/`read_app_state` act on installed apps; the board's
`call_app_tool_<board>`/`read_app_state_<board>` act on the app under construction in the box.

The **28 board tools**: `open_workbench`, `close_workbench`, `orient_app`, `list_app_files`,
`read_app_file`, `search_app_files`, `read_platform_file`, `write_app_file`, `edit_app_file`,
`delete_app_file`, `preview_app`, `look_at_app`, `drive_app`, `call_app_tool`, `read_app_state`,
`test_app`, `check_app`, `run_in_app`, `app_problems`, `resolve_problem`, `commit_app`,
`app_history`, `diff_app`, `restore_app`, `put_app_asset`, `remove_app_asset`, `ship_app`, `merge_app`, `build_app`, `add_forge_task`.
(The same handler serves the Python SDK's `esoul.forge` and the `esoul-mcp` server's `forge_*`
tools for people on a Personal Access Token; the verbs and answers are the same.)

## 2. Who may do what

- Only the **workspace owner** authors on a board (open, write, check, ship, resolve). An
  editing collaborator may wake an app already on the board and use its preview. Guests, read-only
  members, public viewers: nothing. You inherit the person you act for — if their chat is refused
  as not the owner, say so.
- The board needs the owner's **GitHub connection** (Account settings → GitHub) to open a box. A
  friend without access to the platform repo still gets a box: the platform's own installation
  clones for the app arm.
- The box holds the owner's **files grant** (24 h; workspace files + Google Drive of THAT
  workspace; renewed on `open_workbench` / `preview_app`) and nothing else — no PAT, no session.
  Other apps' tools and the person's computer are reached **through the board's open tab** (§4).

## 3. What a preview gives you — and does not

A box runs your app over an in-process stand-in for the platform (a workbench store):

| Arm | In the preview | Not in the preview — install to get it |
|---|---|---|
| events, tools, UI | yes: `call_app_tool` → fold → the frame | — |
| ops (`callPluginOp`, `readAppState`) | yes, over the preview's fold and **in-memory tables with your real rules** | a real database (rows vanish with the box) |
| routes (`pluginRouteUrl`, SSE) | yes; the caller is a writer | auth — the box is single-tenant |
| tasks (`kickPluginTask`) | yes, in-process, same `ctx`; `notify` reaches `usePluginRealtime` | durability, retries, the scheduler (`pollTasks`), `waitForEvent`'s `if`; `step.run` is NOT a replay barrier there — an unwrapped side effect that fires N+1 times on the platform fires once in a box |
| realtime channels + audiences | yes (polled from the store); VIEW AS shows what each persona hears | the broker |
| files + Drive (`filesForOp`, the hooks) | **yes, the REAL files** through the box grant — no board tab needed | — (a write in a box is a real write: drive writes on a scratch folder the person names) |
| other apps' tools, `computer()`, `readAppState` of another app | yes **only while the board's tab is open on the preview**; headless you get "no board is connected to this preview" | — |
| webhooks | the handler runs; no sender can reach a box | receiving |
| connections (OAuth / API key) | not yet | a granted connection |
| `generateAppImage` | refused on purpose (it bills) | — |
| `renderChartImage` | returns `base64`, never a `url` (nothing to store a file in) | a stored PNG URL |
| VIEW AS | personas: `owner`, `member`, `member-readonly`, `visitor-a`, `visitor-b`, `anonymous`, `agent`; with a grant: `visitor-a?grant=customer&customer=143` | production never reads a persona |

**Headless facts** (you drive over MCP; nobody may have the page open):
- `look_at_app` once before the first `call_app_tool`/op — the page seeds the store; without it
  an op answers "the preview holds no … app".
- Events a **tool** emitted are not in the store a later fresh page sees. To prove "the app
  remembers X", drive the UI (`drive_app`) then `look_at_app` again.
- `server.ts` before (or with) `plugin.json`: the box re-registers on either change; a manifest
  naming ops the server does not export is refused and the journal says so.
- A file that does not compile takes the WHOLE preview down (every route 500) until fixed; the
  journal survives and the compile error arrives as a `dev` row.
- Two clients on one box (the person's board chat and you) fight: if the box answers 502 /
  "non-JSON", stop, let one boot finish, continue.

## 4. The board's tab — when the preview needs the person

Anything that reaches OTHER apps from the box (`useWorkspaceTools` in the UI, `callWorkspaceTool`
/ `computer()` / another app's `readAppState` in an op or task) travels through the preview page
→ postMessage → the board's tab → the platform, behind the board's own wall (owner + a real board
+ the manifest's `workspaceTools`, enforced in the box with production's sentence). So: unit-test
those paths with the machine mocked; to drive them for real, ask the person to open the app's
preview on the Forge board, or install.

## 5. The problem journal — the ⚠ paragraph

Every changing or observing answer (`write/edit/delete/restore/call_app_tool/read_app_state/
look_at_app/drive_app/test_app/check_app`) **begins with the problems the running app hit since
your last call**, each with an id (`p_3f2a9c1d`): an op that threw (message, your stack frames,
the args' keys, who was viewing), a call with input the op does not take, a task that failed, a
page console error, an uncaught throw, a failed app call, a compile error, a screenshot defect
(clipped / blank / errored). The same failure in the same place is one row with a count; a
recurrence after you resolved it is "↩ came back". Read it first, fix it first, then
`resolve_problem {id, note}` with one honest line — the person sees the row turn green in the
board's Issues tab. Never resolve what you did not fix; a row your own probe caused is resolved
as "my probe". `app_problems` lists the box's journal and the board's rows (which outlive
restarts). A read that cannot happen (no preview) says nothing rather than "clean".

## 6. Caps — numbers you will hit

| | |
|---|---|
| app files | `.ts .tsx .json .css .md .txt .svg`; ≤ 512 KB each; ≤ 200 files; paths ≤ 6 deep |
| `edit_app_file` | each `find` matches exactly once, or nothing is written |
| `drive_app` | ≤ 40 steps; `type` text ≤ 300 chars |
| `run_in_app` | ≤ 120 s; whole output in `.esoul/logs/run.log` |
| an op | one request, ≤ 300 s; ops must be idempotent (a tool call is retried) |
| a route | as long as one request (minutes on Fluid); nothing outlives it |
| a task | seconds per hop (kick → task 2–15 s; a fold read ≈ 3 s); `description` ≤ 255 chars (it is the Inngest function name — longer breaks the WHOLE sync silently) |
| `pollTasks` | 5-minute granularity, minimum 5 |
| a `my_computer` | one wait ≤ 55 s, one command ≤ 900 s, **8,000 characters of output kept**; commands approval-gated unless the OWNER set Auto |
| files | `read` cap 25 MB (100 MB ceiling); `readMany` ≤ 200 refs; `listAll` max 20,000; a read grant 1 h default, 24 h max; a route token ≤ 30 days |
| tool output to a model | keep answers short; a picture reaches a chat only as a URL — never base64 in text |
| the box | idles out 10 min after the last touch; `check_app` takes minutes; the first `open_workbench` on a board takes minutes; a production deploy after a merge 7–10 min |

## 7. What things cost the person

A running box is billed by the minute — close it when done (`close_workbench`; it idles out
anyway). `generateAppImage` and every model call an app makes spend the OWNER's credits — keep
them behind owner-only ops. A task holds a concurrency slot while running (a parked wait does
not). A `my_computer` command runs on their hardware and is **recorded on the workspace
timeline** — never put a secret in one. A public door (`access: "public"`) is listed on the
install card by name; a public tool that spends credits needs a budget the person sets.

## 8. The review boundary and what "installed" means

`ship_app` opens a pull request (label `user-app`); a person reads the diff; one release script
runs the import wall, the sync, your tests and the type check, merges, deploys, **entitles the
submitter** (the app is theirs alone until the owner makes it public) and tells the board
"released — add it to a workspace". Alternatively the board's REPOSITORY row pushes the app to
its own GitHub repo and the owner installs it by link in Settings → Apps (an `apps.lock.json`
pin; update and uninstall are one-line edits; instances keep their timelines). Then
`create_app(application_type="plugin_<id_with_underscores>", name="…")` puts an instance on a
workspace: its tools are minted natively (`<verb>_<instance name>`), its tasks run on the
platform's executor, its routes are mounted, its tables were created additively at install.

An installed app's server code runs inside the platform's process with the platform's
credentials; the import wall is what makes the review tractable. Say plainly what the app can
reach.
