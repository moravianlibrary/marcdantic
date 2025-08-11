from unittest import TestCase

from pydantic import ValidationError

from marcdantic.query import (
    MarcBoolQuery,
    MarcCondition,
    MarcSearchRequest,
    SearchOperator,
)


class TestMarcSearchRequest(TestCase):
    def test_valid_marc_condition(self):
        cond = MarcCondition(
            field="245",
            subfield="a",
            value="Python",
            operator=SearchOperator.Contains,
        )
        self.assertEqual(cond.operator, SearchOperator.Contains)
        self.assertEqual(cond.field, "245")

    def test_invalid_field_length(self):
        with self.assertRaises(ValidationError):
            MarcCondition(field="24", value="test")

    def test_marc_bool_query(self):
        cond1 = MarcCondition(field="100", value="John Doe")
        cond2 = MarcCondition(field="245", value="Python")
        query = MarcBoolQuery(must=[cond1], should=[cond2])
        self.assertEqual(len(query.must), 1)
        self.assertEqual(len(query.should), 1)

    def test_marc_search_request_defaults(self):
        query = MarcBoolQuery(must=[MarcCondition(field="100", value="John")])
        request = MarcSearchRequest(query=query)
        self.assertEqual(request.page, 1)
        self.assertEqual(request.page_size, 10)
