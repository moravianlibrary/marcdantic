"""What a record is allowed to be missing, and who decides.

Both behaviours here were reached from the same direction: a catalogue
refused a record another catalogue had published, over a field that says
nothing about what the record describes.
"""

import unittest

from lxml import etree

from marcdantic.context import MarcContext
from marcdantic.record import MarcRecord

MARC_NS = "http://www.loc.gov/MARC21/slim"


def _xml(*, control=("001", "005", "008"), subfields='<subfield code="a">Title</subfield>'):
    fields = "".join(
        f'<controlfield tag="{tag}">{"0" * 6}</controlfield>' for tag in control
    )
    return etree.fromstring(
        f'<record xmlns="{MARC_NS}">'
        "<leader>00000nam a2200000 a 4500</leader>"
        f"{fields}"
        f'<datafield tag="245" ind1="1" ind2="0">{subfields}</datafield>'
        "</record>".encode()
    )


class TestMandatoryFieldsFollowTheCaller(unittest.TestCase):
    """The context reaches the check.

    `check_mandatory_fields` used to read `self._context`, which the
    constructors assign only after `model_validate` returns. It therefore
    saw the default on every record, and a caller asking for a shorter
    list was silently held to ["001", "005", "008"].
    """

    def test_the_default_still_requires_005(self):
        with self.assertRaises(ValueError) as caught:
            MarcRecord.from_xml(_xml(control=("001", "008")))

        self.assertIn("005", str(caught.exception))

    def test_a_caller_may_ask_for_less(self):
        record = MarcRecord.from_xml(
            _xml(control=("001",)), MarcContext(mandatory_fields=["001"])
        )

        self.assertEqual(record.fixed_fields.root["001"], "000000")

    def test_a_caller_may_ask_for_more(self):
        with self.assertRaises(ValueError) as caught:
            MarcRecord.from_xml(
                _xml(control=("001", "005", "008")),
                MarcContext(mandatory_fields=["001", "003"]),
            )

        self.assertIn("003", str(caught.exception))

    def test_the_context_survives_onto_the_record(self):
        context = MarcContext(mandatory_fields=["001"])

        record = MarcRecord.from_xml(_xml(control=("001",)), context)

        self.assertEqual(record._context.mandatory_fields, ["001"])


class TestAnEmptySubfieldIsNotABrokenRecord(unittest.TestCase):
    def test_a_subfield_with_no_text_no_longer_fails_the_record(self):
        record = MarcRecord.from_xml(
            _xml(subfields='<subfield code="a">Title</subfield><subfield code="b"/>')
        )

        subfields = record.variable_fields.root["245"][0].subfields
        self.assertEqual(subfields["a"], ["Title"])
        self.assertNotIn("b", subfields)

    def test_the_word_none_is_not_written_into_the_raw_bytes(self):
        """The trap in fixing only the model.

        `from_xml` builds the raw MARC blob with f"{value}", so an absent
        text reaching that line spells "None" into the field — a value no
        catalogue published and every consumer would read as real.
        """

        record = MarcRecord.from_xml(
            _xml(subfields='<subfield code="a">Title</subfield><subfield code="b"/>')
        )

        self.assertNotIn(b"None", record._marc)

    def test_a_control_field_with_no_text_is_absent_rather_than_empty(self):
        with self.assertRaises(ValueError) as caught:
            MarcRecord.from_xml(
                etree.fromstring(
                    f'<record xmlns="{MARC_NS}">'
                    "<leader>00000nam a2200000 a 4500</leader>"
                    '<controlfield tag="001">000001</controlfield>'
                    '<controlfield tag="005"/>'
                    '<controlfield tag="008">000000</controlfield>'
                    "</record>".encode()
                )
            )

        self.assertIn("005", str(caught.exception))


class TestAnIndicatorOutsideTheStandardStillParses(unittest.TestCase):
    """MZK03-001252166 carries ind1="S" on a 500, and vanished over it.

    The record was refused by the parser, so the catalogue answered 404 for
    it and the review queue never saw it. Both halves of that are wrong: the
    record is readable, and the indicator is a cataloguing error somebody
    should be told about — which cannot happen while the record holding it
    is the one thing nobody can open.
    """

    def _record(self, ind1: str, context: MarcContext | None = None) -> MarcRecord:
        return MarcRecord.from_xml(
            etree.fromstring(
                f'<record xmlns="{MARC_NS}">'
                "<leader>00000nam a2200000 a 4500</leader>"
                '<controlfield tag="001">000001</controlfield>'
                '<controlfield tag="005">000000</controlfield>'
                '<controlfield tag="008">000000</controlfield>'
                f'<datafield tag="500" ind1="{ind1}" ind2=" ">'
                '<subfield code="a">A note</subfield>'
                "</datafield>"
                "</record>".encode()
            ),
            context or MarcContext(),
        )

    def _field(self, ind1: str):
        return self._record(ind1).variable_fields.root["500"][0]

    def test_an_uppercase_indicator_is_kept_as_it_was_catalogued(self):
        self.assertEqual(self._field("S").ind1, "S")

    def test_the_fill_character_is_kept_too(self):
        self.assertEqual(self._field("|").ind1, "|")

    def test_a_blank_is_still_nothing(self):
        self.assertIsNone(self._field(" ").ind1)

    def test_a_lowercase_indicator_is_unaffected(self):
        self.assertEqual(self._field("a").ind1, "a")

    def test_the_raw_bytes_keep_the_indicator(self):
        self.assertIn(b"S ", self._record("S")._marc)

    def test_a_caller_may_hold_records_to_the_standard(self):
        with self.assertRaises(ValueError) as caught:
            self._record("S", MarcContext(indicator_pattern=r"^[0-9a-z| ]?$"))

        self.assertIn("'S'", str(caught.exception))

    def test_a_tighter_pattern_still_takes_what_it_allows(self):
        field = self._record(
            "1", MarcContext(indicator_pattern=r"^[0-9a-z| ]?$")
        ).variable_fields.root["500"][0]

        self.assertEqual(field.ind1, "1")

    def test_two_characters_are_not_an_indicator_under_any_pattern(self):
        with self.assertRaises(ValueError):
            self._record("10")


if __name__ == "__main__":
    unittest.main()
