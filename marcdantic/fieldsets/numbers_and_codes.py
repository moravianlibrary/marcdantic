from pydantic import BaseModel

from .common import RepeatableField, VariableFieldModel


class Nbn(VariableFieldModel):
    active: str | None = None


class Isbn(VariableFieldModel):
    active: str | None = None
    terms_of_availability: str | None = None


class Issn(VariableFieldModel):
    active: str | None = None


class NumbersAndCodes(BaseModel):
    nbn: RepeatableField[Nbn] | None = None
    isbn: RepeatableField[Isbn] | None = None
    issn: RepeatableField[Issn] | None = None

    @property
    def isxn(self) -> RepeatableField[Isbn | Issn]:
        """
        Returns:
            A list of Isbn or Issn objects, or None if neither exists.
        """
        return self.isbn or self.issn
