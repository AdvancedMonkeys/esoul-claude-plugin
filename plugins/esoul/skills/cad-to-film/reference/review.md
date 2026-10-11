# Reviewing a machine film like a critic

Use to check a machine film before calling it done: every check ends in a picture or a number, and the person who built a shot is not the one who passes it. Part of the cad-to-film skill (SKILL.md has the order of the work).

1. EVERY CHECK ENDS IN A PICTURE OR A NUMBER
"It looks right" is not a check. Each of these is:
- RENDER STUDIO'S REVIEW. read_render { renderId } on a finished film returns: a contact sheet of 16 finished frames, evenly spaced, with the overlays drawn (left to right, top to bottom), as a picture; and in words, frozen stretches (the picture barely changes for ≥4 s), black stretches, labels that overlap each other, labels whose point is off screen. A clean review says "no frozen or black stretches, labels clear".
- THE EXPORT'S CHECK. export_job on a done export ends with "Checked the finished film: …" — frozen (≥4 s), black, silent (≥3 s) stretches of the whole cut. Clean reads "no frozen, black or silent stretches".
- STILLS AT THE MOMENTS THAT MATTER. stills: [t1, t2, …] with quality "draft" for the busiest frame of each shot, the moment a part is named, and the closest frame. Seconds each.
- NUMBERS FROM THE APPS. cad_build's body count against the part list; RunMachine's metrics against the facts page; the video editor's timeline warnings (read_timeline) for lines that run past their shot.

2. LOOK AT EVERY PICTURE, AND SAY WHAT YOU SEE IN IT
For each contact sheet, write one line per frame that has a problem: frame position, what is wrong, which scene key causes it. If you cannot say what a frame shows, you did not look. The automatic findings miss taste: a label over a bright part, a camera that frames the wrong thing, a part that should be lit and is not.

3. REVIEWERS, EACH WITH ONE LENS
If you can start sub-agents (Claude Code's Agent tool), give each one lens and the pictures and numbers above — never the builder's report. Without sub-agents, take the lenses yourself one at a time.
- TRUTH: every number, ratio and motion against the facts page. Wrong is a defect even when it is beautiful.
- MOTION: anything that pops (a value jumping between frames), anything frozen, a camera that parks, a shot with two moves, an effect before its cause.
- LEGIBILITY: text on bright parts, two labels in one corner, a caption over a busy region, a label naming a part that is not visible, type too small at 720p.
- DETAIL: pause on the closest frame — grey paint, floating parts, plain surfaces, a hollow cut.
- THE VIEWER: watch it as a stranger, start to end. Where would they stop understanding? Where would they look away?
Each finding names the shot, the second, what is wrong and the smallest fix ("S07 4.2 s: the X coil glows before 'X' is said — start the hold at 4.6").

4. ROUNDS UNTIL A ROUND FINDS NOTHING
A FIXER applies the findings, re-renders only the shots that changed (a still first, then the film), and the reviewers look again at the new pictures. Stop when a whole round finds nothing, not when the list gets short. Keep a PROGRESS page in the workspace: per round, the findings, the fixes, what was re-rendered.

5. FAULTS THAT HAVE ALREADY HAPPENED — CHECK FOR EACH
- "The renders are extremely bland and ugly": default grey look, flat light, one camera angle throughout.
- "The renders lacked much detail": 27 bodies where 90 were needed; plain covers; hollow cuts.
- Frozen pictures: shots ending in a still tail hold while the narration finished.
- White type on a white scanner; gold captions on a brass base.
- Two labels in the same corner at the same time.
- A label pinned to a point the render never recorded (Render Studio now refuses it by name).
- A shot rendered in a code sandbox that restarted mid-render and lost it (render on the person's computer).
- A described shot nobody looked at.

6. BEFORE HANDING IT OVER
Watch the exported film start to end. Then tell the person: the length, how many shots, which app made each kind, the render time, the last review round's result, and anything simplified or dropped. The person decides what goes out under their name.
