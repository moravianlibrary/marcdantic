import re
from typing import Any, Dict, List

from lxml.etree import _Element

from marcdantic.fields import FIELD_TAG_PATTERN
from marcdantic.mapper import MARC_MAPPER

from .constants import LEADER_LENGTH, MARC_NS


def from_xml(root: _Element) -> Dict[str, Any]:
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
    def append_to_marc(tag: str, field_data: bytes) -> None:
        if len(tag) != 3:
            raise ValueError(f"Invalid tag: {tag}")

        nonlocal data_length

        directory.append(tag.encode("utf-8"))
        directory.append(f"{len(field_data) + 1:04d}".encode("utf-8"))
        directory.append(f"{data_length:05d}".encode("utf-8"))

        data_length += len(field_data) + 1

        data.append(field_data)

    # Process Control Fields
    for controlfield in root.findall(".//marc:controlfield", MARC_NS):
        tag = controlfield.get("tag")
        text = controlfield.text

        if not re.match(FIELD_TAG_PATTERN, tag):
            if tag not in MARC_MAPPER.tag_alias:
                print(f"Warning: Invalid MARC tag '{tag}' encountered. ")
                continue
            tag = MARC_MAPPER.tag_alias[tag]

        record["fixed_fields"][tag] = text
        append_to_marc(tag, text.encode("utf-8"))

    # Process Data Fields
    for datafield in root.findall(".//marc:datafield", MARC_NS):
        tag = datafield.get("tag")

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

        variable_field["subfields"] = subfields
        record["variable_fields"].setdefault(tag, []).append(variable_field)

        append_to_marc(tag, marc_data)

    directory.append(b"\x1e")
    marc_directory = b"".join(directory)
    marc_data = b"\x1e".join(data)

    base_address = LEADER_LENGTH + len(marc_directory)
    record_length = base_address + len(marc_data) + 1

    new_leader = (
        str(record_length).zfill(5).encode("utf-8")
        + leader_text.encode("utf-8")[5:12]
        + str(base_address).zfill(5).encode("utf-8")
        + leader_text.encode("utf-8")[17:]
    )

    record["marc"] = new_leader + marc_directory + marc_data + b"\x1d"
    record["leader"] = new_leader.decode("utf-8")

    return record
