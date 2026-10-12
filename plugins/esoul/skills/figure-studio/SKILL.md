---
name: figure-studio
description: Make crafted, animated isometric figures of real machines and objects in the ExternalSoul Figure Studio app (plugin_figure_studio), in the style of Ryan's "anatomy" skill (skills.wheresryan.sh/anatomy, kit MIT) — a paper-white or dark card with a nameable machine of 40–300 precise parts, four-tone shading, one lit accent, parts that move, an exploded view and a live readout; written as code against his kit, built and checked on the server, scripted into shots and filmed to WebM clips for the video editor. Use for "draw how X works as an isometric figure", "an exploded view of this mechanism", "an anatomy-style diagram", "animate the parts of a machine", or the "how it is put together" beats of an explainer film.
---

# Figure Studio: isometric figures built, checked, shot and filmed

A Figure Studio app on a workspace (`plugin_figure_studio`; find it with `list_workspaces` / `get_app_tools(<app id>)`;
none yet → `create_app` with `application_type: "plugin_figure_studio"`, a name, and `offer: true` — without `offer`
the app exists but `call_app_tool` cannot reach it). Its tools are minted `<verb>_<Name>` from the app's name with
anything not a letter or digit turned into `_`: for an app called "Figure Studio", `write_figure_Figure_Studio`.
Below they are written `write_figure_<Name>`. Call each with
`call_app_tool(workspace_id, app_id, "<tool>_<Name>", arguments)`. Every answer ends with the next call.

The craft and the kit are Ryan's (**anatomy**, MIT, © 2026 Ryan). A figure is
CODE against his kit; the studio builds it in a sandboxed page, checks it with his audits, paints pictures and films
on the figure's own clock, and keeps the built page, stills, checks and films as workspace files under
`Figures/<name>/`. A person with the app open sees the card live and can drive it with their own pointer and keys.

**The one idea that matters: the object is the explanation.** No boxes and arrows. Invent a real physical thing
whose working *is* the concept (a cache key → a pin-tumbler lock; a separable blur → a bed of nails beside two
combs). Too abstract and too bland fail the same way; the fix is a recognisable machine of many precise parts.

## 1. Read before you build — a budget, not a library (every first figure in a session)

The guide ONCE, the examples list ONCE, at most ONE example file, then build: a first figure within the first five
calls, improved from its picture, beats a perfect read (eight example reads — the big ones are 100 KB — once cost a
first figure its whole turn before a line was drawn).

1. `figure_guide_<Name>` — `topic: "skill"` (the default) is his whole workflow; read it once. Then the topic you
   need: `craft` (parts, painter's order, pipes), `motion` (springs, tours, explodes), `kit` (every function —
   `lathe` for round parts on any axis, `tube` for pipes, prisms, coils), `verify` (the critic's checklist), `webgl`
   (shaders that live in the drawing), `3d`, `walkthrough`, `react`. `find: "spring"` narrows to matching sections.
2. `figure_examples_<Name>` — no arguments lists them; `{ name }` gives its files; `{ name, file }` the source with
   line numbers, 300 lines a page (`from` for the next). Pick the closest SMALL one and start from it
   (`write_figure { name, from }`, then `edit_figure`) or page through its `build.mjs` — never several, never a big
   one whole. What each shows:
   `starter` (a bench with a sliding carriage — the smallest working figure, written to be grown),
   `dial-indicator` (~300 lines, hover slides the carriage), `desk-computer` (types onto a CRT in the case plane),
   `four-stroke-engine` (a cutaway, ~74 solids, `model.mjs` + `parts.mjs` + `live.js`), `raptor-engine` (comes apart
   into 11 assemblies, fires a WebGL plume, records shapes for the audit), `arcade-cabinet` (a Hero, ~240 solids,
   moving parts rebuilt in the page from a shared `parts.mjs`), `ripple-tank` (two WebGL layers registered to the
   iso plane), `turning-dial` (the true-3D mode).

## 2. Size it and say so (his rule)

**Figure**: one mechanism, 40–80 parts, ~30–90 min. **Hero**: 80–150 parts or several WebGL layers, 2–4 h. **Epic**:
don't start — propose a Hero. Tell the person which, before any geometry.

## 3. Truth, object, parts — before geometry

Write the real numbers (sizes, ratios, timings) as a small pure module, `model.mjs`, that the build AND the page
import; every readout, motion and caption comes from it. Write a parts list of 40+ (base · structure · mechanism ·
controls · the one lit subject), each part sitting on another.

## 4. Build — `write_figure_<Name>`

`{ name, from: "<example>" }` starts from an example (its files copied; `files` you pass replace any of them), or
`{ name, files: { "build.mjs": "…", "model.mjs": "…", "parts.mjs": "…", "live.js": "…", "figure.css": "…" }, theme }`
(`theme` `"dark"` | `"light"`, default dark; `source` alone is a one-file `build.mjs`; `id` replaces an existing
figure's files). `build.mjs` is his Node program unchanged: it imports `../../kit/iso-kit.mjs` (and `lathe.mjs`,
`tube.mjs`, `../../scripts/inline-kit.mjs`), reads its sibling files with `readFileSync` and `writeFileSync`s its
page — the runtime shims `fs`, `path`, `url` and `process.argv` (`--light`, `--audit`). The answer: solids, paths,
the card's corners, the CONTROLS a shot can drive, the build time, the error at its file:line, and a picture.

Change one file with `edit_figure_<Name> { id, file, edits: [{ find, replace, all? }] }` (each `find` exact and
unique unless `all: true`; `file` defaults to `build.mjs`), or `text` for the whole file (also how a file is added),
`fromFile` (a workspace file id or path) for a whole file kept in the workspace, or `remove: true`. A long figure
travels whole: `write_figure { fromFiles: { "build.mjs": "<path or id>" } }` or `{ fromFolder }`, never pasted in
pieces. It rebuilds and answers like `write_figure`. `read_figure_<Name>` reads the studio (no id), one
figure (files, build, card, controls, checks, shots) or one file with line numbers (`file`, `from`, `to`). Figures
are named by id or by name.

**Write it in pieces — every tool input under ~300 lines (~12 KB).** A reply has an output limit and a tool call cut
off by it never runs (a whole figure sent as one `write_figure` input was cut, retried and cut again). Start from an
example (`write_figure { from }`) or a short build.mjs that already builds, then add `model.mjs` / `parts.mjs` /
`live.js` one file per `edit_figure { file, text }`, and change files with `edits`, never by resending them.
`write_figure { id, files }` REPLACES every file of that figure — never use it to add one. Between pieces the studio
shows "Being written — waiting for parts.mjs" (an import of a file not written yet); that is not an error to fix,
it builds when the last piece lands.

Rules that each cost a round when forgotten:
- **Painter's order is yours**: paint back to front (`k.depthOf`); split what wraps another part (a spring round a
  stem: back half, stem, front half). Anything behind a cut or a body comes BEFORE it in the markup — check every
  pair that overlaps on screen.
- **Moving parts**: translate pre-built groups (`translateAlong`); anything that rotates off the z axis is rebuilt
  per frame in the page from the same `parts.mjs` (inline it, and `lathe.mjs`, into the page script — the arcade and
  the engine do).
- **Motion is time-based**: `dt` from rAF clamped to 1/30, springs or exponential follow, an idle tour, keys and
  pointer drive the same targets, stop when settled. The studio films on a stepped clock, so a figure that reads
  wall time will not film.
- **Words stay out of the drawing**: card corners (Fig n · title · hint · readout), legend keys, a TRUE caption.
- **The hint names its keys** ("Hover to turn · → next stroke · A apart"): the studio reads them as the controls.
- **Name the moving parts** (`data-part="valve"` on their group): shots frame them by name.
- **Colour from one hex**: `import { materialsCss } from "../../kit/esoul-colour.mjs"`, then
  `materialsCss({ ".fur": "#a47a57", ".bow": "#f3b8c4" })` in the page's `<style>` gives every solid drawn with
  `className: "fur"` its paper, top and four shades in both themes. Never hand-pick the ramp; two or three materials.
- **A story** (characters, scenes): one figure holds it all; scenes are data and the pose a pure function of (scene,
  seconds); name them in `data-scenes` and expose `window.figure.scene(i)`. `figure_guide { topic: "story" }`.

## 5. Look like a critic — `view_figure_<Name>`

`{ id, theme?, actions?, at?, region?, width? }`. Pictures come back as images, at most three per answer and scaled
to 1280 px — so the whole card shows composition, never line ends. Look at the whole card, then `region` close-ups
(`{ x, y, width, height }` in card fractions, e.g. `{ x: 0.4, y: 0.3, width: 0.25, height: 0.25 }`, `width: 2400`)
at every junction, in BOTH themes, assembled and apart (`actions: [["key","a"]], at: 2`). Actions are what a person
does first: `["key","i"]`, `["click","button[data-fire]"]`, `["move",".iso-stage",0.6,0.4]`, `["wait",1.5]`.
Is it instantly a real object? Rich at 1× and still rewarding at 4×? Every line landing on something? Iterate
until yes.

## 6. His checks — `check_figure_<Name>`

`{ id, kind: "lines" }` must report 0 floating texture-line ends (it rings the ones that float on a picture); repeat
in the apart pose with `actions` / `at`. `{ id, kind: "audit" }` builds with `--audit` (clearance at rest, apart and
in flight, terminals, folds, crowding, depth order) and must end "audit passed" — it needs the build to record shapes
(`A.recorder` / `A.settle` / `A.auditOrExit`, see `raptor-engine`), and is required for pipes, cables and round parts.
A Hero's audit is slow.

## 7. Shots — `write_shot_<Name>`

`{ figure, name, seconds, width, height, fps?, theme?, script, preview: true, id? }` — size 1920×1080 (default),
1080×1080 or 1080×1920; fps 30 by default. `script` is `[seconds, action, ...args]` lines:
`key "<key>" selector?` · `click selector x? y?` · `move selector x y glide?` · `leave selector` ·
`press selector x? y?` · `release selector x? y?` · `eval js` · `until js maxSeconds` · `wait seconds` · and the
film's own `push { zoom, x, y, over }` (a camera move over the card, eased), `push { on: ["valve"], margin?, over }`
(frames those parts where they stand when it starts, zoom fitted — prefer it to hand-aimed x/y), `caption "words"
seconds?` (drawn on the film at the foot, readable through every push; `""` clears), `scene i` (a story figure's
scene; `read_figure` lists them) and `fade "in"|"out" seconds`. Selectors come from the figure's controls (`read_figure`).

Open on `fade in`, let the idle motion breathe, push into the junction the narration names, pull back, take it
apart, put it back, `fade out`. Zoom is over the whole CARD on its paper and the drawing is about half the card:
×1.4–2 frames the machine in a 16:9 film, ×3–4 one junction. Pull back to ×1.4 (not ×1) BEFORE "apart", or the
lifted parts leave the frame. `push` with `over: 0` is a CUT: open a shot with `[0, "push", { …, over: 0 }]` — any
`over` above 0 eases in from the whole card, so frame 0 shows the whole card; below ×1.4 a 16:9 frame shows the
card's border. A story told in shots: one shot per scene, each opening on its framing at second 0
(`[0, "push", { on: [...], over: 0 }]`, `[0, "scene", i]`, `[0, "caption", "…"]`), and the figure REDRAWS ON THE PRESS (call its draw in the key handler, not on the
next animation frame), or frame 0 shows the old pose. `preview: true` answers with four frames — look at them
before filming.

Film one shot at a time and keep each short: a film call can outlast your client's timeout (it keeps running on the
platform — `read_film` shows it land), and several at once queue behind each other. The video editor exports
1280×720, so 720p shots lose nothing. A whole story: `film_story_<Name> { shots: [ids in order], editor: "<video
editor app id>" }` films them one after another on the platform and, when the last lands, puts them into the video
editor in that order with their lengths.

## 8. Film — `film_shot_<Name>` and `read_film_<Name>`

`film_shot_<Name> { shot }` (`from` / `to` film part of it) paints the card frame by frame on the figure's clock
into a WebM under `Figures/<name>/films/`. A short film answers in the same call with its file and a 16-frame contact
sheet; a long one is filmed in parts in the background — poll `read_film_<Name> { id }` until it is done or failed
(no id: the recent films). The review names stretches where nothing moves, blank frames, and anything the painter
could not draw. Look at EVERY frame of the sheet and fix what the review names before calling it done. A person with
the app open can film the same shot in their own tab (Shots → Film), faster.

Into a video: `send_to_editor_<Name> { films: [ids in order], editor? }` puts finished films into a video editor
as clips with their lengths (no measuring export); then the editor's `read_timeline` and `export_timeline`. Figures are the "how it is put together" beats beside Render Studio's photographic ones and manim's
maths (`cad-to-film`, `render-studio`, `math-explainer-video`).

Housekeeping: `rename_figure_<Name> { id, name }`; `remove_from_studio_<Name> { kind: "figure" | "shot" | "film", id }`
(a removed film's file stays in the workspace).

## 9. Honesty

- Never describe a figure, a pose or a film you did not look at in a `view_figure` picture, a shot preview or the
  film's contact sheet. "It builds" is not "it looks right".
- Report the real check results (`lines` count, "audit passed" or not), not what they should say.
- Say what the figure simplifies from the real machine.
- A failed build or film: read the error at its line, say it in a sentence, fix the cause — never resend unchanged.

## 10. What to tell the person

The figure (its size class, part count, both themes), what moves and which keys drive it, the check results, the
shots and films with their seconds and where they are (`Figures/<name>/`), and that the card is live in the app.
Offer the next knob in their words: a close-up shot of one junction, the apart pose, a vertical short, the other
theme.
