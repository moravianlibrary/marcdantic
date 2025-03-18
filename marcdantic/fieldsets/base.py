from typing import List, TypeVar, Optional
from pydantic import BaseModel

F = TypeVar("F", bound="BaseModel")
S = TypeVar("S")


RepeatableField = Optional[List[F]]
RepeatableSubfield = Optional[List[S]]


class VariableFieldModel(BaseModel):
    ind1: str | None = None
    ind2: str | None = None
