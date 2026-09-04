---
name: repo-view
description: >-
  Opens a local read-only repository browser with a file tree, syntax highlighting, media preview,
  path filters, focus zones, and Git workspace/branch/commit diffs. Use when the user asks to inspect
  a repository visually, open Repo Viewer, browse a source tree, or review a session diff. Do not use
  it as a project-management dashboard or an editor.
---

# Repo Viewer

Use the bundled zero-dependency Python server to inspect a local source directory. It binds only to `127.0.0.1` and does not modify repository files.

## Start

```bash
python3 serve.py /path/to/repository 8770
python3 serve.py /path/to/repository 8770 --focus src/prompts --focus tests
python3 serve.py /path/to/skill-library 8770 --follow-symlinks
```

Open `http://127.0.0.1:8770`. To enter Session Diff directly, open `http://127.0.0.1:8770/?mode=session`.

Every file click reads the current disk contents. Text files larger than 1 MB are truncated with a notice; non-media binary files are not previewed. Heavy generated directories are ignored, and trees above 20,000 files are rejected.

## Session Diff

The header switches between the full repository and Session Diff. Diff entries include:

- workspace changes against `HEAD`;
- the entire branch against its detected base branch;
- each commit on the branch, newest first.

In Session Diff, the tree contains only changed files and opens their diff by default. The viewer interprets a session as the current Git branch plus workspace; it does not depend on a product-specific session identifier.

## Focus zones

Pin frequently used subdirectories as sidebar chips without hiding the full repository tree:

- Repeat `--focus relative/path` at startup.
- Use `?focus=path-a,path-b` in the URL.
- Pin folders interactively from the tree.
- Use `?zone=relative/path` for a deep link without persisting a pin.

Focus zones apply only to the full-tree view. Pins are stored per absolute repository path in browser local storage.

## Symlinks and boundaries

Directory symlinks are skipped by default. `--follow-symlinks` enables them with real-path cycle protection. Requests still reject absolute paths and `..` path traversal.

Repo Viewer is read-only. Use repository tools for edits and tests, and use a project-management Skill for mission state, resource approval, delegation, or acceptance.
