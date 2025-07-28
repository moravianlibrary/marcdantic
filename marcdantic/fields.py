from typing import Annotated, Dict, List

from pydantic import BaseModel, Field, model_validator

# Pattern used to validate field tags (must be exactly three digits)
FIELD_TAG_PATTERN = r"^\d{3}$"

#: MARC field tag (e.g., '100', '245')
FieldTag = Annotated[str, Field(..., pattern=FIELD_TAG_PATTERN)]
#: MARC subfield code (e.g., 'a', 'b', '1')
SubfieldCode = Annotated[str, Field(..., pattern=r"^[a-z0-9]$")]
#: MARC indicator (one character: digit, letter, or space)
Indicator = Annotated[str | None, Field(None, pattern=r"^[0-9a-z ]?$")]


class VariableField(BaseModel):
    """
    Represents a MARC variable field with indicators and subfields.

    Attributes
    ----------
    ind1 : Indicator
        First indicator character. May be `None` if not applicable.
    ind2 : Indicator
        Second indicator character. May be `None` if not applicable.
    subfields : dict of SubfieldCode to list of str
        Mapping of subfield codes to their respective values. A single
        subfield code can have multiple values.
    """

    ind1: Indicator
    ind2: Indicator
    subfields: Dict[SubfieldCode, List[str]]

    @model_validator(mode="after")
    def postprocess_indicators(self) -> "VariableField":
        """
        Converts space indicators (' ') to None for consistency.
        """
        if self.ind1 == " ":
            self.ind1 = None
        if self.ind2 == " ":
            self.ind2 = None
        return self


#: Mapping of fixed field tags to their values (e.g., {'008': '...'})
FixedFields = Dict[FieldTag, str]
#: Mapping of variable field tags to a list of field instances
# (e.g., {'245': [VariableField(...)]})
VariableFields = Dict[FieldTag, List[VariableField]]


class MarcFieldDefinition(BaseModel):
    """
    Schema definition for a MARC field specification.

    Attributes
    ----------
    field : FieldTag
        The tag of the MARC field (e.g., '100', '245').
    subfield : SubfieldCode or None, optional
        Optional subfield code if targeting a specific subfield.
    """

    field: FieldTag
    subfield: SubfieldCode | None = None
