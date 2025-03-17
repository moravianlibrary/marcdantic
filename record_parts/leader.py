from pydantic import BaseModel, Field


class Leader(BaseModel):
    record_length: int = Field(..., ge=0, le=99999)
    record_status: str = Field(..., min_length=1, max_length=1)
    type_of_record: str = Field(..., min_length=1, max_length=1)
    bibliographic_level: str = Field(..., min_length=1, max_length=1)
    control_type: str = Field(..., min_length=1, max_length=1)
    character_encoding_scheme: str = Field(..., min_length=1, max_length=1)
    base_address_of_data: int = Field(..., ge=0)
    encoding_level: str = Field(..., min_length=1, max_length=1)
    cataloging_form: str = Field(..., min_length=1, max_length=1)
    multipart_resource_record_level: str = Field(
        ..., min_length=1, max_length=1
    )
    entry_map: str = Field(..., min_length=4, max_length=4)

    @classmethod
    def from_bytes(cls, data: bytes) -> "Leader":
        if len(data) < 24:
            raise ValueError(
                "Invalid MARC record: Leader must be exactly 24 bytes long."
            )

        return cls(
            record_length=int(data[0:5].decode("utf-8").strip() or 0),
            record_status=data[5:6].decode("utf-8"),
            type_of_record=data[6:7].decode("utf-8"),
            bibliographic_level=data[7:8].decode("utf-8"),
            control_type=data[8:9].decode("utf-8"),
            character_encoding_scheme=data[9:10].decode("utf-8"),
            base_address_of_data=int(data[12:17].decode("utf-8").strip() or 0),
            encoding_level=data[17:18].decode("utf-8"),
            cataloging_form=data[18:19].decode("utf-8"),
            multipart_resource_record_level=data[19:20].decode("utf-8"),
            entry_map=data[20:24].decode("utf-8"),
        )
