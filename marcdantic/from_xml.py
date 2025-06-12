from collections import Counter
from typing import Any, Dict, List

from lxml.etree import _Element

from .constants import LEADER_LENGTH, MARC_NS
from .mapper import MarcMapper


def from_xml(root: _Element, mapper: MarcMapper) -> Dict[str, Any]:
    record: Dict[str, Any] = {"leader": {}}
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

    record["leader"] = {
        "record_length": int(leader_text[0:5].strip() or 0),
        "record_status": leader_text[5:6],
        "type_of_record": leader_text[6:7],
        "bibliographic_level": leader_text[7:8],
        "control_type": leader_text[8:9],
        "character_encoding_scheme": leader_text[9:10],
        "base_address_of_data": int(leader_text[12:17].strip() or 0),
        "encoding_level": leader_text[17:18],
        "cataloging_form": leader_text[18:19],
        "multipart_resource_record_level": leader_text[19:20],
        "entry_map": leader_text[20:24],
    }

    def add_fixed_field(tag: str, content: str) -> None:
        if tag not in mapper.fixed_fields:
            return

        field_info = mapper.fixed_fields[tag]
        record.setdefault(field_info.section, {})[field_info.field] = content

    def add_variable_field(
        tag: str, index: int, ind1: str, ind2: str, code: str, value: str
    ) -> bool:
        if tag not in mapper.variable_fields:
            return False

        field_info = mapper.variable_fields[tag]

        if code not in field_info.subfields:
            return False

        section = record.setdefault(field_info.section, {})

        subfield_name = field_info.subfields[code].subfield

        if field_info.repeatable:
            entries = section.setdefault(field_info.field, [])

            if index == len(entries):
                entries.append({"ind1": ind1, "ind2": ind2})

            entry = entries[index]
        elif index > 0:
            raise ValueError(f"Non-repeatable field {tag} repeated")
        elif field_info.field not in section:
            section[field_info.field] = (entry := {"ind1": ind1, "ind2": ind2})
        else:
            entry = section[field_info.field]

        if (
            not field_info.subfields[code].repeatable
            and subfield_name in entry
        ):
            raise ValueError(f"Non-repeatable subfield {code} repeated")

        if field_info.subfields[code].repeatable:
            entry.setdefault(subfield_name, []).append(value)
        else:
            entry[subfield_name] = value

        return True

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

        add_fixed_field(tag, text)
        append_to_marc(tag, text.encode("utf-8"))

    # Process Data Fields
    vf_indexes = Counter()

    for datafield in root.findall(".//marc:datafield", MARC_NS):
        tag = datafield.get("tag")
        index = vf_indexes[tag]

        ind1 = datafield.get("ind1", " ")
        ind2 = datafield.get("ind2", " ")

        marc_data = ind1.encode("ascii") + ind2.encode("ascii")

        was_added = False

        for subfield in datafield.findall("marc:subfield", MARC_NS):
            code = subfield.get("code")
            value = subfield.text

            marc_data += "\x1f".encode("utf-8")
            marc_data += f"{code}".encode("ascii")
            marc_data += f"{value}".encode("utf-8")

            was_added |= add_variable_field(
                tag, index, ind1, ind2, code, value
            )

        if was_added:
            vf_indexes[tag] += 1

        append_to_marc(tag, marc_data)

    directory.append(b"\x1e")
    marc_directory = b"".join(directory)
    marc_data = b"\x1e".join(data)

    base_address = LEADER_LENGTH + len(marc_directory)
    record_length = base_address + len(marc_data) + 1

    record["leader"].update(
        {
            "record_length": f"{record_length:04d}",
            "base_address_of_data": base_address,
        }
    )

    marc_leader = (
        str(record_length).zfill(5).encode("utf-8")
        + leader_text.encode("utf-8")[5:12]
        + str(base_address).zfill(5).encode("utf-8")
        + leader_text.encode("utf-8")[17:]
    )

    record["marc"] = marc_leader + marc_directory + marc_data + b"\x1d"

    return record
