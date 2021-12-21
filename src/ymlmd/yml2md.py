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
import dateparser
import docopt
from schema import And, Schema, SchemaError, Use
import yaml

from ._version import __version__

Software = list[dict[str, Any]]


def load(filename: str) -> Software:
    """Load the YML into a Python dictionary."""
    ans = None
    with open(filename, "r") as f:
        ans = yaml.safe_load(f)

    return ans


def calculate_status(software: Software) -> Software:
    """Calculate status field for each software entry."""
    for s in software:
        if len(s["affected_versions"]) == 0:
            if len(s["patched_versions"]) == 0:
                if s["investigated"]:
                    s["status"] = "Not Affected"
                else:
                    s["status"] = "Unknown"
            else:  # patched_versions is not empty
                s["status"] = "Fixed"
        else:  # affected versions is not empty
            if len(s["patched_versions"]) == 0:
                s["status"] = "Affected"
            else:
                s["status"] = "Fixed"
    return software


def generate_markdown(software: Software) -> None:
    """Generate markdown manually."""
    # Print header
    print(
        "| Vendor | Product | Affected Versions | Patched Versions | Status | Vendor Link | Notes | References | Reporter | Last Updated |"
    )
    print(
        "| ------ | ------- | ----------------- | ---------------- | ------ | ----------- | ----- | ---------- | -------- | ------------ |"
    )
    # Print table converting lists to comma separated strings
    for s in software:
        print(
            "| {vendor} | {product} | {affected_versions} | {patched_versions} | {status} | {vendor_link} | {notes} | {references} | {reporter} | {last_updated} |".format(
                vendor=s["vendor"],
                product=s["product"],
                affected_versions=",".join(
                    [x for x in s["affected_versions"] if len(x) != 0]
                ),
                patched_versions=",".join(
                    [x for x in s["patched_versions"] if len(x) != 0]
                ),
                status=s["status"],
                # convert vendor link to markdown link if it starts with http
                vendor_link=f'[link]({s["vendor_link"]})'
                if s["vendor_link"].startswith("http")
                else s["vendor_link"],
                notes=s["notes"],
                references="; ".join([x for x in s["references"] if len(x) != 0]),
                reporter=s["reporter"],
                # create a datetime from string and print date portion
                last_updated=dateparser.parse(s["last_updated"]).strftime("%Y-%m-%d"),
            )
        )


def main() -> int:
    """Set up logging and call the data loading, data conversion, and Markdown generation functions."""
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

    # Do that voodoo that you do so well...
    generate_markdown(calculate_status(load(validated_args["<yml_file>"])))

    # Stop logging and clean up
    logging.shutdown()
    return 0
