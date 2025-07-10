from typing import Annotated, Dict, List

from pydantic import BaseModel, Field, model_validator

FIELD_TAG_PATTERN = r"^\d{3}$"

FieldTag = Annotated[str, Field(..., pattern=FIELD_TAG_PATTERN)]
SubfieldCode = Annotated[str, Field(..., pattern=r"^[a-z0-9]$")]
Indicator = Annotated[str | None, Field(None, pattern=r"^[0-9a-z ]?$")]


class VariableField(BaseModel):
    ind1: Indicator
    ind2: Indicator
    subfields: Dict[SubfieldCode, List[str]]

    @model_validator(mode="after")
    def postprocess_indicators(self) -> "VariableField":
        if self.ind1 == " ":
            self.ind1 = None
        if self.ind2 == " ":
            self.ind2 = None
        return self


FixedFields = Dict[FieldTag, str]
VariableFields = Dict[FieldTag, List[VariableField]]


class MarcFieldDefinition(BaseModel):
    field: FieldTag
    subfield: SubfieldCode | None = None
