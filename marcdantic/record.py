from lxml.etree import _Element
from pydantic import BaseModel, PrivateAttr, model_validator

from marcdantic.selectors import (
    ControlFieldsSelector,
    LeaderSelector,
    MarcIssuesSelector,
)

from .context import MarcContext
from .fields import FixedFields, VariableFields
from .from_mrc import from_mrc
from .from_xml import from_xml


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

    # --- Private attributes (not part of serialization) ---
    _marc: bytes | None = PrivateAttr(default=None)
    _context: MarcContext = PrivateAttr(default_factory=MarcContext)

    # --- Public fields (serialized/deserialized) ---
    leader: str
    fixed_fields: FixedFields
    variable_fields: VariableFields

    # --- Properties ---
    @property
    def leader_selector(self) -> LeaderSelector:
        return LeaderSelector(self.leader)

    @property
    def control_fields_selector(self) -> ControlFieldsSelector:
        return ControlFieldsSelector(self.fixed_fields)

    @property
    def issues_selector(self) -> MarcIssuesSelector:
        return MarcIssuesSelector(self.variable_fields, self._context)

    @classmethod
    def from_json(
        cls, data: dict, context: MarcContext = MarcContext()
    ) -> "MarcRecord":
        record = cls.model_validate(data)
        record._context = context
        return record

    @classmethod
    def from_mrc(
        cls, data: bytes, context: MarcContext = MarcContext()
    ) -> "MarcRecord":
        record = cls.model_validate(from_mrc(data, context))
        record._marc = data
        record._context = context
        return record

    @classmethod
    def from_xml(
        cls, data: _Element, context: MarcContext = MarcContext()
    ) -> "MarcRecord":
        parsed_data = from_xml(data, context)
        record = cls.model_validate(parsed_data)
        record._marc = parsed_data["marc"]
        record._context = context
        return record

    # --- Validation ---
    @model_validator(mode="after")
    def check_mandatory_fields(cls, model: "MarcRecord") -> "MarcRecord":
        missing = []

        for tag in model._context.mandatory_fields:
            if tag in model.fixed_fields.root:
                continue
            if tag in model.variable_fields.root:
                continue

            missing.append(tag)

        if missing:
            raise ValueError(
                f"Missing mandatory MARC field(s): {', '.join(missing)}"
            )

        return model
