import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_env() -> None:
    with patch.dict(
        os.environ,
        {"HA_URL": "http://localhost:8123", "HA_TOKEN": "test_token"},
        clear=False,
    ):
        yield


@pytest.fixture
def mock_requests() -> MagicMock:
    with patch("mcp_homeassistant._core.requests") as mock:
        yield mock
