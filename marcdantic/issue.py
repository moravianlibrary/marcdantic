from pydantic import BaseModel, PrivateAttr

from .fields import VariableField


class MarcIssue(BaseModel):
    """
    Representation of a MARC issue entry with mapped subfields.

    This class provides convenient accessors for specific issue-related
    subfields defined in the `MARC_MAPPER`.

    Attributes
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
    """

    _variable_field: VariableField | None = PrivateAttr(default=None)

    barcode: str
    issuance_type: str
    volume_number: str | None
    volume_year: str | None
    bundle: str | None
