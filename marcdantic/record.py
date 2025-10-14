from lxml.etree import _Element
from pydantic import BaseModel, Field

from marcdantic.selectors.variable_field import FieldSelection

from .fields import FixedFields, VariableFields
from .from_mrc import from_mrc
from .from_xml import from_xml
from .selectors.control_fields import ControlFields
from .selectors.issue import MarcIssues
from .selectors.leader import Leader


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

    fixed_fields : FixedFields
        A dictionary mapping fixed field tags (e.g., "008", "005")
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

    issues : MarcIssues
        Provides access to issue-level bibliographic data
        (e.g., barcode, volume).

    selection : FieldSelection
        Selector for querying variable fields and subfields.

    Class Methods
    -------------
    from_mrc(data: bytes, encoding: str = "utf-8") -> MarcRecord
        Create a `MarcRecord` instance from raw MRC (ISO 2709) binary data.

    from_xml(data: _Element) -> MarcRecord
        Create a `MarcRecord` instance from a parsed MARCXML `_Element`.
    """

    marc: bytes = Field(..., exclude=True)

    leader: str
    fixed_fields: FixedFields
    variable_fields: VariableFields

    @property
    def leader_data(self) -> Leader:
        return Leader(self.leader)

    @property
    def control_fields(self) -> ControlFields:
        return ControlFields(self.fixed_fields)

    @property
    def issues(self) -> MarcIssues:
        return MarcIssues(self.variable_fields)

    @property
    def selection(self) -> FieldSelection:
        return FieldSelection(self.variable_fields)

    @classmethod
    def from_mrc(cls, data: bytes, encoding: str = "utf-8") -> "MarcRecord":
        return cls.model_validate(from_mrc(data, encoding))

    @classmethod
    def from_xml(cls, data: _Element) -> "MarcRecord":
        return cls.model_validate(from_xml(data))
