---
description: Open this folder's ExternalSoul memory and recall what was learned here before.
---

Ground yourself in this project's durable memory before doing anything else.

1. Call `memory_open` to create or re-attach the memory space for the current
   working directory. The folder→space map persists, so reopening a folder
   brings its memories back.
2. Call `memory_recall` with a query describing what we are about to work on.
3. Report back briefly: what you already knew about this folder, and what is
   missing. Do not restate everything — name the facts that bear on the work.

If the user gave an argument, use it as the recall query: $ARGUMENTS

Throughout the session, save durable facts, decisions and preferences with
`memory_remember` (grouping related ones under a `topic`), then call
`memory_graph` so they link up. Save what would be expensive to rediscover —
not what the repository already records.
