---
name: website-caliber
description: Build or rebuild a local business's Site-app website that ANSWERS FIRST and has its OWN shape — within the first screen who, what and a call or booking button; prices and today's hours one tap away (AnswerBar, the live Today line, anchors, a scroll budget of ≤ 7 phone screens); one opening, one spine, one close and one motion family per site so two sites never share a skeleton; the client's object as a PHOTOREAL still (CAD → render → generate_image with the render as reference), never a live Model3D blob; judged by the phone ship critique first. Stage 2b of the website skills (start at `website`). Not for a Forge app's look.
---

# Caliber — sites that answer first, each in its own shape

The platform skill `site-caliber` is the same text: in a workspace chat read it with
`read_skill("platform:site-caliber")`. This file is that text for a Claude that builds over MCP
(`call_app_tool` reaches every `_<site>` tool below; the CAD app is `plugin_cad` — see the `cad` skill).

Previous stage: `website-look`. Next: `build-esoul-website` (the block manual) → `website-publish`.

Two failures this replaces (owner, 2026-10-13): fifteen sites in ONE skeleton (poster hero → marquee →
pins → rail → stack → wall), and pages a visitor had to scroll 7–12 screens through to find the phone,
the prices and today's hours. The bar now: **the girlfriend test** — within the first screen: who,
what, a call or booking button; within one tap: prices and today's hours; within a flick: where.
Craft (giant type, one accent, the client's object, motion) serves that; it never delays it. Every
fact from the brief is on the page, GROUPED (tabs, chips, a timetable), never one fact per screen.

## 1. Who visits, in what state

Write one line before anything: the visitor, their device, what they need NOW. "Water on the floor
at 2 a.m., on a phone, afraid of the price." "Wants a massage: which, how long, what it costs."
Two kinds of visitor (a pub and the party planner; a passport photo now and a family session)?
The first screen holds both doors and nothing else; the second door's chapter comes second.

## 2. The shape: one opening, one spine, one close, one motion

Choose each from its list. Two sites of one owner never share an opening + spine + close.

| Opening (the first screen answers the visitor's first question) | when |
|---|---|
| **board** — the board IS the hero (`PriceTable` on its slate, a tap wall `Board`) + `Today` | pub, wine shop, café |
| **dial** — the phone number as the headline, one call button, one price line | emergency trades |
| **ticket** — one offer as a card (`Card variant: brutal`) + its button | first training free, a countdown |
| **two doors** — two cards, two buttons, nothing else | two kinds of visitor |
| **notice** — the honest line first (`Notice`), then the answers | closed shop, no new patients |
| **letter** — the owner's own words, signed (`Quote`) + two ways to reach them | adviser, accountant |
| **process** — the three steps as the hero (`Timeline`) | architect, studio |
| **calm line + Today** — a short heading, the live opening line, two buttons | salon, massage |
The poster headline (`Display size: poster`) is allowed for ONE site of a set.

**Spines** (how the facts are grouped): `PriceTable {tabs}` · `Board {chips, search}` ·
`Timetable` (chips by group) · `Tabs` / `Accordion` · `Timeline` · `Estimate` · `Booking`.
**Closes**: the practical band (Hours + where + buttons) · a form · their own words (`Statement` or
`Quote`) · a giant `Today {size: xl}` (at most one site in three).
**Motion** (one family): calm fades · urgency (one pulsing button) · drawing (`Svg draw`) · count-up
`Stats` · paper, nothing moves · fill tiles · silk in the opening only · sticker + hard reveals.

## 3. Answers first

- `AnswerBar {items: [{label, href, icon}] ×4, today, openLabel, closedLabel}` first on the page
  (after the `DemoRibbon` on a demo): a phone's bottom bar, a desktop pill. One word per item (Zavolat · Ceník · Dnes · Kde);
  `href` = `tel:`, `#anchor`, a map URL. `today: true` reads the page's `Hours`; a 24/7 service
  sets `closedLabel: "Teď: havarijní služba 24/7"` (never "Zavřeno"); no hours known → `today: false`.
- `Today {size: lg|xl, openLabel, closedLabel, prefix}` — the live line from `Hours`;
  `deadline: {time: "17:00", before, after}` counts down ("Objednáte do 17:00, doručíme zítra ·
  zbývá 2 h"); `from: "timetable"` says the next session ("Příští trénink: Dnes 19:00 · Začátečníci").
- `Section {anchor: "cenik", anchorLabel: "Ceník"}` for every chapter the bar or a button names.
- **Scroll budget**: ≤ 7 phone screens (≤ 8 desktop). Group, don't cut: a long price list goes in
  `PriceTable {tabs: true}`, forty categories in `Board {compact: true, search: true, more: 8}`, a
  week in a `Timetable`. One pinned chapter at most; none on a phone.
- A price that buys several things says what: "200 Kč · 8 vstupů za 1 280 Kč", never "200 Kč · 8
  vstupů 1 280 Kč" (on a phone it wrapped into "· 10 / vstupů 3 500 Kč").
- A SHORT brief (≤ 6 facts): the board opening + the practical close, the second door a row of the
  board (wedding koláčky "na objednávku · 3 dny předem") — never chapters padded to fill screens.
- `Hours` rows: the `day` label is read ("Po–Pá", "So a Ne", "denně"), else `weekday` 1–7 or
  "1-5" — one row per day or per range, or the live line says the wrong thing.

## 4. The client's object: photoreal, never a blob

A live `Model3D` of a CAD export reads as a low-poly, one-colour blob — the owner rejected it. Make
a STILL that looks like a photograph:
1. Model the object in the CAD app (`read_skill platform:cad`; a round thing = a revolved
   profile; give it character — a glass has a handle, a loaf has cuts) and render it
   (`platform:render-studio`, or the CAD app's own view) — a composed picture of the object.
2. `generate_image {workspace_id, prompt: "Photorealistic studio product photograph of exactly the
   object in the reference: <what it is, its materials>. Same object, proportions, angle and framing.
   Plain seamless background <the section's hex>, soft contact shadow. No text, no logo, no people.",
   references: ["<the render's file id or name>"], aspect_ratio: "1:1", folder: "Site/Renders"}` — on
   the colour of the band it will sit on (`read_site_` prints each band's hex; glass shows it through).
   The background comes back NEAR that colour, not exact: on a plain band it melts in; elsewhere set
   it as a rounded picture (`Image` without `size`), not a mark. `dry_run: true` first shows the price.
3. `Image {image, size: sm|md|lg}` beside the words it belongs to (the valve beside "zavřete hlavní
   uzávěr"), or `place: "behind"` under a SHORT headline — never under a paragraph or a quote (red
   words over red book covers could not be read; put the object beside them in `Columns`); `swap:
   {url}` cross-fades a second state (a bulb that lights — make it by editing the first picture so
   the two align); `drift: true` for life.
Generated pictures show objects, materials, atmosphere — never the business's premises, staff,
customers or work; caption "Ilustrační foto" where a visitor could take it for theirs (`Image
{caption}`, `Card {imageNote}`).

## 5. The vocabulary

`Board {items: [{title, sub, price, tag, group, href, url}], columns, chips: "filter", search,
compact}` · `PriceTable {groups: [{title, note, url, rows: [{name, price, note, minutes}]}], layout:
table|grid|bars, tabs}` · `Timetable {rows: [{day 1–7, from, to, title, who, group}], chips, next}` ·
`Tabs {labels, tab1…tab4}` · `Accordion {items, item1…item6, open}` · `Estimate {inputs, formula,
formulaMax, note, cta}` (a range stays a range) · `Timeline {items: [{year, title, line}]}` ·
`Notice {text, tone, action}` · `Booking {source, deliver, next: 3}` (the nearest free times as chips —
honest availability where there are no hours) · `Hours` · `Card` · `Stats` · `Quote` · `Statement` ·
`Display` · `Columns` · `Button {icon}`. Kicker: RichText `<p class="site-kicker">Ceník</p>` (drawn mono,
tracked, in the accent's ink, a hairline before it). `set_theme_ {headings: "display"}`: every chapter heading at
display size (~120 px on a desktop, sized by its column; its words cascade in on a lively site) — the judge's scale.

## 6. The grader's rules (every one came from a real mistake)

Measured by `screenshot_page_` / `critique_page_`, named by id with the fix: **buried-answers**
(severe: no answer bar and the phone or hours below 1.2 screens), **too-long**, **no-jumps**,
**pin-heavy**, **horizontal-overflow / clipped-headline**, **leaked-markup**, **empty-media**,
**low-contrast**, **tiny-text**, **crowded-hero**. Judged by eye: **template-row** (identical tiles —
vary or group them), **art-front-loaded** (the object only in the opening — place it where it
explains), **empty-screen**, **palette-drift**.

## 7. The loop (≤ 4 rounds)

1. `critique_page_ {viewport: "phone", mode: "ship"}` — the girlfriend test, and it names what is
   missing. This is the acceptance test.
2. `screenshot_page_` at `small` (320), `phone`, `tablet`, `desktop` — every measured rule clean at
   every width; read "Navigation: N screens, answers at …". `{at: 0}` is the real first screen,
   with the live answer bar (a full-page capture rests the bar at the end).
3. `critique_page_ {viewport: "desktop", mode: "caliber"}` — craft, after the answers work.
Stop at a phone PASS with clean lint, or say what still fails and why. Verdicts move ±.05 between
runs: fix what two runs both name; a change that fails the phone is undone (`undo_last_edit_`).
