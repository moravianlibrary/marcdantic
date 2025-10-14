import unittest

from lxml import etree

from marcdantic.context import MarcContext
from marcdantic.from_mrc import from_mrc
from marcdantic.from_xml import from_xml


class TestParsers(unittest.TestCase):
    def setUp(self):
        # Sample minimal MARC XML record string for testing
        self.sample_xml = """
        <record xmlns="http://www.loc.gov/MARC21/slim">
          <leader>00000nam  2200000   4500</leader>
          <controlfield tag="001">123456</controlfield>
          <datafield tag="245" ind1="1" ind2="0">
            <subfield code="a">Test Title</subfield>
            <subfield code="b">Test Subtitle</subfield>
          </datafield>
        </record>
        """
        self.xml_root = etree.fromstring(self.sample_xml)

        # Sample minimal MARC record bytes for testing from_mrc
        # Using ASCII encoding, leader 24 bytes + directory + field data
        # This is a simplified and contrived example just for test purpose
        self.sample_mrc = (
            b"00086nam  2200049   4500"  # Leader (24 bytes), base address = 49
            b"001000500000"  # Directory entry: tag=001, len=0005, offset=00000
            b"245003000005"  # Directory entry: tag=245, len=0030, offset=00005
            b"\x1e1234"  # Field 001 data (4 bytes)
            b"\x1e10"  # Field 245 begins: indicators "1", "0"
            b"\x1faTest Title"  # Subfield a
            b"\x1fbTest Subtitle"  # Subfield b
            b"\x1d"  # Record terminator
        )

    def test_from_xml(self):
        record = from_xml(self.xml_root, MarcContext())
        self.assertIn("leader", record)
        self.assertIn("fixed_fields", record)
        self.assertIn("variable_fields", record)

        self.assertIn("001", record["fixed_fields"])
        self.assertEqual(record["fixed_fields"]["001"], "123456")

        self.assertIn("245", record["variable_fields"])
        self.assertEqual(
            record["variable_fields"]["245"][0]["subfields"]["a"][0],
            "Test Title",
        )
        self.assertEqual(
            record["variable_fields"]["245"][0]["subfields"]["b"][0],
            "Test Subtitle",
        )

    def test_from_mrc(self):
        record = from_mrc(self.sample_mrc, MarcContext())
        self.assertIn("leader", record)
        self.assertIn("fixed_fields", record)
        self.assertIn("variable_fields", record)

        self.assertIn("001", record["fixed_fields"])
        self.assertEqual(record["fixed_fields"]["001"], "1234")

        self.assertIn("245", record["variable_fields"])
        self.assertEqual(
            record["variable_fields"]["245"][0]["subfields"]["a"][0],
            "Test Title",
        )
        self.assertEqual(
            record["variable_fields"]["245"][0]["subfields"]["b"][0],
            "Test Subtitle",
        )
