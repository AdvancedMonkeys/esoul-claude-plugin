---
description: Ground yourself in this project's ExternalSoul memory, and write back what is worth keeping.
---

Use the ExternalSoul workspace as durable memory for this project, so what you
learn here survives the session.

## Recall first

1. `search_workspace` for the project you are in — its name, the repo, the
   thing you are about to work on. Search spans every workspace you own.
2. For each promising hit, `read_app_entry` with the returned `app_id` and
   `entry_key`. Read only the entries that matter; do not load whole apps.
3. Report briefly: what you already knew about this project, and what is
   missing. Name the facts that bear on the work — do not restate everything.

If the user gave an argument, use it as the search query: $ARGUMENTS

## Write back

When you learn something worth keeping — a decision and its reasoning, a
constraint, a preference, a hard-won gotcha — put it in a notes app:

- find an existing notes app with `list_workspaces` (look for a
  `block_note_editor`), or make one with
  `create_app({application_type: "block_note_editor", name: "Memory"})`;
- `get_app_tools` on it, then `call_app_tool` with `create_page_*` or
  `append_to_page_*` to add what you learned.

Prefer appending to a page that already covers the topic over creating a new
one. Save what would be expensive to rediscover — not what the repository
already records.
