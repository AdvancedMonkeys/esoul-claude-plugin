# Assets — images, films, fonts and PDFs an app ships with

An app's package holds text (the workbench wall: `.ts .tsx .json .css .md .txt .svg`, 512 KB a
file). Its media does not live there and never did — until 2026-09-24 there was no way to give an
app a picture at all; the platform's own homepage kept its films in the platform repository with
a hand-rolled cache-buster. Now an app has an **asset store**: the bytes go to a content-addressed
store the platform runs, the package carries `assets.json` (written FOR you), and the app renders
one immutable, same-origin URL that is identical in the workbench preview, installed, and on a
custom domain. There is nothing to configure and no environment switch to write.

## Put one

Board tool: `put_app_asset {pluginId, name, contentBase64 | sourceUrl}`.
Over MCP (esoul-mcp): `forge_put_asset(plugin_id, name, file= | source_url= | content_base64=)`.
SDK: `wb.put_asset("hero.mp4", file="./hero.mp4")`.

- `name` is the file's name inside the app — `hero.mp4`, `logo.webp`, `brand.woff2`. Allowed:
  `webp png jpg jpeg gif avif svg mp4 webm mp3 m4a woff2 woff pdf json`. Never a script, never a page.
- **`file`** (esoul-mcp / SDK only — it reads the customer's own disk) takes anything up to 64 MB;
  big files stream straight to the store, small ones ride inline. This is the arm for a film.
- **`sourceUrl`** is a public https URL the platform fetches (≤ 64 MB) — a photo on the web, a
  file already in the workspace (`list_files` gives its URL), a render a task produced.
- **`contentBase64`** is for what a model can author itself — an SVG, a tiny PNG — and is capped
  at 3 MB. Do not paste a film through it; the tool says so and names the other arms.

The answer names the URL (`/pa/<pluginId>/<sha256>.<ext>`), says whether the bytes were new or
already stored (the same bytes twice is one object), and confirms `assets.json` was written. The
write is a checkpoint like any other: it appears on the board and `restore_app` can undo it.

## Use it in the app

```tsx
import assets from "./assets.json";
import { assetUrl } from "esoul-sdk";

<video src={assetUrl(assets, "hero.mp4")} poster={assetUrl(assets, "hero.jpg")} playsInline muted loop />
<img src={assetUrl(assets, "logo.webp")} alt="" />
```

`assetUrl` THROWS on a name that is not in the manifest — a missing asset is a bug in the app, and
a blank `<img>` would hide it. `assetUrlOrNull` is for an asset that is genuinely optional. Fonts go
through `@font-face { src: url(...) }` in a `<style>` string built from `assetUrl` (the wall forbids
`next/font`). Never build a `/pa/...` string by hand and never re-derive the sha: the manifest is
the only source, and it is only ever written by the platform.

## Replace, remove, review

- Put a new file under the same name → a new object, a new URL, the manifest entry replaced. The
  old address stays valid (nothing is ever deleted), so an open page never breaks mid-deploy and a
  restore to an earlier checkpoint still renders.
- `remove_app_asset {pluginId, name}` / `forge_remove_asset` drops the entry; the bytes stay.
- Limits: 64 MB per asset, 256 MB per app. Storage is billed to the workspace owner.
- `assets.json` is in the pull request. The reviewer sees names, sizes and hashes — the install
  gate verifies every hash exists in the store before an app can be added, and an app installed
  from its own GitHub repository may carry the real files under `assets/<name>`; the gate uploads
  those (content-addressed) and refuses a file whose hash disagrees with the manifest.

## What this is not

- Not workspace files. A product photo the CUSTOMER uploads, a label file, a render for one
  workspace — those are `WorkspaceFile`s (`data-people-files.md`): per workspace, in the Files
  app, replaceable. Assets are the APP's own chrome: the same in every workspace it is installed in.
- Not a place for HTML or scripts. Every asset is served inert (`nosniff`, a sandboxed CSP).
