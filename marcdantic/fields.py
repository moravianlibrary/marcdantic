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

    def query_fields(self, jq_filter: str) -> List[VariableField]:
        """
        Execute a jq query that returns variable fields.

        Parameters
        ----------
        jq_filter : str
            A jq filter string that selects variable fields,
            e.g., '.["245"][]'

        Returns
        -------
        List[VariableField]
            List of VariableField instances matching the query.
        """
        results = self.query(jq_filter)
        return [VariableField.model_validate(r) for r in results]

    def query_field(self, jq_filter: str) -> VariableField | None:
        """
        Execute a jq query that returns a single variable field.

        Parameters
        ----------
        jq_filter : str
            A jq filter string that selects a variable field,
            e.g., '.["245"][0]'

        Returns
        -------
        VariableField | None
            The VariableField instance matching the query,
            or None if no match is found.
        """
        results = self.query(jq_filter)
        if not results:
            return None
        if len(results) > 1:
            raise ValueError("Query returned multiple results; expected one.")
        return VariableField.model_validate(results[0])

    def query_subfields(
        self, jq_filter: str
    ) -> List[Dict[SubfieldCode, List[str]]]:
        """
        Execute a jq query that returns subfields.

        Parameters
        ----------
        jq_filter : str
            A jq filter string that selects subfields,
            e.g., '.["100"][].subfields'

        Returns
        -------
        List[Dict[SubfieldCode, List[str]]]
            List of subfield dictionaries matching the query.
        """
        results = self.query(jq_filter)
        return [dict[SubfieldCode, List[str]](r) for r in results]

    def query_subfield(
        self, jq_filter: str
    ) -> Dict[SubfieldCode, List[str]] | None:
        """
        Execute a jq query that returns a single subfield dictionary.

        Parameters
        ----------
        jq_filter : str
            A jq filter string that selects a subfield dictionary,
            e.g., '.["100"][0].subfields'

        Returns
        -------
        Dict[SubfieldCode, List[str]] | None
            The subfield dictionary matching the query,
            or None if no match is found.
        """
        results = self.query(jq_filter)
        if not results:
            return None
        if len(results) > 1:
            raise ValueError("Query returned multiple results; expected one.")
        return dict[SubfieldCode, List[str]](results[0])

    def query_subfield_values(self, jq_filter: str) -> List[str]:
        """
        Execute a jq query that returns subfield values.

        Parameters
        ----------
        jq_filter : str
            A jq filter string that selects subfield values,
            e.g., '.["100"][].subfields.a[]'

        Returns
        -------
        List[str]
            List of subfield values matching the query.
        """
        results = self.query(jq_filter)
        return [str(r) for r in results]

    def query_subfield_value(self, jq_filter: str) -> str | None:
        """
        Execute a jq query that returns a single subfield value.

        Parameters
        ----------
        jq_filter : str
            A jq filter string that selects a subfield value,
            e.g., '.["100"][0].subfields.a[0]'

        Returns
        -------
        str | None
            The subfield value matching the query,
            or None if no match is found.
        """
        results = self.query(jq_filter)
        if not results:
            return None
        if len(results) > 1:
            raise ValueError("Query returned multiple results; expected one.")
        return str(results[0])


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
