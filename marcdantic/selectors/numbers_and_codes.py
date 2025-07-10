from typing import List

from .common import VariableFieldSelector


class Nbn(VariableFieldSelector):
    @property
    def active(self) -> List[str]:
        return self._select_repeatable("015", "a")


class Isbn(VariableFieldSelector):
    @property
    def active(self) -> List[str]:
        return self._select_repeatable("020", "a")

    @property
    def terms_of_availability(self) -> List[str]:
        return self._select_repeatable("020", "c")


class Issn(VariableFieldSelector):
    @property
    def active(self) -> List[str]:
        return self._select_repeatable("022", "a")


class NumbersAndCodes(VariableFieldSelector):
    @property
    def nbn(self) -> Nbn:
        return Nbn(self._variable_fields)

    @property
    def isbn(self) -> Isbn:
        return Isbn(self._variable_fields)

    @property
    def issn(self) -> Issn:
        return Issn(self._variable_fields)

    @property
    def isxn(self) -> Isbn | Issn:
        return self.isbn or self.issn
