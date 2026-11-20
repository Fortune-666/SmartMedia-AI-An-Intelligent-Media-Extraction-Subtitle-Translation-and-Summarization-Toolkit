"""Shared pytest fixtures."""

import pytest

import ai_engine


@pytest.fixture(autouse=True)
def _fresh_whisper_model_cache():
    """The Whisper model is cached per process (review finding F2).

    Clear the cache around every test so that a mocked model from one test can
    never leak into the next one.
    """
    ai_engine._MODEL_CACHE.clear()
    yield
    ai_engine._MODEL_CACHE.clear()
