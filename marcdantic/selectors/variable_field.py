from typing import List, Tuple

from pydantic import BaseModel

from ..fields import FieldTag, SubfieldCode, VariableField, VariableFields


class FieldSelector(BaseModel):
    tag: FieldTag
    code: SubfieldCode | None = None


class SubfieldSelection:
    def __init__(self, vf: VariableField):
        self._vf = vf

    def first(self, code: SubfieldCode) -> str | None:
        if code is None:
            raise ValueError("Subfield code must be provided")

        if code not in self._vf.subfields:
            return None
        return self._vf.subfields[code][0]

    def all(self, code: SubfieldCode) -> List[str]:
        if code is None:
            raise ValueError("Subfield code must be provided")

        return self._vf.subfields.get(code, [])


class FieldSelection:
    def __init__(self, vfs: VariableFields):
        self._vfs = vfs

    def first(self, selector: FieldSelector) -> SubfieldSelection | None:
        fields = self._vfs.get(selector.tag)
        if not fields:
            return None
        return SubfieldSelection(fields[0])

    def all(self, selector: FieldSelector) -> List[SubfieldSelection]:
        return [
            SubfieldSelection(vf) for vf in self._vfs.get(selector.tag, [])
        ]

    def first_value(self, selector: FieldSelector) -> str | None:
        field = self.first(selector)
        return field.first(selector.code) if field else None

    def all_values(self, selector: FieldSelector) -> List[str]:
        field = self.first(selector)
        return field.all(selector.code) if field else []

    def first_value_all_fields(self, selector: FieldSelector) -> List[str]:
        fields = self.all(selector)
        values = [f.first(selector.code) for f in fields]
        return [v for v in values if v]

    def all_values_all_fields(
        self, selector: FieldSelector
    ) -> List[List[str]]:
        fields = self.all(selector)
        return [f.all(selector.code) for f in fields]


VariableFieldSelection = str | Tuple[str, ...]

NbnActiveSelector = FieldSelector(tag="015", code="a")
IsbnActiveSelector = FieldSelector(tag="020", code="a")
IsbnTermsOfAvailabilitySelector = FieldSelector(tag="020", code="c")
IssnActiveSelector = FieldSelector(tag="022", code="a")

TitleSelector = FieldSelector(tag="245", code="a")
SubtitleSelector = FieldSelector(tag="245", code="b")
