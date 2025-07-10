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
