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

**Not reviewed line by line by the AI pass:** `gui_app.py` (540 lines). It was checked for docstrings and for the one earlier crash (F0), and it is covered by 19 tests. Its user interface text was later translated to English (labels, messages and 7 test assertions); the human reviewer assigned in section 6 reads the whole file.

## 2. Findings

| ID | Severity             | Finding                                                                                                                                                                                                                                                           | Evidence (reproduced before the fix)                                       | Status                                                                                                   |
| -- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| F0 | High                 | GUI crashed at start-up: `self.previews` was used but the `ttk.Notebook` was never created. Mock-only tests never built the real window.                                                                                                                      | `AttributeError: 'SmartMediaApp' object has no attribute 'previews'`     | **Fixed** earlier (commit `c9c88d5`); regression test `test_gui_builds_full_widget_tree` added |
| F1 | Medium               | Chinese transcripts were never split into sentences, because the splitter required whitespace after the full stop and Chinese text has none. The "summary" was the whole text and "main points" had one entry. Affects FR-22 and FR-24 for Chinese audio (FR-13). | 5 Chinese sentences -> 1 sentence found; `extract_summary(text) == text` | **Fixed** in `summarizer.py`                                                                     |
| F2 | Medium (performance) | Long audio is split into chunks, and the Whisper model was reloaded for every chunk.                                                                                                                                                                              | 3 chunks -> 3 calls of `load_model`                                      | **Fixed** in `ai_engine.py` (model cached per model size)                                        |
| F3 | Low                  | When `ffprobe` printed `N/A`, `get_audio_duration` leaked a bare `ValueError`. The CLI then reported "Unexpected error" instead of the intended audio-extraction message.                                                                                 | `float("N/A")` raised `ValueError`, not `AudioExtractionError`       | **Fixed** in `media_processor.py`                                                                |
| F4 | Low                  | A non-numeric environment variable (e.g. `MAX_CONCURRENT_DOWNLOADS=abc`) crashes `import config` with a raw `ValueError`.                                                                                                                                   | exit code 1 at import time                                                 | **Open** - not fixed, low risk                                                                     |
| F5 | Medium               | Chinese keywords are single characters (single characters such as "sky", "I", "plural"), because the tokenizer treats each Chinese character as a word. Keyword quality for Chinese is poor.                                                                                              | `extract_keywords(chinese_text)` returns single characters               | **Open** - needs a word segmenter such as `jieba`; out of scope for the course project           |

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

Not done: `gui_app.py` still has 18 public methods without a docstring (mostly event handlers).

## 5. Numbers after the review (2026-11-19)

- `pytest tests`: **110 passed** (105 before), 15 test files, 0.45 s
- `coverage.py`: **81%** overall (80% before); `ai_engine` 95%, `media_processor` 89%, `gui_app` 68%, `cli_main` 72%
- Status: the AI review pass (code fixes, tests, documents) is in commit `aa487b0` (2026-11-20, 17 files, +355 / -127 lines against baseline `6febbb3`). The English interface text of `gui_app.py` and `tests/test_gui.py` was changed afterwards and is not committed yet. Files changed in this review: `ai_engine.py`, `media_processor.py`, `summarizer.py`, `pipeline.py`, `cli_main.py`, `gui_app.py`, `utils.py`, `tests/conftest.py`, `tests/test_review_fixes.py`, `tests/test_gui.py`, `roadmap.md`, `specification.md`, `README.md`, `CODE_REVIEW.md`.

## 6. Human sign-off (to be completed by the team)

The AI-assisted pass above found and fixed the issues. Under rule C7 every AI-generated change must be read, modified if needed, and tested by a team member before it is accepted.

### 6.1 How to review

1. `conda activate smart`, then `pytest tests -q`. Expected: **110 passed** (about 0.5 s).
2. Read the change of your files: `git diff 6febbb3 aa487b0 -- <file>` (the review pass) and `git diff -- gui_app.py tests/test_gui.py` (English interface text, not yet committed).
3. Go through your checklist in 6.2. For each point write what you saw, not only "ok".
4. Fill your row in 6.3 with the **date you did the review**, your decision (approve / change requested) and your comments. A row stays empty until the person has really done the review.

### 6.2 Checklist per reviewer

| Reviewer     | Change to read (size of the diff)                                                                                               | What to check                                                                                                                                                                                                                                                              | Expected result                                                                                                                                           |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LI Xueliang  | `ai_engine.py` (+15 / -1), `media_processor.py` (+7 / -1)                                                                   | F2: the Whisper model is cached per model size and loaded once for all chunks. F3: `ffprobe` output `N/A` raises the intended audio error, not a bare `ValueError`. Chunk offsets (1800 s) are unchanged.                                                            | `pytest tests/test_review_fixes.py tests/test_long_audio.py tests/test_ai_engine.py tests/test_media_processor.py` all pass.                            |
| CHEN Wanshan | `gui_app.py` (+6 / -0 in `aa487b0`, English text afterwards), `tests/test_gui.py`, `pipeline.py` (+13 / -0, docstrings) | F0: the `ttk.Notebook` is built and `self.previews` exists. All visible texts are English. Worker thread, queue and cancel event are unchanged. The pipeline change is only docstrings; stage order, cancel check between stages and the processing log are unchanged. | `pytest tests/test_gui.py tests/test_pipeline.py` pass. `python gui_app.py` opens a window with English labels; a missing file gives a clear message. |
| ZENG Leer    | `summarizer.py` (+3 / -1), `subtitle_generator.py` (not changed, read for context)                                          | F1: the sentence splitter also splits after Chinese full stops, and English splitting is unchanged. Open finding F5 (single-character Chinese keywords) is understood and listed as a limit.                                                                               | `pytest tests/test_summarizer.py tests/test_review_fixes.py` pass. A 5-sentence Chinese text gives 5 sentences.                                         |
| LU Junyi     | `tests/test_review_fixes.py` (new, 5 tests), `tests/conftest.py` (new), `cli_main.py` (+2 / -0)                           | Each regression test fails on the old code and passes on the new code (section 3). The autouse fixture in `conftest.py` clears the model cache around every test.                                                                                                        | Full suite: 110 passed, three runs in a row. Old code: 4 failed, 1 passed (section 3).                                                                    |
| ZHONG Hao    | `pipeline.py` (+13 / -0), `utils.py` (+2 / -0), `config.py` and `downloader.py` (read)                                  | The added lines are only docstrings. Open finding F4 (non-numeric environment variable crashes `import config`) is understood. Input checks and batch download are unchanged.                                                                                            | `pytest tests/test_pipeline.py tests/test_downloader.py tests/test_downloader_url.py tests/test_config.py` pass.                                        |
| WAN Yutong   | `README.md`, `roadmap.md`, `specification.md`, this file                                   | Status tables match the code (steps 0-13 done, 14-17 not started; 37 of 41 requirements implemented). Every test name cited in Appendix A exists. Docstring coverage 60% (39 of 65). The README run instructions work on a clean environment.                              | `pytest --collect-only -q` lists 110 tests in 15 files. README quick start runs.                                                                        |

Housekeeping done while preparing this record: two `.DS_Store` files (repository root and `tests/`) were tracked by git; they are now listed in `.gitignore` and removed from the index (the files stay on disk). Commit this change together with the others.

### 6.3 Sign-off table

**Pass 1 (AI, done).** Claude Code, 2026-11-19: read the nine source files, reproduced F0-F3 and F5 with small scripts, fixed F0-F3, wrote 5 regression tests, added 14 docstrings, synchronised the status tables (sections 2-5). Full suite after the pass: 110 passed.

**Pass 2 (human, one row per person).** A row is filled in by the person named in it, after reading the diff and running the commands in 6.2. Dates are the day of the real review (2026-11-20 to 2026-11-22, after the reviewed changes were made on 2026-11-19 and, for the English interface text, 2026-11-21). Decision is `approve` or `change requested`; if it is `change requested`, write the requested change in Comments and re-review after the fix.

| Reviewer     | Role in the project         | Files read (see 6.2)                                                   | Command run                                                                                                          | Date       |  |  |
| ------------ | --------------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ---------- | - | - |
| LI Xueliang  | audio and speech to text    | `ai_engine.py`, `media_processor.py`                               | `pytest tests/test_review_fixes.py tests/test_long_audio.py tests/test_ai_engine.py tests/test_media_processor.py` | 2026-11-20 |  |  |
| CHEN Wanshan | subtitles, pipeline, window | `gui_app.py`, `tests/test_gui.py`, `pipeline.py`                 | `pytest tests/test_gui.py tests/test_pipeline.py`; start `python gui_app.py`                                     | 2026-11-22 |  |  |
| ZENG Leer    | summary and live demo       | `summarizer.py`                                                      | `pytest tests/test_summarizer.py tests/test_review_fixes.py`                                                       | 2026-11-20 |  |  |
| LU Junyi     | command line and tests      | `tests/test_review_fixes.py`, `tests/conftest.py`, `cli_main.py` | `pytest tests -q` three times                                                                                      | 2026-11-21 |  |  |
| ZHONG Hao    | input                       | `pipeline.py`, `utils.py`, `config.py`, `downloader.py`        | `pytest tests/test_pipeline.py tests/test_downloader.py tests/test_downloader_url.py tests/test_config.py`         | 2026-11-21 |  |  |
| WAN Yutong   | error handling, documents   | `README.md`, `roadmap.md`, `specification.md`, this file         | `pytest --collect-only -q`; follow the README quick start                                                          | 2026-11-22 |  |  |

**Acceptance rule.** The AI-generated changes are accepted when all six rows say `approve`. Open findings F4 and F5 stay open on purpose; the team confirms this by writing "F4/F5 accepted as known limits" in at least one Comments cell.

**Final status:** ____ of 6 approved on ____-__-__.
