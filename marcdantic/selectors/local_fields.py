from typing import List

from ..mapper import MARC_MAPPER
from .common import VariableFieldSelector


class LocalFields(VariableFieldSelector):
    """Selector for local fields in MARC-like records using inverse mapping.

    This class allows querying MARC variable fields using local field names
    and subfield names based on an inverse mapping configuration.
    """

    def __call__(self, field: str, subfield: str) -> List[str]:
        """Retrieve subfield values for a given local field and subfield.

        Parameters
        ----------
        field : str
            The name of the local field (as defined in the mapping).
        subfield : str
            The name of the local subfield.

        Returns
        -------
        list of str
            List of values found for the specified local field and subfield.
        """

        field_mapping = MARC_MAPPER.local.get(field)
        if field_mapping is None:
            return []

        subfield_code = field_mapping.subfields.get(subfield)
        if subfield_code is None:
            return []

        return self._select_repeatable(field_mapping.tag, subfield_code)
