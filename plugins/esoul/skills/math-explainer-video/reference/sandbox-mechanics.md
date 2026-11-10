# Sandbox mechanics — how the code sandbox actually behaves

> Read this when running anything in the `e2b_sandbox` app that takes longer than a minute,
> installing packages, moving files across the workspace boundary, or diagnosing "my render died
> halfway". `SKILL.md` says what to build; this is how the machine behaves underneath it.
> Everything here is driven as `call_app_tool(workspace_id, sandbox_app_id, tool_name, args)`.

## THE MACHINE (get the mental model right first)

- **One Jupyter kernel**, shared by every `run_code` call. Variables, imports, `os.environ` and
  `sys.path` persist from call to call — you are continuing one session, not running isolated
  scripts.
- **Tabs are CELLS, not files.** Tab code lives in app state; editing a tab writes NOTHING to the
  sandbox disk. The filesystem only changes when code runs.
- **The sandbox is a THROWAWAY VM.** `/home/user`, pip installs and kernel state all vanish
  whenever it is replaced (see LIFECYCLE) — the workspace is the only durable store. Anything you
  care about: save it the MOMENT it exists, never deferred to the end. That does NOT mean one call
  per file — `save_files_to_workspace([{filePath}, …])` saves each poll's newly-finished files in
  ONE call (and returns each `durationSeconds`), which keeps the "save as you go" durability without
  the per-file round-trip tax.
- `os.environ` carries `ESOUL_TOKEN` + `ESOUL_BASE_URL` — a short-lived scoped API session,
  refreshed on each run entry, so code inside the sandbox can call the ExternalSoul API directly.

## GETTING SET UP

- `get_app_tools` on the sandbox app to learn its exact per-app tool names (suffixed `_<base>`).
  Never guess them.
- **Check the environment before assuming it**: run one cell importing what you need. Assume
  little beyond `requests`, `numpy`, `matplotlib` — manim is NOT preinstalled (~26s to add).
- **You have root.** Debian 12, passwordless `sudo`, working apt (verified 2026-08-10). System
  packages are installable, LaTeX included:
  `sudo apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-extra dvisvgm`
  → ~56s, 255MB, and `MathTex` renders. "There is no LaTeX" describes the cold image, not a limit.
  Note the kernel runs `/usr/local/bin/python3.13`, which is NOT the same interpreter as a bare
  `pip` in a shell command — install with `sys.executable -m pip` or `!pip` inside a cell, or you
  will install into one Python and import from another.
- Install with `!pip install X` inside a `run_code` cell. Each cell has ~60 SECONDS total, so
  install ONE heavy package per cell (manim, torch and friends each get their own). Installs
  persist across calls but die with the sandbox.

## THE 60-SECOND RULE (why cells die)

Every `run_code` call has roughly one minute end to end. A cell that blocks longer does not merely
error: on timeout the platform may EVICT the sandbox, create a FRESH one and RE-RUN your cell
there. So **a heavy cell can execute TWICE**, and everything on the old box (files, installs,
variables) is gone. Two consequences:

- Keep every interactive cell well under a minute. Chunk work; precompute; print progress.
- Anything longer runs **DETACHED** — a background process the cell only LAUNCHES:

```python
subprocess.Popen(['bash','-lc','setsid nohup /home/user/r.sh > /home/user/r.log 2>&1 < /dev/null &'],
                 start_new_session=True)
```

In `r.sh`: `set -euo pipefail` (else a failed job still writes its success marker — a green light
over a red run); append each finished output's name to a PROGRESS file; SKIP anything already on
disk so a relaunch RESUMES instead of redoing; write final artifacts directly under `/home/user`.

Then poll with `list_files` — it reads the disk and needs no kernel, so it works while the job
runs. Between polls you can run other short cells; the kernel is free.

## LIFECYCLE — the sandbox will restart on you; plan for it

- Lifetime is ~30 minutes, ABSOLUTE, from the last `run_code` entry. Polling `list_files` extends
  NOTHING; only real `run_code` calls reset the clock.
- A sandbox saturated by heavy work answers the platform slowly and can get silently replaced by
  an EMPTY one — this is the mechanism behind "/home/user wiped every 15–30 minutes".
- After any restart sign (imports gone, files gone, unfamiliar sandbox id): reinstall, copy the
  inputs in again (FILES IN), re-run only what is MISSING from the workspace — which is why you
  saved as you went.
- There is no restart tool: `start_sandbox` refuses while a sandbox is alive; a fresh box comes
  from letting the old one expire.
- **Done → `delete_sandbox`.** When the film is delivered and every output is saved, delete the
  sandbox app: it stops every sandbox the app ever started. An app YOU created (over MCP, or an
  agent in-app) goes at once; one the person added is theirs — the call asks them (Delete / Keep)
  and only their tap deletes it. Unsure the job is over? Ask, don't delete.
- A sandbox belongs to its app: the app's tools reach only its own sandbox. Never carry a sandbox
  id over from another app or a log.
- **A recycle loses the TOOLCHAIN, not just files** — manim and LaTeX vanish too, and the failure
  surfaces as `FAIL <scene>` with a log reading `No module named manim`, which looks EXACTLY like
  a code bug. Defend against the misdiagnosis:
  - Save `setup.sh` (the pip + apt install script) to the WORKSPACE, not just `/home/user`, so a
    recycle can't take it.
  - **Assert the toolchain before every render batch**: one cell that does `import manim, av` and
    `shutil.which("latex")` and PRINTS the result. A green line here means a later `FAIL` is a
    real code bug; its absence means reinstall, not debug.
  - Re-save the SOURCE tarball after every edit round, not once. Saving the scene files pre-fixes
    and then hitting a recycle means re-applying every patch by hand.

## FILES IN — workspace → sandbox

- **THE COPY RULE**: a workspace with FEWER THAN 10 files is copied into a new sandbox whole, to
  `/home/user/<name>` (flat, exact name). A bigger one is NOT: only the files your code NAMES —
  `/home/user/<name>`, a path ending `/<name>`, or a quoted `'<name>'` — up to 20, copied before
  each `run_code`. A file listing copies nothing, and code that globs `/home/user/*` sees only
  what was copied in.
- `copy_files_to_sandbox({fileIds|fileNames, destDir?})` copies SEVERAL (≤50) in one call,
  skipping ones already there; `copy_file_to_sandbox({fileId|fileName, destPath?})` copies one to
  an exact path. Both start a sandbox if none is running and return the paths to use.
- Two workspace files with the SAME NAME land on one path (one shadows the other): keep names
  unique, or copy by fileId to a `destPath`.

## FILES OUT — sandbox → workspace

- `save_to_workspace({filePath, saveAs?, overwrite?})` — `filePath` must be under `/home/user`;
  per-file cap ~25MB; a name collision auto-renames (or set `overwrite:true` to replace the
  same-named file, retry-safe). The result ends with `[fileId: ...]` — THAT id is what attachment,
  messaging and file tools take — plus `[durationSeconds: N]` for media. Saving is the only
  durability there is.
- `save_files_to_workspace({files:[{filePath, saveAs?}, …], overwrite?})` — the BATCH form: one
  call, results in caller order, each with its `[fileId]` + `[durationSeconds]`. Prefer it whenever
  more than one file is ready.
- `list_workspace_files()` / `delete_workspace_files({fileIds})` — the ids you have, and cleanup of
  stale saves (workspace-scoped; removes them from the file panel live). Between `overwrite:true`
  and delete, filenames stay load-bearing across re-renders.
- **Saves are not downloaded back** (since 2026-08-17 a save is recorded as already in the
  sandbox). Still name outputs per iteration (`out_v2.mp4`): a DIFFERENT workspace file with the
  same name that your code names can land on that path.

## SEEING YOUR OWN OUTPUT (vision over MCP since 2026-08-10)

**An image written under `/home/user` during a run comes back to you as an actual image** — the
storefront returns it as a typed MCP image block, so you SEE it. Plot something,
`plt.savefig('/home/user/check.png')`, and LOOK: this is the verification loop.

The mechanics that shape it:

- **At most 3 images per tool result, downscaled to ≤1280px.** Many frames → ONE contact-sheet
  PNG, never nine separate files (`SKILL.md` step 5 has the snippet).
- The capture is **NOT recursive**: a file written in a subdirectory (`media/videos/...`) is
  not captured — `look_at_sandbox_files({paths})` sees it (up to 6 files, any path under
  `/home/user`, images as pictures, small text as text, no code run). Prefer it for checking
  outputs: it never needs a cell.
- **VIDEOS never come back directly** on any surface. Sample frames into a sheet.
- An image that failed to render/attach shows as `imagesDropped` in the result — say so and fall
  back to the printed-assertion battery; never claim a look you did not get.
- Already-saved workspace images can be re-viewed WITHOUT running code: the storefront's
  `view_image(workspace_id, file)` (find them via `list_files(images_only: true)`).
- Whatever you want the USER to keep must reach the workspace: `save_to_workspace` it and say its
  name.

Eyes AND numbers: the look catches what no assertion anticipates; `verify_frames.py` measures
what a glance cannot (exact frame-fill %, a silent narration beat). Use both on anything that
ships.

## READING RESULTS HONESTLY

- A cell's returned text is stdout plus the final expression. `print()` what you need to see; a
  bare variable on the last line also comes back.
- stderr arriving as literal `[object Object]` is a REAL error with a mangled traceback: re-run
  the code wrapped in try/except with `import traceback; traceback.print_exc()` — the traceback
  then arrives via stdout.
- The app state's "Running: yes" can be a stale flag after a transport failure. Believe the DISK
  (`list_files`, your PROGRESS file), not the flag.

## TOOLS AT A GLANCE (names suffixed `_<base>`)

- `create_tab` / `set_code` / `read_tab_code` / `apply_patch_to_tab({edits:[{find,replace}]})` —
  manage cells; patching beats resending whole code.
- `run_code({tabId?})` — execute the tab's code in the shared kernel.
- `list_files({path?})` — the REAL disk listing. `list_sandbox_files` is NOT the disk: it is
  what has been copied in, with fileIds.
- `copy_file_to_sandbox` / `save_to_workspace` / `save_output_to_workspace` — files across the
  boundary; `save_output_to_workspace` saves a produced image by index when you never wrote it to
  disk.
- `copy_files_to_sandbox({fileIds|fileNames, destDir?})` — several files in, one call (≤50).
- `look_at_sandbox_files({paths, maxSide?})` — SEE up to 6 outputs, subfolders included.
- `start_sandbox` — only when dead; refuses while alive. `delete_sandbox` — when the job is done.
- `mount_drive` / `download_drive_file` — Google Drive under `/home/user/drive`.

## THINGS THAT GO WRONG, AND WHAT THEY MEAN

- **A cell died near the minute mark with no error worth reading** — client timeout. Detach the
  work; check whether it ran twice.
- **Everything vanished (imports, files, id changed)** — the sandbox restarted. Reinstall +
  re-copy; what you saved to the workspace survived.
- **`FileNotFoundError` for a workspace file** — it was never copied in (a workspace of 10+ files
  copies only what the code names). `copy_files_to_sandbox`, then run again.
- **An artifact reverted to an older version at run start** — a same-name workspace file your code
  names was copied over it. Rename per iteration.
- **A file you wrote never came back as an image** — it is in a subdirectory.
  `look_at_sandbox_files` it.
- **`[object Object]` in stderr** — wrap in try/except + `traceback.print_exc()` and re-run.
- **pip install times out** — one heavy package per cell, or install detached.
- **`start_sandbox` refuses** — one is alive; just use it, `run_code` wakes it.
- **The same file seems to shadow another** — duplicate workspace filenames. Rename one.
