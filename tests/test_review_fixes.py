"""Regression tests for the findings of the 2026-11-19 code review (see CODE_REVIEW.md).

Each test fails on the code as it was before the review and passes after the fix:
F1 Chinese sentence splitting, F2 Whisper model reloaded per chunk,
F3 unclear error for unusable ffprobe output.
"""

import pathlib
from unittest.mock import MagicMock, patch

import pytest

import ai_engine
import summarizer
from media_processor import AudioExtractionError, get_audio_duration

CHINESE_TEXT = "今天天气很好。我们去公园玩。明天会下雨。我们留在家里。后天又是晴天。"


def test_chinese_text_is_split_into_sentences():
    """F1: Chinese sentences have no space after 。 and were treated as one sentence."""
    sentences = summarizer._split_sentences(CHINESE_TEXT)

    assert len(sentences) == 5
    assert sentences[0] == "今天天气很好。"


def test_chinese_summary_is_shorter_than_the_whole_text():
    """F1: the summary of a long Chinese text used to be the whole text."""
    summary = summarizer.extract_summary(CHINESE_TEXT, num_sentences=3)

    assert summary != CHINESE_TEXT
    assert len(summarizer.extract_main_points(CHINESE_TEXT, num_points=2)) == 2


def test_english_sentence_splitting_is_unchanged():
    """F1: the fix must not change how English text is split."""
    text = "It is sunny. We go out. It rains later! Do we stay home? Yes."

    assert len(summarizer._split_sentences(text)) == 5


def test_whisper_model_is_loaded_once_for_all_chunks(tmp_path):
    """F2: a 3-chunk audio file used to load the Whisper model 3 times."""
    chunks = []
    for index in range(3):
        chunk = tmp_path / f"part{index}.wav"
        chunk.write_bytes(b"fake wav")
        chunks.append(chunk)

    model = MagicMock()
    model.transcribe.return_value = {
        "language": "en",
        "segments": [{"start": 0.0, "end": 1.0, "text": "hello"}],
    }
    fake_whisper = MagicMock()
    fake_whisper.load_model.return_value = model

    with patch.dict("sys.modules", {"whisper": fake_whisper}), patch.object(
        ai_engine, "split_audio", return_value=chunks
    ):
        result = ai_engine.transcribe_long_audio(str(chunks[0]), 1800, str(tmp_path))

    assert fake_whisper.load_model.call_count == 1
    assert len(result["segments"]) == 3


def test_get_audio_duration_unusable_output_raises_clear_error():
    """F3: ffprobe printing "N/A" used to leak a bare ValueError."""
    completed = MagicMock(returncode=0, stdout="N/A\n", stderr="")

    with patch("media_processor.subprocess.run", return_value=completed):
        with pytest.raises(AudioExtractionError, match="no usable duration"):
            get_audio_duration("broken.wav")
