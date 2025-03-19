from .fieldsets import (
    ControlFields,
    FixedLengthDataElements,
    Isbn,
    Issn,
    Leader,
    MarcIssue,
    Nbn,
    NumbersAndCodes,
    RepeatableField,
    RepeatableSubfield,
    TitleRelated,
    TitleStatement,
    VariableFieldModel,
)
from .default_mapping import DEFAULT_MAPPING
from .mapper import MarcMapper
from .marc_record import MarcRecord

# import os


# def read_version():
#     current_dir = os.path.dirname(__file__)
#     parent_dir = os.path.dirname(current_dir)
#     version_file_path = os.path.join(parent_dir, "VERSION")
#     with open(version_file_path, "r") as version_file:
#         return version_file.read().strip()


# __version__ = read_version()


__all__ = [
    "ControlFields",
    "DEFAULT_MAPPING",
    "FixedLengthDataElements",
    "Isbn",
    "Issn",
    "Leader",
    "MarcIssue",
    "MarcMapper",
    "MarcRecord",
    "Nbn",
    "NumbersAndCodes",
    "RepeatableField",
    "RepeatableSubfield",
    "TitleRelated",
    "TitleStatement",
    "VariableFieldModel",
]
