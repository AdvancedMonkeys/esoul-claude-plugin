---
name: agent-recipes
description: Complete, working agent networks for ExternalSoul's agent builder — inbox triage when an email arrives, a researcher with web search writing into notes, lead enrichment over every row of a spreadsheet, a report that builds its own slide deck, approval before anything is sent, a planner handing work to specialists, a daily/event watcher, image making, and networks that call networks. Use with the agent-builder skill when someone asks for a kind of agent and you need the right shape fast; adapt names, apps and instructions to their workspace.
---

# Agent recipes

Each recipe is a spec for `set_agent_network_<App>` (see the **agent-builder** skill for the tools,
the loop and `reference/spec.md` for every field). Before using one:

1. `agent_builder_catalogue_<App>` — replace app names with the person's real apps, event names with
   the ones their mail/calendar app actually emits, and pick models from the list.
2. Create any app the recipe writes to that does not exist yet (`create_app`): a spreadsheet with
   the columns the instructions name, a notes app, a slideshow. Agents write into existing apps.
3. Send the spec; fix every listed problem; `run_agent_network_` once with a realistic input;
   read the run; only then `start_agent_network_` (triggered recipes).

Instructions are written for the model — keep them concrete: which app, which columns, what to do
when unsure, how to finish.

---

## 1. Inbox triage — several agents, each with its own tools, on every new email

A sorter logs every email and decides; specialists act. Two hand-offs leave the sorter, so the
router chooses (or ends the run when neither fits).

Apps: Gmail (`plugin_gmail`, named "Gmail" here), a spreadsheet "Mail Log" with columns
From, Subject, Verdict, Action; Calendar; Todo.

```json
{
  "name": "Mail Triage",
  "default_model": "anthropic/claude-haiku-4.5",
  "max_iter": 6,
  "nodes": [
    { "id": "new-mail", "type": "trigger", "event": "gmail_synced", "source_app": "Gmail",
      "run_mode": "per_item",
      "prompt": "New email.\nFrom: {{email.from}}\nSubject: {{email.subject}}\nThread: {{email.threadId}}\n\n{{email.snippet}}" },
    { "id": "sorter", "type": "agent", "name": "Sorter",
      "description": "Reads and logs every email, decides what it needs.",
      "instructions": "Add one row to the Mail Log sheet: From, Subject, Verdict (one of: reply, meeting, task, info, promo). Then finish with the verdict and one line of reason. Do nothing else." },
    { "id": "replier", "type": "agent", "name": "Replier", "model": "anthropic/claude-sonnet-4.6",
      "description": "Writes replies.",
      "instructions": "Read the thread in Gmail, then create a reply DRAFT in the person's voice — short, specific, no promises of money or dates. Update the email's Mail Log row: Action = 'draft written'. Finish with the draft's first line." },
    { "id": "scheduler", "type": "agent", "name": "Scheduler",
      "description": "Handles requests to meet.",
      "instructions": "Find two free 30-minute slots in the next five working days in the Calendar. Draft a reply in Gmail proposing them. Update the Mail Log row: Action = 'slots proposed'." },
    { "id": "tasker", "type": "agent", "name": "Tasker",
      "description": "Turns requests into todos.",
      "instructions": "Add one todo in Todo describing what the sender asked for, with the sender's name. Update the Mail Log row: Action = 'todo added'." },
    { "id": "log", "type": "app_tools", "app": "Mail Log" },
    { "id": "gmail", "type": "app_tools", "app": "Gmail" },
    { "id": "cal", "type": "app_tools", "app": "Calendar" },
    { "id": "todo", "type": "app_tools", "app": "Todo" }
  ],
  "edges": [
    { "from": "new-mail", "to": "sorter" },
    { "from": "sorter", "to": "replier", "when": "the verdict is reply" },
    { "from": "sorter", "to": "scheduler", "when": "the verdict is meeting" },
    { "from": "sorter", "to": "tasker", "when": "the verdict is task" },
    { "from": "sorter", "to": "log" },
    { "from": "replier", "to": "gmail" }, { "from": "replier", "to": "log" },
    { "from": "scheduler", "to": "cal" }, { "from": "scheduler", "to": "gmail" }, { "from": "scheduler", "to": "log" },
    { "from": "tasker", "to": "todo" }, { "from": "tasker", "to": "log" }
  ]
}
```

Test: `run_agent_network_` with an input shaped like the prompt ("New email.\nFrom: Ana <ana@…>\n
Subject: Coffee next week?\n…"). Then start it and send the inbox a real email.
Add `"filter": "{{email.fromEmail}} not in noreply@…, notifications@…"` to the trigger to skip noise.

## 2. Researcher that writes a brief into notes

Apps: a notes app (`block_note_editor`) "Briefs".

```json
{
  "name": "Researcher",
  "default_model": "anthropic/claude-sonnet-4.6",
  "nodes": [
    { "id": "research", "type": "agent", "name": "Researcher",
      "instructions": "Research the topic in the task with web search (several focused queries). Write a page in the Briefs notes app titled with the topic: a five-line summary, key facts with sources as links, open questions. Finish with the page title." },
    { "id": "web", "type": "web_search", "limit": 6 },
    { "id": "notes", "type": "app_tools", "app": "Briefs" }
  ],
  "edges": [ { "from": "research", "to": "web" }, { "from": "research", "to": "notes" } ]
}
```

Run: `run_agent_network_` with `input: "Heat pumps for Czech family houses in 2026"`.

## 3. Enrich every row of a spreadsheet (fan-out)

Two networks. The per-row one first, then the one that fans out.

Apps: spreadsheet "Leads" with columns Company, Website, Summary, Size, Done.

Network **"Lead Row"**:
```json
{
  "name": "Lead Row",
  "default_model": "deepseek/deepseek-v4-flash",
  "nodes": [
    { "id": "enrich", "type": "agent", "name": "Enricher",
      "instructions": "The input is one row of the Leads sheet (the company name and all its columns). Find the company's website, a one-sentence summary and the rough headcount with web search. Update THAT row (find it by Company) with Website, Summary, Size, and Done = yes. Finish with the company name." },
    { "id": "web", "type": "web_search", "limit": 4 },
    { "id": "leads", "type": "app_tools", "app": "Leads" }
  ],
  "edges": [ { "from": "enrich", "to": "web" }, { "from": "enrich", "to": "leads" } ]
}
```

Network **"Lead Fan-out"**:
```json
{
  "name": "Lead Fan-out",
  "default_model": "anthropic/claude-haiku-4.5",
  "nodes": [
    { "id": "start", "type": "agent", "name": "Dispatcher",
      "instructions": "Confirm the Leads sheet has rows to enrich and finish with how many." },
    { "id": "each", "type": "sub_agent_mapper", "sub_agent_network": "Lead Row", "sheet": "Leads", "column": "Company" },
    { "id": "leads", "type": "app_tools", "app": "Leads" }
  ],
  "edges": [ { "from": "start", "to": "leads" }, { "from": "start", "to": "each" } ]
}
```

Run the fan-out once; each row gets its own sub-run (visible in the Runs tab). Test "Lead Row"
alone first with one row as input.

## 4. A report that builds its own deck

`open_app` makes a fresh slideshow per run.

```json
{
  "name": "Weekly Report",
  "default_model": "anthropic/claude-sonnet-4.6",
  "nodes": [
    { "id": "analyst", "type": "agent", "name": "Analyst",
      "instructions": "Read the Sales sheet. Work out this week's totals, the three biggest changes and one risk. Hand the numbers on as a short list." },
    { "id": "designer", "type": "agent", "name": "Deck writer",
      "instructions": "Make a five-slide deck in the new slideshow: title, totals, three changes (one slide), the risk, next steps. Short text, big numbers. Finish with the deck's name." },
    { "id": "sales", "type": "app_tools", "app": "Sales" },
    { "id": "deck", "type": "open_app", "app_type": "slideshow", "name": "Weekly report" }
  ],
  "edges": [
    { "from": "analyst", "to": "sales" },
    { "from": "analyst", "to": "designer", "when": "the numbers are ready" },
    { "from": "designer", "to": "deck" }
  ]
}
```

One hand-off → always taken: a two-step pipeline.

## 5. Nothing goes out without the person's yes

The writer drafts, asks, and sends only on approval.

```json
{
  "name": "Careful Sender",
  "default_model": "anthropic/claude-sonnet-4.6",
  "nodes": [
    { "id": "writer", "type": "agent", "name": "Writer",
      "instructions": "Write the email the task asks for. Then ask the person with ask_user, showing the full email, with options [\"Send\", \"Change\", \"Cancel\"]. On Send: send it from Gmail. On Change: ask what to change, rewrite, ask again. On Cancel: finish without sending." },
    { "id": "ask", "type": "workspace_tools", "tools": ["ask_user"] },
    { "id": "gmail", "type": "app_tools", "app": "Gmail" }
  ],
  "edges": [ { "from": "writer", "to": "ask" }, { "from": "writer", "to": "gmail" } ]
}
```

The run waits on the question: the person answers in the app (the bell), or you relay their answer
with `answer_agent_question_<App>` — only their words.

## 6. A planner and specialists

The planner decides who works next; specialists hand back to the planner, which ends the run when
the goal is met (two or more hand-offs → the router may end).

```json
{
  "name": "Event Planner",
  "default_model": "anthropic/claude-haiku-4.5",
  "max_iter": 10,
  "nodes": [
    { "id": "plan", "type": "agent", "name": "Planner", "model": "anthropic/claude-sonnet-4.6",
      "instructions": "Turn the task into steps: venue research, invitations list, schedule. After each specialist reports, decide what is still missing. When everything is done, finish with a summary." },
    { "id": "venues", "type": "agent", "name": "Venue scout", "description": "Finds venues.",
      "instructions": "Find three venues that fit with web search; add them to the Plan notes page under Venues." },
    { "id": "guests", "type": "agent", "name": "Guest list", "description": "Builds the invitation list.",
      "instructions": "Build the invitation list from the Contacts app into the Guests sheet (Name, Email)." },
    { "id": "sched", "type": "agent", "name": "Scheduler", "description": "Books time.",
      "instructions": "Put the event and two prep meetings in the Calendar." },
    { "id": "web", "type": "web_search" },
    { "id": "notes", "type": "app_tools", "app": "Plan" },
    { "id": "contacts", "type": "app_tools", "app": "Contacts" },
    { "id": "sheet", "type": "app_tools", "app": "Guests" },
    { "id": "cal", "type": "app_tools", "app": "Calendar" }
  ],
  "edges": [
    { "from": "plan", "to": "venues", "when": "venues are still missing" },
    { "from": "plan", "to": "guests", "when": "the guest list is still missing" },
    { "from": "plan", "to": "sched", "when": "the schedule is still missing" },
    { "from": "venues", "to": "plan", "when": "always, to report" },
    { "from": "guests", "to": "plan", "when": "always, to report" },
    { "from": "sched", "to": "plan", "when": "always, to report" },
    { "from": "venues", "to": "web" }, { "from": "venues", "to": "notes" },
    { "from": "guests", "to": "contacts" }, { "from": "guests", "to": "sheet" },
    { "from": "sched", "to": "cal" }
  ]
}
```

`max_iter` bounds the back-and-forth; a run that hits it ends as an error saying so.

## 7. React to something in the workspace

Any event in the catalogue can start a network — a todo added, a contact added, a calendar event
created, a new Telegram message, a notes page created:

```json
{
  "name": "Todo Helper",
  "default_model": "deepseek/deepseek-v4-flash",
  "nodes": [
    { "id": "added", "type": "trigger", "event": "<todo item added event from the catalogue>", "source_app": "Todo",
      "prompt": "A todo was added: {{<variable from the catalogue>}}" },
    { "id": "helper", "type": "agent", "name": "Helper",
      "instructions": "If the todo needs information from the web, research it and put a short note in the Notes app linked from the todo. Otherwise finish with 'nothing to add'." },
    { "id": "web", "type": "web_search" },
    { "id": "notes", "type": "app_tools", "app": "Notes" }
  ],
  "edges": [ { "from": "added", "to": "helper" }, { "from": "helper", "to": "web" }, { "from": "helper", "to": "notes" } ]
}
```

## 8. Images

```json
{
  "name": "Product Shots",
  "nodes": [
    { "id": "brief", "type": "agent", "name": "Art director",
      "instructions": "Turn the product description into one precise image prompt: subject, setting, light, lens, mood." },
    { "id": "paint", "type": "image_agent", "name": "Painter",
      "instructions": "Make the image the prompt describes. Describe what you made in one line." }
  ],
  "edges": [ { "from": "brief", "to": "paint", "when": "the prompt is written" } ]
}
```

## 9. Waiting — durable, days if needed

Give an agent `wait_for_reply` (a reply to a thread it sent), `wait_for_app_state` (a condition on an
app, e.g. a sheet cell becoming "approved"), or `sleep` (until a time). The run parks without cost
and resumes when the condition holds.

```json
{ "id": "wait", "type": "workspace_tools", "tools": ["wait_for_reply", "sleep"] }
```

Instruction pattern: "After sending, wait for a reply for up to 3 days with wait_for_reply; if none,
send one short follow-up; if still none, mark the row 'no reply' and finish."

## 10. Networks that use networks

A network is a tool for another: in the catalogue's `workspace_tools`, each other network appears as
`run_agent_network_<Name>`.

```json
{ "id": "delegate", "type": "workspace_tools", "tools": ["run_agent_network_Researcher"] }
```

Use it when a reusable skill (research, enrichment) should be one call inside a bigger flow. For
"once per row", use a `sub_agent_mapper` instead (recipe 3).
