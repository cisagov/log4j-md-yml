"""yml2md Markdown table generation tool.

Generates a Markdown table from the combined, normalized, and sorted output of normalize_yml.

EXIT STATUS
    This utility exits with one of the following values:
    0   No error occurred.
    >0  An error occurred.

Usage:
  yml2md [--log-level=LEVEL] <yml_file>
  yml2md (-h | --help)

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
import docopt
from pytablewriter import MarkdownTableWriter
from schema import And, Schema, SchemaError, Use
import yaml

from . import _version

Software = list[dict[str, Any]]
TableData = list[list[Any]]

DataConversionMap = {
    "vendor": "Vendor",
    "product": "Product",
    # "investigated": "Investigated",
    "affected_versions": "Affected Versions",
    "patched_versions": "Patched Versions",
    "vendor_link": "Vendor Link",
    "notes": "Notes",
    "references": "References",
    "reporter": "Reporter",
    "last_updated": "Last Updated",
}


def load(filename: str) -> Software:
    """Load the YML into a Python dictionary."""
    ans = None
    with open(filename, "r") as f:
        ans = yaml.safe_load(f)

    return ans


def convert_data_format(software: Software) -> TableData:
    """Convert the YML data into a format that pytablewriter likes."""
    return [
        [
            s["vendor"],
            s["product"],
            # s["investigated"],
            ",".join([x for x in s["affected_versions"] if len(x) != 0]),
            ",".join([x for x in s["patched_versions"] if len(x) != 0]),
            s["vendor_link"],
            s["notes"],
            "\n".join([x for x in s["references"] if len(x) != 0]),
            s["reporter"],
            s["last_updated"],
        ]
        for s in software
    ]


def generate_markdown(data: TableData) -> None:
    """Generate the Markdown table."""
    writer = MarkdownTableWriter(
        headers=DataConversionMap.values(),
        value_matrix=data,
    )

    writer.write_table(flavor="github")


def main() -> int:
    """Set up logging and call the data loading, data conversion, and Markdown generation functions."""
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

    # Do that voodoo that you do so well...
    generate_markdown(convert_data_format(load(validated_args["<yml_file>"])))

    # Stop logging and clean up
    logging.shutdown()
    return 0
