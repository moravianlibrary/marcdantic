from typing import List

from pydantic import BaseModel


class NbnEntry(BaseModel):
    value: str


Nbn = List[NbnEntry]


class IsbnEntry(BaseModel):
    value: str


Isbn = List[IsbnEntry]


class IssnEntry(BaseModel):
    value: str


Issn = List[IssnEntry]


class NumbersAndCodes(BaseModel):
    nbn: Nbn | None
    isbn: Isbn | None
    issn: Issn | None
