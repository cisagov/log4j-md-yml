"""convert_ncsc_nl Markdown conversion tool.

Fetches the contents of the NCSC-NL/log4shell GitHub repository
and converts it to YAML.

EXIT STATUS
    This utility exits with one of the following values:
    0   No error occurred.
    >0  An error occurred.

Usage:
  convert-ncsc-nl [--log-level=LEVEL]
  convert-ncsc-nl (-h | --help)

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
import docopt
from schema import And, Schema, SchemaError, Use
import yaml

from . import MD_LINK_RE, __version__

RAW_URL = "https://raw.githubusercontent.com/NCSC-NL/log4shell/main/software/README.md"

EXPECTED_COLUMN_NAMES = [
    "vendor",
    "product",
    "affected_versions",
    "investigated",
    "notes",
    "vendor_link",
]
EXPECTED_COLUMN_COUNT = len(EXPECTED_COLUMN_NAMES)
ORDERED_FIELD_NAMES = [
    "Supplier",
    "Product",
    "Version (see Status)",
    "Status CVE-2021-4104",
    "Status CVE-2021-44228",
    "Status CVE-2021-45046",
    "Status CVE-2021-45105",
    "Notes",
    "Links",
]


def convert() -> None:
    """Parse the Markdown at the given URL and convert it to YAML."""
    # We are using a hardcoded URL so there is no danger of unexpected schemes.
    response = urllib.request.urlopen(RAW_URL)  # nosec

    # Read rows from all tables
    table_rows = []
    in_table = False
    skip_next_line = False
    for raw_line in response:
        line = html.unescape(raw_line.decode("utf-8"))
        if skip_next_line:
            skip_next_line = False
            continue
        if not in_table and line.startswith("|") and "Supplier" in line:
            in_table = True
            skip_next_line = True
            continue
        if not line.startswith("|"):
            in_table = False
            continue
        if in_table:
            table_rows.append(line)

    all_rows = []
    row_count = 0
    for row in table_rows:
        row_count += 1
        row_data = row.split("|")[1:-1]
        logging.debug(
            "Processing line %d with %d columns: %s", row_count, len(row_data), row
        )
        if len(row_data) != EXPECTED_COLUMN_COUNT:
            logging.warning(
                "Skipping line %d with unexpected number of columns %d: %s",
                row_count,
                len(row_data),
                row_data,
            )
            continue
        # Trim whitespace from each field
        row_data = [field.strip() for field in row_data]
        # Create a dictionary from the row data
        row_dict = dict(zip(EXPECTED_COLUMN_NAMES, row_data))
        row_dict["investigated"] = row_dict["investigated"].lower() in (
            "fix",
            "not vuln",
            "vulnerable",
            "workaround",
        )
        if row_dict["affected_versions"]:
            row_dict["affected_versions"] = [row_dict["affected_versions"]]
        else:
            row_dict["affected_versions"] = []
        row_dict["patched_versions"] = []
        row_dict["references"] = []
        row_dict["reporter"] = "ncsc-nl"
        row_dict["last_updated"] = datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        )
        # Extract link from Markdown
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


def main() -> None:
    """Set up logging and call the convert function."""
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

    convert()

    # Stop logging and clean up
    logging.shutdown()
