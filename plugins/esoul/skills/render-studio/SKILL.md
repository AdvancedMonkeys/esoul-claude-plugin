---
name: render-studio
description: Render studio-quality films and stills with Blender on the person's own computer through the ExternalSoul Render Studio app (plugin_render_studio) — CAD models handed over as machines, RunMachine runs exactly as they were simulated, any 3D file (glTF, OBJ, STL, FBX, USD…) or a Blender project. Ten looks, real materials chosen from body names, camera moves framed for the aspect, explode / x-ray / glow / section cuts over time, label anchors for overlays, MP4 / MOV / WebM / stills, templates. Use for "render this nicely", "make a film of the machine", "a product shot", "a turntable", or whenever a CAD or RunMachine picture is not good enough to show people.
---

# Render Studio: Blender on the person's computer, driven by a scene

A Render Studio app (`plugin_render_studio`; find it with `list_workspaces` / `get_app_tools(<app id>)`; none yet →
`create_app` with `application_type: "plugin_render_studio"`) sends a SCENE to a computer the person connected; the
app's program there runs Blender with Cycles on the graphics card and puts the film into the workspace's
`Renders/` folder. Its tools are minted `<verb>_<Name>` from the app's name — for an app called "Render Studio":
`render_scene_Render_Studio`. Below they are written `render_scene_<Name>`.

The CAD app's and RunMachine's own pictures are for checking work. Render Studio is for showing it. For a drawn,
isometric "how it is put together" figure of a machine (anatomy style, exploded, filmed to WebM), use the
`figure-studio` skill instead.

## 0. A computer first — the person's click, never yours

`list_computers_<Name>` says which computers render for the app and where each stands. Nothing renders until one says
`Blender … ready · OPTIX/CUDA/HIP/METAL: <card>`. If none is connected or ready, say so and ask the person to open
Render Studio, press the computer pill (or **Connect a computer**), run the command it shows or assign a computer they
already connected, and **approve the program**. The approval is theirs; never try to get round it. Setup installs
Blender 4.2 LTS (about 350 MB, checksummed) unless the computer already has 4.2 or newer, runs a self-test that
finds the graphics card, and then the card reads ready. A render sent while the computer is busy queues behind the
running one.

## 1. The loop: preview, then film

1. `render_catalog_<Name>` once: every look, camera move, material preset and quality with a sentence each.
2. **Preview a still first**: `render_scene_<Name> { …scene, stills: [4.0], quality: "draft", output: { format: "png" } }`.
   It answers at once with a `renderId`. A draft still takes seconds; LOOK at it before spending minutes on a film.
3. `read_render_<Name> { renderId }` until it says DONE and names the files (`Renders/<title>.png`, with their file
   ids). A still is a picture you can view; a film is an mp4 / mov / webm. A finished FILM also comes back with the
   computer's own review: a contact sheet of 16 finished frames as a picture, and in words any frozen or black
   stretch and any label that overlaps another or points off screen. Look at every frame of the sheet; fix what it
   names before calling the film done.
4. Render the film: the same scene with `duration` and a real `quality`, no `stills`.
5. `cancel_render_<Name>` stops one; `retry_render_<Name>` sends the same scene again, also to another computer.

A render runs on the person's GPU: about 1.5–3 s a frame at 720p / 32 samples on a laptop RTX card, so 8 s at 30 fps
(240 frames) is roughly 6–12 minutes, and `final` (1080p, 192 samples) costs several times that. The person sees
progress in the app: frames, time left, and the film playing when it lands. Tell them where to watch.

## 2. The scene

```jsonc
{
  "title": "Gyroscope — hero",                       // the file is Renders/<title>.mp4
  // WHAT is in it (one or more):
  "machines": [{ "from": "Machines/Gyroscope HD" }],   // a CAD export (folder, its machine.json path, or file id)
  // or a RunMachine run, exactly as simulated (its machine, pose and trajectory):
  //   "machines": [{ "run": { "app": "<RunMachine app id>", "runId": "<run id>" } }]
  // or a newer CAD model driven by an older run's motion:
  //   "machines": [{ "from": "<machine.json file id>", "trajectory": "<.traj file id>", "placement": { "yaw": 90 } }]
  // "models": [{ "from": "Models/robot.glb" }]         // any 3D file Blender reads
  // "blend":  { "from": "Projects/intro.blend" }       // a Blender project as it is (its camera, lights, frames)
  "duration": 8, "fps": 30,
  "look": { "preset": "studio-dark" },
  "camera": { "preset": "hero", "zoom": 1.1, "dof": { "fstop": 2.8 } },
  "quality": "standard",
  "output": { "format": "mp4", "aspect": "16:9" }
}
```

- **Looks**: `studio-dark` (near-black, soft key, cool rim, glossy floor), `studio-light`, `cyclorama` (white
  infinity cove), `product` (black mirror floor, hard rims), `blueprint` (clay bodies, drawn outlines, gridded blue
  floor), `clay`, `hologram`, `sunset`, `outdoor`, `night`. `look.hdriFile` lights the scene with the person's own
  `.hdr` / `.exr` from the workspace (`showHdri: true` shows it behind); `light`, `exposure`, `floorColor` tune it.
- **Camera**: `orbit: { turns, elevation }` (a turntable), `preset`: `hero` (low three-quarter, pushing in),
  `reveal`, `dolly`, `crane`, `pan`, `iso`, `front`, `side`, `top`, `low`; `follow: { target: "<body pattern>" }`
  tracks a moving body; `keys: [{ t, eye, lookAt, fov }]` is exact keyframes in metres. Presets are framed for the
  aspect (a 9:16 frame is narrow). A RunMachine run with no `camera` uses the camera its program drove. `focus:
  "<pattern>"` frames presets on some bodies instead of the whole scene. `zoom` > 1 is closer.
- **Materials** come from BODY NAMES, so name bodies in CAD for what they are: a name ending `(brass)`, `(steel)`,
  `(stainless)`, `(aluminium)`, `(copper)`, `(rubber)`, `(plastic)`, `(glass)`, `(wood)`, `(gold)` or `(chrome)`
  picks that material before any other rule; then words do (`bolt`, `shaft`, `gear` → brass, `wheel` → rubber,
  `coil`, `bracket`, `glass`, `cable`…). Override by pattern: `materials: { "*housing*": "painted-matte",
  "*lens*": { "preset": "glass", "color": "#cfe8ff" } }` (presets in `render_catalog`, 32 of them).
- **Over time** (keys are `[seconds, value]`, eased between; ANYTHING that takes keys also takes an ENVELOPE so
  nothing pops — `{ base?, keys?, holds: [{ from, to, value, ease? }]` (lit while the narration names it),
  `bursts: [{ at, peak, rise?, fall? }]` (a flash that decays), `pulses: { start, every, count | until, peak, rise?,
  hold?, fall? }` (a coil knocking) `}` — the parts add up over the base):
  `explode: { keys: [[0, 0], [3, 1.2]] }` slides bodies apart from the centre; `xray: [{ match, keys | opacity }]`
  makes bodies see-through; `glows: [{ match, color, keys }]` lights bodies up (a coil when its current flows);
  `visibility: [{ match, keys: [[t, 0|1]] }]` hides and shows; `machines[i].section: [{ point, normal }]` (mm, the
  model's frame) cuts the model open with capped faces; `props: [{ kind: "arrow", from, to, color, grow: [[t, 0–1]] }]`
  draws a field line or a force that grows from its tail.
- **Finish**: `glare` 0–1 (bloom on highlights and lights), `vignette` 0–1, `outlines: { thickness }` (drawn edges).
- **Output**: `quality`: `preview` (EEVEE, fast), `draft` 540p, `standard` 720p, `final` 1080p, `4k`, or exact
  `{ engine, samples, width, height, noise, motionBlur }`; `output.format`: `mp4` (H.264), `mov` (ProRes, alpha),
  `webm` (VP9, alpha), stills `png` / `jpg` / `exr`; `output.aspect`: 16:9, 9:16, 1:1, 4:5, 4:3, 21:9, 2:1;
  `output.transparent: true` (MOV / WebM) to lay the model over other footage. `time: { start, speed }` takes part
  of a trajectory or plays it faster.
- **Words in the film**: `overlays: { kicker, title: { text, sub?, on, off }, captions: [{ text, on, off }],
  labels: [{ anchor, text, sub?, color?, offset?: [x, y], on, off }] }` — drawn by the computer while it encodes,
  in Inter on dark plates, fading in and out. A label follows an `anchors` point frame by frame with a leader line:
  `anchors: [{ id, body, point }]` (`point` in mm in that body's frame); a label naming an anchor the scene does
  not record is refused. Keep a label's plate over dark background (`offset` moves it) and end one label as the
  next one starts. The anchors are also saved as `Renders/<title> — camera.json` (pixels per frame).
- **Camera follow**: `follow: { target, lag }` — `lag` is seconds to catch up (0.12–0.4 reads as an operator).

## 3. Templates

`save_render_template_<Name> { name, scene }` keeps a house style (look, camera move, effects, output);
`render_template_<Name> { name, title, overrides }` renders it again for another model saying only what differs;
`remove_render_template_<Name>` forgets one.

## 4. What goes wrong, and what it means

- **"no computer is ready"** — none connected, setup still running, or the program not approved: §0, the person's job.
- **A body you expected is missing** — the answer notes bodies with no mesh; an STL / OBJ that is not a closed solid
  still renders, but check the still.
- **A spinning part looks like a ghost** — a part turning more than ~60° a frame is rendered sharp on purpose (motion
  blur cannot interpolate it); slow the playback with `time.speed` if it must blur.
- **Two rules match one body** — the later rule wins; name bodies so one rule fits.
- **The film is long and slow** — preview stills first; render `standard` while iterating and `final` once; split a
  very long film into shots (it is a film anyway).
- **Scene too big for one call** — thin keyframe lists to their change points (a straight run of keys between two
  values is one pair); the result is identical.

- **The review says "frozen"** — a stretch of ≥4 s where the picture barely changes: give it a camera move, a
  breathing glow (`pulses` with a low peak), or cut the shot shorter. **"labels … overlap"** — end one before the
  next starts, or move one with `offset`. **"points off screen"** — the anchor left the frame; shorten the label's
  on/off or frame the shot wider.

- **A render FAILED** — `read_render` names the reason (the last lines Blender said). Read it the moment it fails,
  tell the person in a sentence and fix the cause; `retry_render` sends the SAME scene and fails the same way. Watch
  every render you sent until it is DONE or FAILED — the person must never be the first to see a failure.

## 5. What to tell the person

What you rendered (the look, the move, how long, at what quality), on which computer, how long it took, and where it
is (`Renders/<title>.mp4`, and that it plays in the app's Renders tab). Offer the next knob in their words: another
look, a closer camera, a slower turntable, the same move as a vertical short.

For the whole job — modelling in CAD, motion in RunMachine, rendering here and assembling a narrated film — read the
`cad-to-film` skill.
