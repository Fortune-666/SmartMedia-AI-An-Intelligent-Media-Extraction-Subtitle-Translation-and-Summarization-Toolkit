**Project Proposal**

**SmartMedia-AI: An Intelligent Media Extraction, Subtitle Translation and Summarization Toolkit**

**1. Project Overview**

Our group proposes to develop **SmartMedia-AI**, a Python-based intelligent audio/video processing and content summarization system. The project aims to solve practical problems in cross-border meetings, online education, academic video learning, and multimedia content creation.

At present, users often need to use several different tools to download media, extract audio, convert formats, generate transcripts, translate subtitles, and summarize long videos. This process is time-consuming and technically complicated, especially when the original video does not contain subtitles.

SmartMedia-AI will provide an integrated workflow:

Media downloading → Audio extraction → Speech transcription → Bilingual subtitle generation → Key-point summarization

For example, a user can enter a legal English speech or lecture link. The system will download the media, extract the audio using FFmpeg, generate English and Chinese subtitles, and produce a concise summary of the main content.

The system will support both **Command-Line Interface (CLI)** and **Graphical User Interface (GUI)** modes. The project will be developed using modular Python components so that it can be executed in PyCharm, IntelliJ IDEA, Visual Studio Code, or a standard terminal environment.



**2. Real-World Problem**

The project addresses the following practical problems:

- International meetings may not have complete transcripts or bilingual     records.
- Students may find it difficult to understand foreign-language     lectures and online courses.
- Content creators often need to generate subtitles for videos without     captions.
- Long interviews, speeches, and lectures require a considerable amount     of time to review manually.
- Users usually need multiple independent applications to complete     downloading, conversion, transcription, translation, and summarization.

Unlike a simple video downloader, SmartMedia-AI provides a complete intelligent media-processing workflow. Its main value is not only downloading media, but also transforming unstructured audio/video content into accessible subtitles and useful written information.



**3. Project Objectives**

The objectives of this project are:

1. To design and implement a Python application with CLI and GUI     interaction modes.
2. To support legal downloading or local importing of audio/video files.
3. To use FFmpeg for audio extraction and media format conversion.
4. To use an AI speech-recognition model to convert speech into text.
5. To generate timestamped subtitle files, such as .srt or .vtt.
6. To produce bilingual subtitles, such as English-Chinese subtitles.
7. To extract key points, keywords, and summaries from the transcript.
8. To provide clear error handling for invalid links, missing files,     network interruptions, and API failures.
9. To use unit tests and CI/CD automation to improve code quality.
10. To create a portable project that can run in common Python development     environments.



**4. Main Features**

**4.1 Media Downloading and Local File Import**

Users can either provide a legal media URL or select a local audio/video file. The downloading module will support media retrieval through tools such as yt-dlp, while the local-file mode will allow users to process existing media files.

The system will also include basic file management functions, including:

- Input file validation;
- Output directory selection;
- File naming;
- Media format checking;
- Download progress display;
- Error handling for invalid or unavailable links.

Only media that users have permission to access or download will be used for demonstrations and testing.

**4.2 FFmpeg Audio Extraction and Conversion**

The system will use FFmpeg to process media files. The main functions will include:

- Extracting audio from video;
- Converting audio to WAV, MP3, or M4A;
- Converting audio to a standard format suitable for speech     recognition;
- Adjusting sampling rate and audio channels;
- Splitting long audio files into smaller segments if necessary.

For example, the system may convert an input video into a 16 kHz WAV audio file before sending it to the speech-recognition model.

**4.3 AI Speech Transcription**

The speech-recognition module will use Whisper or another suitable speech-to-text model/API to convert spoken content into text.

The module will aim to support:

- Automatic language detection;
- English and Chinese speech recognition;
- Timestamped transcription;
- Long-audio processing;
- Basic handling of different accents and speaking speeds.

The transcription results will be used by both the subtitle-generation module and the summarization module.

**4.4 Bilingual Subtitle Generation**

Based on the speech transcription and timestamps, the system will generate subtitle files in formats such as .srt or .vtt.

The subtitle workflow will include:

1. Obtaining the original-language transcript;
2. Dividing the transcript according to timestamps;
3. Translating the text into the target language;
4. Combining the original and translated text;
5. Exporting bilingual subtitles.

For example, an English speech may produce subtitles in the following format:

1

00:00:01,000 --> 00:00:04,000

Good morning, everyone.

[Chinese translation: "Good morning, everyone."]

**4.5 Text Summarization and Keyword Extraction**

The system will analyze the transcript and generate:

- A concise summary;
- Main ideas;
- Key points;
- Important keywords;
- Optional chapter or topic divisions.

This feature is particularly useful for lectures, meetings, interviews, and long-form online videos.

**4.6 CLI and GUI Interaction**

The project will provide two possible interaction modes.

**CLI Mode**

Example command:

python main.py --url "https://example.com/video" --source en --target zh

The CLI will allow users to:

- Enter a media URL or local file path;
- Select the source and target languages;
- Choose the output format;
- Start the processing workflow;
- View progress messages and errors;
- Locate the generated subtitles and summary.

**GUI Mode**

The GUI may be implemented using Tkinter, PySide6, or another suitable Python framework. It may include:

- URL input box;
- Local-file selection button;
- Language selection menus;
- Start and cancel buttons;
- Progress bar;
- Processing-status display;
- Subtitle preview;
- Summary preview;
- Output-folder button.

The GUI and CLI will share the same backend modules. This means that the core processing logic will not be duplicated, which improves maintainability and demonstrates a clear software architecture.



**5. System Architecture**

The proposed project will use a modular architecture:

SmartMedia-AI/

│

├── main.py

├── cli_main.py

├── gui_app.py

├── downloader.py

├── media_processor.py

├── ai_engine.py

├── summarizer.py

├── subtitle_generator.py

├── config.py

├── utils.py

├── requirements.txt

├── README.md

├── tests/

│  ├── test_downloader.py

│  ├── test_media_processor.py

│  ├── test_subtitle_generator.py

│  └── test_utils.py

└── .github/

  └── workflows/

​    └── tests.yml

**Main Components**

- main.py: Application entry point and mode selection.
- cli_main.py: Command-line argument parsing and CLI workflow.
- gui_app.py: Graphical user interface.
- downloader.py: Media downloading and local-file handling.
- media_processor.py: FFmpeg audio extraction and conversion.
- ai_engine.py: Speech transcription and AI service integration.
- summarizer.py: Summary and keyword extraction.
- subtitle_generator.py: Timestamp processing and bilingual subtitle     output.
- config.py: API keys, language settings, and system configuration.
- tests/: Unit tests and integration tests.



**6. Team Division**

The project will be completed by six members. Each member will take primary responsibility for one module, while all members will participate in integration, debugging, documentation, and the final presentation.

| **Member** | **Main Responsibility**                                      | **Main File or Module**                            |
| ---------- | ------------------------------------------------------------ | -------------------------------------------------- |
| Member A   | System  architecture, project coordination, and CLI workflow | main.py, cli_main.py                               |
| Member B   | GUI design and  user interaction                             | gui_app.py                                         |
| Member C   | Media  downloading and file management                       | downloader.py                                      |
| Member D   | FFmpeg  processing and audio conversion                      | media_processor.py                                 |
| Member E   | AI  transcription, translation, subtitle generation, and summarization | ai_engine.py, subtitle_generator.py, summarizer.py |
| Member F   | Testing,  CI/CD, quality control, and documentation          | tests/, GitHub  Actions, README.md                 |

**Member A: System Architecture and CLI**

Responsibilities include:

- Designing the overall system architecture;
- Defining interfaces between modules;
- Implementing command-line argument parsing;
- Managing the main workflow;
- Coordinating the integration of all modules;
- Tracking project progress and preparing the final demonstration.

**Member B: GUI Development**

Responsibilities include:

- Designing the graphical interface;
- Implementing URL and local-file input;
- Adding language-selection controls;
- Displaying progress and status messages;
- Providing subtitle and summary previews;
- Connecting the GUI to the shared backend.

**Member C: Downloading and File Management**

Responsibilities include:

- Implementing media downloading using yt-dlp or a similar tool;
- Supporting local media-file import;
- Checking URLs and file formats;
- Managing output directories;
- Handling invalid links, unavailable files, and network failures.

**Member D: FFmpeg Media Processing**

Responsibilities include:

- Extracting audio from video;
- Converting audio formats;
- Preparing audio for AI processing;
- Splitting long audio files when necessary;
- Testing different input formats and audio qualities.

**Member E: AI Processing and Content Extraction**

Responsibilities include:

- Integrating Whisper or another speech-recognition model/API;
- Generating timestamped transcripts;
- Translating the transcript;
- Generating bilingual .srt or .vtt subtitles;
- Producing summaries and keywords;
- Evaluating transcription and summarization results.

**Member F: Testing, CI/CD, and Documentation**

Responsibilities include:

- Writing unit tests with pytest;
- Testing normal and abnormal cases;
- Testing failures such as network interruptions and invalid inputs;
- Configuring GitHub Actions for automated testing;
- Preparing the README file and installation guide;
- Supporting final quality control and project documentation.

Although each member has a primary responsibility, the team will jointly participate in debugging, integration testing, code review, documentation, and the final presentation.



**7. Demonstration Plan**

The proposed demonstration will take approximately 15 minutes.

**Demonstration Scenario**

We will use a legally accessible English speech, lecture, or interview without subtitles.

**Demonstration Steps**

1. Open the GUI or run the CLI program.
2. Paste the media URL or select a local video file.
3. Select English as the source language and Chinese as the target     language.
4. Start the processing workflow.
5. Display the download progress.
6. Demonstrate FFmpeg audio extraction.
7. Display the speech-transcription status.
8. Generate bilingual .srt subtitles.
9. Preview the subtitles.
10. Generate and display the key-point summary.
11. Export all results to the output folder.

**Expected Output**

The system will generate:

- Processed audio file;
- Original-language transcript;
- Bilingual .srt or .vtt subtitle file;
- Summary text file;
- Keyword list;
- Processing log.

This demonstration clearly shows that SmartMedia-AI is more than a media downloader. It is an integrated tool for converting audio/video content into subtitles and structured information.



**8. Technologies and Development Tools**

The proposed technologies include:

- **Programming language:** Python
- **Media downloading:** yt-dlp
- **Media processing:** FFmpeg and possibly ffmpeg-python
- **Speech recognition:** Whisper or another suitable speech-recognition     API/model
- **Translation:** Translation API or language model
- **Summarization:** LLM API or local language model
- **CLI:** argparse or Click
- **GUI:** Tkinter, PySide6, or Streamlit
- **Testing:** pytest
- **Version control:** Git and GitHub
- **CI/CD:** GitHub Actions
- **Configuration:** .env and environment variables

API keys will not be hard-coded into the source code. They will be stored through environment variables or a local configuration file that is excluded from version control.



**9. Error Handling and Reliability**

The system will include error handling for:

- Invalid URLs;
- Unsupported media formats;
- Download failures;
- Network interruptions;
- FFmpeg execution errors;
- Missing dependencies;
- API timeouts;
- Invalid API keys;
- Empty or low-quality audio;
- Large files and long processing times.

The CLI will display clear error messages, while the GUI will provide user-friendly status notifications or dialog boxes. The system should fail gracefully instead of terminating unexpectedly.



**10. Testing and CI/CD**

Testing will be conducted at several levels:

**Unit Testing**

Individual functions will be tested separately, including:

- URL validation;
- File validation;
- Audio-format conversion;
- Subtitle formatting;
- Timestamp conversion;
- Summary-output validation.

**Integration Testing**

The team will test whether the modules work together correctly:

Downloader → FFmpeg Processor → AI Engine → Subtitle Generator → Summarizer

**CI/CD**

GitHub Actions will automatically:

1. Install project dependencies;
2. Run unit tests;
3. Check whether the project can be imported successfully;
4. Report test failures to the team.

Generative AI tools such as Codex or GitHub Copilot may be used to assist with code generation, debugging, test writing, and refactoring. All AI-generated code will be reviewed, modified, and tested by team members. The use of AI assistance will be documented transparently in the final report if required by the course.



**11. Compatibility with Codex and Development Environments**

SmartMedia-AI will be designed as a standard Python project rather than an IDE-specific project. Therefore, it can be developed and executed in:

- PyCharm;
- IntelliJ IDEA with Python support;
- Visual Studio Code;
- A standard operating-system terminal.

The project will provide:

- requirements.txt;
- A clear README.md;
- A standard entry point such as main.py;
- Environment-variable instructions;
- Setup and execution commands;
- Optional configuration templates.

Typical installation commands will be:

python -m venv .venv

pip install -r requirements.txt

CLI execution:

python main.py --url "MEDIA_URL" --source en --target zh

GUI execution:

python main.py --gui

The exact commands may be adjusted according to the final implementation. Codex or other AI-assisted programming tools can be used within the supported IDEs, but the application itself will not depend on Codex or any specific IDE plugin to run.



**12. Project Scope and Feasibility**

The core functions will be completed first:

1. Local media import or legal media downloading;
2. FFmpeg audio extraction;
3. AI speech transcription;
4. Bilingual subtitle generation;
5. Text summarization;
6. CLI interface;
7. Unit testing and CI/CD.

The GUI, multi-threaded downloading, offline local LLM deployment, real-time multilingual translation, and automatic subtitle embedding will be treated as extension features. This approach ensures that the project remains achievable while still providing opportunities for advanced functionality.

The project is feasible because:

- Python provides suitable libraries for all major functions;
- Each module can be developed independently;
- The backend can be reused by both CLI and GUI;
- The project can use pre-trained AI models or APIs instead of training     a model from scratch;
- Testing and integration can be performed incrementally.



**13. Expected Outcomes**

At the end of the project, we expect to deliver:

- A functional Python application named SmartMedia-AI;
- CLI and, if time permits, GUI interaction;
- Media downloading or local-file importing;
- FFmpeg-based audio processing;
- AI-generated transcripts;
- Bilingual subtitle files;
- Automated summaries and keyword extraction;
- Error handling and logging;
- Unit tests and GitHub Actions CI/CD;
- User documentation and installation instructions;
- A 15-minute demonstration showing the complete workflow.



**14. Deadline**

The proposal and related course-design materials will be submitted by:

**26 November**
