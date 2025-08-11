from unittest import TestCase

from marcdantic import LocalFieldMapping, MarcIssueMapping
from marcdantic.mapper import MarcMapper


class TestMarcMapper(TestCase):
    def test_set_local_mapping(self):
        mapping = {
            "100": LocalFieldMapping(
                name="author", subfields={"a": "name", "b": "title"}
            )
        }
        MarcMapper.set_local_mapping(mapping)
        self.assertIn("author", MarcMapper.local)
        self.assertEqual(MarcMapper.local["author"].tag, "100")
        self.assertEqual(MarcMapper.local["author"].subfields["name"], "a")

    def test_set_issue_mapping(self):
        issue_mapping = MarcIssueMapping(
            tag="008", barcode="a", issuance_type="b"
        )
        MarcMapper.set_issue_mapping(issue_mapping)
        self.assertEqual(MarcMapper.issue.tag, "008")
        self.assertEqual(MarcMapper.issue.barcode, "a")

    def test_get_non_existent_local_value(self):
        result = MarcMapper.local.get("nonexistent", default="default_value")
        self.assertEqual(result, "default_value")
