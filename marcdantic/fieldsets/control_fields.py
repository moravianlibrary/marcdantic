from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, field_validator, model_validator


class FixedLengthDataElements(BaseModel):
    date_entered: datetime | None = None
    publication_status: str | None = None
    date1: str | None = None
    date2: str | None = None
    place_of_publication: str | None = None
    language: str | None = None

    @model_validator(mode="before")
    def validate(cls, values: Any) -> Dict[str, Any]:
        if isinstance(values, dict):
            return values

        if not isinstance(values, str):
            raise TypeError(
                "Expected data of type 'str', "
                f"got '{type(values).__name__}' instead."
            )

        if len(values) != 40:
            raise ValueError(
                "MARC 008 field must be exactly 40 characters long."
            )

        def parse_publication_date(date: str) -> str | None:
            return None if date in ["0000", "    ", "----"] else date

        return {
            "date_entered": datetime.strptime(values[0:6], "%y%m%d"),
            "publication_status": values[6],
            "date1": parse_publication_date(values[7:11]),
            "date2": parse_publication_date(values[11:15]),
            "place_of_publication": values[15:18].strip(" -"),
            "language": values[35:38],
        }


class ControlFields(BaseModel):
    control_number: str
    control_number_identifier: str | None = None
    latest_transaction: datetime | None = None
    fixed_length_data_elements: FixedLengthDataElements

    @field_validator("latest_transaction", mode="before")
    def validate_latest_transaction(cls, value: str) -> datetime:
        try:
            return datetime.strptime(value, "%Y%m%d%H%M%S.%f")
        except ValueError:
            raise ValueError(
                "Invalid format: "
                "Must follow 'yyyymmddhhmmss.f' (ISO 8601 format)"
            )
