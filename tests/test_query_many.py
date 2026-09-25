"""Asking several filters together must answer exactly as asking them apart.

Handing a record to jq converts the whole of it into jq's own values, so the
cost follows the size of the record rather than the work the filter does --
a filter matching nothing measured the same as one matching two values.
Asking three selectors separately pays that three times. One program asking
all three pays it once, which is only worth doing if the answers are
indistinguishable.
"""

import unittest

from marcdantic import selectors
from marcdantic.fields import VariableField, VariableFields

FIELDS = VariableFields(
    {
        "015": [VariableField(subfields={"a": ["cnb002370652", "cnb000000001"]})],
        "020": [
            VariableField(subfields={"a": ["8020411163"], "c": ["Kc 99,00"]}),
            VariableField(subfields={"a": ["9788020411167"]}),
        ],
        "022": [VariableField(subfields={"a": ["1234-5678"]})],
        "245": [
            VariableField(ind1="1", ind2="0", subfields={"a": ["Title"], "b": ["Sub"]})
        ],
        "856": [
            VariableField(subfields={"u": ["https://example.test/a"], "y": ["Link"]}),
            VariableField(subfields={"u": ["https://example.test/b"]}),
        ],
    }
)

SELECTOR_NAMES = sorted(
    name
    for name in dir(selectors)
    if name.endswith("Jq") and isinstance(getattr(selectors, name), str)
)


class TestTogetherIsTheSameAsApart(unittest.TestCase):
    def test_every_selector_this_package_ships(self):
        self.assertTrue(SELECTOR_NAMES, "no selectors found to check")
        filters = [getattr(selectors, name) for name in SELECTOR_NAMES]

        together = FIELDS.query_many(filters)
        apart = [FIELDS.query(jq_filter) for jq_filter in filters]

        self.assertEqual(len(together), len(filters))
        for name, got, want in zip(SELECTOR_NAMES, together, apart):
            with self.subTest(selector=name):
                self.assertEqual(got, want)

    def test_results_come_back_in_the_order_asked(self):
        self.assertEqual(
            FIELDS.query_many(
                [selectors.IssnActiveJq, selectors.NbnActiveJq, selectors.IsbnActiveJq]
            ),
            [
                FIELDS.query(selectors.IssnActiveJq),
                FIELDS.query(selectors.NbnActiveJq),
                FIELDS.query(selectors.IsbnActiveJq),
            ],
        )

    def test_a_filter_matching_nothing_keeps_its_place(self):
        results = FIELDS.query_many(
            ['.["999"]?[]?.subfields.a[]?', selectors.IsbnActiveJq]
        )

        self.assertEqual(results[0], [])
        self.assertEqual(results[1], ["8020411163", "9788020411167"])

    def test_several_values_do_not_bleed_between_filters(self):
        results = FIELDS.query_many([selectors.NbnActiveJq, selectors.IssnActiveJq])

        self.assertEqual(results, [["cnb002370652", "cnb000000001"], ["1234-5678"]])

    def test_the_same_filter_twice_answers_twice(self):
        results = FIELDS.query_many([selectors.IsbnActiveJq, selectors.IsbnActiveJq])

        self.assertEqual(results[0], results[1])
        self.assertEqual(len(results), 2)

    def test_a_filter_returning_whole_fields_still_works(self):
        together = FIELDS.query_many(['.["856"][]?', selectors.TitleJq])

        self.assertEqual(together[0], FIELDS.query('.["856"][]?'))
        self.assertEqual(together[1], ["Title"])

    def test_asking_for_nothing_returns_nothing(self):
        self.assertEqual(FIELDS.query_many([]), [])

    def test_one_filter_matches_querying_it_alone(self):
        self.assertEqual(
            FIELDS.query_many([selectors.IsbnActiveJq])[0],
            FIELDS.query(selectors.IsbnActiveJq),
        )

    def test_a_record_with_none_of_the_tags_answers_empty_for_each(self):
        empty = VariableFields({"100": [VariableField(subfields={"a": ["Someone"]})]})

        self.assertEqual(
            empty.query_many([selectors.IsbnActiveJq, selectors.TitleJq]), [[], []]
        )


class TestTheCombinedProgramIsCompiledOnce(unittest.TestCase):
    def test_repeating_the_same_filters_reuses_the_program(self):
        import jq
        from unittest.mock import patch

        from marcdantic.fields import _compiled

        _compiled.cache_clear()
        filters = [selectors.IsbnActiveJq, selectors.IssnActiveJq]

        with patch("marcdantic.fields.jq.compile", wraps=jq.compile) as compile_:
            for _ in range(50):
                FIELDS.query_many(filters)

        self.assertEqual(compile_.call_count, 1)


if __name__ == "__main__":
    unittest.main()
