import re
from typing import Any, Dict

from .constants import DIRECTORY_ENTRY_LENGTH, FIXED_FIELDS, LEADER_LENGTH
from .fields import FIELD_TAG_PATTERN
from .mapper import MARC_MAPPER


def from_mrc(data: bytes, encoding: str) -> Dict[str, Any]:
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
        "fixed_fields": {},
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

        if entry_tag in FIXED_FIELDS:
            record["fixed_fields"][entry_tag] = decode(entry_data)
        else:
            variable_field = {
                "ind1": ascii_slice(entry_data, 0, 1),
                "ind2": ascii_slice(entry_data, 1, 2),
            }

            subfields = {}
            for subfield_entry in entry_data[3:].split(b"\x1f"):
                subfields.setdefault(subfield_entry[0:1], []).append(
                    decode(subfield_entry[1:])
                )

            variable_field["subfields"] = subfields

            record["variable_fields"].setdefault(entry_tag, []).append(
                variable_field
            )

    return record
