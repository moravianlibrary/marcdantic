from pydantic import BaseModel
from typing import Dict, List


class MarcIssue(BaseModel):
    barcode: str
    issuance_type: str | None = None
    volume_number: str | None = None
    volume_year: str | None = None
    bundle: str | None

    local: Dict[str, str | List[str]] = {}

    def has_local(self, property: str) -> bool:
        return property in self.local

    def get_local(self, property: str) -> str | List[str]:
        return self.local[property]
