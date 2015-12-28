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

        self.assertEqual(foo_prot.get_serialized_n_bits(), 16)
        self.assertEqual(foo_prot.get_serialized_n_bytes(), 2)

    def test_get_field_position(self):

        foo_prot = Structure("foo_prot", [
            Field("field1", uint8, 2, FMT_BE_MSB),
            Field("field2", uint8, 3, FMT_BE_MSB),
            Field("field3", uint8, 3, FMT_BE_MSB),
            Field("field4", int8, 8, FMT_BE_MSB),
            ])

        self.assertEqual(foo_prot.field_bit_position(foo_prot.fields[2]), 5)


if __name__ == "__main__":
    unittest.main()
