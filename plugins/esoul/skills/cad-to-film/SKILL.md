---
name: cad-to-film
description: Make a film people will actually watch from a machine — model it in the ExternalSoul CAD app with the detail a YouTube audience expects, bring it to life in RunMachine, render every shot in Render Studio with Blender on the person's own GPU (envelopes so nothing pops, labels and captions drawn into the film, a self-review of every film), and cut a narrated film in the video editor (drift on held shots, a check of the finished film). Use for "make a video of how X works", "animate my CAD model", "an explainer film of this machine", "render the simulation properly", or when a CAD / RunMachine picture is too plain to publish.
---

# From CAD to a film: a folder of rules

Every app is driven with `call_app_tool(workspace_id, app_id, "<tool>_<Name>", args)`; `get_app_tools(app_id)` lists
an app's exact tool names (they are minted from the app's name). Read the `cad`, `run-machine` and `render-studio`
skills before their step; this skill is the ORDER and the craft between them, and `reference/` holds the deep parts:
`reference/detail.md` (modelling for the camera), `reference/motion.md` (nothing pops, nothing freezes),
`reference/review.md` (checking without eyes). Written from an 18-minute MRI explainer that went through every step,
and from skills.wheresryan.sh "anatomy".

Four apps, joined by files in the workspace:
CAD (plugin_cad) → Machines/<name>/ · RunMachine (plugin_run_machine) → runs with a motion file · Render Studio (plugin_render_studio) → Renders/<shot>.mp4 · Video editor (video_editor) → one exported film.
Tool names are minted per app: render_scene_<Name>, place_machine_<Name>, cad_build_<Name>… Get each app's tools before calling one; never guess a name.

THE RULES BELOW EACH CAME FROM A FAULT. Their wording stays close to the fault on purpose. Keep them.

STEP 1 — SIZE THE JOB, OUT LOUD
- FIGURE: one shot, a still or a ≤10 s loop. Minutes of work, one render.
- HERO: a 30–90 s film, 3–6 shots, no narration or a few lines. An hour or two of rendering.
- EPIC: a narrated explainer of several minutes, 15+ shots. A night of rendering on the person's GPU.
Never start an EPIC without asking. Say the size, the shot count and the render time before the first call (Render Studio: about 1.5–3 s a frame at 720p / 32 samples on a laptop RTX card; 25 s at 30 fps ≈ 20–40 min).

STEP 2 — TRUTH FIRST
Write the real numbers before anything is drawn: dimensions, speeds, field strengths, ratios, what moves and why. Keep them on one notes page in the workspace ("<film> — facts") with their source. Every number in the model, the motion and the narration comes from that page. A film that is beautiful and wrong is worse than none.

STEP 3 — THE OBJECT IS THE EXPLANATION
Pick (or design) a machine whose parts map one to one onto the idea: the part that does the work is the part the viewer watches. A coil glows WHEN its current flows; the cover turns to glass (xray) or is cut open (section) to show what is behind it; the explode slides parts apart in the order they are assembled. A floating label is the last resort, never the explanation.

STEP 4 — LIST THE PARTS, AT LEAST 40, IN FIVE GROUPS
base · structure · mechanism · controls · subject. Name each for what it is AND what it is made of ("Bolt ring (steel)", "Bore liner (plastic)", "Gradient coil X (copper)"). Write the list before modelling; it is the detail budget. → reference/detail.md before modelling.
Fault behind it: "the renders lacked much detail" — the first scanner had 27 bodies; at 90 bodies / 161k triangles it read as a machine.

STEP 5 — PLAN THE WORLD AND THE SHOTS
One camera language for the film: a house angle (three-quarter view, 25–35° above the floor), one look per chapter at most, the same floor and light. Then the shot list, one line per shot: what is SEEN, what MOVES, what is NAMED, what the camera DOES, how long. A shot is 12–30 s; nobody watches 40 s of one angle.
Narrated films: write the narration first, one paragraph per shot, measure it (the video editor's narrate_script with estimateOnly: true gives the voice's real rate), and size every shot from its line. Never size shots before the narration exists.

STEP 6 — BUILD THE GEOMETRY ONCE
CAD: separate bodies for separate materials, joints as variables (a variable-driven rotation is a joint; a part with no variable is welded), cad_build until every body is listed, cad_export_machine. Check the model the way the camera will see it: a Render Studio preview still (stills: [t], quality "draft") in the film's look. Grey paint in Render Studio means a body name lacks a material.

STEP 7 — MOTION
RunMachine: place_machine { cad }, a program per machine, one run per shot as long as the shot (time.speed in Render Studio stretches it). Check a moment with picture { runId, time } before rendering a film of it. A better model later does not need new runs: render the NEW export with the OLD run's trajectory.

STEP 8 — PAINT (RENDER STUDIO)
Per shot one scene: the run or the export, a look ("studio-dark" for a dark film, "cyclorama" for a white one), a camera move, materials by name, glows / xray / explode / section over time, glare and vignette, and overlays (kicker, captions, labels pinned to anchors) drawn by the computer into the film.
Fault behind it: "the renders are extremely bland and ugly" — default grey, flat light, one camera. Never ship the default: pick the look, the move and the materials on purpose, and compare the preview still with the bar ("would this pass on a good YouTube channel?") before the film.

STEP 9 — MAKE IT LIVE
Every shot moves, start to end; nothing pops. → reference/motion.md before writing the first scene. In short: envelopes (bursts, pulses, holds) instead of hard keys; a camera that keeps drifting through a hold; the video editor's drift on any still or held shot.
Fault behind it: 28 shots of the MRI film ended in a still tail hold (wait until the narration ends); beside moving renders they read as frozen pictures, and every one needed a push-in added afterwards.

STEP 10 — VERIFY LIKE A CRITIC
Nothing is done until it was looked at by someone who did not build it. → reference/review.md. Render Studio's read_render returns the computer's own review of each film: 16 finished frames as a picture + frozen / black stretches + labels that overlap or point off screen. The video editor's export_job returns the same check for the whole film (frozen / black / silent). Both must read clean, AND every picture must be looked at.

ASSEMBLY (video editor)
add_clips in shot order with each shot's sourceDuration (and drift: 0.04–0.06 on stills and calm shots) → narrate_script → narration_job until done → sync_narration_to_shots { distribute: "center", shrink: true } → export_timeline → export_job until done. Read its "Checked the finished film" line; fix and export again until it is clean. Watch it start to end before handing it over.

A SMALL TEAM, IF YOU CAN START SUB-AGENTS (Claude Code's Agent tool)
One BUILDER makes the shots. REVIEWERS each hold ONE lens — truth (against the facts page), motion (pops, freezes, pacing), legibility (labels, contrast, text on bright parts), the viewer (would a stranger follow it?) — and they read the review pictures and the numbers themselves, never the builder's report. A FIXER takes their findings. Rounds until a round finds nothing. Keep one PROGRESS page in the workspace: decisions, each round's findings and what was fixed. Without sub-agents, run the lenses yourself, one at a time, on the pictures.

LONG JOBS
Render on the person's computer (Render Studio), not in a code sandbox: a sandbox restarts and loses a render in progress. Send all shots and let them queue; collect each with read_render. WATCH YOUR OWN RENDERS: poll read_render until each is DONE or FAILED, and the moment one FAILS read its reason, say it, and fix the cause before sending anything again — Retry sends the same scene and fails the same way. The person must never be the first to see a failure. Tell the person where to watch progress (the Render Studio app's Renders tab).

HONESTY
Never describe a shot you did not look at. Say which shots are Render Studio renders and which are RunMachine films or stills, how long rendering took, and what you simplified. The person decides what goes out under their name.

OLDER FILMS
`scripts/label_film.py` draws labels onto a film from its `<shot> — camera.json` on your own computer. Render Studio
now draws them itself (scene `overlays`); use the script only for films rendered before that.
