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

## 3. Writing a controller that actually works

Anything that balances, holds a speed or drives to a place is FEEDBACK, and feedback has numbers in
it. Do not guess them. Four readings decide every gain, and the app will tell you three:

- **Mass, and how high the mass sits.** `describe_machine` gives the machine's total mass, each
  link's mass and the height of the centre of mass above a wheel axis. A body whose mass sits `l`
  above its wheels falls with a time constant of `sqrt(l/g)` — 43 mm gives 66 ms, and a loop that
  corrects slower than that will never balance it.
- **What the tyres can transmit, not what the motors can give.** Two wheels carrying `m` kilograms
  transmit at most `mu*m*g*r` newton-metres before they slip, and `describe_machine` states it. A
  motor limit is usually far higher. **A command above the grip limit does not give more push, it
  gives less** — the wheel spins, the loop loses its authority and the machine settles into a fast
  wobble. Cap the command below the grip figure and the wobble disappears.
- **Rates from the IMU, not from differencing an orientation.** `machine.sensor("imu").gyro` is the
  body's angular velocity now; a difference of `part.quat` is the same number a tick late, and a
  tick is most of the phase margin a fast loop has.
- **Travel speed from the WHEELS, not from the body.** `part(id).velocity` is the velocity of that
  link's CENTRE OF MASS. On anything that rocks, its own rocking is in that number (4 rad/s on a
  43 mm arm is 0.17 m/s the machine is not travelling at) and feeding it back makes the machine
  chase itself. Use `(joint rate + body rate) * wheel radius`, which is what a real robot reads.

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
from there along +x to `h` over `l` (yaw 180° makes it fall that way instead).

**One machine, one program.** Two programs bound to the same machine write opposing torques to the
same motors every tick. Pass `programs: [...]` to `run` and keep spare controllers unbound.

When something will not stand up, measure before you tune: a short run that applies a known torque
and logs the tilt, the wheel rate and the travel tells you in one call whether the wheels are
gripping, whether the loop is too slow or whether the machine is simply stuck.

## 4. Several machines, one world

Any number of machines and objects share one world and collide with everything (parts joined by a declared joint
or gear never collide with each other). Programs name the machine they drive; a world program orchestrates:
`machines["car"].motor("drive").speed(30); machines["arm"].motor("shoulder").angle(40)`. The same CAD machine placed
twice is `car` and `car-2`. `set_settings` for gravity, timestep, floor friction and the look.

## 5. Advanced

A package written by hand (`place_machine { package }`, machine/1 in mm: parts with STL fileIds or primitives,
joints with axis { point, dir }, motors, gears by teeth, sensors, ground welds) is for machines that did not come
from the CAD app. `update_machine { id, motors: […], sensors: […], ground: […] }` gives a machine motors and senses
without re-exporting. `check { mjcf: true }` shows the MuJoCo model. `set_world` replaces everything in one call.

## 6. What to tell the person

The metrics in a sentence ("the car drove 1.9 m and closed both loops of the eight in 15.9 s"), what the program
did, and the picture or film. Offer the next knob in their words (a faster motor, a tighter turn, a camera that
follows from the side).
