from enum import Enum
from typing import List, Union

from pydantic import BaseModel, Field


class SearchOperator(str, Enum):
    Exact = "exact"
    Contains = "contains"
    Regex = "regex"
    StartsWith = "startswith"
    EndsWith = "endswith"


class MarcCondition(BaseModel):
    field: str = Field(..., min_length=3, max_length=3, regex=r"^\d{3}$")
    subfield: str | None = Field(None, regex=r"^[a-z0-9]$")
    value: str
    operator: SearchOperator = SearchOperator.Exact
    ind1: str | None = Field(None, regex=r"^[\\_0-9a-z ]?$")
    ind2: str | None = Field(None, regex=r"^[\\_0-9a-z ]?$")


MarcTerm = Union[MarcCondition, "MarcBoolQuery"]


class MarcBoolQuery(BaseModel):
    must: List[MarcTerm] | None = None
    must_not: List[MarcTerm] | None = None
    should: List[MarcTerm] | None = None

    class Config:
        arbitrary_types_allowed = True


MarcBoolQuery.model_rebuild()


class MarcSearchRequest(BaseModel):
    query: MarcBoolQuery
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(
        default=10, ge=1, le=1000, description="Results per page (max 1000)"
    )
