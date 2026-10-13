---
name: website-caliber
description: Make a Site-app website of the gsap.com / lenis.dev / reactbits.dev caliber — giant display type, one idea per screen, one neon accent, art that lives with the type (shader backdrops, the client's own 3D object from the CAD app, a Figure Studio film), scroll as the story (pinned chapters, a sideways rail, a stack, a statement whose words light up, a page that changes colour), magnet buttons and glare, a pill nav and smooth scroll — judged by critique_page_ mode caliber. Stage 2b of the website skills (start at `website`); read before laying out any page. Not for a Forge app's look.
---

# Caliber — sites of the gsap.com / lenis.dev class

The platform skill `site-caliber` is the same text: in a workspace chat read it with
`read_skill("platform:site-caliber")`. This file is that text for a Claude that builds over MCP
(`call_app_tool` reaches every `_<site>` tool below; the CAD app is `plugin_cad` — see the `cad` skill).

Previous stage: `website-look`. Next: `build-esoul-website` (the block manual) → `website-publish`.

Read this BEFORE laying out any page. The bar: giant type, one idea per SCREEN (a long page of many
screens), one neon accent, art that lives with the type, scroll as the story — and EVERYTHING known
about the business on the page (the full price list, the history with years and names, the hours,
the people, the guests' words). A thin page of three poster words is a template, not a site. Every
move below is a PROP with a tuned default; your job is the brand's words and the choices.
`<site>` = the site app's tool suffix. Story first (`platform:site-story`): read the brief notes. Nobody to ask (an autonomous run)? The
brief IS the interview: decide, use only its facts, and say what you assumed; the CAD object, a
backdrop and the type are the art when there are no photos.

## 1. Brand → features (decide once)

Place the brand on four axes — temperature, weight, age, tempo — and take the row. Every site gets
its OWN face and palette (no two of the owner's sites share one).

| Brand reads as | face | bg / fg / accent | backdrop | object behind the type | scroll |
|---|---|---|---|---|---|
| warm · heavy · heritage · fast (pub, restaurant) | `anton` caps | `#120d0b` / `#fff3e2` / `#ffb03b` | `nebula` | tankard, dish | rail of dishes, cream menu chapter |
| warm · light · heritage · still (bakery, books, florist) | `instrument`, `serif`, `bricolage` | cream or bottle green + a warm accent | `silk`, `grain` | loaf, books, tulips | stack, lit statement |
| cool · light · new · still (clinic, adviser, architect) | `gloock`, `grotesk`, `mono` | white/paper + blue, mint or orange | `silk`/`threads` hero, `grid`/`dots` chapters, `grain` dark | calculator, molar, house | pinned steps, rail |
| cool · heavy · new · fast (trades, coach, gym) | `bigshoulders`, `bebas`, `unbounded`, `archivo` | near-black + yellow, lime, cyan, red | `threads`, `stars` | bulb, dumbbell, valve, heavy bag | steps, sticker words |
| warm · light · new · fast (studio, kids, salon) | `syne`, `familjen`, `editorial` | peach/cream + pink, violet | `dots`, `silk` | camera, chestnut, scissors | rail, stack |

ONE call: `set_theme_ {accent, background, foreground, font, radius: "pill", density: "airy",
motion: "lively", nav: "pill", scroll: "smooth"}`. Pill rounds buttons only. Any accent works on any
background: accent TEXT is darkened/lightened automatically until it reads; the fill stays the brand.
Seasonal change (Halloween, a sale): patch only accent/background/backdrop and the hero words.

## 2. The object — made in the CAD app, put behind the type

The persisting object (the lenis.dev hand) is the client's own thing, modelled in the workspace's
CAD app (`create_app plugin_cad` if none; `read_skill`/`cad_help_<Model>` for op shapes):
- a round thing (glass, bottle, bulb, vase, stones) = a half-profile `sketch` on plane `ZX` (u ≥ 0 =
  radius, v = height, lines closed along the axis) + `revolve` about `{x:0,y:0,z:1}`;
- a flat thing (calculator, books, house) = `XY` sketch + `extrude`; a `grid` entity for keys/windows;
- keep separate bodies (no fuse of touching curved parts); `cad_build {view: true}` and LOOK;
- give the thing its character: a loaf has scoring cuts, a glass a stem — a bare primitive reads
  as a placeholder; one `style {node, color}` per body;
- `cad_request {kind: "export", args: {format: ".stl binary", name: "Tankard"}}` → `cad_build` →
  `cad_read_answer {requestId}` (the printed id WITHOUT its `request:` prefix) → `Tankard.stl` is in
  the workspace. Export only your bodies with `args.ids: ["<stepId>:<opId>"]` (no `node:`).
Then `Model3D {file: {url: "Tankard.stl"}, material: chrome|matte|accent|glass, motion: tumble|turn|
follow, color, height: "screen", tone: "clear", place: "behind"}` as a DIRECT child of a pinned
`flow` Section, with the kicker, a Display and one paragraph. `color` paints every material (an STL
carries none). Behind = it fills the band on a desktop with the text over its left side; on a phone
it comes after the text. Bring it back behind the closing wall with another motion. A film (Figure/Render Studio) works
the same as `Video {place: "behind"}`.

## 3. The vocabulary

- `Hero {scale: poster, height: screen, eyebrowStyle: brackets|mono|line, cue: true, backdrop,
  accentWords: "2", accentStyle: color|gradient|sticker|underline, lines: stagger}` — ≤ 12 words,
  ONE button (secondary empty), a subtitle ≤ 120 characters.
- `Display {text "A\nB", size: display|poster|wall, uppercase, accentWords, outlineWords,
  mutedWords, accentStyle, lines: stagger, reveal: scramble, scrub}` — one giant line.
- `Statement {text with *starred* words, size: xl}` — words light as it scrolls; stars only
  around words ("*Hrabůvka*:" is fine).
- `Section {pin: 3|4 (how many screens of scroll the chapter holds), pinLayout: steps|rail|flow, pageColor, pageInk, backdrop, tone, width:
  wide, padding: lg}` — steps: 3–4 Displays (size display, ≤ 3 short lines), one beat each; rail:
  a Display then 5–8 Cards (they become posters; on a phone a swipe row); flow: the object behind
  + text. Any backdrop works on a pinned Section. Cards in a dark band take its colours.
- `Stack {items: [Section tone dark|accent|tint, padding lg, a kicker, a Display, a paragraph, a
  Button]}` — 3–4 cards that pile.
- `Card {title, body, variant: outline|brutal, tag}` · `Button {label, href, variant, icon:
  phone|map|mail|calendar|cart|arrow|play}` · `Marquee {items, tone: accent}` · `Stats` ·
  `Hours` · `Columns` (2) for the practical band.
- Kicker above a chapter: RichText `<p class="site-kicker">01 — Z tanku</p>`.
- Backdrops: `silk nebula threads stars` (living), `grain grid dots glow aurora` (quiet).
- Designed blocks only for what this lacks (`design_block_` lists its motion attributes).

## 4. The page (12–16 chapters, all from the brief)

1 ribbon/nav · 2 poster Hero (backdrop, cue) · 3 Marquee of real offers · 4 pinned flow: the
object behind the first story chapter · 5 Statement in their own words · 6 pinned steps (how it
works / their years / their hours as beats) · 7 pinned rail: the price list as poster cards with
prices · 8 a `pageColor` chapter (the menu/price grid or a designed board) · 9 kicker + Display +
Stack of 3–4 services · 10 Stats of real numbers · 11 Columns: Hours / where / contact with icon
buttons · 12 wall Display close on the brand colour, the object back behind it (another motion) + two
buttons · 13 Footer with the legal name.
Vary it per brand — but never drop the facts, and never repeat one: a thin brief (a few prices,
one address) makes 8–10 chapters, not 16 — fewer, bigger screens beat padding. Phone: pins and stacks work; flow pins unpin.

## 5. The grader's rules (every one came from a real mistake)

`screenshot_page_` and `critique_page_` MEASURE these and name them by id with the fix; a severe one
fails the page: **horizontal-overflow / clipped-headline** (nothing wider than a 320 px phone),
**leaked-markup** (`*`, `\n`, `{{…}}`, `[placeholders]`), **empty-media** (every file name exists),
**low-contrast**, **stadium-panel**, **tight-diacritics**, **tiny-text**, **crowded-hero**. Judged by
eye: **empty-screen**, **art-front-loaded**, **template-row**, **static-pin**, **palette-drift**.

## 6. The loop (≤ 4 rounds)

1. `critique_page_ {viewport: "desktop", mode: "caliber"}` — nine rules 0–2 over frames at 0/35/70 %
   WITH motion. It prints "Measured on the page: …" (pins, stacks, magnets…): if those counts
   contradict your page, the judge did not see it — re-run, never edit to chase it. Fix the lowest
   rule first; the note names the prop. Judges also misread (a wrong time, a "cropped" peek): check.
2. `screenshot_page_ {at: 0.35}` and `{at: 0.7}` — look: one beat per frame, text readable over
   the art, the object visible.
3. `screenshot_page_ {viewport: "small"}` (320 px) and `{viewport: "tablet"}` — every measured rule
   clean at every width.
4. `critique_page_ {viewport: "phone", mode: "ship"}` before publishing (`platform:site-publish`).
Stop at a pass (every rule ≥ 1, score ≥ .75) or say what still fails and why. A verdict moves
about ±.05 between runs, so read the rule NOTES, not one number: fix what two runs both name, and
never trade one viewport for the other — a change that fails the phone is undone
(`undo_last_edit_`), whatever it did for the desktop. A critique that answers "aborted" is retried once.
