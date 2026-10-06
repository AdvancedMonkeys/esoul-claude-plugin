---
name: run-machine
description: Simulate machines designed in the ExternalSoul CAD app inside the RunMachine app (plugin_run_machine, MuJoCo physics) from chat or MCP — bring a machine in from the CAD app in one call, write a small JavaScript program that drives its motors, run it headless and get metrics, a picture and a film; update the machine after the CAD model changes; drive several machines and obstacles in one world; script the camera for films.
---

# RunMachine: a physics world for machines, driven by programs

A RunMachine app on a workspace (`plugin_run_machine`; find it with `list_workspaces` / `get_app_tools(<app id>)`;
its tools are minted `<verb>_<Name>` — `place_machine_RunMachine`, `run_RunMachine`…; none yet → `create_app` with
`application_type: "plugin_run_machine"`) holds a WORLD (objects, machines, metrics, settings), PROGRAMS and RUNS.
Nothing moves until a run. The physics is MuJoCo in a browser page the platform drives headless, so `run` works with
nobody's tab open and answers in the same call with the metrics in words, the programs' logs and a picture; a person
with the app open sees the same world and can press Play.

**Read `read_world` first.** Its last line is `Next: …` — the one call that moves the work forward. Every answer
names the next call. Units: metres, seconds, grams; programs speak degrees. The floor is z = 0.

## 1. The loop

1. `place_machine { cad: { nodeId: "<the CAD app's id>" } }` — the CAD app exports the model's mechanism (its
   variable-driven rotations are the joints, the bodies they carry are the links, linear expressions between
   variables are the gears) to `Machines/<name>/` and RunMachine places it resting on the floor. The answer is the
   machine as a program sees it: motors with the call for each, sensors, joints, gears, parts, and a STARTER PROGRAM
   written for its own motors. `from: "Machines/<name>"` places an export already in the workspace; `pos: [x, y]`,
   `yaw` place it; placing the same machine again updates it in place.
2. `describe_machine { id }` any time you need that text again (it also says when the CAD model changed since).
3. `write_program { machine, name, source }` — `function loop({ t, machine, world, camera, log }) { … }` at 50 Hz.
   It is checked against the machine as it is saved: a motor it names that does not exist comes back here, not from
   a run. `machine: "*"` makes a WORLD program that reaches every machine as `machines["id"]`.
4. `run { film: true }` (20 s by default; a program ends it earlier with `world.stop`). Read the metrics, LOOK at
   the picture; `film { runId, quality: "share" }` for a better film; change; run again. Never describe a result
   without a run record; a failed run names the program line or the body.
5. The model changed in CAD? `update_machine { id }` exports again, takes the new geometry and keeps the pose,
   motors, sensors, colliders and programs set here — the answer lists what changed, what stayed and what needs
   attention (a motor whose joint is gone). `check` / `read_world` say "CAD changed" per machine.

Obstacles and props: `add_object { preset: "ball" | "box" | "ramp" | "wall" | "bucket" | "catapult" }` (metres,
grams; `fixed: true` objects are part of the world). `set_metrics` says what every run answers with: max_height /
distance_from_start / max_speed of a body, joint_angle, inside a region, touched another body, time_to a metric.
`remove { kind, id }` takes anything out.

## 2. Programs (JavaScript, sandboxed, deterministic)

```js
function setup({ machine }) { /* once */ }
function loop({ t, dt, machine, machines, world, camera, log, random }) {
  machine.motor("drive").speed(20);            // velocity motor, rad/s (gear -1 on the motor = the other way)
  machine.motor("steer").angle(15);            // position motor, degrees
  const enc = machine.sensor("axleEnc");       // encoder: .angle (deg), .speed (deg/s)
  const eye = machine.sensor("eye");           // camera: .find("red") → {x, y, area} | null, .image() → {width, height, rgba}
  const red = eye.find("red");
  if (red) machine.motor("steer").angle((0.5 - red.x) * 40);
  camera.follow("car", { distance: 1.0, height: 0.45, lag: 0.7 });   // the view and the film follow this
  if (world.object("ball").height < 0.05 && t > 1) world.stop("the ball landed");
  if (t > 2.95) log("ball at", world.object("ball").position);
  world.metric("score", red ? red.area : 0);   // a number of your own in the result
}
```
`machine.joint("id").angle/.speed`, `machine.part("id").position/.velocity/.speed/.height`, `world.object("id")…`,
`world.body("car.chassis")`, `world.contacts()`, `world.stop(reason)`, `world.shared` (a blackboard every program of
the run shares). A throw fails the run at its line; a loop slower than its period for 10 ticks fails too.

**The camera is scriptable**: `camera.follow(target, { distance, height, azimuthDeg, lag })`, `camera.lookAt(target)`,
`camera.at([x, y, z])`, `camera.fov(deg)`, `camera.frame([targets], { margin })` (fit them all), `camera.path([{ t, at,
lookAt }], { loop, ease })` (keyframes), `camera.release()`. Targets: a machine id, `"machine.part"`, an object id,
`[x, y, z]`. A run whose program drove the camera films through it; a person watching can drag the view away and
press Director to return. For a YouTube shot: a world program that only moves the camera, beside the machines'
programs.

## 3. Several machines, one world

Any number of machines and objects share one world and collide with everything (parts joined by a declared joint
or gear never collide with each other). Programs name the machine they drive; a world program orchestrates:
`machines["car"].motor("drive").speed(30); machines["arm"].motor("shoulder").angle(40)`. The same CAD machine placed
twice is `car` and `car-2`. `set_settings` for gravity, timestep, floor friction and the look.

## 4. Advanced

A package written by hand (`place_machine { package }`, machine/1 in mm: parts with STL fileIds or primitives,
joints with axis { point, dir }, motors, gears by teeth, sensors, ground welds) is for machines that did not come
from the CAD app. `update_machine { id, motors: […], sensors: […], ground: […] }` gives a machine motors and senses
without re-exporting. `check { mjcf: true }` shows the MuJoCo model. `set_world` replaces everything in one call.

## 5. What to tell the person

The metrics in a sentence ("the car drove 1.9 m and closed both loops of the eight in 15.9 s"), what the program
did, and the picture or film. Offer the next knob in their words (a faster motor, a tighter turn, a camera that
follows from the side).
