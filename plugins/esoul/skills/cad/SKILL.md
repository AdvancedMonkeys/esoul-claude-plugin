---
name: cad
description: Model, assemble and print-prepare real parts in the ExternalSoul CAD app (plugin_cad, a chili3d kernel) from chat or MCP — bring a person's existing parts in from Onshape or any CAD site through their cloud browser (STEP export → workspace file → cad_import), place them by the source assembly's own mates, design NEW parts around them (mounts, housings, hats, caps) as separate bodies with real screw holes and clearances, replicate a bought component from its datasheet drawing, measure every fit (esoul.measure: distance + interference, never a boolean), build on the server with no tab open, show an exploded view through a variable, and export each printable part by name. Triggers on "import this CAD / STEP file", "put these parts in the drawing", "design a mount / housing / hat for it", "exploded view", "does it fit", "export for printing", "download the parts from Onshape".
---

# CAD in ExternalSoul: parts in, design around them, parts out

A CAD app on a workspace (`plugin_cad`, usually named by the person — find it with `list_workspaces` /
`get_app_tools(<app id>)`; its tools are minted `cad_<verb>_<Name>`) holds a MODEL as a timeline of
STEPS: parametric programs (sketch → extrude/revolve → boolean/fillet/transform/style), imports of
workspace CAD files, and a person's by-hand edits. Every step is an event; the server replays them
in a headless kernel on `cad_build`, so nothing needs a tab. Read `cad_help_<Name>` once per
session for the op shapes — this skill is about the WORKFLOW a CAD specialist expects.

## 1. Bring the person's parts into the workspace (Onshape, through their cloud browser)

Onshape has no anonymous export. The person logs into Onshape in their `cloud_browser` app (ask
them to; `browser_status_<Browser>` shows the login). Then everything is the browser's own session:

1. Parse the document link: `https://cad.onshape.com/documents/<did>/w/<wid>/e/<eid>` — `did`
   document, `wid` workspace, `eid` the open element (a part studio OR an assembly).
2. Find the parts with `browser_run_script_<Browser>` (same-origin fetch, the session's cookies):
   ```js
   const get = async (u) => { const r = await fetch(u, { credentials: 'include', headers: { Accept: 'application/json' } }); return r.ok ? r.json() : { status: r.status }; };
   const asm = await get(`/api/v6/assemblies/d/${did}/w/${wid}/e/${eid}?includeMateFeatures=true`);
   // asm.rootAssembly.instances → { name, elementId (the part studio), partId, transform (16 numbers, row-major 4×4, metres), hidden }
   // asm.rootAssembly.features → the mates. Or for a part studio: get(`/api/v6/parts/d/${did}/w/${wid}/e/${studioId}`)
   return asm;
   ```
   A hidden instance is still a part of the design — export it too.
3. Export each part studio as STEP (one translation per studio; poll until `DONE`):
   ```js
   const xsrf = decodeURIComponent((document.cookie.match(/(?:^|; )XSRF-TOKEN=([^;]+)/) || [])[1] || '');
   const hdr = { Accept: 'application/json', 'Content-Type': 'application/json', 'X-XSRF-TOKEN': xsrf };
   const r = await fetch(`/api/v6/partstudios/d/${did}/w/${wid}/e/${studioId}/translations`, { method: 'POST', credentials: 'include', headers: hdr,
     body: JSON.stringify({ formatName: 'STEP', storeInDocument: false, stepVersionString: 'AP242', allowFaultyParts: true }) });
   const { id } = await r.json();
   // poll: GET /api/v6/translations/${id} → { requestState: 'DONE', resultExternalDataIds: [dataId] }
   ```
   The `X-XSRF-TOKEN` header is what makes the POST pass; without it Onshape answers 403.
4. Save the file into the workspace with `browser_download_<Browser>`:
   `{ url: "https://cad.onshape.com/api/v6/documents/d/<did>/externaldata/<dataId>", saveAs: "<part>.step", folderPath: "<project>" }`
   — the in-page fetch carries the login. The answer's `fileId` is what the CAD app imports.
   A public CDN file (a datasheet drawing) that fails in-page on CORS: add `serverFetch: true`.

Any other CAD site works the same way: its export endpoint in a `browser_run_script`, then
`browser_download`. A file the person already dropped into the workspace needs none of this:
`list_files` → the id.

## 2. Import into the drawing and LEARN the part before placing it

- `cad_import_<Name> { fileId, fileName, name, color, label }` — one step, the body is
  `node:<stepId>:part`. Nothing is built until `cad_build` or an open tab replays.
- Measure it before touching it: `cad_build` reports every body's world bbox + volume. For the
  geometry that matters (which end is open, where the holes are) ask the kernel instead of guessing:
  `cad_request { kind:"query", method:"run_program", args:{ ops:[ { method:"shape.findSubShapes", target:"<node>", id:"f", args:{ subshapeType:"face" } } ] } }`
  then `shape.boundingBox` + `face.area` per `f#i` (batches of 40): a small round face with
  dx≈dy is a hole, its bbox centre the hole's position, its z range the plate it goes through.
  Thin slabs (`extrude` of a Ø100 circle, 0.4 mm) measured against the part with
  `esoul.measure` give an area-vs-z profile — the cheapest way to see walls, lips and open ends.
- The person's parts are DONE. Never cut, fuse or fillet them. Everything you design is a new
  body that attaches to them through THEIR holes and faces.

## 3. Place by the source assembly's mates, not by eye

Onshape's occurrence `transform` is a row-major 4×4 in metres: `p' = M·p`. Two fastened parts keep
that relation; express it in the model's frame with one `transform` op per part
(`{ op:"transform", node, rotate:{ axis, angle, origin? }, translate:{x,y,z} }` — rotate first, then
translate; translations and angles take expressions). Keep physical gaps explicit (a fabric skin
between magnets: `SKIN = 1.5`) and name them in the step label.

## 4. Design the new parts as a specialist would

- Every part is its OWN body (a colour belongs to a body; a print is a body). Split a part's
  program across steps when a `call_app_tool` input would pass ~2 KB; a later step cuts/fuses into
  `<earlier stepId>:<opId>`.
- Screws: through-holes Ø2.8 for M2.5 (Ø3.4 for M3), countersinks Ø5.5 × 1.5 on the head side,
  pilot holes Ø2.2 × 8 in bosses for self-tapping screws; bosses Ø7 on the overhang, placed at
  angles that miss everything beneath (legs, slots) — asymmetric angles make the fit keyed.
- A bought component (switch, port, module): take its dimensions from the datasheet drawing
  (download it to the workspace too), model body + pins + actuator as separate bodies where the
  colour or the motion differs, and give its pocket 0.15 mm a side.
- Anything that must stay reachable (a USB-C slot, a side button) gets a WINDOW: build the cutter
  on the +x side, `transform`-rotate it about z to the feature's angle, then `boolean cut`.
- Soft goods (a plush toy): no sharp protrusions — a feature is a sphere sunk into the host along
  the surface normal (`centre = C + (r − R + visible)·n`), a flat-based dome's rim always stands
  proud of a curved surface.
- Fits: `cad_request { kind:"query", method:"esoul.measure", args:{ nodes:[…], pairs:[[a,b],…] } }`
  → each pair's min distance and interference volume. 0 interference and the intended gap, for
  EVERY pair that touches, before you say it fits. Never check a fit with `booleanCommon` — it
  consumes the parts.

## 5. Exploded view, pictures, exports

- Explode is a VARIABLE: `cad_set_variables [{ name:"explode", type:"length", expression:"0" }]`,
  and each part's last op is `{ op:"transform", id:"explode", node, translate:{ z:"explode * k" } }`
  with k in assembly order (cup 1, lid 2, mount 3, switch 3.5, hat 4.6, band 5.2, cap 5.8 — at
  explode=50 every gap ≥ 6 mm). `cad_set_variables explode=50` → `cad_build` → the picture.
- `cad_build_<Name> { view:true }` builds on the server and attaches a full-size picture; a tab the
  person has open builds the same steps live. `force:true` re-records everything.
- Export each printable part by name: `cad_request { kind:"export", args:{ format:".stl", ids:["<node>"], name:"Switch mount" } }`
  (formats `.step .iges .brep .stl ".stl binary" .ply .obj`); the next `cad_build` or tab answers
  it as a workspace file named after the part (`cad_read_answer` → fileId). No `ids` = the whole
  visible model in one file.

## Honesty

Nothing exists until a build report lists the body with its bbox. A FAILED step is named with the
kernel's reason; fix the ops and build again. Say which holes you used and which gap you assumed.
