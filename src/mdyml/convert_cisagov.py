"""convert_cisagov Markdown conversion tool.

Fetches the contents of the cisagov GitHub repository and converts it to YAML.

EXIT STATUS
    This utility exits with one of the following values:
    0   No error occurred.
    >0  An error occurred.

Usage:
  convert-cisagov [--log-level=LEVEL]
  convert-cisagov (-h | --help)

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
import ruamel.yaml
from schema import And, Schema, SchemaError, Use

from . import DEFAULT_CVE_ID, MD_LINK_RE, ORDERED_CVE_IDS
from ._version import __version__

RAW_URL = "https://raw.githubusercontent.com/cisagov/log4j-affected-db/develop/SOFTWARE-LIST.md"

EXPECTED_COLUMN_NAMES = [
    "vendor",
    "product",
    "versions",
    "status",
    "update_available",  # This column will be ignored as it can be inferred from patched_versions
    "vendor_link",
    "notes",
    "references",
    "last_updated",
]
EXPECTED_COLUMN_COUNT = len(EXPECTED_COLUMN_NAMES)


def convert() -> None:
    """Parse the Markdown at the given URL and convert it to YAML."""
    # Get the Markdown
    logging.info("Reading Markdown at %s", RAW_URL)
    # We are using a hardcoded URL so there is no danger of unexpected schemes.
    response = urllib.request.urlopen(RAW_URL)  # nosec

    # Read rows from all tables
    table_rows = []
    in_table = False
    skip_next_line = False
    for raw_line in response:
        line = html.unescape(raw_line.decode("utf-8"))
        logging.debug("Read line: %s", line)
        if skip_next_line:
            skip_next_line = False
            continue
        if not in_table and line.startswith("|"):
            logging.debug("Table start detected")
            # Remove any trailing newline, any beginning or ending pipes, and
            # split the remaining value on pipes.
            possible_header_columns = line.rstrip().strip("|").split("|")
            if len(possible_header_columns) == EXPECTED_COLUMN_COUNT:
                in_table = True
                skip_next_line = True
            continue
        if in_table and not line.startswith("|"):
            logging.warning("Line does not start with |, skipping: %s", line)
            continue
        if in_table:
            logging.debug("Appending row")
            table_rows.append(line)
    logging.info("Done reading markdown table %d rows.", len(table_rows))

    # Process all the data into a list of dictionaries
    out_dict_list = []
    row_count = 0
    for row in table_rows:
        row_count += 1
        in_row_list = row.split("|")[1:-1]
        logging.debug(
            "Processing line %d with %d columns: %s", row_count, len(in_row_list), row
        )
        if len(in_row_list) != EXPECTED_COLUMN_COUNT:
            logging.warning(
                "Skipping line %d with unexpected number of columns %d: %s",
                row_count,
                len(in_row_list),
                in_row_list,
            )
            continue
        # Trim whitespace from each field
        in_row_list = [field.strip() for field in in_row_list]
        # Create a dictionary from the row data
        in_row_dict = dict(zip(EXPECTED_COLUMN_NAMES, in_row_list))
        # Create a dictionary for our calculated output
        out_dict = {}
        out_dict["vendor"] = in_row_dict["vendor"]
        out_dict["product"] = in_row_dict["product"]
        out_dict["cves"] = {}
        for cve in ORDERED_CVE_IDS:
            out_dict["cves"][cve] = {
                "investigated": False,
                "affected_versions": [],
                "fixed_versions": [],
                "unaffected_versions": [],
            }

        # Determine where the data from the versions column is routed using the status column
        if in_row_dict["versions"]:
            # Spit versions out by comma and trim whitespace
            versions = [v.strip() for v in in_row_dict["versions"].split(",")]
            match in_row_dict["status"].lower():
                case "not affected":
                    out_dict["cves"][DEFAULT_CVE_ID]["investigated"] = True
                    out_dict["cves"][DEFAULT_CVE_ID]["unaffected_versions"] = versions
                case "affected":
                    out_dict["cves"][DEFAULT_CVE_ID]["investigated"] = True
                    out_dict["cves"][DEFAULT_CVE_ID]["affected_versions"] = versions
                case "fixed":
                    out_dict["cves"][DEFAULT_CVE_ID]["investigated"] = True
                    out_dict["cves"][DEFAULT_CVE_ID]["fixed_versions"] = versions
                case _:  # anything else; unknown, or missing
                    out_dict["cves"][DEFAULT_CVE_ID]["affected_versions"] = versions

        # Extract link from Markdown
        vendor_link_match = MD_LINK_RE.match(in_row_dict["vendor_link"])
        if vendor_link_match:
            out_dict["vendor_links"] = [vendor_link_match.group("link")]
        else:
            out_dict["vendor_links"] = []

        out_dict["notes"] = in_row_dict["notes"]
        out_dict["references"] = [in_row_dict["references"]]
        out_dict["reporter"] = "cisagov"
        # Parse the existing date, or not
        if parsed_date := dateparser.parse(in_row_dict["last_updated"]):
            # Check if parsed date has a timezone
            if parsed_date.tzinfo is None:
                # Add the UTC timezone to the parsed date
                parsed_date.replace(tzinfo=timezone.utc)
            out_dict["last_updated"] = parsed_date.isoformat(timespec="seconds")
        else:
            out_dict["last_updated"] = datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            )

        # # Sort record keys
        # in_row_dict = {key: in_row_dict[key] for key in ORDERED_FIELD_NAMES}
        out_dict_list.append(out_dict)

    doc = {"version": "1.0", "software": out_dict_list}

    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, offset=2, sequence=4)
    yaml.explicit_start = True
    yaml.explicit_end = True
    yaml.sort_base_mapping_type_on_output = False
    yaml.allow_unicode = True
    yaml.dump(doc, sys.stdout)


def main() -> None:
    """Set up logging and call the mdyml function."""
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
