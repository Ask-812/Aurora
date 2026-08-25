"""
Shared pytest fixtures.

Tests run from the repository root so that `config/config.yaml` resolves.
"""

import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


@pytest.fixture(autouse=True)
def run_from_repo_root(monkeypatch):
    """Modules load config/config.yaml by relative path, so pin the working directory."""
    monkeypatch.chdir(REPO_ROOT)


@pytest.fixture
def config_path():
    return os.path.join(REPO_ROOT, "config", "config.yaml")
