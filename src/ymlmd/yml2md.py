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

# cisagov Libraries
from mdyml import DEFAULT_CVE_ID

from . import __version__

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
        # We are only worrying about the main (default) CVE for now.
        default_cve = s["cves"][DEFAULT_CVE_ID]
        if len(default_cve["affected_versions"]) == 0:
            if len(default_cve["fixed_versions"]) == 0:
                if default_cve["investigated"]:
                    s["status"] = "Not Affected"
                else:
                    s["status"] = "Unknown"
            else:  # fixed_versions is not empty
                s["status"] = "Fixed"
        else:  # affected versions is not empty
            if len(default_cve["fixed_versions"]) == 0:
                s["status"] = "Affected"
            else:
                s["status"] = "Fixed"
    return software


def generate_markdown(software: Software) -> None:
    """Generate Markdown manually."""
    header_fields = [
        "Vendor",
        "Product",
        "Affected Versions",
        "Patched Versions",
        "Status",
        "Vendor Links",
        "Notes",
        "References",
        "Reporter",
        "Last Updated",
    ]

    # Print header and delimiter rows
    for row_contents in [header_fields, ["-" * len(field) for field in header_fields]]:
        print(f'| {" | ".join(row_contents)} |')

    # Print table converting lists to Markdown table rows
    for i, s in enumerate(software, start=1):
        default_cve = s["cves"][DEFAULT_CVE_ID]
        try:
            print(
                "| {vendor} | {product} | {affected_versions} | {patched_versions} | {status} | {vendor_links} | {notes} | {references} | {reporter} | {last_updated} |".format(
                    vendor=s["vendor"],
                    product=s["product"],
                    affected_versions=", ".join(
                        [x for x in default_cve["affected_versions"] if len(x) != 0]
                    ),
                    patched_versions=", ".join(
                        [x for x in default_cve["fixed_versions"] if len(x) != 0]
                    ),
                    status=s["status"],
                    # convert vendor links to Markdown links if they start
                    # with http
                    vendor_links=", ".join(
                        [
                            f"[link]({link})" if link.startswith("http") else link
                            for link in s["vendor_links"]
                        ]
                    ),
                    notes=s["notes"],
                    references="; ".join([x for x in s["references"] if len(x) != 0]),
                    reporter=", ".join(
                        f"[{i['name']}]({i['url']})" for i in s["reporter"]
                    ),
                    # create a datetime from string and print date portion
                    last_updated=dateparser.parse(s["last_updated"]).strftime(
                        "%Y-%m-%d"
                    ),
                )
            )
        except KeyError:
            logging.exception("%d: %s", i, s)


def main() -> None:
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
