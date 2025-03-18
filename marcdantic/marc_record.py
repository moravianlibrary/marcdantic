from typing import Any, ClassVar, Dict, List
from .mapper import MarcMapper

from pydantic import BaseModel, model_validator
from .default_mapping import DEFAULT_MAPPING

from .fieldsets import (
    ControlFields,
    Leader,
    NumbersAndCodes,
    RepeatableField,
    MarcIssue,
    TitleRelated,
)

LEADER_LENGTH = 24
DIRECTORY_ENTRY_LENGTH = 12

LocalFields = Dict[
    str, Dict[str, str | List[str]] | List[Dict[str, str | List[str]]]
]


class MarcRecord(BaseModel):
    _mapper: ClassVar[MarcMapper] = MarcMapper(mapping=DEFAULT_MAPPING)
    _encoding: ClassVar[str] = "utf-8"

    leader: Leader

    control_fields: ControlFields

    numbers_and_codes: NumbersAndCodes | None = None
    title_related: TitleRelated | None = None

    issues: RepeatableField[MarcIssue] = None

    local: LocalFields = {}

    def has_local(self, field: str, subfield: str) -> bool:
        return field in self.local and (
            isinstance(self.local[field], list)
            and any(subfield in entry for entry in self.local[field])
            or subfield in self.local[field]
        )

    def get_local(self, field: str, subfield: str) -> str | List[str]:
        if isinstance(self.local[field], list):
            values = [entry[subfield] for entry in self.local[field]]
            if not values:
                raise KeyError(
                    f"Subfield '{subfield}' not found in field '{field}'"
                )
            return values
        return self.local[field][subfield]

    @model_validator(mode="before")
    @classmethod
    def from_bytes(cls, data: Any) -> Dict[str, Any]:
        if isinstance(data, dict):
            return data

        if not isinstance(data, bytes):
            raise TypeError(
                "Expected data of type 'bytes', "
                f"got '{type(data).__name__}' instead."
            )

        def ascii(data: bytes) -> str:
            return data.decode("ascii")

        def ascii_slice(data: bytes, start: int, end: int) -> str:
            return ascii(data[start:end])

        def decode(data: bytes) -> str:
            return data.decode(cls._encoding)

        def decode_slice(data: bytes, start: int, end: int) -> str:
            return decode(data[start:end])

        def decode_int_slice(data: bytes, start: int, end: int) -> int:
            return int(decode_slice(data, start, end).strip() or 0)

        # Parse Leader Data
        record = {
            "leader": {
                "record_length": decode_int_slice(data, 0, 5),
                "record_status": decode_slice(data, 5, 6),
                "type_of_record": decode_slice(data, 6, 7),
                "bibliographic_level": decode_slice(data, 7, 8),
                "control_type": decode_slice(data, 8, 9),
                "character_encoding_scheme": decode_slice(data, 9, 10),
                "base_address_of_data": decode_int_slice(data, 12, 17),
                "encoding_level": decode_slice(data, 17, 18),
                "cataloging_form": decode_slice(data, 18, 19),
                "multipart_resource_record_level": decode_slice(data, 19, 20),
                "entry_map": decode_slice(data, 20, 24),
            }
        }

        def add_fixed_field(tag: str, data: bytes) -> None:
            ff = cls._mapper.fixed_fields[tag]
            record.setdefault(ff.section, {})[ff.field] = decode(data)

        def add_variable_field(tag: str, data: bytes) -> None:
            vf = cls._mapper.variable_fields[tag]

            ind1 = ascii_slice(entry_data, 0, 1)
            ind2 = ascii_slice(entry_data, 1, 2)

            if data[2:3] != b"\x1f":
                raise ValueError(f"Invalid data for variable field {tag}")

            record.setdefault(vf.section, {})
            new_entry = {}

            if ind1 != " ":
                new_entry["ind1"] = ind1

            if ind2 != " ":
                new_entry["ind2"] = ind2

            for subfield_entry in entry_data[3:].split(b"\x1f"):
                code = ascii_slice(subfield_entry, 0, 1)

                if code not in vf.subfields:
                    continue

                value = decode(subfield_entry[1:])

                subfield_name = vf.subfields[code].subfield
                if vf.subfields[code].repeatable:
                    new_entry.setdefault(subfield_name, []).append(value)
                else:
                    new_entry[subfield_name] = value

            # Handle Repeatable Fields
            if vf.repeatable:
                record[vf.section].setdefault(vf.field, []).append(new_entry)
            else:
                record[vf.section][vf.field] = new_entry

        base_address = record["leader"]["base_address_of_data"]
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

            if entry_tag in cls._mapper.fixed_fields:
                add_fixed_field(entry_tag, entry_data)
            elif entry_tag in cls._mapper.variable_fields:
                add_variable_field(entry_tag, entry_data)

        return record
