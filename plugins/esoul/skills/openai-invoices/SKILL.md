---
name: openai-invoices
description: Pull the user's OpenAI (platform.openai.com) invoices into their ExternalSoul workspace over MCP — all of them, a time window, or ONLY the ones they don't already have, deduped by invoice number against however they track invoices (the PDF filenames, a spreadsheet, or a notes table), batch-downloaded into a folder, and optionally appended to their ledger. Triggers on "download my openai invoices", "get the openai invoices I don't have yet", "pull this year's openai bills into the invoices folder and add them to my sheet". Requires an ExternalSoul MCP connection with tools access AND a cloud_browser app the user is logged into platform.openai.com with — ASK which browser app that is if they haven't said. The Stripe half (resolution + download) generalizes to ANY vendor whose billing links go to invoice.stripe.com. NOT for OpenAI API usage stats.
---

# OpenAI invoices over the ExternalSoul cloud browser

Everything here drives a `cloud_browser` app via `get_app_tools(app_id)` +
`call_app_tool(app_id, tool_name, arguments)` (tool names are `browser_<verb>_<base>`,
`<base>` = the browser's instance name; the pip `esoul-mcp` server also has native
`browser_*` shortcuts). The full browser manual ships separately as the `cloud-browser`
skill — this file is the OpenAI/Stripe-specific playbook, learned on a real 30-invoice run.

THE SHAPE: filter → ledger → enumerate → narrow by date → resolve (exact dedup happens
HERE) → batch download → update records → honest counts.

## STEP 0 — the browser instance: ASK, don't guess

The OpenAI login lives in ONE browser app's profile. If the user hasn't named it, ask.
Logins are the user's: they sign in by hand in the app's live view, and OpenAI's MFA
step-up challenges are theirs to answer too — hand off, wait, continue. Logged out
mid-run? Hand off again, then just re-run: exact dedup makes the whole flow idempotent.

## STEP 1 — pin the filter

A date window ("2026", "since March"), "all", or "only new ones". Even an explicit window
deserves dedup if they already hold part of it: **downloads have no skip-if-exists** — a
repeat download creates a second workspace file with the same name.

## STEP 2 — find the ledger (what they already have)

Look before asking, in this order:
1. **Workspace files** are the "already downloaded" truth: list files (`workspace_list_files`
   on the pip server / `list_files` on a storefront) matching `Invoice-<ACCT>-<NNNN>.pdf`.
   The `<NNNN>` suffix is THE dedup key; `<ACCT>` is per-account — never hardcode. The
   folder those PDFs live in is the default destination for new ones.
2. **A spreadsheet or notes table** (invoice number / amount / date columns) is the
   "already recorded" truth — read it (`read_app_state` on the sheet or the notes app, or the
   sheet's own read tool via `get_app_tools` → `call_app_tool`) when files don't answer or the user says that's their system.
3. **Nothing found** → first run: everything in the window is new. Default folder
   `openai_invoices_<year>`; related files belong in one folder, never loose at root.

Two hard facts: **date+amount is NOT unique** (a real account had two $12.10 invoices on
one day) — only the number dedups. And **number gaps are normal on OpenAI's side** (0079
and 0089 never existed on the reference account) — a gap is not a missing download.

## STEP 3 — enumerate the billing table

`browser_goto_<base>({url: "https://platform.openai.com/settings/organization/billing/history"})`.
Each row: date, amount, status, and a link to the Stripe-hosted invoice
(`invoice.stripe.com/i/<acct>/<token>`). Pull rows deterministically:

```
browser_run_script_<base>({expression: "return [...document.querySelectorAll('a[href*=\"invoice.stripe.com/i/\"]')].map(a => ({href: a.href, row: (a.closest('tr') || a.closest('[role=\"row\"]') || a.parentElement)?.innerText}))"})
```

Parse date + amount from each `row` text, `<acct>`/`<token>` from the href. Page through
any Load-more until rows predate the window. Keep only rows in the window (Paid/finalized
only, unless asked).

## STEP 4 — narrow candidates cheaply (dedup runs)

The table shows NO invoice numbers, so don't resolve everything just to dedup. Take the
newest invoice DATE the ledger knows. Candidates = rows strictly newer, PLUS every row
sharing that date (same-day multiples are real). First runs: all rows are candidates.

## STEP 5 — resolve PDF URLs + exact dedup

Open one invoice tab (`browser_goto_<base>` to any candidate's invoice.stripe.com link —
the resolution endpoint is same-origin-only). From that tab:

```
browser_run_script_<base>({expression: "const out = []; for (const t of arg.tokens) { try { const r = await fetch('https://invoicedata.stripe.com/invoice_pdf_file_url/' + arg.acct + '/' + t); out.push({token: t, url: (await r.json()).file_url || null}); } catch (e) { out.push({token: t, url: null}); } await new Promise(res => setTimeout(res, 800)); } return out;", arg: {acct: "<acct>", tokens: [...]}})
```

- **Chunk ≤10 tokens per call, keep the ~800ms pacing** — invoicedata rate-limits bursts
  (an unpaced batch came back all null on the reference run). Nulls: pause ~5s, retry once.
- Each `file_url` is a signed S3 link whose QUERY carries the filename:
  `decodeURIComponent` it and match `filename="Invoice-...-(\d+).pdf"`. That number —
  available BEFORE any download — is the exact dedup: drop candidates the ledger already has.
- **Signed URLs expire in 600 seconds.** Resolve-then-download promptly; past ~40 new
  invoices, work in resolve→download waves.

## STEP 6 — batch download

One call, never a loop of singles:

```
browser_download_batch_<base>({items: survivors.map(s => ({url: s.url})), serverFetch: true, folderPath: "<folder>"})
```

- `serverFetch: true` is REQUIRED — S3 CORS-blocks the in-page fetch ("Failed to fetch"
  every time). The URL itself is the capability; no cookies needed.
- Filenames come from Content-Disposition automatically. Never `browser_goto` a PDF URL
  (navigation timeout, known trap).
- Check the per-item results: `downloaded` vs `failed`. Failures = the URL likely expired —
  re-resolve those tokens, retry once.

## STEP 7 — update their records (only if they keep records)

Append ONLY the new invoices to their ledger — and you already hold everything a row needs
without parsing a single PDF: date + amount from the billing row, number from the resolved
filename, issuer "OpenAI OpCo, LLC". Use the sheet's `add_rows_<name>` tool via `call_app_tool` (or the notes app's tools),
match THEIR column layout, never rewrite existing rows.

## STEP 8 — report honestly

Say: rows the site shows in the window / already had / downloaded (into WHICH folder) /
failed and why. "Zero were new" is a legitimate result — say it plainly. The browser can be
left running; it parks itself after ~5 idle minutes.

## When it goes wrong

- All-null resolutions → rate limited: smaller chunks, keep the pacing.
- `download_failed` on a resolved URL → expired (600s): re-resolve, retry.
- Duplicate same-named files in the folder → a dedup step was skipped: confess, delete the
  extras (the sandbox app's `delete_workspace_files` tool, or ask the user).
- A "missing" number → check the billing table first: OpenAI's numbering has real gaps.

## Generalizes

Any vendor whose billing links go to `invoice.stripe.com/i/...` reuses steps 5–6 verbatim —
same invoicedata endpoint, same signed-URL anatomy, same dedup-by-filename. Only the step-3
billing page is vendor-specific.
