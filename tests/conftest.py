"""All Git fixtures are synthetic and isolated from user configuration."""

import os
import tempfile

import pytest


@pytest.fixture(autouse=True)
def isolated_git(monkeypatch):
    for key in list(os.environ):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", tempfile.gettempdir())
    monkeypatch.setenv("GIT_AUTHOR_NAME", "Synthetic Contributor")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "fixture@example.invalid")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "Synthetic Contributor")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "fixture@example.invalid")
