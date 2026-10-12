---
name: website-caliber
description: Make a Site-app website of the gsap.com / lenis.dev / reactbits.dev caliber — giant display type, one idea per screen, one neon accent, art that lives with the type (shader backdrops, the client's own 3D object from the CAD app, a Figure Studio film), scroll as the story (pinned chapters, a sideways rail, a stack, a statement whose words light up, a page that changes colour), magnet buttons and glare, a pill nav and smooth scroll — judged by critique_page_ mode caliber. Stage 2b of the website skills (start at `website`); read before laying out any page. Not for a Forge app's look.
---

# Caliber — sites of the gsap.com / lenis.dev class

The platform skill `site-caliber` is the full text: in a workspace chat or over MCP read it with
`read_skill("platform:site-caliber")` — it carries the brand → features map, the nine rules the
judge scores, the vocabulary and three page recipes. This file is the short form for a Claude
that builds over MCP without `read_skill`.

Previous stage: `website-look`. Next: `build-esoul-website` (the block manual) → `website-publish`.

## 1. Brand → features (one row, decided once)

Place the brand on four axes — temperature, weight, age, tempo — and take the row:

| Brand | font | bg / fg / accent | backdrop | persisting object | scroll pattern |
|---|---|---|---|---|---|
| warm · heavy · heritage · still (bakery, pub) | `instrument` | `#141210` / `#f6efe4` / `#ff7a1a` | `silk` | `Model3D` chrome of the thing they make (CAD app export) | `Stack` of 4, `pageColor` cream at the menu |
| cool · light · new · fast (studio, dev) | `syne` / `unbounded` | `#0a0a0f` / `#ffffff` / `#b6ff2e` | `threads` / `nebula` | the mascot as scrubbed `Video` (Figure Studio) | pinned 4-step chapter, `Statement` |
| warm · heavy · heritage · fast (restaurant) | `anton` uppercase | `#0e0b0b` / `#fff6e8` / `#ff3d5a` | `nebula` | a dish turning (`Video`) | `rail` of three dishes, black → cream |
| cool · light · heritage · still (law, wine) | `instrument` | `#f3efe8` / `#15130f` / `#1b5cff` | `grain` + `glow` | a drawn plan, `Svg data-draw` | `Statement` + `Stack` |
| warm · light · new · fast (café, florist) | `bricolage` | `#fff7ef` / `#1e1a17` / `#ff4fa3` | `silk` | `Scene3D orbs` | `Display` wall + `Marquee` |

`set_theme_ {accent, background, foreground, font, radius: "pill", density: "airy", motion:
"lively", nav: "pill", scroll: "smooth"}` in ONE call. Seasonal changes patch only colours,
backdrop and the hero words.

## 2. Nine rules the judge scores (0–2 each)

scale · one idea per screen · palette discipline · art lives with the type · scroll is the
narrative · texture and depth · type craft · micro-interactions · nothing templated. The fix for
each is a prop: `Hero {scale: "poster", height: "screen", backdrop, eyebrowStyle, cue}`,
`Display {size: display|poster|wall, accentWords, outlineWords, scrub}`, `Statement {*starred*
words, lit}`, `Section {pin: 3, pinLayout: steps|rail|flow, pageColor, pageInk}`, `Stack
{items}`, `Model3D {file, material, motion}`, `Video {file, scrub}`, `backdrop: silk|nebula|
threads|grain`, `nav: pill`, `cursor: dot`. Never: centred everything, three cards under a hero,
a hero image on the right, icons in circles, "Welcome", body text in the accent.

## 3. Recipes

**THE LAUNCH**: poster Hero (nebula, cue) → pinned steps ×3 Displays → Statement → rail of 3 Cards
→ Stack of 3 dark Sections (01–03) → closing Display wall on a cream `pageColor` + two buttons → Footer.
**THE CRAFT**: display Hero (silk) → pinned flow with `Model3D {motion: tumble}` + Display →
Statement → pinned steps (how it is made) → Stack of the products → Hours + Booking → Footer.
**THE TABLE**: poster Hero (anton, nebula) → Marquee of dishes → rail of three dish Cards → the
menu on a cream `pageColor` → Statement → `Video {scrub}` → InfoBar + Hours → Footer.

## 4. The loop

`critique_page_ {viewport: "desktop", mode: "caliber"}` → fix the lowest rule (the note names the
prop) → repeat ≤ 4 rounds until pass (every rule ≥ 1, score ≥ .75); look yourself with
`screenshot_page_ {at: 0.35}` and `{at: 0.7}` (frames WITH motion); then `critique_page_
{viewport: "phone", mode: "ship"}` before `website-publish`.
