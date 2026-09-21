---
name: cloud-browser
description: Drive the user's ExternalSoul cloud browser over MCP — browse websites, read and extract pages, click and fill forms, work their logged-in sites, DOWNLOAD files (invoices, CSVs, PDFs — even behind logins) into their workspace, process them in the code sandbox, and open the result in the right ExternalSoul app. Triggers on "download the invoice from my portal", "check the price on that site", "fill in the contact form on", "grab that PDF and translate it", "open twitter and check my mentions". Requires an ExternalSoul MCP connection with tools access (list_workspaces / get_app_tools / call_app_tool, plus create_app or app_create); the browser is a real cloud Chrome the user shares with you. NOT for plain web research a search tool already answers.
---

# Drive the ExternalSoul cloud browser

You are driving a REAL Chrome running in the user's ExternalSoul workspace. They see it live
in their `cloud_browser` app and can grab the mouse at any moment; every action you take lands
on their audit timeline. Browser time bills the user by the minute while a session is awake —
be purposeful, and know that an idle session parks itself after ~5 minutes (parking loses
nothing: tabs and logins survive).

## The two ways the tools appear

1. **Generic pair (always works, always current):** `get_app_tools(<browser app id>)` lists the
   app's own toolkit — ~21 tools named `browser_<verb>_<instance name, spaces as underscores>`
   — and `call_app_tool(app_id, tool_name, arguments)` invokes them. This is the reliable path:
   the toolkit is served by the platform, never by a stale MCP snapshot.
2. **Native `browser_*` MCP tools** (the pip `esoul-mcp` server has them; public storefront
   connections do not): shortcuts for the same operations, taking `node_id` + snake_case args
   (`tab_index`, `max_wait_seconds`). If a native tool you expect is missing, fall back to the
   generic pair — same engine underneath.

Everything below writes toolkit names as `browser_<verb>_<base>`; `<base>` is the browser app's
instance name.

## STEP 0 — find the browser

`list_workspaces` → pick the workspace → find an app of type `cloud_browser` (via the workspace
map / app list). If there is none, create one (`create_app` / `app_create`, application_type
`"cloud_browser"`, a short name like "Browser"), then `get_app_tools` on it.

## STEP 1 — status FIRST, always

`browser_status_<base>()` never wakes a session (never spends) and tells you: awake or parked,
the open tabs WITH their 0-based indices, which sites are signed in, and recent downloads.
Re-read it after closing any tab — **tab indices SHIFT when a tab closes.**

## STEP 2 — navigate and read

- `browser_goto_<base>({url})` wakes the browser if parked and loads the page. **Never goto a
  URL that points at a file (.pdf etc.)** — file loads time out; downloading is STEP 5.
- `browser_read_page_<base>()` — the page as plain text, no AI cost. Read before you act.
- `browser_extract_<base>({instruction})` — structured data ("the 10 results: title, price").
- `browser_observe_<base>({instruction?})` — clickable things with selectors; FIND before acting.
- `browser_screenshot_<base>()` — when you must SEE the page (returns a workspace fileId).

## STEP 3 — act, respecting the autonomy gate

`browser_act_<base>({instruction, irreversible?, approved?, variables?})` — one natural-language
action. Set `irreversible: true` for anything that submits, posts, purchases, sends, signs in.
Sites default to ask-before-acting: a refusal with `needs_approval` is the gate WORKING — do
NOT retry blindly. Ask the user for their OK, then re-issue the SAME call with `approved: true`.
A read-only site refuses all acts and approval cannot override it — only the user can change
that policy in their app. Secrets the user explicitly gives you ride in `variables` as `%name%`
slots referenced in the instruction; the values never reach the model or the logs.

**Logins: the user's hands, not yours.** Never ask for a password. Ask the user to open the
browser app in ExternalSoul and log into the site by hand in its live view (their hand session
is not video-recorded; credentials go straight from the remote Chrome to the site). The browser
then STAYS signed in for you — `browser_status` shows the site under signed-in sites.

## STEP 4 — tabs and waits

- `browser_open_tab_<base>({url?})` opens AND switches to a new tab (returns its index) — hold a
  source page open while working in another. `browser_switch_tab_<base>({tabIndex})`,
  `browser_close_tab_<base>({tabIndex})`. Most tools take an optional `tabIndex`; reads on a
  background tab don't steal the user's focus.
- `browser_wait_for_<base>({selector | gone | text | url | js, maxWaitSeconds?})` — EXACTLY ONE
  condition; polls ~2.5s up to the cap (default 30, max 120) and ALWAYS returns
  `{met, timedOut, waitedSeconds}`. `url` is how you wait FOR a navigation. A timeout is an
  honest answer — check `met`, never assume.

## STEP 5 — download files into the workspace

`browser_download_<base>({url}| {selector})` fetches the file IN the page with the site's own
cookies — files behind the login work — and lands it as a workspace file:
`{fileId, name, bytes, contentType}`. **No fileId = no file; never claim success without it.**
Add `folderPath` ("openai invoices", "invoices/2026") to file it into a workspace folder —
created if missing; a batch of related downloads belongs in one folder, not loose at the root.
Find the URL first via read_page/observe, or enumerate deterministically:
`browser_run_script_<base>({expression: "return [...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => /\\.(pdf|csv|xlsx|zip)([?#]|$)/i.test(h))"})`.
Cap 25MB. A download BUTTON with no href: act it first, then download the URL it lands on; a
POST-only export with no URL genuinely can't be captured — say so. The user sees every download
in the browser app's Downloads panel; you see them under `recentDownloads` in status.

## STEP 6 — process the file in the sandbox (when asked)

Find/create an `e2b_sandbox` app and `get_app_tools` it. Its toolkit (suffixed with ITS
instance name): `create_tab_<sb>({name, code})` → `run_code_<sb>({tabId})` →
`save_to_workspace_<sb>({filePath})`. Every workspace file is auto-copied into `/home/user/`
when the sandbox starts; a file downloaded AFTER the sandbox started needs
`copy_file_to_sandbox_<sb>({fileId})` first. Two rules that save you: a `save()` inside Python
writes SANDBOX scratch only — the file exists for the user only after `save_to_workspace`
returns its `[fileId: …]` marker; and report the file name that tool RETURNS (name collisions
get auto-suffixed). For PDFs, edit with PyMuPDF span-by-span to keep layout, and before saving
RENDER the page (pypdfium2) and LOOK at the image output — bytes being right does not mean
pixels are right.

## STEP 7 — open the result in the right app

Read `reference/open-in-apps.md` — the routing table (pdf → pdf_viewer, docx → word_editor,
xlsx/csv → excel_editor, images → image_viewer, else the files panel) with the exact opener
tool names. A delivered file the user has to hunt for is half-delivered.

## STEP 8 — verify and report honestly

`read_app_state(<browser app id>)` shows the authoritative fold: session, tabs, the action log
(every goto/act/download you performed), downloads. Verify from state, never from a bare
success response. Then tell the user: which WORKSPACE and app you drove (they may be looking at
a different one), what you did, the ACTUAL file names and where they landed, and anything that
degraded — plainly, instead of rounding up to success.

## When this goes wrong

- `needs_approval`: ask the user, re-issue with `approved: true`. Never spin-retry.
- `autonomy_read_only`: the user marked the site read-only; only they can change it.
- `browser_plan_limit` (402): the browser plan is out of minutes — tell the user; retrying won't help.
- "Navigation start timed out" on a file URL: use `browser_download`, not goto.
- `no_such_tab` / `last_tab`: stale index — re-run status and re-address.
- A tool you expected isn't in your MCP tool list: use `get_app_tools` + `call_app_tool` — the
  toolkit is always current.
