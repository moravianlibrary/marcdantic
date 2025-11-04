import re
from typing import Any, Dict, List

from lxml.etree import _Element

from .constants import LEADER_LENGTH, MARC_NS, MAX_RECORD_LENGTH
from .context import MarcContext
from .fields import FIELD_TAG_PATTERN, MarcFieldSelector


def from_xml(root: _Element, context: MarcContext) -> Dict[str, Any]:
    """
    Parses a MARC record from its XML representation into
    a structured dictionary.

    This function converts an XML MARC record element
    (following MARCXML standard) into a dictionary containing:
      - the MARC leader string,
      - fixed control fields,
      - variable data fields (with indicators and subfields),
      - and a reconstructed raw MARC byte string compliant with MARC21 format.

    Parameters
    ----------
    root : lxml.etree._Element
        The root XML element of the MARC record
        (expected to use MARC XML namespace).

    Returns
    -------
    dict[str, Any]
        A dictionary with the following keys:
        - "leader": str
            The MARC leader string (24 characters).
        - "fixed_fields": Dict[str, str]
            Fixed fields with no subfields, keyed by their MARC tag.
        - "variable_fields": Dict[str, List[Dict[str, Any]]]
            Variable fields keyed by MARC tag; each field contains indicators
            and subfields.
        - "marc": bytes
            The reconstructed raw MARC21 byte sequence representing
            the full record.

    Raises
    ------
    ValueError
        If the leader string length is not equal to the expected LEADER_LENGTH.
        If a MARC tag does not have exactly 3 characters.

    Notes
    -----
    - The function validates tags against a pattern and substitutes aliases
      using `MARC_MAPPER`.
    - The leader and directory are rebuilt to reflect the reconstructed
      raw MARC bytes.
    - Fixed fields are stored in `fixed_fields` and variable data fields
      with indicators and subfields are stored in `variable_fields`.
    - The function builds the MARC record raw bytes
      with proper directory entries and field terminators
      as per MARC21 specification.
    """
    record: Dict[str, Any] = {
        "fixed_fields": {},
        "variable_fields": {},
    }
    directory: List[bytes] = []
    data: List[bytes] = []

    data_length = 0

    # Extract and Process Leader
    leader_text = root.find(".//marc:leader", MARC_NS).text

    if len(leader_text) != LEADER_LENGTH:
        raise ValueError(
            f"Invalid leader length: {len(leader_text)} "
            f"(expected {LEADER_LENGTH})"
        )

    record["leader"] = leader_text

    # Define a function to append data to the MARC bytes data
    def append_field_data(tag: str, field_data: bytes) -> int:
        if data_length > MAX_RECORD_LENGTH:
            raise ValueError(
                "MARC record exceeds maximum allowed length of 99,999 bytes."
            )

        directory.append(tag.encode("utf-8"))
        directory.append(f"{len(field_data) + 1:04d}".encode("utf-8"))
        directory.append(f"{data_length:05d}".encode("utf-8"))

        data_inc = len(field_data) + 1

        data.append(field_data)

        return data_inc

    # Process Control Fields
    for controlfield in root.findall(".//marc:controlfield", MARC_NS):
        tag = controlfield.get("tag")
        tag_alias = context.tag_aliases.get(tag)

        if tag_alias is None:
            pass
        elif tag_alias == "skip":
            continue
        elif isinstance(tag_alias, MarcFieldSelector):
            raise ValueError(
                f"Control field tag '{tag}' cannot map to a variable field."
            )
        else:
            tag = tag_alias

        if not re.match(FIELD_TAG_PATTERN, tag):
            if context.ignore_unknown_tags:
                continue
            raise ValueError(f"Invalid MARC tag '{tag}' encountered.")

        text = controlfield.text
        data_length += append_field_data(tag, text.encode("utf-8"))
        record["fixed_fields"][tag] = text

    # Process Data Fields
    for datafield in root.findall(".//marc:datafield", MARC_NS):
        tag = datafield.get("tag")
        tag_alias = context.tag_aliases.get(tag)

        if tag_alias is None:
            pass
        elif tag_alias == "skip":
            continue
        elif isinstance(tag_alias, MarcFieldSelector):
            tag = tag_alias.tag
            code = tag_alias.code
            value = datafield.text

            if not re.match(FIELD_TAG_PATTERN, tag):
                if context.ignore_unknown_tags:
                    continue
                raise ValueError(f"Invalid MARC tag '{tag}' encountered.")

            marc_data = " ".encode("ascii") + " ".encode("ascii")
            marc_data += "\x1f".encode("utf-8")
            marc_data += f"{code}".encode("ascii")
            marc_data += f"{value}".encode("utf-8")

            variable_field = {
                "ind1": " ",
                "ind2": " ",
                "subfields": {code: [value]},
            }

            data_length += append_field_data(tag, marc_data)
            record["variable_fields"].setdefault(tag, []).append(
                variable_field
            )
            continue
        else:
            tag = tag_alias

        if not re.match(FIELD_TAG_PATTERN, tag):
            if context.ignore_unknown_tags:
                continue
            raise ValueError(f"Invalid MARC tag '{tag}' encountered.")

        ind1 = datafield.get("ind1", " ")
        ind2 = datafield.get("ind2", " ")

        variable_field = {"ind1": ind1, "ind2": ind2}

        marc_data = ind1.encode("ascii") + ind2.encode("ascii")

        subfields = {}

        for subfield in datafield.findall("marc:subfield", MARC_NS):
            code = subfield.get("code")
            value = subfield.text

            subfields.setdefault(code, []).append(value)

            marc_data += "\x1f".encode("utf-8")
            marc_data += f"{code}".encode("ascii")
            marc_data += f"{value}".encode("utf-8")

        data_length += append_field_data(tag, marc_data)
        variable_field["subfields"] = subfields
        record["variable_fields"].setdefault(tag, []).append(variable_field)

    directory.append(b"\x1e")
    marc_directory = b"".join(directory)
    marc_data = b"\x1e".join(data)

    base_address = LEADER_LENGTH + len(marc_directory)
    record_length = base_address + len(marc_data) + 1

    if record_length > MAX_RECORD_LENGTH:
        raise ValueError(
            "MARC record exceeds maximum allowed length of 99,999 bytes."
        )

    new_leader_text = (
        str(record_length).zfill(5)
        + leader_text[5:12]
        + str(base_address).zfill(5)
        + leader_text[17:]
    )
    new_leader = new_leader_text.encode("ascii")

    record["marc"] = new_leader + marc_directory + marc_data + b"\x1d"
    record["leader"] = new_leader.decode("utf-8")

    return record
