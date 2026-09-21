---
name: porkbun
description: Work the user's Porkbun account through their ExternalSoul cloud browser over MCP — list their domains and expiry dates, check what's coming up for renewal, and add or change DNS records (TXT/A/CNAME/MX, site-verification tokens, SPF) on domains managed at Porkbun. Triggers on "list my porkbun domains", "when does my domain expire", "add this google-site-verification TXT record", "point app.mydomain.com at this IP", "add the DKIM records". Requires an ExternalSoul MCP connection with tools access AND a cloud_browser app the user is logged into Porkbun with — ASK which browser app that is if they haven't said. NOT for registering/buying domains or renewals (purchases — the user does those by hand) and NOT for changing nameservers (can take a site offline — user-by-hand only).
---

# Porkbun over the ExternalSoul cloud browser

Everything here drives a `cloud_browser` app via `get_app_tools(app_id)` +
`call_app_tool(app_id, tool_name, arguments)`; tool names carry the browser's instance name
(`browser_<verb>_<base>`, spaces as underscores). The full browser manual ships separately as
the `cloud-browser` skill — this file is the Porkbun-specific playbook, learned on a real
account.

## THE BROWSER INSTANCE — ASK, DON'T GUESS

Porkbun's login lives in ONE browser app's profile (each cloud_browser app is its own cookie
jar). If the user hasn't named which browser app is logged into Porkbun, ASK. Never create a
new browser app for this (an empty profile means login + 2FA from scratch) and never guess
between several.

## SESSION FACTS (learned the hard way)

- A parked browser wakes on a NEW machine and IP — the Porkbun login still survives IF the
  user ticked "Remember me for 30 days" at login. Bounced to a login page? Ask the user to log
  in by hand in the app's live view WITH remember-me ticked. Never touch their password.
- Porkbun re-challenges ("device not recognized", SMS/email code) on sensitive pages — the DNS
  manager especially — even for a logged-in session. The code is the user's to enter: hand
  off, wait for their word, continue.
- `browser_status_<base>()` first, always: free, shows awake/parked + signed-in sites.

## LIST DOMAINS + EXPIRY DATES

1. `browser_goto_<base>({url: "https://porkbun.com/account/domainsSpeedy"})`. A result title
   of "account login" = not signed in → hand off, then re-goto.
2. Extract deterministically — THE PAGE HAS A TRAP: the only `<tr>` table on it is a
   URL-forwarding template, NOT the domain list. The reliable read is the text between the
   "Displaying N out of N domains" markers:
   `browser_run_script_<base>({expression: "const t = document.body.innerText; const s = t.indexOf('Displaying'); const e = t.indexOf('Displaying', s + 10); return t.slice(s, e > s ? e : s + 3000);"})`
   Rows repeat as: domain name, DNS|NS, expiry date (YYYY-MM-DD), days left ("130 d"). The
   "N out of N" count is your completeness check — parsed fewer? Say so; never present a
   partial list as complete.
3. Report a table sorted by soonest expiry; flag anything under ~45 days. Renewal is a
   purchase — recommend the user do it by hand.

## ADD / CHANGE A DNS RECORD

1. `browser_goto_<base>({url: "https://porkbun.com/account/dns/<domain>"})` — expect the
   step-up login wall here sometimes; hand off if it appears.
2. The form (three traps):
   - Fields: `#editDNSModal_type` (real `<select>`), `#editDNSModal_host`,
     `#editDNSModal_answer`, `#editDNSModal_ttl` (defaults 600), `#editDNSModal_priority`,
     button `#editDNS_button` ("Add Record").
   - TRAP 1: selecting type TXT HIDES the answer input and reveals TEXTAREA
     `#editDNSModal_answer_long` — TXT values go there; filling the hidden input times out.
   - TRAP 2: duplicate/hidden id instances exist — set values by script and READ BACK.
   - TRAP 3: empty Host = the ROOT domain (what site-verification wants); subdomains use just
     the prefix ("app", not "app.example.com").
3. Fill deterministically — record values must be BYTE-EXACT, never AI-typed:
   `browser_run_script_<base>({expression: "const sel = document.querySelector('#editDNSModal_type'); sel.value = arg.type; sel.dispatchEvent(new Event('change', {bubbles: true})); const box = arg.type === 'TXT' ? document.querySelector('#editDNSModal_answer_long') : document.querySelector('#editDNSModal_answer'); box.value = arg.value; box.dispatchEvent(new Event('input', {bubbles: true})); const host = document.querySelector('#editDNSModal_host'); host.value = arg.host || ''; host.dispatchEvent(new Event('input', {bubbles: true})); return { type: sel.value, host: host.value, answer: box.value };", arg: {type: "TXT", host: "", value: "<exact value>"}})
   If the returned answer isn't byte-identical to what the user gave, STOP and refill.
4. **Add Record only STAGES. "Submit Records" COMMITS.** After clicking Add Record, read the
   staged table; only when it shows exactly the requested record, click Submit Records
   (`browser_act_<base>({instruction: "click the Submit Records button", irreversible: true, approved: true})`
   — the user's explicit record request is the approval for exactly that record). The
   boilerplate about "name servers updated" nearby is harmless ONLY when the domain's
   nameservers are already Porkbun's — any doubt (the user mentioned Cloudflare/Vercel DNS, or
   changes you didn't stage appear) → STOP and show the user.
5. **Verify from DNS itself** — the reloaded records list renders lazily and lies by omission.
   Use the workspace's `e2b_sandbox` app over `call_app_tool` (create a code tab, run it):
   `pip install --quiet dnspython` then
   `import dns.resolver; r = dns.resolver.Resolver(); r.nameservers = ["8.8.8.8"]; print([t.to_text() for t in r.resolve("<domain>", "TXT")])`
   Report done only when the resolver returns the record (allow one retry after ~15s), and
   QUOTE the resolved value so the user can compare.

## WHEN THIS GOES WRONG

- Fill times out on `#editDNSModal_answer`: you selected TXT — use `#editDNSModal_answer_long`.
- Record "saved" but the page list looks empty: lazy render — trust the resolver, not the page.
- Bounced to login mid-flow: staged (uncommitted) records are GONE — after the user logs back
  in, re-stage from step 2.
- MX/SRV records: same flow plus `#editDNSModal_priority`.
- Anything about nameserver changes you didn't ask for: stop and show the user.
