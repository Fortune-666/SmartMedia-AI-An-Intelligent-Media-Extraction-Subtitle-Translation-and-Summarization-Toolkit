"""Tests for subtitle_generator.py — roadmap Phase 1, Step 4 (bilingual subtitles)."""

from unittest.mock import MagicMock, patch

import pytest

from subtitle_generator import (
    TranslationError,
    generate_srt,
    generate_vtt,
    segment_transcript,
    translate_segments,
)


def test_subtitle_segmentation():
    transcript = {
        "language": "en",
        "segments": [
            {"start": 0.0, "end": 2.5, "text": "Hello world."},
            {"start": 2.5, "end": 5.0, "text": "Second line."},
        ],
    }

    segments = segment_transcript(transcript)

    assert len(segments) == 2
    assert segments[0] == {"start": 0.0, "end": 2.5, "text": "Hello world."}
    assert segments[1]["text"] == "Second line."


def _mock_translation_module(translate_fn):
    mock_lang = MagicMock()
    mock_lang.code = "en"
    mock_translation = MagicMock()
    mock_translation.translate.side_effect = translate_fn
    mock_lang.get_translation.return_value = mock_translation

    target_lang = MagicMock()
    target_lang.code = "zh"

    mock_argostranslate = MagicMock()
    mock_argostranslate.translate.get_installed_languages.return_value = [mock_lang, target_lang]

    return mock_argostranslate, mock_translation


def test_subtitle_translation():
    segments = [
        {"start": 0.0, "end": 2.0, "text": "Hello world."},
        {"start": 2.0, "end": 4.0, "text": "Good morning."},
    ]

    mock_argostranslate, mock_translation = _mock_translation_module(
        lambda text: {"Hello world.": "\u4f60\u597d\u4e16\u754c\u3002", "Good morning.": "\u65e9\u4e0a\u597d\u3002"}[text]
    )

    with patch.dict(
        "sys.modules",
        {
            "argostranslate": mock_argostranslate,
            "argostranslate.package": MagicMock(),
            "argostranslate.translate": mock_argostranslate.translate,
        },
    ):
        result = translate_segments(segments, "en", "zh")

    assert result[0]["translated_text"] == "\u4f60\u597d\u4e16\u754c\u3002"
    assert result[1]["translated_text"] == "\u65e9\u4e0a\u597d\u3002"
    assert result[0]["text"] == "Hello world."


def test_subtitle_translation_missing_language_pair():
    mock_argostranslate = MagicMock()
    mock_argostranslate.translate.get_installed_languages.return_value = []

    with patch.dict(
        "sys.modules",
        {
            "argostranslate": mock_argostranslate,
            "argostranslate.package": MagicMock(),
            "argostranslate.translate": mock_argostranslate.translate,
        },
    ):
        with pytest.raises(TranslationError):
            translate_segments([{"start": 0.0, "end": 1.0, "text": "Hi"}], "en", "zh")


def test_bilingual_srt_output(tmp_path):
    translated_segments = [
        {"start": 0.0, "end": 2.5, "text": "Hello world.", "translated_text": "\u4f60\u597d\u4e16\u754c\u3002"},
        {"start": 2.5, "end": 5.0, "text": "Second line.", "translated_text": "\u7b2c\u4e8c\u884c\u3002"},
    ]
    output_file = tmp_path / "output.srt"

    result_path = generate_srt(translated_segments, str(output_file))

    content = result_path.read_text(encoding="utf-8")
    assert "Hello world." in content
    assert "\u4f60\u597d\u4e16\u754c\u3002" in content
    assert "00:00:00,000 --> 00:00:02,500" in content
    assert "00:00:02,500 --> 00:00:05,000" in content
    assert content.strip().startswith("1")


def test_vtt_output(tmp_path):
    translated_segments = [
        {"start": 0.0, "end": 2.5, "text": "Hello world.", "translated_text": "\u4f60\u597d\u4e16\u754c\u3002"},
        {"start": 2.5, "end": 5.0, "text": "Second line.", "translated_text": "\u7b2c\u4e8c\u884c\u3002"},
    ]
    output_file = tmp_path / "output.vtt"

    result_path = generate_vtt(translated_segments, str(output_file))

    content = result_path.read_text(encoding="utf-8")
    assert content.startswith("WEBVTT")
    assert "Hello world." in content
    assert "\u4f60\u597d\u4e16\u754c\u3002" in content
    assert "00:00:00.000 --> 00:00:02.500" in content
    assert "00:00:02.500 --> 00:00:05.000" in content
    assert "," not in content.split("\n\n")[1]  # VTT uses '.' not ',' in timestamps
