from typing import List

from marcdantic.issue import MarcIssue

from ..mapper import MARC_MAPPER
from .common import VariableFieldSelector


class MarcIssues(VariableFieldSelector):
    def all(self) -> List[MarcIssue]:
        return [
            MarcIssue(field)
            for field in self._variable_fields.get(MARC_MAPPER.issue.tag, [])
        ]

    def find_by_barcode(self, barcode: str) -> MarcIssue | None:
        barcode_code = MARC_MAPPER.issue.barcode
        for field in self._variable_fields.get(MARC_MAPPER.issue.tag, []):
            if field.subfields[barcode_code][0] == barcode:
                return MarcIssue(field)
        return None
