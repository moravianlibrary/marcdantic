from typing import Dict, List

from pydantic import BaseModel, RootModel

from .default_mapping import (
    DEFAULT_INVERSE_LOCAL_MAPPING,
    DEFAULT_ISSUE_MAPPING,
)
from .fields import SubfieldCode


class LocalFieldMapping(BaseModel):
    """Mapping of a MARC field to a local field representation.

    Attributes
    ----------
    name : str
        The name of the local field.
    subfields : dict of str to str
        A mapping from MARC subfield codes to local subfield names.
    """

    name: str
    subfields: Dict[str, str]


LocalMapping = Dict[str, LocalFieldMapping]
"""Type alias for the local field mapping.

Maps MARC tags (as strings) to `LocalFieldMapping` instances.
"""


class InverseLocalFieldMapping(BaseModel):
    """
    Inverse mapping of a local field to MARC field representation.

    Attributes
    ----------
    tag : str
        The MARC field tag.
    subfields : dict of str to str
        A mapping from local subfield names back to MARC subfield codes.
    """

    tag: str
    subfields: Dict[str, str]


class InverseLocalMapping(RootModel[Dict[str, InverseLocalFieldMapping]]):
    """
    Inverse mapping of local fields to MARC field representations.
    """

    pass


class MarcIssueMapping(BaseModel):
    tag: str
    barcode: SubfieldCode
    issuance_type: SubfieldCode
    volume_number: SubfieldCode | None = None
    volume_year: SubfieldCode | None = None
    bundle: SubfieldCode | None = None
    local: Dict[SubfieldCode, List[str]] = {}


class MarcMapper:
    tag_alias: Dict[str, str] = {}
    local: InverseLocalMapping = InverseLocalMapping.model_validate(
        DEFAULT_INVERSE_LOCAL_MAPPING
    )
    issue: MarcIssueMapping = MarcIssueMapping.model_validate(
        DEFAULT_ISSUE_MAPPING
    )

    @classmethod
    def set_local_mapping(cls, mapping: LocalMapping) -> None:
        inverse_mapping: InverseLocalMapping = {}
        for tag, field in mapping.items():
            inverse_mapping[field.name] = InverseLocalFieldMapping(
                tag=tag, subfields={v: k for k, v in field.subfields.items()}
            )
        cls.local = inverse_mapping

    @classmethod
    def set_issue_mapping(cls, mapping: MarcIssueMapping) -> None:
        cls.issue = mapping


MARC_MAPPER = MarcMapper
