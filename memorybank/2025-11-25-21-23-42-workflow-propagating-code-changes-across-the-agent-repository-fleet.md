---
filename: 2025-11-25-21-23-42-workflow-propagating-code-changes-across-the-agent-repository-fleet
timestamp: "2025-11-25T21:23:42.824917+00:00"
title: "Workflow: Propagating Code Changes Across the Agent Repository Fleet"
---

This memory outlines the process of taking a feature update or patch from a reference repository (usually `personalbot` or `pb`) and propagating it semantically across the "fleet" of agent repositories.

## The "Fleet"

The user maintains several repositories that share a common architecture (Python-based agent, `uv` for dependency management, `justfile` for task automation).

**Common Repositories:**

- `~/git/pb` (Personal Bot): Often the source of truth or first implementer.
- `~/git/tincan`: Standard structure.
- `~/git/ridwell`: Standard structure.
- `~/git/upwork`: **Non-standard structure.** The `justfile` is at the root, but the agent code resides in `bot0/`.
- `~/git/nira`: Standard structure.

## The Workflow

### 1. Analyze the Reference

First, examine the changes in the source repo (usually via `git show` or reading the file).

- **Understand the Intent:** Don't just look at line numbers. Understand _what_ the feature does (e.g., "Adding Opus model support").
- **Identify Components:** Usually involves changes to:
  - The Python entry point (e.g., `personalbot.py`): Argument parsing, global variables, model configuration.
  - The `justfile`: New commands (`bot-opus`), updated aliases (`alias bo := bot-opus`).

### 2. Locate Targets & Variations

For each target repo, locate the equivalent files. They will not have the same names.

| Repo      | Automation File | Script Location        | Script Name         |
| :-------- | :-------------- | :--------------------- | :------------------ |
| `pb`      | `justfile`      | `./`                   | `personalbot.py`    |
| `tincan`  | `justfile`      | `./`                   | `tincanbot.py`      |
| `ridwell` | `justfile`      | `./`                   | `ridwellbot.py`     |
| `nira`    | `justfile`      | `./`                   | `nirabot.py`        |
| `upwork`  | `justfile`      | `./` (calls `cd bot0`) | `bot0/upworkbot.py` |

### 3. Verification Before Action

**Always read the target files first.**

- **Check for existing implementation:** The feature might already be there (e.g., `nira` already had Opus support).
- **Check for structural drift:** The `get_model_interface` function might look slightly different in older repos.

### 4. Semantic Application

Apply the logic, not the literal text.

- **Namespaces:** Update session namespaces (e.g., copy `personalbot02` -> change to `tincanbot02`).
- **Globals:** Watch out for `global` keywords. In some versions, `global anthropic_model` might be at the top of the block; in others, inside specific `if/elif` blocks. Consolidate if necessary to match the reference pattern.
- **Paths:** In `upwork`, `justfile` commands need `cd bot0` before running the python script.

### 5. Case Study: Adding Opus Support (Nov 2025)

**The Task:** Add `opus` to `argparse` and create `bot-opus` shortcuts.

**Changes made:**

- **Python:** Added `"opus"` to `choices`. Added `elif args.model == "opus":` block. Moved `global anthropic_model` to valid scope.
- **Justfile:** Renamed generic `bot2/bot3` to specific `bot-sonnet/bot-haiku`. Added `bot-opus`. Updated aliases (`bs`, `bh`, `bo`).

**Specific Observations:**

- **Upwork:** The `justfile` commands required `set -euxo pipefail` and `cd bot0` block replacements.
- **Nira:** Required no changes as it was already up to date.
