from typing import List

from pydantic import BaseModel

from .fields import VariableField
from .mapper import MARC_MAPPER


class MarcIssue(BaseModel):
    field: VariableField

    @property
    def barcode(self) -> str:
        return self.field.subfields[MARC_MAPPER.issue.barcode][0]

    @property
    def issuance_type(self) -> str:
        return self.field.subfields[MARC_MAPPER.issue.issuance_type][0]

    @property
    def volume_number(self) -> str | None:
        if MARC_MAPPER.issue.volume_number is None:
            return None
        return self.field.subfields.get(
            MARC_MAPPER.issue.volume_number, [None]
        )[0]

    @property
    def volume_year(self) -> str | None:
        if MARC_MAPPER.issue.volume_year is None:
            return None
        return self.field.subfields.get(MARC_MAPPER.issue.volume_year, [None])[
            0
        ]

    @property
    def bundle(self) -> str | None:
        if MARC_MAPPER.issue.bundle is None:
            return None
        return self.field.subfields.get(MARC_MAPPER.issue.bundle, [None])[0]

    def local(self, property: str) -> List[str]:
        return self.field.subfields.get(
            MARC_MAPPER.issue.local.get(property) or "", []
        )
