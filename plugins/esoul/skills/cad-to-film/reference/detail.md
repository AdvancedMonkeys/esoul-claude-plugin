# Modelling a machine with film-grade detail

Use while modelling a machine in the CAD app for a film: how much detail, which parts, what to name them, so that a close-up reads as a real machine and Render Studio dresses it in the right materials. Part of the cad-to-film skill (SKILL.md has the order of the work).

Fault behind this page: "the renders lacked much detail". The first MRI scanner was 27 bodies and 28k triangles and read as a toy. At 90 bodies and 161k triangles (5.7×) it read as a machine. Detail is the small bodies around the big ones, not more polygons on the big ones.

1. THE PART LIST COMES BEFORE THE MODEL — AT LEAST 40, IN FIVE GROUPS
- BASE: what it stands on. Feet, plinth, floor plate, levelling pads, cable trays.
- STRUCTURE: what holds it together. Frame, housing, covers, flanges, ribs, the bolt rings on every flange.
- MECHANISM: what does the work — the parts the film is about. Coils, rotors, gears, shafts, bearings, pistons, the moving table.
- CONTROLS: what a person touches or reads. Panels, buttons, displays, status lights, handles, cable glands, labels.
- SUBJECT: what the machine acts on. The patient, the workpiece, the fluid, the load.
Write it as a table (group · part · material · moves? · named in the narration?) on the film's facts page. Every part the narration names must be in it and must be visible in some shot.

2. NAME BODIES FOR WHAT THEY ARE AND WHAT THEY ARE MADE OF
Render Studio picks a body's material from its name. A material in brackets wins: (brass) (steel) (stainless) (aluminium) (copper) (rubber) (plastic) (glass) (wood) (gold) (chrome). After that, words decide: bolt, shaft, gear → brass; wheel → rubber; coil, cable, bracket, glass… A body called "body-17" renders as grey paint.
Good: "Bolt ring front (steel)", "Bore liner (plastic)", "Gradient coil X (copper)", "Cover seam left (rubber)", "Display (glass)".
Two materials on one body is two bodies.

3. THE SMALL THINGS ARE THE DETAIL
- Bolt heads round every flange (a ring of 12–24, not one).
- Chamfers and fillets on every visible edge: a sharp edge catches no light and reads as a game asset.
- Seams and panel gaps between covers (a 1–2 mm slot), so a big cover reads as made, not cast.
- Cables with slack, entering through glands; hoses with a bend.
- Feet, hinges, handles, vents (a grid of slots), a nameplate, status lights, a display with something on it.
- Ten small bodies make one big body believable. Spend detail where the camera goes close; the back of the machine can stay plain.

4. THE INSIDE, IF YOU WILL CUT IT OPEN
A Render Studio section (machines[i].section: [{ point, normal }]) shows whatever is modelled behind the cut, with capped faces. If nothing is modelled there, the cut shows a hollow shell. Model every internal part the narration names, in its true place and size from the facts page, and the layers between them (former, liner, shield). An xray of a cover needs something worth seeing behind it too.

5. MOTION NEEDS JOINTS, IN THE MODEL
A rotation whose angle is a variable is a joint; a part with no variable turning it is welded to its parent. Spin the deepest joint first (a wheel before the arm it rides on). A variable that is a linear expression of another is a gear (teeth from the names: "Pinion 8T", "Gear 24T"). Then cad_build, cad_export_machine, and in RunMachine place_machine { cad } or update_machine { fromCad: true } after a change.

6. CHECK IT AS THE CAMERA WILL SEE IT
- cad_build lists every body with its box: count them against the part list.
- A Render Studio preview still in the film's look at the closest planned framing (stills: [t], quality: "draft", camera with zoom > 1 or exact keys). Look for grey paint (a body without a material), floating parts (a wrong transform), and plain big surfaces with nothing on them.
- The review lens for detail: "pause on the closest frame of the film — is there anything a real one would have that this one does not?"
