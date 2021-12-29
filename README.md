# log4j-md-yml #

[![GitHub Build Status](https://github.com/cisagov/log4j-md-yml/workflows/build/badge.svg)](https://github.com/cisagov/log4j-md-yml/actions)
[![Coverage Status](https://coveralls.io/repos/github/cisagov/log4j-md-yml/badge.svg?branch=develop)](https://coveralls.io/github/cisagov/log4j-md-yml?branch=develop)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/cisagov/log4j-md-yml.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/log4j-md-yml/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/cisagov/log4j-md-yml.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/log4j-md-yml/context:python)
[![Known Vulnerabilities](https://snyk.io/test/github/cisagov/log4j-md-yml/develop/badge.svg)](https://snyk.io/test/github/cisagov/log4j-md-yml)

This repository contains Python code to:

1. (Work in Progress) Translate the Markdown table of vulnerable software
   from [NCSC-NL/log4shell](https://github.com/NCSC-NL/log4shell) into a
   common YAML format: [`convert-nscs-nl`](src/mdyml/convert_ncsc_nl.py)
1. Merge the YAML from the previous step with the YAML from
   [cisagov/log4j-affected-db](https://github.com/cisagov/log4j-affected-db)
   into one grand YAML file: [`normalize-yml`](src/yml/normalize_yml.py)
1. Generate a Markdown table from the YAML output of the previous step:
   [`yml2md`](src/ymlmd/yml2md.py)
1. Generate Markdown based on a Markdown template file and a file containing
   a Markdown table such as the output of the previous step:
   [`md-from-template`](src/md_from_template/md_from_template.py)

## Common YAML format ##

The common YAML format looks like this:

```yaml
---
version: '1.0'
software:
  -  cves:
      - affected_versions:
          - 1.0
          - 1.1
        cve: cve-2021-44228
        fixed_versions:
          - 1.2
        investigated: true
        unaffected_versions: []
    notes: Blah blah blah
    product: ProductA
    references:
      - https://www.reddit.com/r/Vendor1/comments/abcdef/log4j
    reporter: cisagov
    vendor: Vendor1
    vendor_links:
      - https://vendor1.com/discussion/comment/622612/#Comment_622612
  ⋮
...
```

The fields and their descriptions are as follows:

| Field  | Description |
| ------ | ----------- |
| `cves` | A list of dictionaries containing a CVE ID together with vulnerability information about the product specific to that CVE. |
| `notes` | A free-form text field for additional notes. |
| `product` | The name of the software product. |
| `references` | A list of links to non-vendor sources concerning the software product and the log4j vulnerabilities. |
| `reporter` | The entity reporting information about the software product. |
| `vendor` | The name of the software vendor. |
| `vendor_links` | A list of links to the vendor's website concerning the software product and the log4j vulnerabilities. |

The subfields in the `cves` entries are as follows:

| `cves` subfield  | Description |
| ---------------- | ----------- |
| `cve` | The [CVE ID](https://www.cve.org/) of the particular log4j vulnerability.  The only valid value is [`cve-2021-44228`](https://www.cve.org/CVERecord?id=CVE-2021-44228). |
| `affected_versions` | A list of the versions of the product that are vulnerable to the particular CVE. |
| `fixed_versions` | A list of the versions of the product that are patched and therefore unaffected by the particular CVE. |
| `investigated` | A Boolean value indicating whether or not the product's vulnerability to the particular CVE has been investigated. |
| `unaffected_versions` | A list of the versions of the product that are completely unaffected by the particular CVE. |

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
