---
description: Recall what your ExternalSoul memory holds about this project (or about the argument), and keep what is worth keeping.
---

Use the user's lifelong ExternalSoul memory. Follow the `memory` skill; this is the short form.

## Recall

Topic: $ARGUMENTS. If that is empty, use this project: the repo name, what it builds, and what you are about to work on.

1. `recall({query: <the topic in plain words>})`. If the user named a time, pass it verbatim as `when`.
   One call searches past work sessions, remembered facts and all workspace content.
2. Open only what matters. Use `read_app_entry` (one page or sheet) or `read_app_state` with the ids
   recall returned.
3. Report briefly:
   - what is already known: dates, decisions, where things live, each artifact's status today (renamed, deleted or in Recently deleted, said plainly), and its `link`;
   - what is missing.

   If `selected_by` says "similarity only", judge relevance yourself. If nothing fits, say so. Never
   guess.

If `recall` is not in your tool list (you are connected to someone else's storefront, not your own
`/mcp/me`), use `search_workspace` → `read_app_entry` instead, and say remembering is unavailable here.

## Keep

When the user states something durable, call `remember({text})` with one fact per call, as a full
sentence that stands alone. Examples: a decision and its reason, a constraint, a preference, who someone
is, where something lives.

A correction is a new `remember` under the same `subject` that recall returned. The old version is
kept as history. Work done in apps is recorded automatically, so do not re-log it.

Never create a separate "Memory" notes app for facts; `remember` is the one memory.
