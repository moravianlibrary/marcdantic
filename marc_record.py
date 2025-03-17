from typing import Any

from pydantic import BaseModel, model_validator

from record_parts import ControlFields, Leader, NumbersAndCodes

LEADER_LENGTH = 24
DIRECTORY_ENTRY_LENGTH = 12


class MarcRecord(BaseModel):
    leader: Leader

    # control_fields: ControlFields
    # numbers_and_codes: NumbersAndCodes

    @model_validator(mode="before")
    @classmethod
    def validate(cls, data: Any) -> "MarcRecord":
        if isinstance(data, MarcRecord):
            return data

        if not isinstance(data, bytes):
            raise TypeError(
                "Expected data of type 'bytes', "
                f"got '{type(data).__name__}' instead."
            )

        leader = Leader.from_bytes(data[0:24])

        directory = data[
            LEADER_LENGTH : leader.base_address_of_data - 1
        ].decode("ascii")

        field_total = len(directory) / DIRECTORY_ENTRY_LENGTH
        print(field_total)

        field_count = 0
        while field_count < field_total:
            entry_start = field_count * DIRECTORY_ENTRY_LENGTH
            entry_end = entry_start + DIRECTORY_ENTRY_LENGTH
            entry = directory[entry_start:entry_end]
            entry_tag = entry[0:3]
            entry_length = int(entry[3:7])
            entry_offset = int(entry[7:12])
            entry_data = data[
                leader.base_address_of_data
                + entry_offset : leader.base_address_of_data
                + entry_offset
                + entry_length
                - 1
            ]
            print(entry_tag)
            field_count += 1

        control_fields_data = data[24 : leader.base_address_of_data]

        # for field in data[24:].split(b"\x1E"):
        #     print(field)

        return {"leader": leader}
