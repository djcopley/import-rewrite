import sys
from pathlib import Path

import pytest

TEST_DIR = Path(__file__).parent
RESOURCES_DIR = TEST_DIR / "resources"


@pytest.fixture(autouse=True)
def setup_resources_path():
    original_path = sys.path.copy()
    sys.path.insert(0, str(RESOURCES_DIR))
    yield
    sys.path = original_path


@pytest.fixture(autouse=True)
def cleanup_meta_path():
    original_meta_path = sys.meta_path.copy()
    yield
    sys.meta_path = original_meta_path
