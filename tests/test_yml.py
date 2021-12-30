#!/usr/bin/env pytest -vs
"""Tests for yml."""

# Standard Python Libraries
import os
import sys
from unittest.mock import patch

# Third-Party Libraries
import pytest

# cisagov Libraries
import yml
import yml.normalize_yml

log_levels = (
    "debug",
    "info",
    "warning",
    "error",
    "critical",
)

# define sources of version strings
RELEASE_TAG = os.getenv("RELEASE_TAG")
PROJECT_VERSION = yml.__version__


def test_stdout_version(capsys):
    """Verify that version string sent to stdout agrees with the module version."""
    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", ["bogus", "--version"]):
            yml.normalize_yml.main()
    captured = capsys.readouterr()
    assert (
        captured.out == f"{PROJECT_VERSION}\n"
    ), "standard output by '--version' should agree with module.__version__"


def test_running_as_module(capsys):
    """Verify that the __main__.py file loads correctly."""
    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", ["bogus", "--version"]):
            # F401 is a "Module imported but unused" warning. This import
            # emulates how this project would be run as a module. The only thing
            # being done by __main__ is importing the main entrypoint of the
            # package and running it, so there is nothing to use from this
            # import. As a result, we can safely ignore this warning.
            # cisagov Libraries
            import yml.__main__  # noqa: F401
    captured = capsys.readouterr()
    assert (
        captured.out == f"{PROJECT_VERSION}\n"
    ), "standard output by '--version' should agree with module.__version__"


@pytest.mark.skipif(
    RELEASE_TAG in [None, ""], reason="this is not a release (RELEASE_TAG not set)"
)
def test_release_version():
    """Verify that release tag version agrees with the module version."""
    assert (
        RELEASE_TAG == f"v{PROJECT_VERSION}"
    ), "RELEASE_TAG does not match the project version"


# @pytest.mark.parametrize("level", log_levels)
# def test_log_levels(level):
#     """Validate commandline log-level arguments."""
#     with patch.object(
#         sys, "argv", ["bogus", f"--log-level={level}", "data/test_file.yml"]
#     ):
#         with patch.object(logging.root, "handlers", []):
#             assert (
#                 logging.root.hasHandlers() is False
#             ), "root logger should not have handlers yet"
#             return_code = None
#             try:
#                 yml.normalize_yml.main()
#             except SystemExit as sys_exit:
#                 return_code = sys_exit.code
#             assert return_code is None, "main() should return success"
#             assert (
#                 logging.root.hasHandlers() is True
#             ), "root logger should now have a handler"
#             assert (
#                 logging.getLevelName(logging.root.getEffectiveLevel()) == level.upper()
#             ), f"root logger level should be set to {level.upper()}"
#             assert return_code is None, "main() should return success"


def test_bad_log_level():
    """Validate bad log-level argument returns error."""
    with patch.object(
        sys,
        "argv",
        ["bogus", "--log-level=emergency", "data/test_file.yml"],
    ):
        return_code = None
        try:
            yml.normalize_yml.main()
        except SystemExit as sys_exit:
            return_code = sys_exit.code
        assert return_code == 1, "main() should exit with error"
