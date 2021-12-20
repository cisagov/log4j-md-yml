"""md_from_template Markdown generation tool.

Output Markdown from a Markdown template file and a file containing JSON data
to be applied to the template.

EXIT STATUS
    This utility exits with one of the following values:
    0   No error occurred.
    >0  An error occurred.

Usage:
  md_from_template [--log-level=LEVEL] <md_template> <template_data_json>
  md_from_template (-h | --help)

Options:
  -h --help              Show this message.
  --log-level=LEVEL      If specified, then the log level will be set to
                         the specified value.  Valid values are "debug", "info",
                         "warning", "error", and "critical". [default: info]
"""

# Standard Python Libraries
import json
import logging
import sys
from typing import Any

# Third-Party Libraries
import chevron
import docopt
from schema import And, Schema, SchemaError, Use

from . import _version


def load(filename: str) -> str:
    """Return the contents of a file."""
    ans = None
    with open(filename, "r") as f:
        ans = f.read()

    return ans


def load_json(filename: str) -> str:
    """Return the contents of a JSON file."""
    ans = None
    with open(filename, "r") as f:
        ans = json.loads(f.read())

    return ans


def generate_markdown_from_template(template: str, data: dict) -> None:
    """Output Markdown from a template and data."""
    print(chevron.render(template, data))


def main() -> int:
    """Set up logging and call the Markdown generation function."""
    args: dict[str, str] = docopt.docopt(__doc__, version=_version)
    # Validate and convert arguments as needed
    schema: Schema = Schema(
        {
            "--log-level": And(
                str,
                Use(str.lower),
                lambda n: n in ("debug", "info", "warning", "error", "critical"),
                error="Possible values for --log-level are "
                + "debug, info, warning, error, and critical.",
            ),
            str: object,  # Don't care about other keys, if any
        }
    )

    try:
        validated_args: dict[str, Any] = schema.validate(args)
    except SchemaError as err:
        # Exit because one or more of the arguments were invalid
        print(err, file=sys.stderr)
        sys.exit(1)

    # Assign validated arguments to variables
    log_level: str = validated_args["--log-level"]

    # Set up logging
    logging.basicConfig(
        format="%(asctime)-15s %(levelname)s %(message)s", level=log_level.upper()
    )

    # Render Markdown from template and data
    generate_markdown_from_template(
        load(validated_args["<md_template>"]),
        load_json(validated_args["<template_data_json>"]),
    )

    # Stop logging and clean up
    logging.shutdown()
    return 0
