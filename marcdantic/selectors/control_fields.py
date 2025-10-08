from datetime import datetime

from ..fields import FixedFields


class FixedLengthDataElements:
    def __init__(self, value: str):
        self._value = value

    @property
    def date_entered(self) -> datetime:
        return datetime.strptime(self._value[0:6], "%y%m%d")

    @property
    def publication_status(self) -> str:
        return self._value[6]

    @property
    def date1(self) -> str | None:
        date1 = self._value[7:11]
        return None if date1 in ["0000", "    ", "----"] else date1

    @property
    def date2(self) -> str | None:
        date2 = self._value[11:15]
        return None if date2 in ["0000", "    ", "----"] else date2

    @property
    def place_of_publication(self) -> str:
        return self._value[15:18].strip(" -")

    @property
    def language(self) -> str:
        return self._value[35:38]


class ControlFields:
    def __init__(self, fixed_fields: FixedFields):
        self._fixed_fields = fixed_fields

    @property
    def control_number(self) -> str:
        return self._fixed_fields["001"]

    @property
    def control_number_identifier(self) -> str | None:
        return self._fixed_fields.get("003", None)

    @property
    def latest_transaction(self) -> datetime | None:
        if "005" not in self._fixed_fields:
            return None
        try:
            return datetime.strptime(
                self._fixed_fields["005"], "%Y%m%d%H%M%S.%f"
            )
        except ValueError:
            raise ValueError(
                "Invalid format: "
                "Must follow 'yyyymmddhhmmss.f' (ISO 8601 format)"
            )

    @property
    def fixed_length_data_elements(self) -> FixedLengthDataElements:
        return FixedLengthDataElements(self._fixed_fields["008"])
