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

## Common YML format ##

The common YML format looks like this:

```yaml
---
version: '1.0'
software:
- affected_versions:
    - 1.1
    - 1.2
  last_updated: '2021-12-17T16:21:12+00:00'
  notes: Blah blah blah
  patched_versions:
    - >1.1,<1.2
    - >1.2,<1.3
    - >=1.3
  product: ProductA
  references:
    - https://www.reddit.com/r/Vendor1/comments/abcdef/log4j
  reporter: cisagov
  status: Fix
  vendor: Vendor1
  vendor_links:
    - https://vendor1.com/discussion/comment/622612/#Comment_622612
- affected_versions:
    - 2.2
  last_updated: '2021-12-18T16:21:12+00:00'
  notes: Blah blah blah
  patched_versions:
    - >=2.2
  product: ProductB
  references:
    - https://www.computerings.com/Vendor2/log4j_vulnerability
    - https://www.zazz.org/new_vulnerability
  reporter: cisagov
  status: Fix
  vendor: Vendor2
  vendor_links:
    - https://vendor2.com/ReleaseNotes
...
```

The fields and their descriptions are as follows:

| Field  | Description |
| ------ | ----------- |
| `affected_versions` | A list of the versions of the product that are vulnerable to the log4j vulnerability. |
| `last_updated` | The [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) timestamp denoting when the product information was last updated. |
| `notes` | A free-form text field for additional notes. |
| `patched_versions` | A list of the versions of the product that are patched and therefore unaffected by the log4j vulnerability. |
| `product` | The name of the software product. |
| `references` | A list of links to non-vendor sources concerning the software product and the log4j vulnerability. |
| `reporter` | The entity reporting information about the software product. |
| `status` | The current status of the software product with respect to the log4j vulnerability. |
| `vendor` | The name of the software vendor. |
| `vendor_links` | A list of links to the vendor's website concerning the software product and the log4j vulnerability. |

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
