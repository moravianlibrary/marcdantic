import re
from typing import Any, Dict

from .constants import CONTROL_FIELDS, DIRECTORY_ENTRY_LENGTH, LEADER_LENGTH
from .fields import FIELD_TAG_PATTERN
from .mapper import MARC_MAPPER


def from_mrc(data: bytes, encoding: str) -> Dict[str, Any]:
    """
    Parses a raw MARC21 record from its binary representation into
    a structured dictionary.

    This function reads a MARC record encoded as bytes (MARC21 format) and
    decodes its components including the leader, control fields,
    and variable fields with indicators and subfields.

    Parameters
    ----------
    data : bytes
        The raw MARC21 record bytes.
    encoding : str
        The character encoding used for decoding the MARC data fields
        (commonly 'utf-8' or 'marc8').

    Returns
    -------
    dict[str, Any]
        A dictionary with the following keys:
        - "marc": bytes
            The original raw MARC record bytes.
        - "leader": str
            The leader string extracted from the record
            (usually 24 characters).
        - "control_fields": Dict[str, str]
            Control fields (fixed fields without subfields), keyed by tag.
        - "variable_fields": Dict[str, List[Dict[str, Any]]]
            Variable fields keyed by tag, each containing:
              - 'ind1': first indicator character,
              - 'ind2': second indicator character,
              - 'subfields': dictionary of subfield codes mapped to
                lists of subfield values.

    Raises
    ------
    ValueError
        If the directory or field lengths are inconsistent
        (not explicitly raised, but such errors may arise from invalid data).

    Notes
    -----
    - The MARC directory is parsed to locate field tags, lengths, and offsets.
    - Tags are validated with a regex and mapped using `MARC_MAPPER` aliases
      if necessary.
    - Control fields (in CONTROL_FIELDS) are parsed as simple text values.
    - Variable fields include indicators and are split into subfields using
      the subfield delimiter (0x1F).
    - The function does not explicitly validate every MARC rule but assumes
      a well-formed input.
    """

    def ascii(data: bytes) -> str:
        return data.decode("ascii")

    def ascii_slice(data: bytes, start: int, end: int) -> str:
        return ascii(data[start:end])

    def decode(data: bytes) -> str:
        return data.decode(encoding)

    def decode_slice(data: bytes, start: int, end: int) -> str:
        return decode(data[start:end])

    record = {
        "marc": data,
        "leader": decode_slice(data, 0, LEADER_LENGTH),
        "control_fields": {},
        "variable_fields": {},
    }

    base_address = int(record["leader"][12:17].strip() or 0)
    directory = ascii_slice(data, LEADER_LENGTH, base_address - 1)
    field_total = len(directory) // DIRECTORY_ENTRY_LENGTH

    # Process Fields
    for field_count in range(field_total):
        entry_start = field_count * DIRECTORY_ENTRY_LENGTH
        entry_end = entry_start + DIRECTORY_ENTRY_LENGTH

        entry = directory[entry_start:entry_end]

        entry_tag = entry[0:3]
        entry_length = int(entry[3:7])
        entry_offset = int(entry[7:12])

        data_start = base_address + entry_offset
        data_end = data_start + entry_length - 1

        entry_data = data[data_start:data_end]

        if not re.match(FIELD_TAG_PATTERN, entry_tag):
            if entry_tag not in MARC_MAPPER.tag_alias:
                print(f"Warning: Invalid MARC tag '{entry_tag}' encountered. ")
                continue
            entry_tag = MARC_MAPPER.tag_alias[entry_tag]

        if entry_tag in CONTROL_FIELDS:
            record["control_fields"][entry_tag] = decode(entry_data)
        else:
            variable_field = {
                "ind1": ascii_slice(entry_data, 0, 1),
                "ind2": ascii_slice(entry_data, 1, 2),
            }

            subfields = {}
            for subfield_entry in entry_data[3:].split(b"\x1f"):
                subfields.setdefault(decode(subfield_entry[0:1]), []).append(
                    decode(subfield_entry[1:])
                )

            variable_field["subfields"] = subfields

            record["variable_fields"].setdefault(entry_tag, []).append(
                variable_field
            )

    return record
