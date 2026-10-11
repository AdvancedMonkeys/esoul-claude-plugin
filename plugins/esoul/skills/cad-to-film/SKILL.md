---
name: cad-to-film
description: Make a film people will actually watch from a machine — model it in the ExternalSoul CAD app with the detail a YouTube audience expects, bring it to life in RunMachine (MuJoCo physics, programs, a scripted camera), render every shot in Render Studio with Blender on the person's own GPU, put labels on the parts from the render's own camera data, and assemble a narrated film in the video editor. Use for "make a video of how X works", "animate my CAD model", "an explainer film of this machine", "render the simulation properly", or when a CAD / RunMachine picture is too plain to publish.
---

# From CAD to a film: model → motion → render → labels → cut

Four apps, each doing the one thing it is good at, joined by files in the workspace:

| Step | App | What comes out |
|---|---|---|
| 1. Model | CAD (`plugin_cad`, skill `cad`) | a machine export `Machines/<name>/` (machine.json + one mesh per body) |
| 2. Motion | RunMachine (`plugin_run_machine`, skill `run-machine`) | runs: the machine's motion as a `.traj`, its camera, metrics, a quick film |
| 3. Render | Render Studio (`plugin_render_studio`, skill `render-studio`) | `Renders/<shot>.mp4` + `<shot> — camera.json` (where each labelled point is, per frame) |
| 4. Labels and cut | `scripts/label_film.py` here, then the video editor (`video_editor`) | labelled shots, narration, one exported film |

Read the three app skills before their step; this skill is the ORDER and the craft between them. It was written from
an 18-minute explainer of an MRI scanner whose models, motion, renders and labels all went through this pipeline.

## 0. Before anything: the shot list, sized by the narration

A film is a story told against a clock. Write the narration first, one paragraph per shot, and give each shot its
length from the words (about 2.6 words a second for a calm explainer voice; measure the voice you will use with the
video editor's `narrate_script` before trusting the number). Then for each shot write ONE line: what is seen, what
moves, what is labelled, what the camera does. A shot is 15–30 s; nobody watches 40 s of one angle.

Plan the render budget now: a laptop RTX card renders about 1.5–3 s a frame at 720p / 32 samples, so a 25 s shot
at 30 fps is 20–40 minutes. Twenty shots is a night. Decide which shots need Render Studio and which can be
RunMachine's own film or a diagram.

## 1. Model for the camera, not just for the fit

What reads as "a toy" on YouTube is missing detail, not missing polygons. Model what a close-up would show:

- **Separate bodies for separate materials**, named for what they are AND what they are made of — `Bob 3 (brass)`,
  `Post (steel)`, `Cover seams (plastic)`, `Vacuum vessel`, `RF shield`. Render Studio chooses materials from these
  names (`(brass)`, `(steel)`, `(stainless)`, `(aluminium)`, `(copper)`, `(rubber)`, `(plastic)`, `(glass)`, `(wood)`,
  `(gold)`, `(chrome)` first, then words like `bolt`, `shaft`, `gear`, `coil`, `cable`, `wheel`). A body named
  `body-17` renders as grey paint.
- **The small things**: bolt heads around a flange, chamfers and fillets on every visible edge (a sharp edge catches
  no light), seams and panel gaps, knurling, cables with slack, labels and displays, feet, hinges. Ten small bodies
  are what make one big body believable.
- **The inside, if you will cut it open.** A cutaway (Render Studio `section`) shows what is behind the cover; if
  nothing is modelled there, the cut shows a hollow shell. Model the internals you will name in the labels.
- **Motion needs joints in CAD** (a variable-driven rotation is a joint; see the `cad` skill's "Make it move"). Then
  `cad_build_<Name>` and `cad_export_machine_<Name>`; the export is what the next two apps read.

Check the model as the camera will see it: a Render Studio **preview still** (`render-studio` §1) in `studio-dark`
at the angle you plan. Plain grey in the CAD view is normal; plain grey in a Render Studio still means a body needs a
better name or a `materials` rule.

## 2. Motion in RunMachine

`place_machine { cad: { nodeId } }`, `describe_machine`, `write_program`, `run`. What matters for a film:

- **Script the camera in the program** (`camera.follow`, `camera.path` with keyframes) when the motion and the
  framing belong together — the run records the camera and Render Studio films through it when the scene has no
  `camera` of its own. Leave it unscripted when Render Studio's presets (hero, orbit, crane…) will frame the shot.
- **Check a moment, not a film**: `picture { runId, time }` shows any instant of a finished run, re-simulated to it.
- **One run per shot**, as long as the shot. A run's length is simulated seconds; Render Studio's `time.speed`
  plays it faster or slower to fit the narration.
- **A better model, old motion**: when the CAD model gains detail after the runs were made, do not re-simulate.
  Render the NEW export with the OLD run's trajectory and the placement it was run with:
  `machines: [{ from: "<new machine.json>", trajectory: "<the run's .traj file id>", placement: { yaw: 90 } }]` —
  the joints are the same, so every link follows its old motion.

## 3. Render each shot in Render Studio

Per shot, one scene (`render-studio` §2). The pattern that made the MRI film:

```jsonc
{
  "title": "MRI — S23 gradient coils",
  "machines": [{ "run": { "app": "<RunMachine id>", "runId": "<run>" },        // exactly as simulated
                 "section": [{ "point": [0, 0, 1150], "normal": [0, 1, 0] }] }], // cut open along the bore
  "time": { "speed": 1.55 },                        // fit the run to the narration's 24.5 s
  "duration": 24.5, "fps": 30,
  "look": { "preset": "studio-dark" },
  "xray": [{ "match": "*cover*", "keys": [[0, 1], [1.5, 1], [2.5, 0.18]] }],   // the outside fades to glass
  "glows": [{ "match": "x gradient coil", "color": "#C084FC", "keys": [[4.4, 0], [4.9, 3], [7.3, 3], [7.7, 0]] }],
  "camera": { "dof": { "fstop": 5.6 } },             // the run's own camera, with depth of field
  "glare": 0.5, "vignette": 0.3,
  "quality": { "engine": "cycles", "samples": 32, "noise": 0.03, "width": 1280, "height": 720 },
  "anchors": [{ "id": "x", "body": "X gradient coil", "point": [300, -356, 1150] }]   // for the label in step 4
}
```

- **Preview the key moments as stills first** (`stills: [2, 9, 18]`, draft quality) and look at every one: the
  framing, the cut, the glow at its peak. A wrong film costs half an hour; a wrong still costs ten seconds.
- **Keys follow the narration**: if the voice names the coils at 4.4 s, they glow at 4.4 s. Keep keyframe lists to
  their change points; a key per frame makes a scene too big for one call and changes nothing.
- **Send the shots and let them queue**: the computer renders one after another; the person watches progress in the
  app's Renders tab. Collect each with `read_render` → its file ids.

## 4. Labels from the render's own camera

`anchors` in the scene make Render Studio write `<shot> — camera.json`: where each point is on screen in every
frame. Labels drawn from it stay pinned to the part while the camera moves. With a shell on the person's computer
(Claude Code), download the film and its camera.json from the workspace and run:

```
python3 scripts/label_film.py "S23.mp4" "S23 — camera.json" plan.json --check     # problems only, writes nothing
python3 scripts/label_film.py "S23.mp4" "S23 — camera.json" plan.json "S23 labelled.mp4"
```

`plan.json` holds the kicker (the chapter heading), a title card, labels (`anchor`, `text`, `sub`, `color`, `on`,
`off`, `offset`) and bottom captions, in film seconds (the script's own help has the format). **Always run `--check`
first**: it reports labels that overlap each other, labels whose point is off screen, and anchors the render never
recorded. Rules it cannot check, from the MRI film:

- **Two labels never share a corner at the same time**: end one as the next appears.
- **Text never sits on a bright part**: white type on a white scanner vanishes, gold captions on a brass base vanish.
  The script draws a soft dark band behind titles and captions; keep labels' boxes over dark background.
- **Look at a frame from every label's life** before calling it done — the check finds geometry, not taste.

Without a shell, skip `anchors` and let the narration and the glows do the pointing.

## 5. Assemble in the video editor

Upload the labelled shots (or put them in workspace files), then in the video editor: `add_clips_<Name>` in shot
order with each clip's `sourceDuration`, `narrate_script_<Name>` for the voice (one line per shot) and
`narration_job_<Name>` until it is done, `sync_narration_to_shots_<Name> { distribute: "center", shrink: true }` so
each line sits on its shot, `export_timeline_<Name>` and `export_job_<Name>` until it names the file. Watch the
export from start to end before handing it over.

## 6. Honesty

Never describe a shot you did not look at. Say which shots are Render Studio renders and which are RunMachine films
or diagrams, how long the renders took, and anything you simplified (a cut that hides a part, a label you dropped
because it collided). The person decides what goes out under their name.
