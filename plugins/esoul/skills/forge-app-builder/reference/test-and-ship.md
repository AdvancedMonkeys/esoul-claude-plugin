# Prove it with tools, then ship it

"It renders" is not "it works". Every arm of the app is proven by a tool before a person is
asked to look, and the evidence is what you report.

## 1. The ladder, after every round

| Step | Tool | Proves | Not |
|---|---|---|---|
| health | the ⚠ paragraph on every answer | the running app threw nothing since your last call | anything you did not exercise |
| layout | `look_at_app {intent, viewer?}` — desktop-light, desktop-dark, phone-light | fits the frame, readable in both themes, no clipped controls, the empty state | behaviour |
| behaviour | `drive_app {steps, viewer?}` — click / type / keys / select / wait / say; console errors, throws, failed calls, a final shot | a flow works as a person, as each persona | what a person would notice in motion |
| the agent's view | `call_app_tool {tool, args}` → `read_app_state` | every tool does what it says, refuses what it cannot, the fold agrees | voice (unit-pin `onClient === execute`) |
| server truth | `call_app_tool` on an op tool; `run_in_app {cmd:"curl …"}` for a route | ops answer over the preview's fold / tables with your rules; routes stream | a real database, real auth |
| durable work | `call_app_tool` on the kicking tool → `read_app_state` → the frame's realtime | the task runs in-process, dispatches, notifies | durability, replay barriers, cadences |
| people | `look_at_app` / `drive_app` with `viewer: "visitor-b"` etc.; `memoryDb` + `fakeViewer` + `runOp` in tests | visitor-b sees 0 of visitor-a's rows; the sign-in wall appears where declared | production's real identities |
| contract | `test_app` (seconds) | the fold contract, ops, the task with a fake ctx, the helper compiles | types (local jest is `isolatedModules`) |
| the bar | `check_app` (minutes) | registry sync, the import wall, your tests + the platform's boundary/crash-safety suites, `tsc`, the thin-preview walk | — |

Read the ⚠ paragraph on every answer first. `check_app`'s `skipped` is not a pass. Every test,
gate and run keeps its whole output in `.esoul/logs/<name>.log`; the answer keeps a tail and
names the file — read the window (`read_app_file {path:".esoul/logs/gates-types.log", from, lines}`)
instead of trusting a tail.

## 2. Writing a drive

```json
[{"type": ["input[aria-label='Folder path']", "sheets/quality_dataset/Type5_quality/passed"]},
 {"keys": ["input[aria-label='Folder path']", "Enter", 1]},
 {"wait": 4000},
 {"say": "[aria-label='Labelling progress']"},
 {"click": "[role='option']:first-child"},
 {"say": "main"}]
```
Give controls `aria-label`s as you build — they are your drive's selectors AND the app's
accessibility. Drive a flow, not a person's live session: a click that starts a job starts it.
`drive_app` with clicks/keys/select and `close_workbench` answer `board_in_use` while a person's
board polled the preview in the last 30 s — do not force past that without their leave. Drive
**both surfaces** when the app has two (the owner's editor AND the visitor's view): a florist
drive once passed while the editor's page was blank.

## 3. Test tools — add, use, remove

Probes that need a door the product does not have (`tools-chat-and-voice.md` §5): `__test_*`
tools / `"__test-*"` ops, owner-gated at the seam, used from `call_app_tool` to set up state,
then the REAL tools and UI are driven against it. Before shipping: `search_app_files
{query:"__test"}` finds nothing in `app.tsx` / `ops.ts` / `server.ts` / `plugin.json`; the
assertions live on in `<id>.test.ts`; `check_app` again after the removal. A product feature the
person asked for (a real reset) ships with its access declared and a confirm — it is not a test tool.

## 4. The journal — closing the loop honestly

`app_problems` lists the box's journal (restarts with the preview) and the board's rows (outlive
restarts). After a fix: drive the same flow, then `resolve_problem {id, note}` with the line the
person will read in the Issues tab ("the poll no longer throws on an empty log"). A row that
comes back after you resolved it is "↩ came back" — say so, do not resolve it again with the same
note. Rows your own probes caused are resolved as "my probe". When the person says "I see red
rows", list them, resolve only what is fixed, name what remains and why. A refusal must never
have an empty reason ("the bridge did not come up: " with nothing after the colon was the first
bug an owner had to photograph).

## 5. Before `ship_app` — the checklist

- [ ] ⚠ paragraph clean on the last five answers; every journal row resolved or explained.
- [ ] `look_at_app` in both themes and on the phone, as every persona the app has.
- [ ] A drive per flow, as owner and as the least-privileged persona; visitor-b sees nothing of
      visitor-a's.
- [ ] Every UI action has a tool twin; `call_app_tool` on each; refusals are words, not throws.
- [ ] `__test` doors removed; `test_app` green; `check_app` three green, none `skipped`.
- [ ] `plugin.json`: `version` bumped; every op/route/task with its access; every grant, public
      door, connection and file source present and explained in your message to the person.
- [ ] No secret anywhere; no `fetch("/api/v1/…")`; no `@/` import; `app.tsx` not `"use client"`.
- [ ] `commit_app` at the milestones so the branch reads like a story.

## 6. Shipping — two paths, one review

**Into the platform** — `ship_app {message}` runs the checks, commits, pushes the app's branch,
opens (or updates) a pull request labelled `user-app` and `submitted-by:<you>`; refuses unless
every check is green (`force:true` only past an ADVISORY, and only when the person decided).
Give the PR URL — nothing reaches anyone's ExternalSoul until a person approves that diff. After
approval: the owner's release script (or `merge_app {prNumber}` for the owner's own apps) runs
the wall, sync, tests, types, merges declared npm dependencies onto the branch, squash-merges,
waits for the deploy (7–10 min), grants the submitter the **entitlement**, and tells the board
"released — add it to a workspace". A released app is the submitter's alone until the owner makes
it public.

**To the app's own repository** — the board's REPOSITORY row: create a repo (private by default)
or link one, then **Open pull request** exports the app directory as one commit on branch
`forge/<id>` (never forced; `main` never written directly); the message carries the journal
resolutions since the last push — write them as a changelog. The owner installs it by link in
**Settings → Apps**: Inspect (manifest, wall over every file, undeclared deps, the tables it
would add, every refusal verbatim) → Install → one durable job (a one-line `apps.lock.json` pin,
the build, the Inngest sync's answer, the entitlement). Updates are asked for (Check for updates
→ Update to <sha>); Uninstall keeps every instance's timeline and every table.

**Then** `create_app(application_type="plugin_<id_with_underscores>", name="…")` on a workspace
(the hosted tool; the person can also use the picker or say "add <name>" in chat). Report the
node id. Its tools are live in chat, voice, agents and MCP; `get_app_tools` on it shows them
minted as `<verb>_<instance name>`.

## 7. After install — what still needs a look

- A task's first real run: kick it from chat, watch the fold; after any deploy touching a task the
  platform's Inngest sync must have accepted the functions (a description over 255 characters
  fails the whole sync while the deploy says READY).
- A webhook's first real delivery (a sender can only reach an installed app).
- A connection's first real credential.
- A public door with a stranger's eyes: open the share link signed out.
- Cost: what the app spends when idle (poll cadences, realtime) and when used (model calls,
  images). Say the numbers you know.

## 8. Words to use and not use

"Shipped" = the PR URL. "Merged" = the merge result. "Released" = the board said so.
"Installed" = the new instance's node id. "Works" = the drive that proved it, as whom. "Ready" =
`check_app` three green. A red or `skipped` gate is reported with its name and detail; a preview
that will not come up is quoted in the compiler's words; a thing you did not run is a thing you
do not claim.
