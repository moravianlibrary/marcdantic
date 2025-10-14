import unittest
from datetime import datetime

from marcdantic.fields import VariableField
from marcdantic.record import MarcRecord


class TestSelectors(unittest.TestCase):
    def test_leader_selector(self):
        leader_selector = MarcRecord(
            leader="00086nam  2200049   4500",
            fixed_fields={},
            variable_fields={},
        ).leader_selector
        self.assertEqual(leader_selector.record_length, 86)
        self.assertEqual(leader_selector.record_status, "n")
        self.assertEqual(leader_selector.type_of_record, "a")
        self.assertEqual(leader_selector.bibliographic_level, "m")
        self.assertEqual(leader_selector.control_type, "")
        self.assertEqual(leader_selector.character_encoding_scheme, "")
        self.assertEqual(leader_selector.base_address_of_data, 49)
        self.assertEqual(leader_selector.encoding_level, "")
        self.assertEqual(leader_selector.cataloging_form, "")
        self.assertEqual(leader_selector.multipart_resource_record_level, "")
        self.assertEqual(leader_selector.entry_map, "4500")

    def test_fixed_length_data_elements(self):
        fixed_fields = MarcRecord(
            leader="00086nam  2200049   4500",
            fixed_fields={
                "008": "210101s2023    xxu           000 0 eng d",
            },
            variable_fields={},
        ).control_fields_selector.fixed_length_data_elements
        self.assertEqual(fixed_fields.date_entered, datetime(2021, 1, 1))
        self.assertEqual(fixed_fields.publication_status, "s")
        self.assertEqual(fixed_fields.date1, "2023")
        self.assertEqual(fixed_fields.date2, None)
        self.assertEqual(fixed_fields.place_of_publication, "xxu")
        self.assertEqual(fixed_fields.language, "eng")

    def test_control_fields_selector(self):
        control_fields = MarcRecord(
            leader="00086nam  2200049   4500",
            fixed_fields={
                "001": "000000123",
                "003": "OCoLC",
                "005": "20230101123456.0",
            },
            variable_fields={},
        ).control_fields_selector
        self.assertEqual(control_fields.control_number, "000000123")
        self.assertEqual(control_fields.control_number_identifier, "OCoLC")
        self.assertEqual(
            control_fields.latest_transaction,
            datetime(2023, 1, 1, 12, 34, 56),
        )

    def test_latest_transaction_none(self):
        control_fields = MarcRecord(
            leader="00086nam  2200049   4500",
            fixed_fields={
                "001": "000000123",
                "003": "OCoLC",
            },
            variable_fields={},
        ).control_fields_selector
        self.assertIsNone(control_fields.latest_transaction)

    def test_latest_transaction_invalid(self):
        control_fields = MarcRecord(
            leader="00086nam  2200049   4500",
            fixed_fields={
                "001": "000000123",
                "003": "OCoLC",
                "005": "invalid-date",
            },
            variable_fields={},
        ).control_fields_selector
        with self.assertRaises(ValueError):
            _ = control_fields.latest_transaction

    def test_issues_selector_empty(self):
        issues_selector = MarcRecord(
            leader="00086nam  2200049   4500",
            fixed_fields={},
            variable_fields={},
        ).issues_selector
        self.assertEqual(len(issues_selector.all), 0)

    def test_issues_selector_with_issues(self):
        record = MarcRecord(
            leader="00086nam  2200049   4500",
            fixed_fields={},
            variable_fields={
                "996": [
                    {
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": {
                            "b": ["123456789"],
                            "m": ["monographic"],
                            "a": ["v.1"],
                        },
                    },
                    {
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": {
                            "b": ["987654321"],
                            "m": ["serial"],
                            "a": ["v.2"],
                        },
                    },
                ]
            },
        )
        record._context.issue_mapping.bundle = None
        issues_selector = record.issues_selector
        self.assertEqual(len(issues_selector.all), 2)
        self.assertEqual(issues_selector.all[0].barcode, "123456789")
        self.assertEqual(issues_selector.all[0].volume_number, "v.1")
        self.assertEqual(issues_selector.all[1].barcode, "987654321")
        self.assertEqual(issues_selector.all[1].volume_number, "v.2")

    def test_issues_selector_find_by_barcode(self):
        issues_selector = MarcRecord(
            leader="00086nam  2200049   4500",
            fixed_fields={},
            variable_fields={
                "996": [
                    {
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": {
                            "b": ["123456789"],
                            "m": ["monographic"],
                            "a": ["v.1"],
                        },
                    },
                    {
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": {
                            "b": ["987654321"],
                            "m": ["serial"],
                            "a": ["v.2"],
                        },
                    },
                ]
            },
        ).issues_selector
        issue = issues_selector.find_by_barcode("987654321")
        self.assertIsNotNone(issue)
        self.assertEqual(issue.barcode, "987654321")
        self.assertEqual(issue.volume_number, "v.2")
        self.assertIsNone(issues_selector.find_by_barcode("000000000"))

    def test_variable_field_query(self):
        variable_fields = MarcRecord(
            leader="00086nam  2200049   4500",
            fixed_fields={},
            variable_fields={
                "015": [
                    {
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": {
                            "a": ["nbn:cz:mzk2023-00001"],
                            "b": ["other data"],
                        },
                    },
                    {
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": {
                            "a": ["nbn:cz:mzk2023-00002"],
                            "b": ["more data"],
                        },
                    },
                ]
            },
        ).variable_fields
        field: VariableField = variable_fields.root["015"][0]
        result = field.query(".subfields.a[]")
        self.assertEqual(result, ["nbn:cz:mzk2023-00001"])
