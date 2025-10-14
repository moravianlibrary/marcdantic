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

    def first(self, tag: FieldTag) -> SubfieldSelection | None:
        fields = self._vfs.get(tag)
        if not fields:
            return None
        return SubfieldSelection(fields[0])

    def all(self, tag: FieldTag) -> List[SubfieldSelection]:
        return [SubfieldSelection(vf) for vf in self._vfs.get(tag, [])]


VariableFieldSelection = str | Tuple[str, ...]

NbnActiveSelector = FieldSelector(tag="015", code="a")
IsbnActiveSelector = FieldSelector(tag="020", code="a")
IsbnTermsOfAvailabilitySelector = FieldSelector(tag="020", code="c")
IssnActiveSelector = FieldSelector(tag="022", code="a")

TitleSelector = FieldSelector(tag="245", code="a")
SubtitleSelector = FieldSelector(tag="245", code="b")


ELocationUrlSelector = FieldSelector(tag="856", code="u")
ELocationLinkTextSelector = FieldSelector(tag="856", code="y")
