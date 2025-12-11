---
filename: 2025-12-11-01-13-16-bot-fleet-management-propagating-diffs-across-similar-bots
timestamp: "2025-12-11T01:13:16.003618+00:00"
title: Bot Fleet Management - Propagating Diffs Across Similar Bots
---

## Overview

We manage a fleet of bots that are structured in a very similar way. When changes are made to one bot, they often need to be propagated to the others.

## Bot File Paths

| Bot          | File Path                        |
| ------------ | -------------------------------- |
| Personal Bot | `~/git/pb/personalbot.py`        |
| Nira Bot     | `~/git/nira/nirabot.py`          |
| TinCan Bot   | `~/git/tincan/tincanbot.py`      |
| Upwork Bot   | `~/git/upwork/bot0/upworkbot.py` |
| Ridwell Bot  | `~/git/ridwell/ridwellbot.py`    |

## Propagation Workflow

1. **Identify the source diff** - Look at recent commits to the source bot file:

   ```bash
   git log -N --oneline -- botfile.py
   git diff COMMIT1^ COMMITN -- botfile.py
   ```

2. **Check which bots need updating** - Look for key patterns that indicate whether a bot has the change:

   ```bash
   grep -l 'pattern' ~/git/*/bot*.py
   ```

3. **Apply changes** - Use string replacement in Python to apply the same transformations to each target file. The bots share similar structure, particularly in:
   - `dsp_console_print()` function - handles display/streaming events
   - `python_exec()` function - executes code
   - Event handling patterns (reasoning-delta, text-delta, tool-input-delta, etc.)

## Example: Display Buffering Change (2025-12-10)

Applied changes from `personalbot.py` commits `e3785b2` and `7ca0c58` to the other bots:

- Added `_dsp_buffers` dictionary for buffering streaming content
- Added `.strip()` calls to `code`, `stdout`, `stderr`
- Updated event handlers to buffer content then render with `Syntax(..., "markdown")`
- Simplified OpenAI streaming event handlers
- Commented out tool-input display

Files updated: `tincanbot.py`, `upworkbot.py`, `ridwellbot.py` (nirabot.py was already updated)
