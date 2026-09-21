---
name: forge-app-builder
description: Build a NEW ExternalSoul app (a plugin with its own UI, events and agent tools) inside the user's Forge over MCP — open a live workbench, write the source, watch it hot-reload in their frame, LOOK at screenshots, call its tools before it is installed, run the checks, open the pull request, and install it once merged. Use whenever the user says "make me an app", "build an app for esoul", "I want an app that …", or asks to change an app that is still being built.
---

# Build an ExternalSoul app with the Forge

You are writing a real, native ExternalSoul app — not a widget, not a page. It will sit on the
user's workspace beside their spreadsheets and notes, hold its state as events on the shared
timeline, expose tools that chat, voice and agents call, and be scrubbable in time like every
other app. The Forge gives you a cloud machine holding a clone of the platform on the app's own
branch, so you write the source, see it running in the user's own frame within seconds, and ship
it as a pull request a person approves. **You are the only model in this loop**: nothing writes
the app but you, and nothing is installed until a human has read the diff.

Two things matter more than everything else in this file:

1. **The app must follow the platform's design philosophy** — events are the truth, agents are
   first-class actors, the app stores knowledge, it works on every surface, and it looks and feels
   native on desktop AND phone in light AND dark. `reference/design-rules.md` is the checklist;
   `reference/app-anatomy.md` is the code contract. Read both before writing a line.
2. **Look at what you built.** The workbench screenshots it for you. Open the images. A tool
   result that says "Preview: DOWN" is the compiler telling you what you broke — fix that first.

## Where the tools are

The Forge is an app on the user's workspace (application type `forge`, usually named "Forge").
Its tools are minted as `<verb>_<board name>` — on a board named "Forge" they are
`open_workbench_Forge`, `write_app_file_Forge`, and so on. Find the board with `app_list` /
`list_workspaces`, confirm the names with `get_app_tools(<board id>)`, and invoke them with
`call_app_tool(<board id>, "<tool>", {…})`. If there is no Forge board yet, the user creates one
(`app_create(application_type="forge", instance_name="Forge")`) and, in Account settings →
GitHub, connects GitHub and binds the ExternalSoul repository to the board. A board with no
GitHub connection refuses to open a workbench and says so — relay that, do not work around it.

The board is also what the user WATCHES: the app being built appears in its picker as
"✦ <name> (building)", the frame shows the live preview, and the "Being built" panel shows every
file, every change as a diff, every checkpoint with a Restore button, and every tool call you
make. Write as if they are reading over your shoulder, because they are.

## The loop

Every step is one board tool. Every argument below is the tool's `args`.

1. **Open.** `open_workbench {pluginId, name, description, icon}` — `pluginId` is lower-case with
   dashes (`sticky-notes`); `name` is what people see; `icon` a lucide name from the list the tool
   prints when yours is wrong. The first open scaffolds the package from the platform template
   (`plugin.json`, `app.tsx`, `ui/<id>-ui.tsx`). Opening again later resumes where you left off.
   The first app on a board takes a few minutes to open (clone + install); every later app on
   that board forks the board's warm base and opens in seconds. Say so and keep going.
2. **Read what you got.** `list_app_files` then `read_app_file {pluginId, path}` for each file.
   The scaffold is a complete, working app (one event, one tool, standard guards). Keep its
   shape; replace its content.
3. **Write the app.** `write_app_file {pluginId, path, content}` for new or wholly-rewritten
   files; `edit_app_file {pluginId, path, edits:[{find, replace}]}` for changes — each `find`
   must match EXACTLY ONCE, and nothing is written unless every edit matches. Files are
   `.ts .tsx .json .css .md .txt .svg`, ≤ 512 KB each, ≤ 200 per app, paths ≤ 6 deep.
   **Every write, edit, delete and restore answers with the preview's health**:
   `Preview: live (answered 200 in 0.9 s)` means that build is on screen;
   `Preview: DOWN — …` carries the dev server's own error lines (the compile error, the file, the
   line). Fix it before doing anything else. `Preview: not running` means start it (step 4).
4. **Run it.** `preview_app {pluginId}` starts the dev server in the workbench (a minute or two
   cold, seconds warm) and puts the URL on the board's frame. After that every write hot-reloads.
5. **Look.** `look_at_app {pluginId, intent}` screenshots the running app on desktop-light,
   desktop-dark and phone-light, and returns the image URLs plus what is on screen, any error the
   page threw, and anything clipped or overflowing. **Open the images and judge them yourself.**
   A phone shot with a horizontal scrollbar, a dark shot with unreadable text, a desktop shot with
   an empty grey box — those are your bugs. Leave `critique` off; it asks a second model to
   describe what you can see.
6. **Drive it like an agent would.** `call_app_tool {pluginId, tool, args}` runs one of the app's
   OWN tools inside the workbench, before it is installed anywhere; the events it emits are
   applied into the live preview, so the user sees the result in their frame exactly as if they
   had tapped. `read_app_state {pluginId}` returns the preview's current state (it needs the
   board open in the user's browser — the state lives in that tab; if nobody's tab answers, the
   tool says so). A tool that needs SERVER truth (a plugin op reading the database) is refused in
   the workbench with a message naming `read_app_state` — that is expected, not a bug: there is no
   database behind a preview.
   **Tasks, ops and routes run in the preview** (2026-09-10): a tool that kicks a task reaches the
   preview's in-process runtime; its `dispatchEvent`s land in the frame, its `notify`s reach
   `usePluginRealtime`; ops and routes answer from the preview's own fold; `read_app_state` reads
   that fold even with no tab open. The frame's greeting names what its box can do (`tasks, ops,
   routes, realtime, viewer, db`) and the frame reloads itself when the build changes. What a preview does not
   give: durability across a process death, retries, a scheduler, real auth — install for those.
7. **Test, then check.** `test_app {pluginId}` runs ONLY the app's own tests — seconds — after
   any change to the schema, an event or a tool; use it freely. `check_app {pluginId}` runs what the pull request will run: the registry sync, the
   app's own tests plus the platform's boundary and crash-safety suites, and a type check. Read
   the detail of every red gate and fix it. **`skipped` is not a pass** — a memory refusal means
   the preview and the checks did not fit together; close the preview's tab work, retry.
8. **Undo when you must.** Every change is a git checkpoint with a short id, shown on the board.
   `restore_app {pluginId, sha}` puts the app back the way it was after that change — and is
   itself a new checkpoint, so nothing is ever lost.
9. **Ship.** `ship_app {pluginId, message}` runs the checks, commits, pushes the branch and opens
   the pull request. It refuses unless every check is green (`force:true` ships past an ADVISORY
   only when the user has decided that). Give the user the PR URL. **This is the review
   boundary**: nothing reaches anyone's ExternalSoul until a person approves that diff.
10. **Merge and install.** After the user approves, `merge_app {pluginId, prNumber}` squash-merges.
    The merge triggers a production deploy (several minutes). Then
    `app_create(application_type="plugin_<id with underscores>", instance_name="<name>")` puts
    the app on the workspace, and its tools are live in chat, voice, agents and MCP.
11. **Close.** `close_workbench {pluginId}` when you are done for now. A running workbench costs
    the user money; it also idles out on its own, and reopening resumes with everything kept.

`commit_app {pluginId, message}` commits without shipping and shows the diff so far — use it at
natural milestones so the branch reads like a story.

## Seeing your app as someone else (VIEW AS)

A box has no accounts, so it has PERSONAS: owner, staff, member-readonly, visitor-a, visitor-b,
anonymous, agent. Set one and every op, route and kick the preview makes carries it
(`x-esoul-preview-viewer`), the app's `useViewer()` re-renders for it, and `pluginDb(ctx)` scopes the
app's own tables (plugin.json `db`) to it — so you can create an order as visitor-a, switch to
visitor-b and watch it disappear, before the app is installed anywhere. The reference shop
(`src/plugins/shop-min`) is the worked example; `scripts/creator/wb-access-drive.sh` drives all of
it and is written to FAIL if visitor-b ever sees visitor-a's row. Production never reads the
persona: a real request is who they are.

## Understanding an app you did not write (zero context)

When the user asks for an improvement to an app that already exists and nothing about it is in
the conversation, do not read files one by one. In this order:

1. `orient_app {pluginId}` — the manifest outline (ops, tools, routes, tasks, tables, roles),
   the files with sizes, the README's head, the last checkpoints, whether the preview runs, the
   board's open issues. One call; it tells you where to look.
2. `search_app_files {pluginId, query, glob?, regex?}` — grep for the name the ask touches.
   `scope:"sdk"` searches the esoul-sdk source and docs when the question is about the SDK.
3. `read_app_file {pluginId, path, from, lines}` — the lines you need, with the file's total.
   `read_platform_file` opens the SDK's own source, its docs, the box's stand-ins and the fixture
   apps (an allowlist; nothing else is readable) when a call's answer surprises you.
4. `app_history` / `diff_app {sha}` — what earlier work changed; `restore_app` goes back.
5. `run_in_app {pluginId, cmd}` — one shell command in the app's directory (`npx jest x.test.ts`,
   `node -e …`, `curl` the preview); ≤ 120 s; the whole output is `.esoul/logs/run.log`.
   Every `test_app` / `check_app` answer names the log holding its whole output the same way.

Then edit with `edit_app_file` (exact `find` text you just read), `test_app`, `look_at_app`,
`resolve_problem` for the rows the ⚠ paragraph listed. Over the `esoul-mcp` server the same
verbs are `forge_orient`, `forge_search`, `forge_read`, `forge_read_platform`, `forge_history`,
`forge_diff`, `forge_run`, `forge_edit` (with `expect` = the checkpoint you read at, refused if
the box moved), `forge_test`, `forge_check`, `forge_look`, `forge_drive`, `forge_resolve`.

## Iterating with the user

The point of the workbench is the conversation. The user plays with the latest build in their
frame and tells you what is wrong; you `edit_app_file`, the preview hot-reloads, they try again.
Keep each round small. After a visual change, `look_at_app`; after a behaviour change,
`call_app_tool` + `read_app_state` or the user's own report. When they say it is right, `check_app`
then `ship_app`.

The other path, `build_app_<board> {brief}`, hands a plain-language brief to a sandbox agent that
writes the whole app unattended and opens a PR. Use it only when the user wants to walk away.
When they are present, the workbench is the honest choice — they see every change as it happens.

## What "responsive" means here

The app renders inside the platform frame at any size: a desktop window, a maximized canvas, a
390 px phone. The root fills its frame (`width:100%; height:100%; overflow:hidden`) as a flex
column; chrome rows do not shrink; the content area is `flex:1; minHeight:0` with its own
scroll. Layout decisions (columns, wrapping) measure the VISIBLE scroller, not a large canvas
inside it, and re-measure on resize. Toolbars wrap; labels collapse on narrow widths; nothing
ever needs a horizontal page scroll. Touch is first-class: tap to act (never double-tap),
`touch-action: manipulation`, larger hit targets on coarse pointers. `look_at_app` gives you the
phone shot — treat a phone defect as a real defect.

## Honest reporting

- Never say "shipped" without the PR URL, "merged" without the merge result, "installed" without
  the new app's node id.
- A red or skipped check is reported as such, with the gate name and its detail.
- If the preview will not come up, quote the dev server's error from the tool result; do not
  guess.
- Cross-app calls from the app's UI (`useWorkspaceTools`) work in the preview through the board's
  tab and, once installed, only through the grants listed in `plugin.json` `workspaceTools` —
  say which grants the app needs and why.

## A worked sequence (sticky notes, built live 2026-09-10)

```
open_workbench   {pluginId:"sticky-notes", name:"Sticky notes", description:"…", icon:"StickyNote"}
read_app_file    {pluginId:"sticky-notes", path:"app.tsx"}            → the scaffold's schema
write_app_file   {pluginId:"sticky-notes", path:"app.tsx", content:…} → events + tools
write_app_file   {pluginId:"sticky-notes", path:"ui/sticky-notes-ui.tsx", content:…}
write_app_file   {pluginId:"sticky-notes", path:"server.ts", content:…}   → a read op
write_app_file   {pluginId:"sticky-notes", path:"sticky-notes.test.ts", content:…}
edit_app_file    {…, path:"plugin.json", edits:[{find:"\"ops\": []", replace:"\"ops\": [\"read-notes\"]"}]}
preview_app      {pluginId:"sticky-notes"}
look_at_app      {pluginId:"sticky-notes", intent:"a warm wall of paper notes; readable in dark"}
call_app_tool    {pluginId:"sticky-notes", tool:"add_note", args:{text:"milk", color:"mint"}}
read_app_state   {pluginId:"sticky-notes"}                              → notes:[{id,text:"milk",…}]
test_app         {pluginId:"sticky-notes"}                              → the app's own tests, seconds
check_app        {pluginId:"sticky-notes"}                              → registry/tests/types green
ship_app         {pluginId:"sticky-notes", message:"Sticky notes: a wall of paper on the timeline"}
… the user approves PR #23 …
merge_app        {pluginId:"sticky-notes", prNumber:23}
app_create       (application_type="plugin_sticky_notes", instance_name="Sticky notes")
```
