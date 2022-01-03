"""normalize_yml YAML combination and normalizing tool.

Combines, normalizes, and sorts the YAML outputs of other scripts in this GitHub repository.

EXIT STATUS
    This utility exits with one of the following values:
    0   No error occurred.
    >0  An error occurred.

Usage:
  normalize-yml [--log-level=LEVEL] [--cisagov-format] <yml_file>...
  normalize-yml (-h | --help)

Options:
  -h --help              Show this message.
  -c --cisagov-format    Generate a YAML file using the cisagov software list
                         format.
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
import ruamel.yaml
from schema import And, Schema, SchemaError, Use
import yaml

from . import __version__

Software = list[dict[str, Any]]


def munge(filenames: list[str]) -> Software:
    """Munge together the "software" nodes from YAML files into a single Python dictionary."""
    ans = []
    for filename in filenames:
        with open(filename, "r") as f:
            ans.extend(yaml.safe_load(f)["software"])

    return ans


def normalize(software: Software) -> Software:
    """Normalize the software entries."""
    return software


def sort(software: Software) -> Software:
    """Sort the software entries."""
    software.sort(key=lambda x: (x["vendor"] + x["product"]).lower())
    return software


def main() -> None:
    """Set up logging and call the munging, normalizing, and sorting functions."""
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
    if validated_args["--cisagov-format"]:
        doc = {
            "version": "1.0",
            "software": sort(normalize(munge(validated_args["<yml_file>"]))),
        }
    else:
        doc = sort(normalize(munge(validated_args["<yml_file>"])))

    yml = ruamel.yaml.YAML()
    yml.indent(mapping=2, offset=2, sequence=4)
    yml.explicit_start = True
    yml.explicit_end = True
    yml.sort_base_mapping_type_on_output = False
    yml.allow_unicode = True
    yml.dump(doc, sys.stdout)

    # Stop logging and clean up
    logging.shutdown()
