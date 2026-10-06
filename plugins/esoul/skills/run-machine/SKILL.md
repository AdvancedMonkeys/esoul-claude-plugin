---
name: run-machine
description: Simulate machines in the ExternalSoul RunMachine app (plugin_run_machine, MuJoCo physics) from chat or MCP — put balls, boxes, ramps, walls, a bucket or a catapult into a world; bring a machine from the CAD app as a package (parts from STL exports or primitives, joints with axes, motors, gears by teeth, sensors incl. a camera); write its program in JavaScript (motors, sensors, logs, world.stop); run it headless on the server and read the metrics, a picture and a film; iterate. Triggers on "simulate", "physics", "make it drive / throw / fall", "catapult", "does it roll", "run the machine", "film the run", "RunMachine".
---

# RunMachine: a physics world for machines, driven by programs

A RunMachine app on a workspace (`plugin_run_machine`; find it with `list_workspaces` / `get_app_tools(<app id>)`;
its tools are minted `rm_<verb>_<Name>`; none yet → `create_app` with `application_type: "plugin_run_machine"`)
holds a WORLD (objects, machines, metrics, settings), PROGRAMS and RUNS. Nothing moves until a run. The
physics is MuJoCo in a browser page the platform drives headless, so `rm_run` works with nobody's tab open and
answers in the same call with the metrics in words, the program's log and a picture; a person with the app open
sees the same world and can press Play. Read `rm_help_<Name>` once per session for the exact shapes.

Units: the world is METRES, kg (masses in grams in the tools), seconds; a machine package is MILLIMETRES (the
CAD app's units). The floor is z = 0.

## 1. The loop

1. Build the world: `rm_add_object { preset }` (ball, box, ramp, wall, bucket, catapult) or a full object; `rm_place_machine { machine }` for a package.
2. Say what to measure: `rm_set_metrics` — max_height / distance_from_start / max_speed of a body, joint_angle, inside a region, touched another body, time_to another metric. A run answers with these in words.
3. Write the program: `rm_set_program { name, source }` — `function loop({ t, machine, world, log }) { … }`, called at 50 Hz (or `rate`).
4. `rm_run { duration, film?: true }` — read the result; LOOK at the attached picture; `rm_film` for a better film; change; run again. Keep the first run short (3–5 s).
5. Never describe a result without a run record. If a run fails, the reason names the program line or the body.

## 2. Programs (JavaScript, sandboxed)

```js
function setup({ machine }) { /* once */ }
function loop({ t, dt, machine, machines, world, log, random }) {
  machine.motor("drive").speed(20);            // velocity motor, rad/s (negative = the other way)
  machine.motor("steer").angle(15);            // position motor, degrees
  const enc = machine.sensor("axleEnc");       // encoder: .angle (deg), .speed (deg/s)
  const eye = machine.sensor("eye");           // camera: .find("red") → {x, y, area} | null, .image() → {width, height, rgba}
  const red = eye.find("red");
  if (red) machine.motor("steer").angle((0.5 - red.x) * 40);
  if (world.object("ball").height < 0.05 && t > 1) world.stop("the ball landed");
  if (t > 2.95) log("ball at", world.object("ball").position);
  world.metric("score", red ? red.area : 0);   // a number of your own in the result
}
```
`machine.joint("id").angle/.speed`, `machine.part("id").position/.velocity`, `world.object("id").position/.velocity/.push(force)`,
`world.contacts()`, `world.stop(reason)`. A throw fails the run at its line; a loop slower than its period for 10 ticks fails too.
Forward drives backwards? Set `gear: -1` on the motor (or a negative speed). Motors: `velocity` (speed in rad/s), `position` (angle in degrees), `torque` (N·m).

## 3. A machine from the CAD app (package `machine/1`, mm)

The CAD model is bodies; a package groups them into PARTS (rigid links) joined by JOINTS. One STL per part (or per
body that needs its own collider, like a wheel):
1. Set the model to its design pose (every kinematic variable 0), then export each part: `cad_request_<Cad> { kind:"export", args:{ format:".stl", ids:[ "<stepId>:<opId>", … ], fileName:"car-chassis.stl" } }` — one request per part — then `cad_build_<Cad>`; `list_files` gives the file ids by name.
2. Write the package: `parts` (id, name, color, material { density | mass (g), friction }, bodies [{ nodeId, name, mesh:{ fileId }, collider:"hull"|"cylinder"|"box"|"sphere"|"none" }]) — wheels and shafts `cylinder`, gears `none` (their teeth are visual; the coupling is a `gear`), everything else `hull`; `joints` (hinge/slide/ball/free/fixed, parent → child part ids, `axis:{ point, dir }` in world mm at the design pose, `range` in degrees, `damping`, `spring`); `motors` ({ id, joint, kind, maxTorque (N·m; a toy motor 0.02–0.5), maxSpeed, gear }); `gears` ({ driver, driven, teeth:[8, 24] } → the driven hinge turns −8/24 of the driver; the two parts never collide); `sensors` (camera { part, position, look, fov, width, height }, encoder { joint }, imu, rangefinder, touch, gps); `ground` (part ids welded to the world; a car has none — it is free).
3. `rm_place_machine { machine:{ id, package, pose:{ pos:[x,y,z] } } }` — z so the wheels touch z = 0 (the CAD frame's z = 0 is the floor when the model was designed on it).
4. A program drives `machine.motor("<motor id>")`; `rm_run`.
Primitives need no file: `mesh:{ primitive:{ kind:"box", min, max } | { kind:"cylinder", center, axis:"x"|"y"|"z", r, length } | { kind:"sphere", center, r } }` (mm) — the catapult preset is built this way.

## 4. Worlds, several machines, obstacles

Any number of machines and objects share one world and collide with everything (parts joined by a declared joint
or gear never collide with each other). Each machine keeps its own names: `machines["car"].motor("drive")`,
`world.body("car.chassis")`. Obstacles are `fixed: true` objects (walls, ramps, a bucket from the preset). Gravity,
timestep, floor friction and the look are `rm_set_settings`.

## 5. Films and pictures

`rm_run { film: true }` renders a draft film of the run (640×360@24); `rm_film { runId, quality:"share"|"youtube",
speed: 0.25, camera:{ kind:"orbit"|"follow"|"lookAt"|"fit", target, turn, distance, elevation } }` re-simulates the
run (deterministic) and renders it at 720p/1080p, in slow motion if asked, as a WebM workspace file — cut and narrate
it in the video editor app. `rm_snapshot { camera, runId }` is one picture.

## 6. What to tell the person

The metrics in a sentence ("the ball flew 0.49 m high and landed 3.9 m away"), what the program did, and the
picture or film. Offer the next knob in their words (a stronger spring, a longer arm, a heavier ball).
