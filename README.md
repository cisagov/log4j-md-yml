# md-table-to-yml #

[![GitHub Build Status](https://github.com/cisagov/md-table-to-yml/workflows/build/badge.svg)](https://github.com/cisagov/md-table-to-yml/actions)
[![Coverage Status](https://coveralls.io/repos/github/cisagov/md-table-to-yml/badge.svg?branch=develop)](https://coveralls.io/github/cisagov/md-table-to-yml?branch=develop)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/cisagov/md-table-to-yml.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/md-table-to-yml/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/cisagov/md-table-to-yml.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/md-table-to-yml/context:python)
[![Known Vulnerabilities](https://snyk.io/test/github/cisagov/md-table-to-yml/develop/badge.svg)](https://snyk.io/test/github/cisagov/md-table-to-yml)

This repository contains Python code to:

1. Translate the Markdown table of vulnerable software from
   [NCSC-NL/log4shell](https://github.com/NCSC-NL/log4shell) into a
   common YML format.
1. Merge the YML from the previous step with the YML from
   [cisagov/log4j-affected-db](https://github.com/cisagov/log4j-affected-db)
   into one grand YML file.
1. Generate a Markdown table from the YML output of the previous step.

## Contributing ##

We welcome contributions!  Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) for
details.

## License ##

This project is in the worldwide [public domain](LICENSE).

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
the [CC0 1.0 Universal public domain
dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0
dedication. By submitting a pull request, you are agreeing to comply
with this waiver of copyright interest.
