"""md_from_template Markdown generation tool.

Output Markdown based on a Markdown template file and a file containing a
Markdown table with the software from cisagov/log4j-affected-db.

EXIT STATUS
    This utility exits with one of the following values:
    0   No error occurred.
    >0  An error occurred.

Usage:
  md-from-template [--log-level=LEVEL] <md_template> <software_md_table_file>
  md-from-template (-h | --help)

Options:
  -h --help              Show this message.
  --log-level=LEVEL      If specified, then the log level will be set to
                         the specified value.  Valid values are "debug", "info",
                         "warning", "error", and "critical". [default: info]
"""

# Standard Python Libraries
import logging
import sys
from typing import Any

# Third-Party Libraries
import chevron
import docopt
from schema import And, Schema, SchemaError, Use

from ._version import __version__


def load(filename: str) -> str:
    """Return the contents of a file."""
    ans = None
    with open(filename, "r") as f:
        ans = f.read().rstrip()

    return ans


def build_template_data(software_markdown_table_file: str) -> dict:
    """Return a dict containing data needed to render the Markdown template."""
    # The only key in the template so far is "software_markdown_table".
    # We read the Markdown for this value from the supplied file.
    template_data = {"software_markdown_table": load(software_markdown_table_file)}

    return template_data


def generate_markdown_from_template(template: str, data: dict) -> None:
    """Output Markdown from a template and data."""
    print(chevron.render(template, data))


def main() -> int:
    """Set up logging and call the Markdown generation function."""
    args: dict[str, str] = docopt.docopt(__doc__, version=__version__)
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

    # Build template data dictionary
    template_data = build_template_data(validated_args["<software_md_table_file>"])

    # Render Markdown from template and data
    generate_markdown_from_template(
        load(validated_args["<md_template>"]),
        template_data,
    )

    # Stop logging and clean up
    logging.shutdown()
    return 0
