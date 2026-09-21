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

The server loads a core set of tools and keeps the rest one call away. If a
capability seems missing — email, calendar, contacts, campaigns, sites,
drawings, agents — call `find_tools` before telling the user it cannot be done,
then `tool_help` for the arguments and `run_tool` to invoke it.
