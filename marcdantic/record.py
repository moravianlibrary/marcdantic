from typing import ClassVar, Dict, List

from pydantic import BaseModel

from .default_mapping import DEFAULT_MAPPING
from .fieldsets.common import RepeatableField
from .fieldsets.control_fields import ControlFields
from .fieldsets.issue import MarcIssue
from .fieldsets.leader import Leader
from .fieldsets.numbers_and_codes import NumbersAndCodes
from .fieldsets.title_related import TitleRelated
from .from_mrc import from_mrc
from .from_xml import from_xml
from .mapper import MarcMapper

LocalFields = Dict[
    str, Dict[str, str | List[str]] | List[Dict[str, str | List[str]]]
]


class MarcRecord(BaseModel):
    _mapper: ClassVar[MarcMapper] = MarcMapper(mapping=DEFAULT_MAPPING)

    marc: bytes

    leader: Leader

    control_fields: ControlFields

    numbers_and_codes: NumbersAndCodes | None = None
    title_related: TitleRelated | None = None

    issues: RepeatableField[MarcIssue] = None

    local: LocalFields = {}

    def has_local(self, field: str, subfield: str) -> bool:
        return field in self.local and (
            isinstance(self.local[field], list)
            and any(subfield in entry for entry in self.local[field])
            or subfield in self.local[field]
        )

    def get_local(self, field: str, subfield: str) -> str | List[str]:
        if isinstance(self.local[field], list):
            values = [entry[subfield] for entry in self.local[field]]
            if not values:
                raise KeyError(
                    f"Subfield '{subfield}' not found in field '{field}'"
                )
            return values
        return self.local[field][subfield]

    @classmethod
    def from_mrc(cls, data: bytes, encoding: str = "utf-8") -> "MarcRecord":
        return cls(**from_mrc(data, encoding, cls._mapper))

    @classmethod
    def from_xml(cls, data: bytes) -> "MarcRecord":
        return cls(**from_xml(data, cls._mapper))
