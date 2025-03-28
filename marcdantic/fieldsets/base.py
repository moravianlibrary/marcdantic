from typing import List, Optional, TypeVar

from pydantic import BaseModel

F = TypeVar("F", bound="BaseModel")
S = TypeVar("S")


RepeatableField = Optional[List[F]]
RepeatableSubfield = Optional[List[S]]


class VariableFieldModel(BaseModel):
    ind1: str
    ind2: str
