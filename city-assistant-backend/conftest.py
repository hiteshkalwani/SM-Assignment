"""
Root conftest.py for pytest configuration.
Ensures proper async test support across all test modules.
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Ensure pytest-asyncio is available
pytest_plugins = ['pytest_asyncio']

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Configure asyncio mode
def pytest_configure(config):
    """Configure pytest with asyncio settings."""
    config.option.asyncio_mode = "auto"
