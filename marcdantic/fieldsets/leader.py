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
