# Motion craft for machine films

Use while writing Render Studio scenes and cutting a machine film: how motion should feel so that nothing pops, nothing freezes and every change has a cause. Part of the cad-to-film skill (SKILL.md has the order of the work).

THE ONE RULE: A VALUE NEVER JUMPS. Every glow, opacity, explode distance, label and camera position starts from rest and comes to rest. A hard key ([[4, 0], [4, 3]]) is a pop; a pop reads as a glitch, not as an event.

1. ENVELOPES INSTEAD OF HARD KEYS
Anything in a Render Studio scene that takes keys (glows[].keys, xray[].keys, explode.keys, visibility) also takes an envelope. Its parts add up over a base:
- holds: [{ from, to, value, ease }] — eases up at `from`, stays, eases down by `to`. A part LIT WHILE THE NARRATION NAMES IT. ease 0.3–0.6 s.
  glows: [{ match: "*gradient coil x*", color: "#C084FC", keys: { holds: [{ from: 4.4, to: 7.6, value: 3 }] } }]
- bursts: [{ at, peak, rise, fall }] — a smoothstep rise (default 0.12 s) and an exponential decay (default 0.6 s). A spark, a click, a radio pulse, an impact.
- pulses: { start, every, count | until, peak, rise, hold, fall } — a repeating smooth plateau. A coil knocking, a pump stroke, a heartbeat. Several pulses blocks may be a list.
- keys still work and may sit under the rest; base is the value with nothing happening (xray's base is 1, opaque).
Timing comes from the narration: if the voice names the coils at 4.4 s, the hold starts at 4.4 s. Write keys only at change points; a key per frame changes nothing and makes the scene too big.

2. THE CAMERA NEVER STOPS
- A preset move (hero, reveal, dolly, crane, orbit) runs the whole shot; pick the move from what the shot says: reveal for "here it is", dolly/hero for "look closer", orbit for "all around it", crane for "from above, the layout".
- Exact keys (camera.keys [{ t, eye, lookAt, fov }]) are eased between; space them 3–8 s apart and keep a small move going through a hold (eye drifting 2–4% of the distance) rather than parking.
- A camera that follows a moving part (camera.follow { target, lag }) approaches it exponentially: lag is the time constant in seconds. 0.12–0.4 s reads as a camera operator; 0 locks on and every jolt of the part shakes the frame.
- One move per shot. Two moves in one shot read as indecision.

3. EVERY SHOT MOVES, START TO END
- A shot whose machine is at rest still moves: the camera drifts, a glow breathes (pulses with a long period and a low peak), or the explode eases a few percent.
- In the video editor, every still and every calm shot gets drift (add_clips item drift: 0.04–0.06, or set_clip_drift). Drift is an eased push-in over the clip's whole length; negative pulls back. Alternate push and pull between neighbouring stills so the cut has a rhythm.
- A tail hold (waiting for the narration to finish) is the commonest frozen picture. Plan shots from the narration's measured length so there is nothing to wait for, and give whatever remains a drift.

4. STAGGER, DON'T STACK
- Things that appear together appear 80–150 ms apart, in reading order (left to right, or the order the narration names them). Ten parts lighting in the same frame is a flash, not an explanation.
- Labels come in after the part is lit (0.3–0.5 s later) and leave before the next part's label arrives; two labels never share a corner at the same time.

5. CAUSE BEFORE EFFECT
The thing that makes the change moves first: the current glows, THEN the field arrow grows (props arrow grow), THEN the protons tip. If the effect starts first, the viewer reads the wrong cause.

6. PACE
- 12–30 s a shot. A new idea every 6–10 s inside a shot.
- Hold the important frame for at least 1.5 s with nothing new arriving.
- Explode out over 2–4 s, hold, come back over 1.5–3 s. An explode of more than 1.5× reads as a parts catalogue, not a machine.
- RunMachine motion too fast to follow: slow it with Render Studio's time.speed (0.5 plays it at half speed) rather than re-simulating; a part turning more than about 60° a frame renders sharp on purpose (motion blur cannot follow it), so slow it if it must blur.

7. OVERLAYS FADE, AND SIT ON DARK
Render Studio overlays (kicker, title, captions, labels) fade in and out in 0.4 s, in Inter, on dark plates. Keep a label's plate over dark background; white type on a white machine vanishes, gold on brass vanishes. Use offset to move a plate into empty space; the review names labels that overlap or point off screen.

8. A CHECKLIST PER SHOT, BEFORE RENDERING IT
- What moves in the first second? In the last second?
- Which keys are hard jumps? Replace each with a hold, a burst or eased keys.
- Does each glow start when its words start?
- Is there one camera move, running the whole shot?
- Is any label shown over a bright part?
Render a draft still at the busiest moment (stills: [t], quality: "draft") and look at it before the film.
