"""The yml library."""
# We disable a Flake8 check for "Module imported but unused (F401)" here because
# although this import is not directly used, it populates the value
# package_name.__version__, which is used to get version information about this
# Python package.
# cisagov Libraries
from mdyml import __version__  # noqa: F401
