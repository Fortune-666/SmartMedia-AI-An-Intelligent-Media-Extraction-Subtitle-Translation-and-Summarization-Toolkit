# SmartMedia-AI Implementation Roadmap

**Document version**: v1.0
**Date written**: 2026-10-12
**Based on**: `specification.md`

This roadmap breaks the 41 functional requirements of the SRS (FR-01 to FR-41) into development steps that can be **completed and accepted one at a time**, instead of asking the team to finish everything at once. The core idea: first get the thinnest end-to-end pipeline working (local file -> audio -> transcript text, without download, translation or GUI), then extend it one capability at a time.

After each step, go back to Appendix A of `specification.md` and change the "Status" column of the matching requirements from "To be implemented" to "Implemented", so that the SRS becomes a live progress board shared by the whole team.

---

## Phase 0 - Scaffold (before any feature)

This is not a feature by itself, but it covers C4, C6, NFR-01, NFR-07 and IFR-06, and everything later depends on it.

| Step | What to do | Requirements | Suggested owner |
|---|---|---|---|
| 0.1 | Set up the repository structure (`main.py`, `cli_main.py`, `downloader.py`, `media_processor.py`, `ai_engine.py`, `subtitle_generator.py`, `summarizer.py`, `config.py`, `utils.py`, `tests/`), `requirements.txt`, and a `.gitignore` that excludes `.env` and configuration files | NFR-01, C6 | Member A |
| 0.2 | `config.py` reads API keys from environment variables / `.env` | IFR-06, C4, NFR-07 | Member A |
| 0.3 | An empty pytest file and a GitHub Actions workflow (it installs the dependencies and runs pytest; even with no test yet, the pipeline must stand from day one) | NFR-09 | Member F |

**Done when**: `pip install -r requirements.txt` succeeds and CI is green on the empty test suite.

---

## Phase 1 - Core pipeline, one "vertical slice" at a time

Each step below must be runnable on its own and committed to git before the next step starts.

### Step 1: Local file in, local file out (no processing yet)

- **Implement**: `downloader.py` accepts a local file path and checks that the file exists and the extension is supported.
- **CLI placeholder**: `python main.py --file <path>` only prints "file accepted" or an error.
- **Requirements**: FR-02, FR-03 (local-file part), FR-04
- **Tests**: `test_import_local_file`, `test_validate_url_and_file_input` (file branch only)
- **Acceptance**: run it on a real video file; run it on a missing file and a file with a wrong extension, which must give a clear error instead of a crash.

### Step 2: FFmpeg audio extraction

- **Implement**: `media_processor.py` extracts the audio of the file from step 1 and converts it to 16 kHz mono WAV.
- **Requirements**: FR-07, FR-08, FR-09
- **Tests**: `test_ffmpeg_audio_extraction`, `test_audio_format_conversion`, `test_audio_converted_to_asr_format`
- **Acceptance**: the generated WAV plays the original audio; `ffprobe` confirms 16 kHz mono.

### Step 3: Speech transcription (first use of AI)

- **Implement**: `ai_engine.py` calls Whisper (or the chosen ASR) on the WAV of step 2 and returns text with timestamps.
- **Requirements**: FR-11, FR-12, FR-13, FR-14, FR-15
- **Tests**: `test_asr_transcription`, `test_transcript_has_timestamps`, `test_transcription_en_zh`, `test_auto_language_detection`, `test_transcription_failure_halts_pipeline` (use a silent or broken audio file)
- **Acceptance**: the transcript roughly matches what is said in the test clip, and the timestamps are reasonable.

> **Milestone checkpoint**: at this point there is a complete (although narrow) pipeline: local video -> audio -> transcript text. Pause here, confirm the architecture is sound, then add more features.

### Step 4: Bilingual subtitles

- **Implement**: `subtitle_generator.py` splits the transcript of step 3 into segments, translates each segment, and writes a bilingual `.srt`.
- **Requirements**: FR-16, FR-17, FR-18
- **Tests**: `test_subtitle_segmentation`, `test_subtitle_translation`, `test_bilingual_srt_output`
- **Acceptance**: open the `.srt` in VLC or a text editor; every subtitle entry has the original line and the translation, and the timing fits.

### Step 5: Summary and keywords

- **Implement**: `summarizer.py` takes the transcript of step 3 and produces a summary, keywords and main points, written to a text file.
- **Requirements**: FR-22, FR-23, FR-24, FR-25
- **Tests**: `test_summary_generation`, `test_keyword_extraction`, `test_main_points_extraction`, `test_summary_output_file`
- **Acceptance**: the summary reads as a fluent paragraph, not garbled text; the keywords match the topic of the clip.

> Steps 4 and 5 depend only on the output of step 3 and are independent of each other, so two people can work on them in parallel. The proposal gives both to Member E, but if time is short they can be split between two people.

### Step 6: `.vtt` export

- **Implement**: in `subtitle_generator.py`, add a `.vtt` output next to `.srt`.
- **Requirements**: FR-19
- **Tests**: `test_vtt_output`
- **Acceptance**: after step 4 this step is easy; it is mainly one more format converter.

### Step 7: URL download (open the input side)

- **Implement**: add yt-dlp support to `downloader.py`, with a download progress display.
- **Requirements**: FR-01, FR-05, FR-03 (URL part)
- **Tests**: `test_download_via_url`, `test_download_progress_indicator`
- **Acceptance**: a valid test URL gives the same downstream pipeline result as a local file.

> **Why is download built after transcription, subtitles and summary instead of first?** Download is the part of the workflow most likely to fail and the least controllable (website compatibility, network, access rights). First build and test steps 2-6 on a local test file, so their development and tests do not depend on the network at all; once `downloader.py` is ready, it plugs in as an input source.

### Step 8: Long-audio splitting

- **Implement**: split audio longer than a configurable duration threshold, then merge the timelines of the transcription results again.
- **Requirements**: FR-10
- **Tests**: `test_audio_split_and_timeline_merge`
- **Acceptance**: run a long test file (for example over one hour); the transcript timestamps stay continuous and in the right order at the joins.

---

## Phase 2 - Harden and package the core pipeline

### Step 9: Error handling for the whole flow

- Go back to steps 1-8 and add the full set of failure handling listed in the SRS (invalid link, unsupported format, download failure, network interruption, FFmpeg error, missing dependency, API timeout, invalid API key, empty or poor-quality audio).
- Add the processing log.
- **Requirements**: FR-39, FR-40
- **Tests**: `test_error_handling_all_categories` (mock every failure one by one), `test_processing_log_written`
- **Why now and not earlier**: error handling has nothing to wrap before the stages exist. Adding it once all stages are in place is more consistent and less likely to miss something than adding a little at every step.

### Step 10: Formal CLI

- Replace the placeholder CLI of step 1 with a proper `argparse`/Click implementation: `--url`/`--file`, `--source`, `--target`, output format choice, progress printing for every stage, output paths printed on success, and a non-zero exit code on failure.
- **Requirements**: FR-28, FR-29, FR-30, FR-31, FR-32
- **Tests**: `test_cli_argument_parsing`, `test_cli_format_selection`, `test_cli_prints_output_paths`, `test_cli_error_exit_code`

### Step 11: Complete test coverage and CI gate

- Complete the unit tests of every module (per NFR-06, all external services are mocked; CI makes no real network request or API call).
- Add the end-to-end integration test (download module -> processing module -> AI engine -> subtitle module -> summary module) on a real sample video.
- Confirm that GitHub Actions runs the whole test suite and reports failures.
- **Requirements**: NFR-06, NFR-09, and the integration tests of SRS section 5.2

> **Milestone: Core scope complete.** All of the above matches items 1-4 of the SRS section 5.4 acceptance criteria. At this point there is a CLI tool that runs end to end and satisfies every Core requirement of the SRS, whether or not any extension is finished.

---

## Phase 3 - Extensions (only after the core is stable; the order can follow the remaining time)

These items are independent of each other and can be ordered freely according to the time left before 26 November (constraint C8).

| Step | Feature | Requirements | Suggested priority |
|---|---|---|---|
| 12 | GUI (Tkinter/PySide6) that reuses the backend of phases 1-2 without changing it | FR-33 to 38, NFR-03 | Highest - the demonstration plan of the proposal explicitly uses it |
| 13 | Multi-threaded download | FR-06 | Medium |
| 14 | Summary divided by chapter / topic | FR-26 | Medium |
| 15 | Subtitle embedding into the video | FR-20 | Lower |
| 16 | Offline local LLM for the summary | FR-27 | Lower |
| 17 | Near-real-time translation | FR-21 | Lowest - the proposal itself calls this the hardest bonus item |

> About step 12: the CLI is built before the GUI so that the GUI of step 12 stays "thin". It should only call the backend functions already written in phases 1-2 and show the result, and must never re-implement the pipeline logic (this is exactly what FR-37/NFR-03 verify: if the same input gives a different result in the GUI than in the CLI, that is a bug).

---

## Overall progress

| Phase | Step | Status |
|---|---|---|
| 0 | 0.1 repository structure / 0.2 configuration / 0.3 CI on an empty suite | Done |
| 1 | 1. Local file import | Done |
| 1 | 2. FFmpeg audio extraction | Done |
| 1 | 3. Speech transcription | Done |
| 1 | 4. Bilingual subtitles | Done |
| 1 | 5. Summary and keywords | Done |
| 1 | 6. .vtt export | Done |
| 1 | 7. URL download | Done |
| 1 | 8. Long-audio splitting | Done |
| 2 | 9. Error handling for the whole flow | Done |
| 2 | 10. Formal CLI | Done |
| 2 | 11. Test coverage and CI gate | Done |
| 3 | 12. GUI | Done |
| 3 | 13. Multi-threaded download | Done |
| 3 | 14. Chapter / topic division | Not started |
| 3 | 15. Subtitle embedding into the video | Not started |
| 3 | 16. Offline local LLM | Not started |
| 3 | 17. Near-real-time translation | Not started |

---

*This roadmap is the implementation plan that goes with `specification.md`; it does not replace the SRS itself. If during development the implementation of a step differs from the SRS description, the SRS prevails; if necessary, revise the SRS first and then continue, so that requirements and code stay consistent (traceability).*
