# marcdantic

**marcdantic** is a Python package designed to parse, validate, and manipulate MARC (Machine-Readable Cataloging) records, a standard data format widely used by libraries and archives for bibliographic information.

Built on **Pydantic** for robust data validation, **marcdantic** supports parsing MARC records from both **binary MARC (MRC)** and **MARC XML** formats, producing clean, structured Python dictionaries for further processing or storage.

---

## Features

* **Binary MARC Parsing (`from_mrc`)**: Decode raw MARC21 records from their binary format with support for various encodings. Extracts leaders, fixed fields, variable fields, indicators, and subfields.
* **MARC XML Parsing (`from_xml`)**: Parse MARC XML records, validate leaders and fields, and reconstruct MARC binary data with correct directory and field lengths.
* **Pydantic Models for Queries**: Define complex MARC search queries using Pydantic models with strong typing and operator support (exact match, regex, contains, etc.).
* **Field Validation**: Validates field tags, subfield codes, and indicator characters according to MARC standards.
* **Flexible and Extensible**: Easily customize field mappings, tag aliases, and add your own MARC processing logic.

Got it! Here’s the updated **Installation** section for your **marcdantic** README using the style and structure from your other lib’s README, but without the YAZ-related notes:

---

## Installation

### Installing from GitHub using version tag

You can install **marcdantic** directly from GitHub for a specific version tag:

```bash
pip install git+https://github.com/moravianlibrary/marcdantic.git@v1.2.3
```

*Replace `v1.2.3` with the desired version tag.*

To always install the most recent version, use the latest tag:

```bash
pip install git+https://github.com/moravianlibrary/marcdantic.git@latest
```

### Installing local dev environment

Install required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

---

## Basic Usage

### Parsing a binary MARC record

```python
from marcdantic.parsers import from_mrc

with open("record.mrc", "rb") as f:
    marc_bytes = f.read()

record = from_mrc(marc_bytes, encoding="utf-8")
print(record["leader"])
print(record["fixed_fields"])
print(record["variable_fields"])
```

### Parsing a MARC XML record

```python
from lxml import etree
from marcdantic.parsers import from_xml

xml_root = etree.parse("record.xml").getroot()
record = from_xml(xml_root)
print(record["leader"])
print(record["fixed_fields"])
print(record["variable_fields"])
print(record["marc"])  # reconstructed MARC binary
```

### Constructing MARC search queries

```python
from marcdantic.search import MarcCondition, MarcBoolQuery, MarcSearchRequest, SearchOperator

query = MarcBoolQuery(
    must=[
        MarcCondition(field="245", subfield="a", value="Python", operator=SearchOperator.Contains),
        MarcCondition(field="100", subfield="a", value="Guido van Rossum")
    ]
)

search_request = MarcSearchRequest(query=query, page=1, page_size=20)
```

---

## Resources

* [Ex Libris Aleph X-Services – Present Service](https://developers.exlibrisgroup.com/aleph/apis/aleph-x-services/present/)
* [Library of Congress MARC Bibliographic Standard](https://www.loc.gov/marc/bibliographic/)
* [A Proposal to Serialize MARC in JSON (Archived)](https://web.archive.org/web/20151112001548/http://dilettantes.code4lib.org/blog/2010/09/a-proposal-to-serialize-marc-in-json)

These references provide background on MARC structure, encoding, and usage in real-world library systems.
