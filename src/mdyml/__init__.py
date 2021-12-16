"""The mdyml library."""
# We disable a Flake8 check for "Module imported but unused (F401)" here because
# although this import is not directly used, it populates the value
# package_name.__version__, which is used to get version information about this
# Python package.
from ._version import __version__  # noqa: F401

ORDERED_FIELD_NAMES = [
    "vendor",
    "product",
    "status",
    "affected_versions",
    "patched_versions",
    "vendor_link",
    "notes",
    "references",
    "reporter",
    "last_updated",
]

__all__ = ["ORDERED_FIELD_NAMES"]