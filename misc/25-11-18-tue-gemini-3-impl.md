## Gemini 3 Integration Notes (2025-11-18)

### Probing the API
- Script: `scripts/25-11-18-tue-gemini3-probe.py` (uv + requests). It logs every request/response so we can diff payloads vs. docs.
- Payload shape confirmed:
  - `tools:[{"functionDeclarations":[...]}]`
  - `toolConfig.functionCallingConfig.mode` controls AUTO/ANY.
  - `generationConfig.thinkingConfig.{thinkingLevel,includeThoughts}` works (model emits `thought` + `thoughtSignature` parts).
  - Function calls arrive inside `candidate.content.parts[*].functionCall`; no separate `functionCalls` array observed.
- Multimodal tool results accepted when we send `role:"user"` message containing:
  1. A `functionResponse` part.
  2. Optional `text` part describing the attachment.
  3. An `inlineData` part with `mimeType`, `data`, `displayName`.

### Wiring into `personalbot.py`
- Model selector now supports `-m gemini`, using session namespace `personalbot03`.
- Histories under GEMINI sessions are stored exactly as wire-format `{"role": ..., "parts": [...]}` entries; no duplicate `content` arrays.
- `gemini_call` POSTs directly to `https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-preview:generateContent` with:
  - `contents = history`
  - `systemInstruction.parts[0].text = assemble_system_prompt()`
  - Single shared `python_exec` tool declaration.
- `gemini_run_turn` loop mirrors Anthropic/OpenAI structure:
  - Append every assistant response verbatim (so `thought_signature` survives).
  - Detect function calls by scanning `content.parts`.
  - Execute each python snippet via existing `python_exec`, build a sequence of response parts (`functionResponse`, then alternating text/image parts when attachments exist), append as a user turn, and continue until no calls remain.
- `gemini_construct_function_response` converts `python_exec` results to the new part list, emitting `image path` text + `inlineData` blocks for each attachment so Gemini can "see" the screenshot just like OpenAI/Anthropic.
- `gemini_dsp_write` streams reasoning/tool/text output into the console. IDs are deterministic (`{responseId}-function-call-{index}` etc.) since the API doesn’t supply call IDs.
- Validation: `gemini_validate_history` now simply enforces “every entry has parts” and “at least one user text part,” which is enough to reject OpenAI/Anthropic session JSON before we replay it.
- Turn counting: `calc_turn_number` now distinguishes fake user turns via dedicated helpers (Anthropic tool results vs. Gemini functionResponse-only turns), keeping numbering consistent across providers.

### Misc decisions
- No service-tier / future-proof knobs; we keep the code minimal and match the API exactly (no extra abstractions such as `gemini_history_to_contents`).
- `Helpers.check_expected_env` now checks `GEMINI_API_KEY` so missing keys are surfaced up front.
- Image display names reuse the real filesystem path, which is the same convention we print in the surrounding text part.
- Deep copies were intentionally removed in the Gemini codepath; history entries are already the exact payload we POST, so copying only added overhead.

### Known non-issues
- Probe confirmed that response `functionCall` objects lack an `id`, so we fabricate call IDs only for DSP logging. The API does not require them in `functionResponse`.
- The documented `response.functionCalls` array doesn’t appear in the REST payloads we receive. If Google introduces it later, we’ll re-add handling, but today everything is driven by the parts list.
