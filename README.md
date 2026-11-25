# SmartMedia-AI

Give it a video, an audio file or a URL, and it produces **bilingual subtitles (SRT or VTT) and an extractive summary**. A command-line tool and a Tkinter desktop window share one processing pipeline (`pipeline.py`).

Course project for INT6181 Applied Programming with Python, Group 13. Requirements are in `specification.md`, the development order is in `roadmap.md`, and the code review record is in `CODE_REVIEW.md`.

## What it does

```
video / audio / URL
   -> 1. import or download      downloader.py          (yt-dlp for URLs)
   -> 2. audio extraction        media_processor.py     (FFmpeg, 16 kHz mono WAV)
   -> 3. speech to text          ai_engine.py           (Whisper, runs on your own computer)
   -> 4. translation + subtitles subtitle_generator.py  (Argos Translate, SRT / VTT)
   -> 5. summary and keywords    summarizer.py          (picks the most important sentences)
```

Supported input files: `.mp4 .mkv .mov .avi .webm .mp3 .wav .m4a`. Languages: English and Chinese (the source language can be detected automatically; the default target is Chinese).

Output folder after one run: `audio.wav`, `transcript.txt`, `subtitles.srt` (or `.vtt`), `summary.txt`, `processing.log`.

## Requirements

- **Python 3.10** in a conda environment named `smart`. Use this environment, not the system or base Python.
- **FFmpeg and ffprobe** installed and on the `PATH`.
- Python packages from `requirements.txt`: `openai-whisper`, `torch` (CPU build is enough), `argostranslate`, `yt-dlp`, `python-dotenv`, `pytest`.
- Internet access for the one-time downloads in step 4 below, and for downloading from URLs. Processing a local file afterwards works offline.

## Setup

### 1. Create and activate the environment

```bash
conda create -n smart python=3.10
conda activate smart
```

If the `smart` environment already exists, only run `conda activate smart`.

### 2. Install the Python packages

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

Download a build for your platform from [ffmpeg.org](https://ffmpeg.org/download.html) (or use a package manager such as `brew install ffmpeg`) and make sure its `bin` folder is on the `PATH`. Check:

```bash
ffmpeg -version
ffprobe -version
```

### 4. One-time downloads (internet needed)

- **Whisper model:** it is downloaded automatically the first time the tool runs, so the first run can be slow.
- **Argos Translate language packages:** install the pair you need (here English to Chinese and Chinese to English):

  ```bash
  python - <<'PY'
  import argostranslate.package as p
  p.update_package_index()
  for a in p.get_available_packages():
      if (a.from_code, a.to_code) in {("en", "zh"), ("zh", "en")}:
          p.install_from_path(a.download())
  PY
  ```

  If a package is missing, the tool stops with the message "No installed argostranslate language pair ... Install the matching language package first."

### 5. Optional: configuration file

The speech-to-text step uses the local Whisper model and needs no API key. If you want to change the output folder or add keys for future cloud services, create a `.env` file in the project root:

```
ASR_API_KEY=
TRANSLATION_API_KEY=
SUMMARIZATION_API_KEY=
OUTPUT_DIR=output
TEMP_DIR=temp
```

`.env` is excluded by `.gitignore` and is never committed.

## Run

### Command line

```bash
python main.py --file <path to a local media file>
# or one URL
python main.py --url <media URL> --source en --target zh --format srt --output-dir output
# or download several URLs in parallel (download only: no transcript, subtitles or summary)
python main.py --download-urls <URL1> <URL2> ... --max-concurrent-downloads 3 --output-dir output
```

Run `python main.py --help` for the full list. Options:

- `--file`, `--url`, `--download-urls`: choose exactly one.
  - `--file`: a local media file (full processing: transcript, subtitles, summary).
  - `--url`: one media URL (full processing).
  - `--download-urls`: several URLs, downloaded in parallel and then stop (no transcription).
- `--max-concurrent-downloads`: maximum parallel downloads in batch mode (default 3; can also be set with the environment variable `MAX_CONCURRENT_DOWNLOADS`).
- `--source`: source language code (`en` or `zh`). If you leave it out, Whisper detects the language. Single-item mode only.
- `--target`: language of the translated subtitle line, default `zh`. Single-item mode only.
- `--format`: subtitle format, `srt` (default) or `vtt`. Single-item mode only.
- `--output-dir`: folder for all results.

On success the tool prints the path of every result (audio, transcript, bilingual subtitles, summary, processing log) and exits with code 0. If any stage fails it prints an error message and exits with code 1. In batch mode one failed URL does not stop the others, but the exit code is 1 if any URL failed.

### Desktop window (GUI)

```bash
python gui_app.py
```

The window (Tkinter, no extra package; all text is in English) offers:

- a local file or a URL as input;
- source and target language, SRT or VTT format, and an output folder;
- **Start** and **Cancel** buttons, and a status line that names the current stage;
- after the run, two preview tabs, **Bilingual subtitles** and **Summary / keywords / key points**, and an **Open output folder** button;
- a **batch download** mode: several URLs (one per line), the number of parallel downloads, and the result of each item (path or reason for failure).

Notes:

- The window and the command line call the same pipeline, `pipeline.py`, so they behave the same (NFR-03).
- **Cancel:** when you click Cancel, or close the window during processing, the stage that is running (for example Whisper transcription) finishes first, and no later stage starts. In batch mode, items that have not started are skipped and running downloads finish. Files already made and the processing log stay in the output folder.
- The first run loads the local Whisper model and can be slow. Translation needs the Argos language package for the language pair (see step 4).

### Show the bilingual subtitles in VLC

The subtitle file is a separate **external subtitle file**. It is not burned into the video, and VLC does not load it by itself because its name and folder differ from the video. To check the result with VLC:

1. Open the original video in VLC (for example `test_python.mp4`).
2. In the menu bar choose **Subtitles -> Add Subtitle File...** and select `subtitles.srt` from the output folder.
3. Play a part where someone speaks. Each entry shows the original line and, below it, the translation.

The SRT file is UTF-8. If Chinese characters appear as empty boxes, open **VLC -> Preferences -> Subtitles / OSD** and choose a font that contains Chinese characters, then add the subtitle file again. Other players that support UTF-8 external subtitles can also be used; Windows Media Player depends on the version and is not used for the acceptance check. The subtitle preview inside our window is a text preview, not video playback.

## Tests

```bash
pytest tests -v
```

All external dependencies (the FFmpeg subprocess, the Whisper model, the network) are replaced by fakes in the unit tests, so the whole suite runs without internet and without model files.

There are 110 tests in 15 test files, and all of them pass (about half a second). Measured with `coverage.py`, the overall line coverage is about 81% (`gui_app.py` 68%, `cli_main.py` 72%, the other modules 88-100%). A GitHub Actions workflow (`.github/workflows/test.yml`) runs the same tests on Python 3.10, 3.11 and 3.12 for every push and pull request.

## Project structure

| File | Purpose |
| --- | --- |
| `main.py` | Entry point of the command-line program |
| `cli_main.py` | Command line: argument parsing, progress output, exit codes |
| `gui_app.py` | Tkinter window: input, progress, cancel, previews |
| `pipeline.py` | Shared processing pipeline used by both the command line and the window |
| `downloader.py` | Local file import and URL download (including parallel batch download) |
| `media_processor.py` | FFmpeg audio extraction, audio duration, and cutting long audio into parts |
| `ai_engine.py` | Speech to text with Whisper, including joining the parts of long audio back into one timeline |
| `subtitle_generator.py` | Translation with Argos Translate and bilingual `.srt` / `.vtt` files |
| `summarizer.py` | Summary, keywords and main points |
| `config.py` | Environment variables and API-key configuration |
| `utils.py` | Helper functions, including the processing log |
| `tests/` | Automated tests (pytest) |
| `specification.md`, `roadmap.md`, `CODE_REVIEW.md` | Requirements, development plan, code review record |

## Development progress

See `roadmap.md` for the status of every step and Appendix A of `specification.md` for the table that links requirements to tests.

- Phase 0 (scaffold, configuration, CI) and Phase 1 (steps 1-8, core pipeline): done.
- Phase 2 (steps 9-11: error handling and log, formal command line, end-to-end tests): done.
- Phase 3: step 12 (Tkinter window) and step 13 (parallel batch download) are done. Steps 14-17 (chapter summary, subtitles embedded in the video, local large-model summary, near-real-time translation) are not started and are not needed for the core acceptance.

## Known limits

- The summary picks existing sentences; it does not write new sentences.
- Subtitles are a separate file; they are not embedded in the video.
- Batch mode only downloads; it does not transcribe.
- Chinese keywords are single characters, because the tokenizer has no Chinese word splitter (finding F5 in `CODE_REVIEW.md`).
- Setting a non-numeric value in an environment variable such as `MAX_CONCURRENT_DOWNLOADS` makes `import config` fail (finding F4).

## Team (module owner)

ZHONG Hao (input, `downloader.py`), LI Xueliang (audio and speech to text), CHEN Wanshan (subtitles, pipeline and window: `subtitle_generator.py`, `pipeline.py`, `gui_app.py`), ZENG Leer (summary, `summarizer.py`, and the live demo), LU Junyi (command line and tests), WAN Yutong (error handling and log, code review, documents).

## Third-party software and AI use

Not written by us: [OpenAI Whisper](https://github.com/openai/whisper) (speech to text), [FFmpeg](https://ffmpeg.org) (audio), [Argos Translate](https://github.com/argosopentech/argos-translate) (offline translation), [yt-dlp](https://github.com/yt-dlp/yt-dlp) (download), PyTorch, python-dotenv, pytest.

The generative AI assistant Claude Code helped with the regression tests, the first code review pass and the docstrings. A team member reads and approves every AI-generated change (rule C7 in `specification.md`; see `CODE_REVIEW.md`).
