from enum import Enum
from typing import List, Union

from pydantic import BaseModel, Field


class SearchOperator(str, Enum):
    """
    Enumeration of supported operators for matching MARC field values.

    Members
    -------
    Exact : str
        Exact match of the value.
    Contains : str
        Value contains the search string.
    Regex : str
        Value matches the given regular expression.
    StartsWith : str
        Value starts with the search string.
    EndsWith : str
        Value ends with the search string.
    """

    Exact = "exact"
    Contains = "contains"
    Regex = "regex"
    StartsWith = "startswith"
    EndsWith = "endswith"


class MarcCondition(BaseModel):
    """
    Represents a single search condition on a MARC field or subfield.

    Attributes
    ----------
    field : str
        The MARC field tag (three digits, e.g., "245").

    subfield : str | None, optional
        The MARC subfield code (a single lowercase letter or digit),
        if specified.

    value : str
        The value to search for.

    operator : SearchOperator, default=SearchOperator.Exact
        The operator used to match the value.

    ind1 : str | None, optional
        First indicator value to match;
        supports digits, letters, space, or underscore.

    ind2 : str | None, optional
        Second indicator value to match;
        supports digits, letters, space, or underscore.
    """

    field: str = Field(..., min_length=3, max_length=3, pattern=r"^\d{3}$")
    subfield: str | None = Field(None, pattern=r"^[a-z0-9]$")
    value: str
    operator: SearchOperator = SearchOperator.Exact
    ind1: str | None = Field(None, pattern=r"^[\\_0-9a-z ]?$")
    ind2: str | None = Field(None, pattern=r"^[\\_0-9a-z ]?$")


MarcTerm = Union[MarcCondition, "MarcBoolQuery"]
"""
Type alias for terms in a MARC boolean query.

A term can be either a single `MarcCondition` or a nested
`MarcBoolQuery` for complex boolean logic.
"""


class MarcBoolQuery(BaseModel):
    """
    Represents a boolean combination of MARC search terms.

    Attributes
    ----------
    must : List[MarcTerm] | None, optional
        List of terms that **must** match (logical AND).

    must_not : List[MarcTerm] | None, optional
        List of terms that **must not** match (logical AND with negation).

    should : List[MarcTerm] | None, optional
        List of terms where at least one **should** match (logical OR).
    """

    must: List[MarcTerm] | None = None
    must_not: List[MarcTerm] | None = None
    should: List[MarcTerm] | None = None

    class Config:
        arbitrary_types_allowed = True


MarcBoolQuery.model_rebuild()
# Ensures recursive model types are properly initialized


class MarcSearchRequest(BaseModel):
    """
    Represents a full MARC search request with pagination.

    Attributes
    ----------
    query : MarcBoolQuery
        The root boolean query containing all search terms.

    page : int, default=1
        The 1-based page number for paginated results.

    page_size : int, default=10
        Number of results per page. Allowed range is 1 to 1000.
    """

    query: MarcBoolQuery
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(
        default=10, ge=1, le=1000, description="Results per page (max 1000)"
    )
