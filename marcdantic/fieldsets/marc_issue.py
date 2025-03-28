from enum import Enum
from typing import Dict, List

from pydantic import BaseModel


class IssuanceType(Enum):
    Unit = "Unit"
    Volume = "Volume"
    Bundle = "Bundle"


class MarcIssue(BaseModel):
    barcode: str
    issuance_type: IssuanceType
    volume_number: str | None = None
    volume_year: str | None = None
    bundle: str | None

    local: Dict[str, str | List[str]] = {}

    def has_local(self, property: str) -> bool:
        return property in self.local

    def get_local(self, property: str) -> str | List[str]:
        return self.local[property]
