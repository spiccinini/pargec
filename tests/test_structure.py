import unittest
from pargec.structure import (Structure, Field, uint8, uint16, int8,
                               FMT_BE_MSB)


class StructureTestCase(unittest.TestCase):
    def test_init(self):

        foo_prot = Structure("foo_prot", [
            Field("field1", uint8, 2, FMT_BE_MSB),
            Field("field2", uint8, 3, FMT_BE_MSB),
            Field("field3", uint8, 3, FMT_BE_MSB),
            Field("field4", int8, 8, FMT_BE_MSB),
            ])
        self.assertEqual(len(foo_prot.fields), 4)

