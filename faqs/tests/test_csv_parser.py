# encoding: utf-8

import unittest
import StringIO

from ..csv_parser import CsvConverter, closest_ascii


class CsvConverterTests(unittest.TestCase):
    def test_parse(self):
        converter = CsvConverter()
        input = StringIO.StringIO("\r\n".join([
        ]))
        faqs = converter.parse(input, 'fr')
        self.assertEqual(faqs, {
        })

    def test_save(self):
        converter = CsvConverter()
        faqs = {}
        converter.save("refugee", "fr", faqs)


class ClosestAsciiTests(unittest.TestCase):
    def test_pure_ascii(self):
        self.assertEqual(closest_ascii(u"abc"), b"abc")
        self.assertEqual(closest_ascii(u"aZ:. 123!"), b"aZ:. 123!")

    def test_non_ascii(self):
        self.assertEqual(closest_ascii(u"ä"), b"a")
        self.assertEqual(closest_ascii(u"æ"), b"")
        self.assertEqual(closest_ascii(u"ó"), b"o")
        self.assertEqual(closest_ascii(u"ß"), b"")
        self.assertEqual(closest_ascii(u"áąéêöó"), b"aaeeoo")
