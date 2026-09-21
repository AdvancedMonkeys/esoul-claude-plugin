# The anatomy of an ExternalSoul app (plugin package)

An app is a folder `src/plugins/<id>/` on the platform's branch. The workbench scaffolds it; you
fill it in. Every file below is what the platform expects, in the order you should write them.

## `plugin.json` — the manifest

```json
{
  "manifestVersion": 1,
  "id": "sticky-notes",
  "name": "Sticky notes",
  "version": "0.1.0",
  "description": "A wall of paper notes: pin, colour, drag, and let agents add to it.",
  "applicationType": "plugin_sticky_notes",
  "entry": "app",
  "icon": "StickyNote",
  "ops": ["read-notes"],
  "workspaceTools": ["spreadsheet:add_row"]
}
```

- `id`: lower-case, dashes. `applicationType`: `plugin_` + the id with underscores — the platform
  tells plugins from built-ins by that prefix. Never change either after shipping.
- `icon`: a lucide-react component name; `open_workbench` lists the allowed ones.
- `ops`: the server operations `server.ts` exports (below). `workspaceTools`: the grants the UI
  needs to call OTHER apps' tools once installed — `<applicationType>:<tool base name>`. Absent =
  no cross-app access; the user sees these at install.
- Secrets never live in a manifest. An external service is declared as a `connections` entry
  (oauth2 / apiKey) naming ENV VARIABLE NAMES and header NAMES, never values.

## `app.tsx` — the schema (NOT `"use client"`)

This module is evaluated in the server bundle. It exports `pluginSchema`: the state shape, the
events that change it, the tools agents call, and the description agents read. The UI is a
separate client module it imports.

```ts
import { nanoid } from "nanoid";
import { z } from "zod";
import { incompleteStateNotice, EventTypes,
  type ApplicationIdentifier, type ApplicationSchema, type ApplicationPort,
  type EventData, type EventDefinition } from "esoul-sdk";
import { StickyNotesUi } from "./ui/sticky-notes-ui";

export interface StickyNotesData extends ApplicationIdentifier {
  notes: { id: string; text: string; color: NoteColor; x: number; y: number; pinned: boolean; createdAt: number; updatedAt: number }[];
}

export const noteAddedEvent: EventDefinition<StickyNotesData> = {
  eventName: "plugin_sticky_notes_added",
  type: EventTypes.Client,
  // dataCreator MINTS ids and timestamps. Called by the UI and by tools.
  dataCreator: (args) => ({
    eventName: "plugin_sticky_notes_added",
    eventData: { noteId: args.noteId ?? nanoid(), text: String(args.text ?? "").slice(0, 2000), color: args.color ?? "butter", x: args.x ?? 24, y: args.y ?? 76, at: args.at ?? Date.now() },
    timestamp: Date.now(),
    workspaceId: args.workspaceId,
    applicationId: args.applicationId || args.nodeId,
    instanceName: args.instanceName,
    chatIdSource: args.chatIdSource,
  }) as EventData<any>,
  // processor is PURE and IDEMPOTENT: same input, same output, on every replay.
  processor: (state, event) => {
    const d = event.eventData ?? {};
    if (typeof d.noteId !== "string" || typeof d.text !== "string") return state;   // refuse what you cannot trust
    if (state.notes.some((n) => n.id === d.noteId)) return state;                      // replay-safe
    if (state.notes.length >= 300) return state;                                        // bounded
    return { ...state, notes: [...state.notes, { id: d.noteId, text: d.text, color: d.color, x: d.x, y: d.y, pinned: false, createdAt: d.at, updatedAt: d.at }] };
  },
};

export const pluginSchema: ApplicationSchema<StickyNotesData> = {
  applicationType: "plugin_sticky_notes",
  description: "A wall of sticky notes on the workspace timeline.",
  reactNode: StickyNotesUi,
  reconstructStateFromEventLog: true,       // state IS the fold of events — never a shadow copy
  events: [noteAddedEvent /*, …*/],
  getPorts: (): ApplicationPort[] => [],
  stateCreator: (identifier) => ({ ...identifier, notes: [] }),
  toolkitCreator: (identifier, forChatId, eventCallback) => {
    const base = identifier.instanceName.replace(/[^a-zA-Z0-9]/g, "_");
    const idArgs = { ...identifier, applicationId: identifier.nodeId, chatIdSource: forChatId };
    return {
      [`add_note_${base}`]: {
        description: `Pin a new sticky note on "${identifier.instanceName}". Returns the note's id.`,
        parameters: z.object({ text: z.string().min(1).max(2000), color: z.enum(["butter","rose","mint","sky","lilac"]).optional() }),
        execute: async (args) => {                       // server surfaces: chat, agents, MCP
          const noteId = nanoid();
          await eventCallback(noteAddedEvent.dataCreator({ ...idArgs, noteId, ...args }));
          return `Pinned note ${noteId}.`;
        },
        onClient: (args) => {                            // browser surfaces: voice, WebMCP — SAME event
          const noteId = nanoid();
          eventCallback(noteAddedEvent.dataCreator({ ...idArgs, noteId, ...args }));
          return `Pinned note ${noteId}.`;
        },
      },
      [`read_notes_${base}`]: {
        description: `Read every note on "${identifier.instanceName}" with the ids the other tools take.`,
        parameters: z.object({}),
        readOnly: true,
        publicSafe: true,
        onClient: () => {},
        execute: async () => {
          // Server truth through the plugin's own op — never a self-fetch of /api/v1.
          const { callPluginOp } = await import("@/lib/plugins/call-op");
          const s = await callPluginOp<Pick<StickyNotesData, "notes">>("sticky-notes", "read-notes", identifier.nodeId);
          return describeNotes(s);
        },
      },
    };
  },
  // What an agent reads about this app every turn. Missing is NOT empty.
  getStateDescription: (state) => {
    const notLoaded = incompleteStateNotice({ title: "Sticky notes", instanceName: state?.instanceName, shape: { lists: { notes: state?.notes } } });
    if (notLoaded) return notLoaded;
    return describeNotes(state);
  },
};
```

Rules the checks enforce and reviewers look for:

- **Events are the truth.** No component state that the timeline does not know about, except
  what is honestly local to a device (a drag in progress, text still being typed). No writes to
  anything but events.
- **Ids and timestamps are minted in `dataCreator`, never in `processor`.** A processor that calls
  `nanoid()` or `Date.now()` folds differently on every replay and breaks time-scrubbing.
- **Processors are pure, idempotent, bounded, and refuse untrusted payloads** — return `state`
  unchanged rather than throw.
- **Bursts collapse.** A typing burst or a drag is ONE row on the timeline: give such an event a
  `collapseConfig: { collapseKeyFn: (eventData, ctx) => `${ctx.applicationId}:${eventData.noteId}:text`, collapseWindowMs: 2500 }`
  so consecutive events with the same key within the window merge, and a paragraph is not fifty
  events. Key by the entity AND the field; never share a key across entities.
- **Every UI action has a tool twin.** If a person can do it by hand, an agent can do it by tool,
  through the same event. Provide both `execute` (server surfaces) and `onClient` (browser
  surfaces) so chat, voice, agents and MCP all reach it. **Never an empty `onClient` stub**: the
  voice runtime reports a tool that returns nothing as a success, so a stub makes the agent claim
  work it did not do. Simplest correct form, at the end of the toolkit:
  `for (const t of Object.values(tools)) t.onClient = t.execute;` (events dispatch in the browser
  too, and `callPluginOp` rides the session there). The checks refuse the stub.
- **Tool names are `<verb>_<instance base>`**; verbs are lower-case with underscores; describe
  them for a model, name what they return, and say where ids come from.
- **`getStateDescription` never claims a count or emptiness it could not read** — use
  `incompleteStateNotice` for a missing collection; `[]` is real, `undefined` means not loaded.
- A tool that needs server truth calls a plugin OP (`server.ts`); it never fetches `/api/v1/*`
  itself (that route is token-gated and will refuse the tool). In the workbench such a tool is
  refused by design — `read_app_state` reads the preview instead.

## `ui/<id>-ui.tsx` — the UI (`"use client"`)

```tsx
"use client";
import React from "react";
import { useAppCanEdit, usePluginEventDispatch, useWorkspaceTools } from "esoul-sdk/react";
import { noteAddedEvent, type StickyNotesData } from "../app";

export function StickyNotesUi({ state }: { state: StickyNotesData }) {
  const dispatch = usePluginEventDispatch();      // the ONLY way to change state
  const canEdit = useAppCanEdit();                // readers of a share see the app, cannot mutate
  const dark = useIsDark();                       // document.documentElement.classList.contains("dark"), observed
  const tools = useWorkspaceTools(state);         // other apps' tools, gated by plugin.json workspaceTools
  // …
}
```

- Props are `{ state }`: the folded state, live. You never fetch it.
- `dispatch(noteAddedEvent.dataCreator({ …identifier fields from state, …args }))` is a write.
  Disable writes when `!canEdit`.
- Theme: read the `.dark` class on `<html>` (observe it — the user toggles at runtime) and choose
  from a per-app `LIGHT`/`DARK` palette object of the same shape. See design-rules.md.
- Cross-app: `useWorkspaceTools({ workspaceId, nodeId })` (the state carries both) returns
  `{ call({appType|targetNodeId, tool, args}) → {ok, text}, listApps() }`.
  In the workbench it works through the board's tab (dev mode); installed, only the manifest's
  grants are allowed.

## `server.ts` — server operations (optional)

```ts
import "server-only";
import { readFoldedAppState } from "@/lib/workspace-apps/read-folded-app-state";
import type { PluginOpContext, PluginServerModule } from "@/lib/plugins/server";

async function readNotes(ctx: PluginOpContext) {
  const folded = await readFoldedAppState(ctx.nodeId);
  if (!folded) throw new Error(`no Sticky notes app ${ctx.nodeId}`);
  const s = folded.state as Partial<StickyNotesData>;
  if (!Array.isArray(s.notes)) throw new Error("the wall did not fold (notes missing)");  // missing ≠ empty
  return { notes: s.notes };
}
export const pluginServer: PluginServerModule = { ops: { "read-notes": readNotes } };
```

List every op in `plugin.json` `ops`. Ops run in the platform with the caller's access checks; a
tool reaches one through `callPluginOp(pluginId, op, nodeId, args)`.

## Tests — `<id>.test.ts` and `<id>-ui.test.tsx`

`check_app` runs them with jest. Write the fold contract as tests, because that is what a
reviewer trusts: starts empty; an event adds exactly what it says; replaying the same event is a
no-op; a bad payload leaves state unchanged; caps hold; no processor mints an id or a timestamp
(assert two folds of the same log are deep-equal); `getStateDescription` refuses a missing
collection. A UI test renders with a fixed state and checks the visible chrome and the empty
state. Keep them fast — they run beside the preview on the same machine.

## What the checks run

`check_app` = registry sync (your app is generated into the plugin registry), the app's tests +
the platform's boundary and crash-safety suites (schema must not be `"use client"`, describers
must be crash-safe, no server-only import reaches the client graph), and a type check of the
package. Green everywhere is what `ship_app` requires.
