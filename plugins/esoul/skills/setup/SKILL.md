---
name: setup
description: Connect or reconnect ExternalSoul — use when esoul tools are missing, when a call returns unauthorized, on first install, or when the user asks to sign in to / connect ExternalSoul.
---

# Connecting ExternalSoul

There is no token to paste and nothing to configure. The server authenticates
over OAuth, so connecting is a sign-in.

## First time

1. Ask the user to run `/mcp` in Claude Code.
2. They pick **esoul** and choose to authenticate. A browser opens.
3. They sign in to ExternalSoul and approve the request. The consent screen
   names what is being granted: every project and workspace on their account.
4. Claude Code stores the token in the OS keychain and refreshes it on its own.

Once connected, `list_workspaces` should return their workspaces.

Never ask the user to paste an access token into the chat.

## What the connection reaches

Everything they own — all their projects and workspaces — because this is
their own account, not a shared slice. There is no per-workspace permission to
set up.

## Troubleshooting

| Symptom | Meaning | Fix |
|---|---|---|
| Tools missing entirely | not connected yet | `/mcp` → esoul → authenticate |
| `unauthorized` on a call | token expired and refresh failed | `/mcp` → esoul → re-authenticate |
| `insufficient_scope` | connected with a narrowly-scoped access token rather than OAuth | re-authenticate through `/mcp` |
| Sign-in succeeds, no workspaces | the account has no projects yet | create one at externalsoul.com, then retry |

## Finding capabilities

The connection exposes a small set of general tools, not one tool per feature.
Anything an app can do is reached through its own app tools, so if a capability
seems missing — email, calendar, contacts, campaigns, sites, drawings, agents —
do not tell the user it cannot be done. Instead:

1. `list_workspaces` to see the apps that exist (or `search_workspace` to find
   one by content);
2. `get_app_tools` on the app, with `names_only: true` first if it is large;
3. `call_app_tool` to invoke the one you need.

If no suitable app exists, `create_app` makes one, and `create_workspace` makes
somewhere to put it.
