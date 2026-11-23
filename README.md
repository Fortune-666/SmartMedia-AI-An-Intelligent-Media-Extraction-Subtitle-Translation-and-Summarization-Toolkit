# SmartMedia-AI

Video / audio / URL in, **bilingual subtitles (SRT/VTT) and an extractive summary** out. Command line and Tkinter window share one pipeline (`pipeline.py`). Course project INT6181, Group 13.

## Quick start (English)

1. Python 3.10 in the conda environment `smart`, and **FFmpeg** on the PATH (`ffmpeg -version`):
   ```bash
   conda create -n smart python=3.10 && conda activate smart
   pip install -r requirements.txt
   ```
2. **One-time downloads (need internet):**
   - Whisper downloads its speech model the first time it runs.
   - Translation needs the Argos language packages for the pair you use (English to Chinese and back):
     ```bash
     python - <<'PY'
     import argostranslate.package as p
     p.update_package_index()
     for a in p.get_available_packages():
         if (a.from_code, a.to_code) in {("en", "zh"), ("zh", "en")}:
             p.install_from_path(a.download())
     PY
     ```
   Without the package the tool stops with the message "No installed argostranslate language pair ... Install the matching language package first."
3. Run:
   ```bash
   python main.py --file lecture.mp4 --target zh --format srt --output-dir output   # command line
   python gui_app.py                                                              # window
   ```
   Output folder: `audio.wav`, `transcript.txt`, `subtitles.srt` (or `.vtt`), `summary.txt`, `processing.log`.
4. **Play the subtitles in VLC.** The subtitle file is a separate file, so VLC does not load it by itself (its name and folder differ from the video):
   1. Open the original video in VLC (for example `test_python.mp4`).
   2. Menu **Subtitles -> Add Subtitle File...** and choose `subtitles.srt` from the output folder.
   3. Play a part with speech: each entry shows the original line and, below it, the translation.
   If Chinese characters look wrong (empty boxes), open **VLC -> Preferences -> Subtitles / OSD** and choose a font that has Chinese glyphs; the file is UTF-8. Subtitles are not burned into the video.
5. Tests: `pytest tests` (110 tests, no internet or model needed; FFmpeg and Whisper are replaced by fakes).

Third-party software used (not written by us): [OpenAI Whisper](https://github.com/openai/whisper) (speech to text), [FFmpeg](https://ffmpeg.org) (audio), [Argos Translate](https://github.com/argosopentech/argos-translate) (offline translation), [yt-dlp](https://github.com/yt-dlp/yt-dlp) (download), PyTorch, python-dotenv, pytest. Generative AI (Claude Code) helped with tests, the first code review pass and docstrings; a team member approves every change (rule C7, see `CODE_REVIEW.md`).

Team (module owner): ZHONG Hao (input, `downloader.py`), LI Xueliang (audio and speech to text), CHEN Wanshan (subtitles, pipeline and window: `subtitle_generator.py`, `pipeline.py`, `gui_app.py`), ZENG Leer (summary, `summarizer.py`, and the live demo), LU Junyi (command line and tests), WAN Yutong (error handling and log, review, documents).

Known limits: the summary picks existing sentences; subtitles are separate files; batch mode only downloads; Chinese keywords are single characters (finding F5).

---

## 中文说明

智能音视频处理与字幕摘要工具。详细需求见 `specification.md`，开发顺序见 `roadmap.md`。

## 环境要求

**本项目统一使用 conda 环境 `smart`（Python 3.10），不要用系统/base Python 运行本项目。**

依赖已在该环境安装验证，包括：

- `openai-whisper` 20250625（ASR 语音转写）
- `torch` 2.14（CPU 版）
- `pytest` 9.x
- `python-dotenv`

还需要系统安装 **FFmpeg**（音频提取/转换）并保证其在 PATH 中可用。

## 环境搭建

### 1. 创建/激活 conda 环境

```bash
conda create -n smart python=3.10
conda activate smart
```

如果 `smart` 环境已经存在（本项目开发时使用的环境），直接激活：

```bash
conda activate smart
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装 FFmpeg

从 [ffmpeg.org](https://ffmpeg.org/download.html) 下载对应平台的构建版本，解压后将其 `bin` 目录加入系统 PATH。验证：

```bash
ffmpeg -version
ffprobe -version
```

### 4. 配置 API 密钥（可选，视后续功能而定）

复制 `.env.example`（如有）或手动创建 `.env` 文件于项目根目录，内容示例：

```
ASR_API_KEY=
TRANSLATION_API_KEY=
SUMMARIZATION_API_KEY=
OUTPUT_DIR=output
TEMP_DIR=temp
```

`.env` 已被 `.gitignore` 排除，不会被提交到版本库。当前阶段的语音转写使用本地 Whisper 模型，不需要 API 密钥；密钥用于后续接入的翻译/摘要云服务。

## 运行

### CLI

```bash
python main.py --file <本地媒体文件路径>
# 或
python main.py --url <媒体URL> --source en --target zh --format srt --output-dir output
# 或批量下载（只下载，不转写/字幕/摘要）
python main.py --download-urls <URL1> <URL2> ... --max-concurrent-downloads 3 --output-dir output
```

参数说明：

- `--file` / `--url` / `--download-urls`：三者互斥，选其一
  - `--file`：本地媒体文件（完整处理：转写、字幕、摘要）
  - `--url`：单个媒体 URL（完整处理）
  - `--download-urls`：多个 URL，并发下载后停止（不自动转写）
- `--max-concurrent-downloads`：批量下载的最大并发数（默认 3，可通过环境变量 `MAX_CONCURRENT_DOWNLOADS` 配置）
- `--source`：源语言代码（`en`/`zh`），缺省时由 Whisper 自动检测；仅单项处理时有效
- `--target`：字幕翻译目标语言，默认 `zh`；仅单项处理时有效
- `--format`：字幕格式 `srt`（默认）或 `vtt`；仅单项处理时有效
- `--output-dir`：所有产物的输出目录

成功时打印各产物（音频、转写文本、双语字幕、摘要、处理日志）的路径并返回退出码 0；任何阶段失败时打印错误信息并返回退出码 1。批量下载中单个 URL 失败不影响其他 URL，但存在失败项时整体返回退出码 1。当前支持的媒体扩展名：`.mp4 .mkv .mov .avi .webm .mp3 .wav .m4a`。

### 桌面 GUI

```bash
python gui_app.py
```

图形界面（Tkinter，无需额外依赖；界面文字为英文）提供：本地文件 / URL 二选一、源与目标语言选择、SRT/VTT 格式与输出目录选择、开始 / 取消按钮、当前阶段进度提示，以及处理完成后应用内的双语字幕与摘要预览标签页和"打开输出目录"按钮。

图形界面还提供**批量下载模式**：多行 URL 输入、最大并发数选择，逐项显示下载进度、完成路径或失败原因，处理结束后可打开下载目录。

- GUI 与 CLI 调用同一共享流水线 `pipeline.py`，处理行为一致（NFR-03）。
- **取消语义**：点击"取消"或处理中关闭窗口后，当前正在执行的阻塞阶段（如 Whisper 转写）会先运行结束，随后的所有阶段不再执行；批量下载会停止尚未开始的项目并等待进行中的下载收尾。已生成的文件与处理日志保留在输出目录。
- 首次运行会加载本地 Whisper 模型，可能较慢；翻译需要已安装对应语言的 argostranslate 语言包。

### 使用 VLC 播放双语字幕

**本项目使用 VLC 验证字幕播放，请使用 VLC 打开视频并加载生成的字幕文件。** Windows Media Player 对外挂 SRT 的支持因版本而异，可能出现字幕不显示或中文乱码，不作为本项目的字幕播放验收工具；其他支持 UTF-8 外挂字幕的播放器也可能正常使用。

1. 用 VLC 打开原视频（例如 `test.mp4`）。
2. 点击菜单 **字幕 → 添加字幕文件**，选择输出目录中的 `subtitles.srt`。
3. 播放到有讲话的时间段，即可看到原文与中文译文。

生成的 SRT 是 UTF-8 编码的**外挂字幕**，不会自动嵌入或修改原视频。仅打开视频不代表已经加载字幕；GUI 中的字幕预览也是文本预览，不是视频播放。

若中文字幕仍显示异常，可在 VLC 的 **工具 → 首选项 → 字幕/OSD** 中检查字幕编码为 UTF-8，并选择支持中文的字体（如微软雅黑或宋体），然后重新加载字幕。

## 测试

```bash
pytest tests -v
```

所有外部依赖（FFmpeg 子进程、Whisper 模型）在单元测试中均通过 mock 隔离，无需真实网络连接或真实模型权重即可运行测试套件。

当前共 110 个测试（15 个测试文件），全部通过；用 `coverage.py` 测得整体覆盖率约 81%。GitHub Actions 工作流（`.github/workflows/test.yml`）在每次推送和合并请求时运行同一套测试。

## 项目结构

| 文件                      | 职责                                       |
| ------------------------- | ------------------------------------------ |
| `main.py`               | CLI 程序入口                               |
| `cli_main.py`           | 命令行接口（参数解析、进度打印、退出码）   |
| `gui_app.py`            | Tkinter 桌面界面（输入、进度、取消、预览） |
| `pipeline.py`           | 共享处理流水线（CLI 与 GUI 共用后端）      |
| `downloader.py`         | 本地文件导入 / URL 下载                    |
| `media_processor.py`    | FFmpeg 音频提取与格式转换                  |
| `ai_engine.py`          | 语音转写（ASR）、翻译                      |
| `subtitle_generator.py` | 双语字幕生成（.srt / .vtt）                |
| `summarizer.py`         | 摘要与关键词提取                           |
| `config.py`             | 环境变量 / API 密钥配置                    |
| `utils.py`              | 通用工具函数（含处理日志）                 |
| `tests/`                | 单元测试（pytest）                         |

## 开发进度

详见 `roadmap.md`（逐步状态）与 `specification.md` 附录 A（需求到测试的对应表）。

- 阶段 0（脚手架、配置、CI）与阶段 1（第 1–8 步，核心流水线）：已完成
- 阶段 2（第 9–11 步：错误处理与日志、正式 CLI、端到端测试）：已完成
- 阶段 3：第 12 步 Tkinter GUI、第 13 步多线程批量下载已完成；第 14–17 步（章节摘要、字幕嵌入视频、本地大模型摘要、近实时翻译）未开始，不影响核心验收

代码审查记录见 `CODE_REVIEW.md`。
