from typing import Any, Dict
import json
from pydantic import BaseModel


class FixedFieldMapping(BaseModel):
    """
    Represents a fixed field mapping for a MARC record.

    Attributes
    ----------
    section : str
        The section of the MARC record this field belongs to.
    field : str
        The name of the field being mapped.
    """

    section: str
    field: str


class SubfieldMapping(BaseModel):
    """
    Represents a subfield mapping within a variable field for a MARC record.

    Attributes
    ----------
    subfield : str
        The name of the subfield being mapped.
    repeatable : bool
        Whether the subfield is repeatable (can appear multiple times).
    """

    subfield: str
    repeatable: bool = False


class VariableFieldMapping(FixedFieldMapping):
    """
    Represents a variable field mapping, extending the FixedFieldMapping to
    include subfields and repeatability information.

    Attributes
    ----------
    subfields : Dict[str, SubfieldMapping]
        A dictionary of subfield mappings, where the key is the subfield code
        and the value is a SubfieldMapping instance.
    repeatable : bool
        Whether the field is repeatable (can appear multiple times).
    """

    subfields: Dict[str, SubfieldMapping] = dict()
    repeatable: bool = False


class MarcMapper:
    """
    A class for mapping MARC record fields (fixed and variable) from a provided
    mapping file or dictionary.

    Parameters
    ----------
    mapping_file : str | None, optional
        A path to a JSON file containing the mapping configuration.
        If provided, `mapping` must be None. Default is None.
    mapping : Dict[str, Any] | None, optional
        A dictionary containing the mapping configuration.
        If provided, `mapping_file` must be None. Default is None.

    Attributes
    ----------
    fixed_fields : Dict[str, FixedFieldMapping]
        A dictionary of fixed field mappings, where the key is the field tag
        and the value is a FixedFieldMapping instance.
    variable_fields : Dict[str, VariableFieldMapping]
        A dictionary of variable field mappings, where the key is the field tag
        and the value is a VariableFieldMapping instance.
    """

    def __init__(
        self,
        mapping_file: str | None = None,
        mapping: Dict[str, Any] | None = None,
    ):
        """
        Initializes a MarcMapper instance.

        Parameters
        ----------
        mapping_file : str | None, optional
            A path to a JSON file containing the mapping configuration.
            If provided, `mapping` must be None. Default is None.
        mapping : Dict[str, Any] | None, optional
            A dictionary containing the mapping configuration.
            If provided, `mapping_file` must be None. Default is None.

        Raises
        ------
        ValueError
            If neither `mapping_file` nor `mapping` is provided, or if both
            are provided.
        """

        if mapping_file is None and mapping is None:
            raise ValueError(
                "Either mapping_file or mapping must be provided."
            )
        if mapping_file is not None and mapping is not None:
            raise ValueError(
                "Both mapping_file and mapping cannot be provided."
            )

        self.fixed_fields: Dict[str, FixedFieldMapping] = dict()
        self.variable_fields: Dict[str, VariableFieldMapping] = dict()

        if mapping_file is not None:
            with open(mapping_file, "r") as file:
                self._load_mapping(json.load(file))
        else:
            self._load_mapping(mapping)

    def _load_mapping(self, mapping: Dict[str, Any]) -> None:
        """
        Loads and processes the provided mapping dictionary.

        Parameters
        ----------
        mapping : Dict[str, Any]
            A dictionary containing the mapping configuration.
        """

        for tag, data in mapping.items():
            section = data["section"]
            field = data["field"]
            subfields = data.get("subfields", None)

            if subfields is None:
                self.fixed_fields[tag] = FixedFieldMapping(
                    section=section, field=field
                )
            else:
                self.variable_fields[tag] = VariableFieldMapping(
                    section=section,
                    field=field,
                    repeatable=data.get("repeatable", False),
                    subfields={
                        code: SubfieldMapping(
                            subfield=subfield_data["subfield"],
                            repeatable=subfield_data.get("repeatable", False),
                        )
                        for code, subfield_data in subfields.items()
                    },
                )
