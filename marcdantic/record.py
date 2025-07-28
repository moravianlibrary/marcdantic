from lxml.etree import _Element
from pydantic import BaseModel, Field

from .fields import FixedFields, VariableFields
from .from_mrc import from_mrc
from .from_xml import from_xml
from .selectors.control_fields import ControlFields
from .selectors.leader import Leader
from .selectors.local_fields import LocalFields
from .selectors.marc_issues import MarcIssues
from .selectors.numbers_and_codes import NumbersAndCodes
from .selectors.title_related import TitleRelated


class MarcRecord(BaseModel):
    """
    A parsed MARC bibliographic record.

    This model represents a MARC record that has been deserialized
    from MRC or XML. It exposes convenient property accessors
    for key MARC field groups via selector classes.

    Attributes
    ----------
    marc : bytes
        Raw MARC record data (binary). This is excluded from model export.

    leader : str
        The MARC leader string.

    control_fields : FixedFields
        A dictionary mapping control field tags (e.g., "008", "005")
        to their values.

    variable_fields : VariableFields
        A dictionary mapping data field tags (e.g., "245", "700")
        to a list of field instances.

    Properties
    ----------
    leader_data : Leader
        Structured representation of the MARC leader
        for accessing metadata like record type or status.

    control_fields : ControlFields
        Accessor for control fields such as "001", "005", "008".

    numbers_and_codes : NumbersAndCodes
        Extracts identifiers and classification codes
        (e.g., ISBN, ISSN, DDC, etc.).

    title_related : TitleRelated
        Accessor for title-related fields like title statement
        and responsibility.

    issues : MarcIssues
        Provides access to issue-level bibliographic data
        (e.g., barcode, volume).

    local_fields : LocalFields
        Accessor for any local/custom-defined MARC fields.

    Class Methods
    -------------
    from_mrc(data: bytes, encoding: str = "utf-8") -> MarcRecord
        Create a `MarcRecord` instance from raw MRC (ISO 2709) binary data.

    from_xml(data: _Element) -> MarcRecord
        Create a `MarcRecord` instance from a parsed MARCXML `_Element`.
    """

    marc: bytes = Field(..., exclude=True)

    leader: str
    control_fields: FixedFields
    variable_fields: VariableFields

    @property
    def leader_data(self) -> Leader:
        return Leader(self.leader)

    @property
    def control_fields(self) -> ControlFields:
        return ControlFields(self.control_fields)

    @property
    def numbers_and_codes(self) -> NumbersAndCodes:
        return NumbersAndCodes(self.variable_fields)

    @property
    def title_related(self) -> TitleRelated:
        return TitleRelated(self.variable_fields)

    @property
    def issues(self) -> MarcIssues:
        return MarcIssues(self.variable_fields)

    @property
    def local_fields(self) -> LocalFields:
        return LocalFields(self.variable_fields)

    @classmethod
    def from_mrc(cls, data: bytes, encoding: str = "utf-8") -> "MarcRecord":
        return cls.model_validate(from_mrc(data, encoding))

    @classmethod
    def from_xml(cls, data: _Element) -> "MarcRecord":
        return cls.model_validate(from_xml(data))
