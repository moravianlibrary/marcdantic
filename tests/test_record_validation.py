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


if __name__ == "__main__":
    unittest.main()
