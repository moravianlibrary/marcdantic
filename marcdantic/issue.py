from typing import List

from pydantic import BaseModel

from .fields import VariableField
from .mapper import MARC_MAPPER


class MarcIssue(BaseModel):
    """
    Representation of a MARC issue entry with mapped subfields.

    This class provides convenient accessors for specific issue-related
    subfields defined in the `MARC_MAPPER`.

    Attributes
    ----------
    field : VariableField
        A MARC variable field object containing subfield data.

    Properties
    ----------
    barcode : str
        The barcode value from the MARC issue field. Extracted from the
        mapped subfield defined in `MARC_MAPPER.issue.barcode`.

    issuance_type : str
        The type of issuance (e.g., "monograph", "serial") from the
        mapped subfield defined in `MARC_MAPPER.issue.issuance_type`.

    volume_number : str or None
        The volume number associated with the issue, if available.

    volume_year : str or None
        The year of the volume associated with the issue, if available.

    bundle : str or None
        The bundle identifier associated with the issue, if available.

    Methods
    -------
    local(property: str) -> List[str]
        Returns a list of values for a custom local property defined in
        `MARC_MAPPER.issue.local`. If the property is not found, returns an
        empty list.
    """

    field: VariableField

    @property
    def barcode(self) -> str:
        return self.field.subfields[MARC_MAPPER.issue.barcode][0]

    @property
    def issuance_type(self) -> str:
        return self.field.subfields[MARC_MAPPER.issue.issuance_type][0]

    @property
    def volume_number(self) -> str | None:
        if MARC_MAPPER.issue.volume_number is None:
            return None
        return self.field.subfields.get(
            MARC_MAPPER.issue.volume_number, [None]
        )[0]

    @property
    def volume_year(self) -> str | None:
        if MARC_MAPPER.issue.volume_year is None:
            return None
        return self.field.subfields.get(MARC_MAPPER.issue.volume_year, [None])[
            0
        ]

    @property
    def bundle(self) -> str | None:
        if MARC_MAPPER.issue.bundle is None:
            return None
        return self.field.subfields.get(MARC_MAPPER.issue.bundle, [None])[0]

    def local(self, property: str) -> List[str]:
        """
        Get a list of values for a custom local property.

        Parameters
        ----------
        property : str
            The local subfield name as defined in `MARC_MAPPER.issue.local`.

        Returns
        -------
        list of str
            A list of values for the specified local property, or an empty list
            if the property is not found.
        """
        return self.field.subfields.get(
            MARC_MAPPER.issue.local.get(property) or "", []
        )
