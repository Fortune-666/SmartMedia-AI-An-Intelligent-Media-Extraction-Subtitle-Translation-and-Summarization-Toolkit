# Code Review Record

|                             |                                                                                                                                                                                                                                                                 |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Date**              | 2026-11-19                                                                                                                                                                                                                                                      |
| **Reviewer (pass 1)** | Claude Code (generative AI assistant)                                                                                                                                                                                                                           |
| **Human approval**    | _pending_ - see the sign-off table at the end. By our rule C7 (`specification.md`) AI-generated changes are reviewed, modified if needed, and tested by a team member before they are merged.                                                               |
| **Method**            | Change-focused review in the style of Lecture 10 (modern code review): read the code, form a hypothesis, **reproduce it with a small script before touching anything**, fix, add a regression test that fails on the old code and passes on the new code. |
| **Baseline**          | commit `6febbb3` (105 tests passing)                                                                                                                                                                                                                          |
| **Result**            | 3 defects fixed, 2 findings left open, 5 new tests, 14 docstrings added, status tables synchronised                                                                                                                                                             |

## 1. Scope

Read in full: `ai_engine.py`, `cli_main.py`, `config.py`, `downloader.py`, `media_processor.py`, `pipeline.py`, `subtitle_generator.py`, `summarizer.py`, `utils.py`, plus the test files that exercise them.

**Not reviewed line by line:** `gui_app.py` (540 lines). It was checked for docstrings and for the one earlier crash (F0), and it is covered by 19 tests, but a human reviewer should read it.

## 2. Findings 

| ID | Severity             | Finding                                                                                                                                                                                                                                                           | Evidence (reproduced before the fix)                                       | Status                                                                                                   |
| -- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| F0 | High                 | GUI crashed at start-up: `self.previews` was used but the `ttk.Notebook` was never created. Mock-only tests never built the real window.                                                                                                                      | `AttributeError: 'SmartMediaApp' object has no attribute 'previews'`     | **Fixed** earlier (commit `c9c88d5`); regression test `test_gui_builds_full_widget_tree` added |
| F1 | Medium               | Chinese transcripts were never split into sentences, because the splitter required whitespace after the full stop and Chinese text has none. The "summary" was the whole text and "main points" had one entry. Affects FR-22 and FR-24 for Chinese audio (FR-13). | 5 Chinese sentences -> 1 sentence found; `extract_summary(text) == text` | **Fixed** in `summarizer.py`                                                                     |
| F2 | Medium (performance) | Long audio is split into chunks, and the Whisper model was reloaded for every chunk.                                                                                                                                                                              | 3 chunks -> 3 calls of `load_model`                                      | **Fixed** in `ai_engine.py` (model cached per model size)                                        |
| F3 | Low                  | When `ffprobe` printed `N/A`, `get_audio_duration` leaked a bare `ValueError`. The CLI then reported "Unexpected error" instead of the intended audio-extraction message.                                                                                 | `float("N/A")` raised `ValueError`, not `AudioExtractionError`       | **Fixed** in `media_processor.py`                                                                |
| F4 | Low                  | A non-numeric environment variable (e.g. `MAX_CONCURRENT_DOWNLOADS=abc`) crashes `import config` with a raw `ValueError`.                                                                                                                                   | exit code 1 at import time                                                 | **Open** - not fixed, low risk                                                                     |
| F5 | Medium               | Chinese keywords are single characters (`天`, `我`, `们`), because the tokenizer treats each Chinese character as a word. Keyword quality for Chinese is poor.                                                                                              | `extract_keywords(chinese_text)` returns single characters               | **Open** - needs a word segmenter such as `jieba`; out of scope for the course project           |

Known gap that is not a code defect: the API-timeout failure category in FR-39 has no dedicated test (8 of the 9 listed categories are tested).

## 3. Fixes and regression tests

All five tests are in `tests/test_review_fixes.py`.

| Finding    | Regression test                                                | On the old code | On the new code                            |
| ---------- | -------------------------------------------------------------- | --------------- | ------------------------------------------ |
| F1         | `test_chinese_text_is_split_into_sentences`                  | fails           | passes                                     |
| F1         | `test_chinese_summary_is_shorter_than_the_whole_text`        | fails           | passes                                     |
| F1 (guard) | `test_english_sentence_splitting_is_unchanged`               | passes          | passes (English behaviour must not change) |
| F2         | `test_whisper_model_is_loaded_once_for_all_chunks`           | fails           | passes                                     |
| F3         | `test_get_audio_duration_unusable_output_raises_clear_error` | fails           | passes                                     |

Result on the old code: **4 failed, 1 passed**. Result on the fixed code: **5 passed**.

### Review of the fix itself (a lesson)

The first version of the F2 fix made the suite go from 105 passed to **1 failed, 109 passed** and five times slower. The model cache is global to the process, and `test_integration.py` swaps in different mock Whisper models in different tests: a mock cached by one test was returned in the next, so the pipeline ran on to the real translation stage. The fix was not in the production code but in the tests: `tests/conftest.py` now clears the cache around every test. After that the suite is stable (110 passed in 0.45 s, three runs in a row).

## 4. Documentation review

| Item                                            | Before                                                                  | After                                                                                                                                                                              |
| ----------------------------------------------- | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Public functions and classes with a docstring   | 25 / 65 (38%)                                                           | 39 / 65 (60%); `pipeline.run_pipeline`, `PipelineOptions`, `cli_main.main`, the GUI worker classes and others now document their contract and the requirement they implement |
| `roadmap.md` progress table                   | Steps 0-11 still "not started"                                          | Steps 0-13 "done", steps 14-17 "not started"                                                                                                                                       |
| `specification.md` Appendix A and section 5.3 | 40 of 41 rows "To be implemented"; 8 rows named tests that do not exist | 37 rows "Implemented", 4 extension rows "Not implemented"; every cited test was checked to exist                                                                                   |
| `README.md` development progress              | Listed only steps 0-3 and 12-13                                         | Matches the roadmap; gives the test count and coverage                                                                                                                             |

Not done: the README and specification have no English-only version of the GUI text, and `gui_app.py` still has 18 public methods without a docstring (mostly event handlers).

## 5. Numbers after the review (2026-11-19)

- `pytest tests`: **110 passed** (105 before), 15 test files, 0.45 s
- `coverage.py`: **81%** overall (80% before); `ai_engine` 95%, `media_processor` 89%, `gui_app` 68%, `cli_main` 72%
- Nothing is committed yet. Changed files: `ai_engine.py`, `media_processor.py`, `summarizer.py`, `pipeline.py`, `cli_main.py`, `gui_app.py`, `utils.py`, `tests/conftest.py`, `tests/test_review_fixes.py`, `tests/test_gui.py`, `roadmap.md`, `specification.md`, `specification (中文版).md`, `README.md`, `CODE_REVIEW.md`.

## 6. Human sign-off (to be completed by the team)

The AI-assisted pass above found and fixed the issues. A team member should read the diff (`git diff`) and record the decision here before merging.

| Reviewer | Date | Decision (approve / change requested) | Comments |
| -------- | ---- | ------------------------------------- | -------- |
|          |      |                                       |          |
|          |      |                                       |          |
