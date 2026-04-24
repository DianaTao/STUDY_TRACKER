
import sys
from pathlib import Path

# Add project root to sys.path to ensure local code is prioritized
# This allows testing local changes without installing the package
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock
from session_cli import cli

"""
TEST PLAN: Study Tracker CLI

1. Functional Unit Tests (pytest + click.testing):
    - test_get_default_store_path: Verify the default path logic uses home directory.
    - test_add_command_success: Mock session_store.add_session to return a session and verify CLI output.
    - test_add_command_error: Mock session_store.add_session to raise ValueError and verify 'Error: ...' output and non-zero exit.
    - test_list_command_empty: Verify output when no sessions exist.
    - test_list_command_data: Mock session_store.list_sessions and verify formatted string output.
    - test_stats_command: Mock session_store.summarize and verify sorting logic (descending minutes).
    - test_custom_store_path: Verify the --store option correctly overrides the default path.

2. Edge Cases & Formal Verification (Z3):
    - Sorting Logic Verification: Use Z3 to formally prove that the stats sorting logic always results in a list where element[i].minutes >= element[i+1].minutes.
    - Path Validation: Ensure the default path logic always returns a Path object ending in 'sessions.json'.

"""

# --- Fixtures ---

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def mock_store(tmp_path):
    """Provides a temporary path for the store."""
    return tmp_path / "sessions.json"

# --- Unit Tests ---

@patch("session_cli.add_session")
def test_add_command_success(mock_add, runner, mock_store):
    # Mock return value based on session_store_usage description
    mock_add.return_value = {"id": 1, "topic": "Python", "minutes": 30, "created_at": "2023-01-01"}
    
    result = runner.invoke(cli, ["--store", str(mock_store), "add", "--topic", "Python", "--minutes", "30"])
    
    assert result.exit_code == 0
    assert "1" in result.output  # the created ID is surfaced somewhere
    mock_add.assert_called_once_with(mock_store, "Python", 30)

@patch("session_cli.add_session")
def test_add_command_error(mock_add, runner, mock_store):
    # Simulate a validation error from the backend
    mock_add.side_effect = ValueError("Minutes must be positive")
    
    result = runner.invoke(cli, ["--store", str(mock_store), "add", "--topic", "Python", "--minutes", "-10"])
    
    assert result.exit_code != 0
    assert "Error: Minutes must be positive" in result.output

@patch("session_cli.list_sessions")
def test_list_command_empty(mock_list, runner, mock_store):
    mock_list.return_value = []
    
    result = runner.invoke(cli, ["--store", str(mock_store), "list"])
    
    assert result.exit_code == 0
    assert "No sessions recorded yet." in result.output

@patch("session_cli.list_sessions")
def test_list_command_data(mock_list, runner, mock_store):
    mock_list.return_value = [
        {"id": 1, "topic": "Python", "minutes": 45, "created_at": "2023-10-01 10:00"},
        {"id": 2, "topic": "Z3", "minutes": 60, "created_at": "2023-10-01 11:00"}
    ]
    
    result = runner.invoke(cli, ["--store", str(mock_store), "list"])
    
    assert result.exit_code == 0
    # Format: "{id} | {created_at} | {minutes}m | {topic}"
    assert "1 | 2023-10-01 10:00 | 45m | Python" in result.output
    assert "2 | 2023-10-01 11:00 | 60m | Z3" in result.output

@patch("session_cli.summarize")
def test_stats_command_sorting(mock_sum, runner, mock_store):
    # Data with unsorted minutes
    mock_sum.return_value = {
        "total_sessions": 3,
        "total_minutes": 100,
        "by_topic": {
            "SmallTask": 10,
            "BigTask": 70,
            "MedTask": 20
        }
    }
    
    result = runner.invoke(cli, ["--store", str(mock_store), "stats"])
    
    assert result.exit_code == 0
    idx_big = result.output.find("BigTask")
    idx_med = result.output.find("MedTask")
    idx_small = result.output.find("SmallTask")
    assert idx_big != -1 and idx_med != -1 and idx_small != -1
    assert idx_big < idx_med < idx_small

if __name__ == "__main__":
    pytest.main([__file__])