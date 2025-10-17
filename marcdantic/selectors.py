from datetime import datetime
from typing import List

from .context import MarcContext
from .fields import FixedFields, VariableField, VariableFields
from .issue import MarcIssue


class LeaderSelector:
    def __init__(self, leader: str):
        self._leader = leader

    @property
    def record_length(self) -> int:
        return int(self._leader[0:5].strip() or 0)

    @property
    def record_status(self) -> str:
        return self._leader[5:6].strip()

    @property
    def type_of_record(self) -> str:
        return self._leader[6:7].strip()

    @property
    def bibliographic_level(self) -> str:
        return self._leader[7:8].strip()

    @property
    def control_type(self) -> str:
        return self._leader[8:9].strip()

    @property
    def character_encoding_scheme(self) -> str:
        return self._leader[9:10].strip()

    @property
    def base_address_of_data(self) -> int:
        return int(self._leader[12:17].strip() or 0)

    @property
    def encoding_level(self) -> str:
        return self._leader[17:18].strip()

    @property
    def cataloging_form(self) -> str:
        return self._leader[18:19].strip()

    @property
    def multipart_resource_record_level(self) -> str:
        return self._leader[19:20].strip()

    @property
    def entry_map(self) -> str:
        return self._leader[20:24].strip()


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


class ControlFieldsSelector:
    def __init__(self, fixed_fields: FixedFields):
        self._fixed_fields = fixed_fields

    @property
    def control_number(self) -> str:
        return self._fixed_fields.root["001"]

    @property
    def control_number_identifier(self) -> str | None:
        return self._fixed_fields.root.get("003", None)

    @property
    def latest_transaction(self) -> datetime | None:
        if "005" not in self._fixed_fields.root:
            return None
        try:
            return datetime.strptime(
                self._fixed_fields.root["005"], "%Y%m%d%H%M%S.%f"
            )
        except ValueError:
            raise ValueError(
                "Invalid format: "
                "Must follow 'yyyymmddhhmmss.f' (ISO 8601 format)"
            )

    @property
    def fixed_length_data_elements(self) -> FixedLengthDataElements:
        return FixedLengthDataElements(self._fixed_fields.root["008"])


class MarcIssuesSelector:
    def __init__(self, variable_fields: VariableFields, context: MarcContext):
        self._variable_fields = variable_fields
        self._context = context

    def _create_issue(self, field: VariableField) -> MarcIssue:
        """Convert a MARC variable field into a MarcIssue model."""
        mapping = self._context.issue_mapping

        def first_or_none(code: str | None) -> str | None:
            if not code:
                return None
            values = field.subfields.get(code, [])
            return values[0] if values else None

        return MarcIssue(
            _variable_field=field,
            barcode=first_or_none(mapping.barcode),
            issuance_type=first_or_none(mapping.issuance_type),
            volume_number=first_or_none(mapping.volume_number),
            volume_year=first_or_none(mapping.volume_year),
            bundle=first_or_none(mapping.bundle),
        )

    @property
    def all(self) -> List[MarcIssue]:
        """
        Return all issue records defined by the context's issue mapping.
        """
        tag = self._context.issue_mapping.tag
        fields = self._variable_fields.root.get(tag, [])
        return [self._create_issue(field) for field in fields]

    def find_by_barcode(self, barcode: str) -> MarcIssue | None:
        """
        Find the first issue by barcode using jq query.
        Returns None if no match is found.
        """
        tag = self._context.issue_mapping.tag
        code = self._context.issue_mapping.barcode

        query = (
            f'.["{tag}"][] | select(.subfields["{code}"][0] == "{barcode}")'
        )

        result = self._variable_fields.query(query)
        if not result:
            return None

        field_data = result[0] if isinstance(result, list) else result
        field = VariableField.model_validate(field_data)

        return self._create_issue(field)


NbnActiveJq = '.["015"]?[]?.subfields.a[]?'
IsbnActiveJq = '.["020"]?[]?.subfields.a[]?'
IsbnTermsOfAvailabilityJq = '.["020"]?[]?.subfields.c[]?'
IssnActiveJq = '.["022"]?[]?.subfields.a[]?'
IsxnActiveJq = '.["020","022"]?[]?.subfields.a[]?'

TitleJq = '.["245"]?[]?.subfields.a[]?'
SubtitleJq = '.["245"]?[]?.subfields.b[]?'

ELocationUrlJq = '.["856"]?[]?.subfields.u[]?'
ELocationLinkTextJq = '.["856"]?[]?.subfields.y[]?'
