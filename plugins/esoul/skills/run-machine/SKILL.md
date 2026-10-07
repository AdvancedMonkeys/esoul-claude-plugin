---
name: run-machine
description: Simulate machines designed in the ExternalSoul CAD app inside the RunMachine app (plugin_run_machine, MuJoCo physics) from chat or MCP — bring a machine in from the CAD app in one call, write a small JavaScript program that drives its motors, run it headless and get metrics, a picture and a film; update the machine after the CAD model changes; drive several machines and obstacles in one world; script the camera for films; and design a real feedback controller (balancing, driving to a position, holding a speed) against the machine's own measured mass and grip instead of guessing gains.
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
   variables are the gears) to `Machines/<name>/` and RunMachine places it resting on the floor. **A part with
   no variable turning it in CAD is WELDED**, so a wheel that must spin needs its own variable, written before
   the op that turns the link it rides on — the `cad` skill's "Make it move" section is the other half of this
   sentence. A machine whose wheels will not turn is almost always that, not the simulation. The answer is the
   machine as a program sees it: motors with the call for each, sensors, joints, gears, parts, and a STARTER PROGRAM
   written for its own motors. `from: "Machines/<name>"` places an export already in the workspace; `pos: [x, y]`,
   `yaw` place it; placing the same machine again updates it in place.
2. `describe_machine { id }` any time you need that text again (it also says when the CAD model changed since).
3. `write_program { machine, name, source }` — `function loop({ t, machine, world, camera, log }) { … }` at 50 Hz.
   It is checked against the machine as it is saved: a motor it names that does not exist comes back here, not from
   a run. `machine: "*"` makes a WORLD program that reaches every machine as `machines["id"]`.
4. `run { film: true }` (20 s by default; a program ends it earlier with `world.stop`). Read the metrics, LOOK at
   the picture; `film { runId, quality: "share" }` for a better film (a film longer than one call can render —
   about 3 s of share quality — renders in the BACKGROUND in parts and lands on the run as one WebM: the answer says
   so, `read_run` lists it under files when it is there; never chunk it by hand); change; run again. Never describe a result
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

## 3. Writing a controller that actually works

Anything that balances, holds a speed or drives to a place is FEEDBACK, and feedback has numbers in
it. Do not guess them — **`describe_machine` measures them off the machine's own meshes** and prints
them before you write a line:

```
mass 258 g total — base 192 g, its centre 42.9 mm above the wheelL/wheelR axis;
wheelL 32.7 g; wheelR 32.7 g.
  the whole machine's centre of mass is (0, 0, 64) mm in its own frame
  wheelL/wheelR roll on base, radius 32 mm; the machine's centre of mass is
  32 mm above that axis — the arm a balance law swings.
  On a level floor the two wheels can transmit about 0.065 N·m between them
  before they slip — a balance law that asks for more is not balancing.
```

Four readings decide every gain, and that one call gives you three of them:

- **How high the mass sits, which is NOT the body's own centre.** The arm a balance law swings is
  the whole machine's centre of mass above the wheel axis — 32 mm here, not the base's 42.9 mm,
  because the wheels sit on the axis and pull the average down. It falls with a time constant of
  `sqrt(l/g)`: 32 mm is 57 ms, and a loop that corrects slower than that will never catch it. Raise
  the control rate before you raise a gain — `write_program { rate: 500 }` costs nothing.
- **What the tyres can transmit, not what the motors can give.** The printed grip figure is usually
  far below the motor limit (0.065 against 0.2 here). **A command above it does not give more push,
  it gives less** — the wheel spins, the loop loses its authority, and the machine settles into a
  fast wobble that looks like bad tuning and is not. Cap the command under the figure. A mass the
  app could not compute (a mesh that is not a closed solid) is reported as UNKNOWN with the reason,
  never guessed — measure it yourself before trusting a gain.
- **Rates from the IMU, not from differencing an orientation.** `machine.sensor("imu").gyro` is the
  body's angular velocity now; a difference of `part.quat` is the same number a tick late, and a
  tick is most of the phase margin a fast loop has.
- **Travel speed from the WHEELS, not from the body.** `part(id).velocity` is the velocity of that
  link's CENTRE OF MASS — the PROGRAM API says so in the answer, because it is the trap that costs
  the most. On anything that rocks, its own rocking is in that number (4 rad/s on a 32 mm arm is
  0.13 m/s the machine is not travelling at) and feeding it back makes the machine chase itself. Use
  `(joint rate + the body's own rate about that axis) * wheel radius`, which is what a real robot
  reads. A joint's `.speed` is measured against its PARENT LINK, not the world — add the body rate.

A balancing machine ends up as one line, with every gain positive and no modes:

```js
tau = KP*tilt + KD*tiltRate + KV*(speed - speedWanted) + KI*∫(speed - speedWanted)
```

`KP`/`KD` are the balance loop; put it just above the falling rate. `KV` is the speed loop and must
stay several times SLOWER than the balance loop — raise it too far and the two meet and the machine
throws itself over. `KI` is what climbs: without it a slope needs more push than `KV*speedWanted`
can ever ask for, so the body settles at a lean that is in perfect static balance and the wheels
simply stand still, which looks exactly like being stuck. Bound the integral, and stop it adding up
while the body is leaning hard — an integral that keeps growing against an obstacle is how a
balancing machine throws itself over.

**Design the gains outside the simulator, then verify inside it.** A few lines of planar maths
(wheel + body, the motor's reaction on both) run in milliseconds, so you can sweep a grid of gains
across ±60 % on every number you had to estimate and keep only what survives. That is how you find
the STRUCTURE — which sensor, which cap, whether an integral is needed. It is NOT how you find the
last 20 %: gains that read smoother on paper took a real machine through 28°. Trust the sim for the
final value, and say which one you trusted for what.

**Raise the control rate before you raise a gain.** `write_program { rate: 500 }` costs nothing and
buys phase; 50 Hz is for machines that do not balance.

**Scale the course to the machine.** A 32 mm wheel does not climb a 20 mm step, and the edge of a
shallow-looking round bump is steeper than it reads: a segment of radius `R` standing `h` proud
meets the wheel at about `sqrt(2h/R)` of slope — 12 mm on a 250 mm radius is 16°, three times the
ramps around it. Build a convex bump out of two gentle ramps and a short flat top and the whole
course stays inside what the machine can do. A `ramp`'s pose is its LOW edge: the top surface rises
from there along +x to `h` over `l` (yaw 180° makes it fall that way instead) — `add_object` and
`read_world` both answer with the span it actually occupies and which way it rises, so read the
answer back rather than trusting the arithmetic you meant.

**One machine, one program.** Two programs bound to the same machine write opposing torques to the
same motors every tick. `run` and the view's Play now REFUSE that and name both programs; pass
`programs: [...]` to pick one, and keep spare controllers unbound.

**Say how long the world wants to run.** A person watching presses Play, and Play takes the world's
own `set_settings { defaultRun }` (20 s if it is unset). A patrol whose round trip is 17 seconds,
watched through a 20-second Play, reads as "it does not go back and forth" — the machine was right
and the demonstration was cut in half. Set `defaultRun` to one natural cycle of whatever you built,
and say so when you hand it over.

When something will not stand up, measure before you tune: a short run that applies a known torque
and logs the tilt, the wheel rate and the travel tells you in one call whether the wheels are
gripping, whether the loop is too slow or whether the machine is simply stuck.

## 4. Before the first run: colliders, mass, motors

A machine that falls over at t = 0.1 s, before any program moved it, is a collider problem, not a control problem.

- **Contacts are excluded only between a joint's two parts.** Every other pair collides, so two links that sit near
  each other at rest (a neck and the arm two joints away) push each other apart the moment the run starts. A
  collider is the body's convex HULL by default — a fork's two prongs become one slab — and `cylinder`/`sphere`
  is fitted to the bounding box, so read the warnings and set colliders on purpose: `none` for decoration
  (springs, bulbs, buttons), `hull` for the rest, a primitive only for a body that really is one (the runtime
  refuses a cylinder the body fills under 60 % of). Proof: a 1 s run with the motors holding 0° must log the
  joints at ~0.
- **Mass.** A closed mesh weighs its own volume at 1000 kg/m³ (runtime 7); a mesh that is not a closed solid
  weighs its hull and the load says so. Real parts are not water: give the part that should anchor the machine a
  realistic `material.mass` (a lamp's cast base 900 g, not 360 g of plastic), and check with `describe_machine`.
- **Will it stand?** Sum the parts' masses × their centres (the `describe_machine` lines) for each pose you
  intend; the centre of mass must stay well inside the footprint. Do it on paper before the run — a few lines of
  forward kinematics answer in milliseconds what a fallen run answers in a minute.
- **Position motors are springs.** Their stiffness grows with `maxTorque` (≈ 0.8 × maxTorque N·m per radian), so
  a toy torque sags under gravity (3–7° on a desk lamp at 1–2 N·m). Size `maxTorque` so the static sag is ~1°,
  then add joint `damping` near half of critical, `2·sqrt(k·I)` — less rings, more is sluggish. Joint `range` and
  `damping` live in the package (`set_world` or `place_machine { package }`).
- **Diagnose a fall by logging, not guessing:** the base's uprightness `1 − 2(qx² + qy²)` from `part.quat`, the
  joint angles and `world.contacts()` every 0.1 s around the moment it goes; a contact between two links that
  should never meet names the cause.

## 5. Making a machine perform (character, emotion)

Motion reads as feeling when it is timed like animation, not when it is precise. What worked for a desk lamp
that wakes, startles, plays with a ball, sulks and is delighted:

- **Keyframed poses with easing.** A list of `[start, duration, pose, ease]`; each beat eases from where the
  last one left the joints. `snap` (fast out) for a startle, a cubic in-out for anything deliberate, `back`
  (overshoot) for a happy settle, ease-IN for a strike so it accelerates into the hit.
- **Anticipation before every fast move:** a wind-up the other way (lean back before the bonk, crouch before a
  hop). **Follow-through** after it.
- **The head leads, the body follows:** aim the head at its target every tick (a gaze solved from the machine's
  own joint geometry and the target's live position), and let the turning joint chase its target through a lag
  (`out += (target − out)·(1 − e^(−dt/τ))`, τ 0.1 s alert … 0.9 s sad).
- **Layers on top of the pose:** a slow breath (all joints, 3–4 s period, bigger when sad or asleep), a decaying
  tremble after a fright, a two-nod sniff, a wag. Never a still pose.
- **Speed is the budget:** a big joint swinging 90° in 0.16 s throws a 1 kg machine over; scale amplitude ×
  speed to what the base can hold and test the fastest beat first.
- **Props are staged, the key contact is physics.** A small steering force on an object (`world.object(id).push`
  as a PD toward a path, capped at ~0.3 N) places a ball between beats; switch it OFF for the moment that
  matters (the bonk) so the result is real, and make the next staged path continue the direction physics gave.
- **Shoot it:** a world-length `camera.path` that cuts between angles at beat boundaries — profile for sadness
  (a droop reads as a silhouette), wide when an object leaves, and end with the machine looking into the lens.
  Set `defaultRun` to the performance length so Play shows all of it.

## 6. Several machines, one world

Any number of machines and objects share one world and collide with everything (parts joined by a declared joint
or gear never collide with each other). Programs name the machine they drive; a world program orchestrates:
`machines["car"].motor("drive").speed(30); machines["arm"].motor("shoulder").angle(40)`. The same CAD machine placed
twice is `car` and `car-2`. `set_settings` for gravity, timestep, floor friction and the look.

## 7. Advanced

A package written by hand (`place_machine { package }`, machine/1 in mm: parts with STL fileIds or primitives,
joints with axis { point, dir }, motors, gears by teeth, sensors, ground welds) is for machines that did not come
from the CAD app. `update_machine { id, motors: […], sensors: […], ground: […] }` gives a machine motors and senses
without re-exporting. `check { mjcf: true }` shows the MuJoCo model. `set_world` replaces objects, machines and metrics in one call and
keeps the settings it does not name. A run whose call died before it finished reads `lost` — run it again.

## 8. What to tell the person

The metrics in a sentence ("the car drove 1.9 m and closed both loops of the eight in 15.9 s"), what the program
did, and the picture or film. Offer the next knob in their words (a faster motor, a tighter turn, a camera that
follows from the side).
