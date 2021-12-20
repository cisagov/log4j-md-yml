"""The mdyml library."""
# We disable a Flake8 check for "Module imported but unused (F401)" here because
# although this import is not directly used, it populates the value
# package_name.__version__, which is used to get version information about this
# Python package.
# Standard Python Libraries
import re

from ._version import __version__  # noqa: F401

DEFAULT_CVE_ID = "cve-2021-44228"

MD_LINK_RE = re.compile(r"\[(?P<text>.*?)\]\((?P<link>.*?)\)")

ORDERED_CVE_IDS = [
    "cve-2021-4104",
    DEFAULT_CVE_ID,
    "cve-2021-45046",
    "cve-2021-45105",
]

__all__ = ["DEFAULT_CVE_ID", "MD_LINK_RE", "ORDERED_CVE_IDS"]
