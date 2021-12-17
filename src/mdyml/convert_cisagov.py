"""convert_cisagov markdown conversion tool.

Fetches the contents of the cisagov GitHub repository and converts it to YAML.

EXIT STATUS
    This utility exits with one of the following values:
    0   No error occurred.
    >0  An error occurred.

Usage:
  convert_cisagov [--log-level=LEVEL]
  convert_cisagov (-h | --help)

Options:
  -h --help              Show this message.
  --log-level=LEVEL      If specified, then the log level will be set to
                         the specified value.  Valid values are "debug", "info",
                         "warning", "error", and "critical". [default: info]
"""

# Standard Python Libraries
from datetime import datetime, timezone
import html
import logging
import sys
from typing import Any
import urllib.request

# Third-Party Libraries
import dateparser
import docopt
import pytz
from schema import And, Schema, SchemaError, Use
import yaml

from . import MD_LINK_RE, ORDERED_FIELD_NAMES, _version

RAW_URL = (
    "https://raw.githubusercontent.com/cisagov/log4j-affected-db/develop/README.md"
)
EXPECTED_COLUMNS = 9


def convert() -> None:
    # Parse the markdown at the given URL and convert it to YAML.

    # Get the markdown
    response = urllib.request.urlopen(RAW_URL)

    # Read rows from all tables
    table_rows = []
    in_table = False
    skip_next_line = False
    for raw_line in response:
        line = html.unescape(raw_line.decode("utf-8"))
        if skip_next_line:
            skip_next_line = False
            continue
        if not in_table and line.startswith("|") and "Vendor link" in line:
            table_field_names = line.split("|")[1:-1]
            assert (
                len(table_field_names) == EXPECTED_COLUMNS
            ), f"Expected {EXPECTED_COLUMNS} fields in header line, found: {table_field_names}"
            in_table = True
            skip_next_line = True
            continue
        if not line.startswith("|"):
            in_table = False
            continue
        if in_table:
            table_rows.append(line[1:-1])

    # Set our field names that line up with the columns in the table
    table_field_names = [
        "vendor",
        "product",
        "affected_versions",
        "status",
        "update_available",  # This field will be ignored as it can be inferred from patched_versions
        "vendor_link",
        "notes",
        "references",
        "last_updated",
    ]

    all_rows = []
    for row in table_rows:
        row_data = row.split("|")
        row_data = [cell.strip() for cell in row_data]
        # Combine header fields with data into a dict
        row_dict = dict(zip(table_field_names, row_data))
        if row_dict["affected_versions"]:
            row_dict["affected_versions"] = [row_dict["affected_versions"]]
        else:
            row_dict["affected_versions"] = []
        row_dict["patched_versions"] = []
        row_dict["references"] = [row_dict["references"]]
        row_dict["reporter"] = "cisagov"
        if row_dict["last_updated"]:
            # Parse the existing date
            parsed_date = dateparser.parse(row_dict["last_updated"])
            # Check if the parsed date has a timezone
            if parsed_date.tzinfo is None:
                # Add the UTC timezone
                parsed_date = pytz.utc.localize(parsed_date)
            row_dict["last_updated"] = parsed_date.isoformat(timespec="seconds")
        else:
            row_dict["last_updated"] = datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            )

        # Extract link from markdown
        vendor_link_match = MD_LINK_RE.match(row_dict["vendor_link"])
        if vendor_link_match:
            row_dict["vendor_link"] = vendor_link_match.group("link")
        # Sort record keys
        row_dict = {key: row_dict[key] for key in ORDERED_FIELD_NAMES}
        all_rows.append(row_dict)

    doc = {"version": "1.0", "software": all_rows}

    yaml.dump(
        doc,
        sys.stdout,
        explicit_start=True,
        explicit_end=True,
        sort_keys=False,
        allow_unicode=True,
    )


def main() -> int:
    """Set up logging and call the mdyml function."""
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

    convert()

    # Stop logging and clean up
    logging.shutdown()
    return 0
