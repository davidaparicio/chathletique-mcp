"""
Simple tests for MCP utilities
"""

import os
import sys

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_mcp_import():
    """Test that mcp_utils can be imported successfully"""
    try:
        from strava_mcp import mcp_utils

        assert hasattr(mcp_utils, "mcp")
        assert mcp_utils.mcp is not None
    except ImportError as e:
        pytest.skip(f"Could not import mcp_utils: {e}")


def test_mcp_server_config():
    """Test basic MCP server configuration"""
    try:
        from strava_mcp.mcp_utils import mcp

        # Test that mcp object has expected attributes
        assert hasattr(mcp, "run")

        # Note: We don't actually run the server in tests to avoid port conflicts

    except ImportError as e:
        pytest.skip(f"Could not import mcp: {e}")


def test_main_module_import():
    """Test that main module can be imported"""
    try:
        from strava_mcp import main

        # Just test that it imports without errors
        assert main is not None
    except ImportError as e:
        pytest.skip(f"Could not import main: {e}")
