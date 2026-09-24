import unittest
from unittest.mock import patch

import jq

from marcdantic.fields import VariableField, VariableFields, _compiled
from marcdantic.selectors import IsbnActiveJq, NbnActiveJq

FIELDS = VariableFields(
    {
        "015": [VariableField(subfields={"a": ["cnb002370652"]})],
        "020": [
            VariableField(subfields={"a": ["9788087186824"]}),
            VariableField(subfields={"a": ["9788090424890"], "c": ["250 Kc"]}),
        ],
    }
)


class TestQueryCompilation(unittest.TestCase):
    def setUp(self):
        _compiled.cache_clear()

    def test_a_filter_is_compiled_once_however_often_it_is_used(self):
        # Compiling costs far more than running, and callers query the
        # same module-level selectors once per record across a catalogue.
        with patch(
            "marcdantic.fields.jq.compile", wraps=jq.compile
        ) as compile_:
            for _ in range(100):
                FIELDS.query(IsbnActiveJq)

        self.assertEqual(compile_.call_count, 1)

    def test_distinct_filters_are_compiled_separately(self):
        with patch(
            "marcdantic.fields.jq.compile", wraps=jq.compile
        ) as compile_:
            FIELDS.query(IsbnActiveJq)
            FIELDS.query(NbnActiveJq)
            FIELDS.query(IsbnActiveJq)

        self.assertEqual(compile_.call_count, 2)

    def test_a_reused_program_keeps_returning_the_right_answer(self):
        # A compiled program holds no input, so sharing one between
        # calls must not leak one caller's record into another's result.
        first = FIELDS.query(IsbnActiveJq)
        other = VariableFields(
            {"020": [VariableField(subfields={"a": ["9780000000002"]})]}
        )

        self.assertEqual(first, ["9788087186824", "9788090424890"])
        self.assertEqual(other.query(IsbnActiveJq), ["9780000000002"])
        self.assertEqual(FIELDS.query(IsbnActiveJq), first)

    def test_a_single_field_shares_the_same_cache(self):
        field = VariableField(subfields={"a": ["9788087186824"]})

        with patch(
            "marcdantic.fields.jq.compile", wraps=jq.compile
        ) as compile_:
            field.query(".subfields.a[]")
            field.query(".subfields.a[]")

        self.assertEqual(compile_.call_count, 1)


if __name__ == "__main__":
    unittest.main()
