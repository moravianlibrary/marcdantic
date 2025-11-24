from typing import Dict, List, Literal

from pydantic import BaseModel

from .fields import FieldTag, MarcFieldSelector, SubfieldCode

SkipTag = Literal["skip"]
TagAliasMapping = Dict[str, FieldTag | MarcFieldSelector | SkipTag]


class MarcIssueMapping(BaseModel):
    """
    Defines the mapping of MARC issue-related fields and subfields.
    """

    tag: FieldTag
    barcode: SubfieldCode
    issuance_type: SubfieldCode
    volume_number: SubfieldCode | None = None
    volume_year: SubfieldCode | None = None
    bundle: SubfieldCode | None = None


class TagAlias(BaseModel):
    from_tag: str
    tag: FieldTag
    code: SubfieldCode | None = None


class MarcContext(BaseModel):
    skip_tags: List[str] = ["LDR"]
    tag_aliases: List[TagAlias] = [
        TagAlias(from_tag="FMT", tag="990", code="a"),
        TagAlias(from_tag="MZK", tag="991"),
    ]
    issue_mapping: MarcIssueMapping = MarcIssueMapping(
        tag="996",
        barcode="b",
        issuance_type="s",
        volume_number="v",
        volume_year="y",
        bundle="i",
    )
    ignore_unknown_tags: bool = True
    mrc_encoding: str = "utf-8"
    mandatory_fields: List[FieldTag] = ["001", "005", "008"]
