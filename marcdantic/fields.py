from typing import Annotated, Any, Dict, List

import jq
from pydantic import BaseModel, Field, PrivateAttr, RootModel, model_validator

#: Pattern used to validate field tags (must be exactly three digits)
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

    def query(self, jq_filter: str) -> Any:
        """
        Execute a jq query on the variable field.

        Parameters
        ----------
        jq_filter : str
            A jq filter string, e.g., '.subfields.a[]'

        Returns
        -------
        Any
            The result of the jq query (list, string, number, etc.)
        """
        compiled = jq.compile(jq_filter)
        return compiled.input(self.model_dump()).all()


class FixedFields(RootModel[Dict[FieldTag, str]]):
    pass


class VariableFields(RootModel[Dict[FieldTag, List[VariableField]]]):
    _plain_root: Dict[str, Any] | None = PrivateAttr(default=None)

    def query(self, jq_filter: str) -> Any:
        """
        Execute a jq query on the variable fields.

        Parameters
        ----------
        jq_filter : str
            A jq filter string, e.g., '.["015"][].subfields.a[]'

        Returns
        -------
        Any
            The result of the jq query (list, string, number, etc.)
        """
        compiled = jq.compile(jq_filter)

        if self._plain_root is None:
            self._plain_root = {
                tag: [field.model_dump() for field in fields]
                for tag, fields in self.root.items()
            }

        return compiled.input(self._plain_root).all()


class MarcFieldSelector(BaseModel):
    """
    Schema definition for a MARC field selector.

    Attributes
    ----------
    tag : FieldTag
        The tag of the MARC field (e.g., '100', '245').
    code : SubfieldCode or None, optional
        Optional subfield code if targeting a specific subfield.
    """

    tag: FieldTag
    code: SubfieldCode | None = None
