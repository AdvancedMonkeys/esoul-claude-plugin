---
name: browser-use
description: How to drive a web page RELIABLY and know whether it worked — the failure modes of browser automation and the verification discipline that catches them. Reading a page fails loudly; WRITING to one fails silently, so a successful tool result proves keystrokes were delivered, never that the page changed. Covers verifying by artifact rather than by result, silent per-write drops, missed clicks that type into the wrong element, unstable selectors inside embedded editors, locale-parsed input, stuck embedded apps, tab addressing, and what changes when the page is somebody's record. Read alongside the cloud-browser skill, which covers WHICH tools to call; this one covers whether to believe them. Triggers whenever a browser task WRITES — filling a form, editing a document, entering data, submitting anything.
---

# Driving a page you cannot fully see

Browser automation is two very different jobs. **Reading** a page fails loudly: no element, no
text, an error you can act on. **Writing** to one fails silently — and almost every rule here was
paid for by a real document that got damaged before anyone noticed.

## The rule everything else follows from

> **A success result is evidence that keystrokes were DELIVERED. It is never evidence that the
> page CHANGED.**

Write ops report what they sent, not what happened. Measured on a real task: roughly **one write in
fifty vanishes with a clean `ok`** — not an error, not a warning, just a cell that stayed empty
while the tool said it wrote four.

So a write task is not finished when the calls return. It is finished when you have re-read the
**artifact** — download the file, reload the record, read the page back — and compared it against
what you intended. Ask **two** questions, never one:

1. Did my changes land?
2. **Did anything else change?**

The second question is the one that catches real damage, and answering it requires a **pristine
copy taken before your first edit**. Take it. Always.

**Retry what failed, then verify again.** A single pass plus a single check is not enough when the
drop rate is per-write. Loop until clean.

## Verification traps

- **The stored copy lags the live session.** A verification that fails immediately after writing
  should be retried before it is believed. Distinguish the cases with a screenshot: visible on
  screen but absent from the file = lag, wait; absent on screen = a genuine drop, rewrite it.
- **Add a cache-buster** to any download URL (`&_=<epoch ms>`); an in-page fetch is otherwise
  served from the browser's HTTP cache and you will diff the same stale bytes three times.
- **Some surfaces cannot be read back at all.** Excel for the web keeps its formula bar and cell
  reference off the DOM — every selector returns `""`. When in-browser read-back is impossible, say
  so and fall back to the artifact rather than pretending a check happened.

## A missed click does not error

A write op with a selector clicks, then types into **whatever has focus**. If the click misses, the
text lands somewhere else entirely and you still get `ok`. Live consequence: a cell reference typed
into a spreadsheet cell, and a paragraph of prose into a title row — which then broke a formula and
blanked a whole column.

- **Prefer routes with no selector.** A keyboard shortcut that opens an already-focused field beats
  an element you have to find. (`ControlOrMeta+G`, `ControlOrMeta+F`, `/`, `Escape` first.)
- **When you must use a selector**, screenshot before typing, or type into a field you can read
  back and check.
- **Clear before typing** into any dialog field — they remember their last value, and appending
  turns `O43` into `O43O43`.

## Selectors inside embedded editors

Office, Docs, and any `<iframe>`-hosted editor: only the **frame-piercing absolute xpath** reaches
inside; CSS and relative xpath silently fail to cross the boundary. Worse, those xpaths encode DOM
position and **shift between renders** — one moved from `div[4]` to `div[5]` mid-session. Re-derive
with an observe call rather than caching one, and prefer keyboard routes.

## One verb per act call

An AI-steered `act` given "click the box, type X, press Enter" clicked the box and then sent `X` to
the page **body**, where it was swallowed. It reported success. Use one verb per call, or the
deterministic type/press ops.

## Typed values are parsed in the PAGE's locale

`6.8` typed into a Czech spreadsheet stored **6 August**, and the month's total read 46 294 hours.
The same string is a valid number in one locale and a valid date in another, so nothing errors.

- Read a value a **human already entered** and match its format.
- **Verify a computed total, not a single field.** A wrong field looks plausible; a wrong total
  does not. Totals are the cheapest lie detector you have.

## When an embedded app renders blank

The iframe exists, the accessibility tree is nearly empty, the screenshot is white. Reloading
rarely helps — three loads failed in a row. **Park and wake**; a fresh browser fixed it instantly.
Tabs and logins survive parking.

## Tab addressing

**Switch once, then stop passing a tab index.** The stored tab order and the browser's own can
disagree, so an index-addressed op may drive a different page than you think — a read of "the
spreadsheet tab" once returned the document library instead. Unaddressed ops all act on the active
tab, consistently. Re-read status after closing any tab; indices shift.

## Opening a document by URL

Vendor "pretty" URLs and viewer wrappers time out surprisingly often. When a site has its own API
and you are already authenticated in the browser, ask it directly — one eval against the site's own
REST endpoint resolved a file id after every URL form had failed. Note that eval takes a function
**body**, not an expression: `1+1` evaluates and is discarded, `return 1+1;` works.

## When the page is somebody's record

An invoice, a timesheet, a shared tracker, an account that is not yours: the blast radius is other
people's trust, not your afternoon.

- **Prove which document you are on before the first keystroke** — read the title back and assert
  the expected name is in it. Filenames differ by one surname.
- **Guard the target's identity in CODE, not in your intentions**, and **prove the guard refuses a
  real sibling** before trusting it. A guard written for this work silently allowed everything
  because its pattern excluded spaces and the filenames contained one. A scan that matches nothing
  reads exactly like coverage.
- **Match the conventions already in the document** — open a previous period and copy its
  vocabulary, its rounding, where it puts a remainder. Consistency is itself a signal to whoever
  reviews it.
- **Never invent content.** Structure, dates and arithmetic can be derived. What a person actually
  did cannot — get it from them or from a record, and say plainly which parts are derived so they
  can correct you before it is submitted.

## Related

- `cloud-browser` skill — which tools to call and in what order; this skill covers whether to
  believe them.
- `reference/web-spreadsheets.md` — the specifics for grids that live in a web app.
