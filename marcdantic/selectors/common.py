from typing import List

from ..fields import VariableFields


class VariableFieldSelector:
    def __init__(self, variable_fields: VariableFields):
        self._variable_fields = variable_fields

    def _select(self, tag: str, code: str) -> str | None:
        fields = self._variable_fields.get(tag)
        if not fields:
            return None
        subfields = fields[0].subfields
        if code not in subfields:
            return None
        return subfields[code][0]

    def _select_repeatable(self, tag: str, code: str) -> List[str]:
        return [
            value
            for field in self._variable_fields.get(tag, [])
            for value in field.subfields.get(code, [])
        ]
