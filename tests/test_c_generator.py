import os
import unittest
import subprocess
from tempfile import NamedTemporaryFile

from pargec.structure import (Structure, Field, uint8, int8,
                               FMT_BE_MSB)
from pargec.c_generator import (gen_c_struct_decl, gen_c_serialize_decl,
                                 gen_c_deserialize_decl, gen_c_serialize_def,
                                 gen_c_deserialize_def,
                                 gen_c_defines, generate,
                                 build_bit_masks, Byte)

FOO_STRUCT = """typedef struct foo_prot {
    uint8_t field1;
    uint8_t field2;
    uint8_t field3;
} foo_prot_t;
"""

FOO_DEFINES = """\
#define FOO_PROT_SERIALIZED_N_BYTES 2
"""

FOO_SERIALIZE_DECL = "void foo_prot_serialize(foo_prot_t* in_struct, uint8_t *out_buff);"
FOO_DESERIALIZE_DECL = "void foo_prot_deserialize(foo_prot_t* out_struct, uint8_t *in_buff);"

FOO_SERIALIZE_DEF = """\
void foo_prot_serialize(foo_prot_t* in_struct, uint8_t *out_buff) {
    out_buff[0] = 0;
    out_buff[0] |= (in_struct->field1 & 0b111111) << 2;
    out_buff[0] |= (in_struct->field2 & 0b1100) >> 2;
    out_buff[1] = 0;
    out_buff[1] |= (in_struct->field2 & 0b11) << 6;
    out_buff[1] |= (in_struct->field3 & 0b111111) << 0;
}"""

FOO_DESERIALIZE_DEF = """\
void foo_prot_deserialize(foo_prot_t* out_struct, uint8_t *in_buff) {
    out_struct->field1 = 0;
    out_struct->field1 |= (in_buff[0] >> 2) & 0b111111;
    out_struct->field2 = 0;
    out_struct->field2 |= (in_buff[0] & 0b11) << 2;
    out_struct->field2 |= (in_buff[1] >> 6) & 0b11;
    out_struct->field3 = 0;
    out_struct->field3 |= (in_buff[1] >> 0) & 0b111111;
}"""

MULTIBYTE_DESERIALIZE_DEF = """\
void prot_multi_deserialize(prot_multi_t* out_struct, uint8_t *in_buff) {
    out_struct->field1 = 0;
    out_struct->field1 |= (in_buff[0] >> 2) & 0b111111;
    out_struct->field2 = 0;
    out_struct->field2 |= (in_buff[0] & 0b11) << 10;
    out_struct->field2 |= (in_buff[1] & 0b11111111) << 2;
    out_struct->field2 |= (in_buff[2] >> 6) & 0b11;
    out_struct->field3 = 0;
    out_struct->field3 |= (in_buff[2] & 0b111111) << 10;
    out_struct->field3 |= (in_buff[3] & 0b11111111) << 2;
    out_struct->field3 |= (in_buff[4] >> 6) & 0b11;
}"""

MULTIBYTE_SERIALIZE_DEF = """\
void prot_multi_serialize(prot_multi_t* in_struct, uint8_t *out_buff) {
    out_buff[0] = 0;
    out_buff[0] |= (in_struct->field1 & 0b111111) << 2;
    out_buff[0] |= (in_struct->field2 & 0b110000000000) >> 10;
    out_buff[1] = 0;
    out_buff[1] |= (in_struct->field2 & 0b1111111100) >> 2;
    out_buff[2] = 0;
    out_buff[2] |= (in_struct->field2 & 0b11) << 6;
    out_buff[2] |= (in_struct->field3 & 0b1111110000000000) >> 10;
    out_buff[3] = 0;
    out_buff[3] |= (in_struct->field3 & 0b1111111100) >> 2;
    out_buff[4] = 0;
    out_buff[4] |= (in_struct->field3 & 0b11) << 6;
}"""

class TestCGenerator(unittest.TestCase):
    def setUpClass():
        foo_prot = Structure("foo_prot", [
            Field("field1", uint8, 6, FMT_BE_MSB),
            Field("field2", uint8, 4, FMT_BE_MSB),
            Field("field3", uint8, 6, FMT_BE_MSB),
            ])
        TestCGenerator.foo_prot = foo_prot

    def test_gen_c_struct_decl(self):
        c_struct = gen_c_struct_decl(self.foo_prot)
        self.assertEqual(c_struct, FOO_STRUCT)

    def test_gen_c_serialize_decl(self):
        self.assertEqual(gen_c_serialize_decl(self.foo_prot), FOO_SERIALIZE_DECL)

    def test_gen_c_deserialize_decl(self):
        self.assertEqual(gen_c_deserialize_decl(self.foo_prot), FOO_DESERIALIZE_DECL)

    def test_gen_c_serialize_def(self):
        self.assertEqual(gen_c_serialize_def(self.foo_prot), FOO_SERIALIZE_DEF)

    def test_gen_c_deserialize_def(self):
        self.maxDiff = None
        self.assertEqual(gen_c_deserialize_def(self.foo_prot), FOO_DESERIALIZE_DEF)

    def test_gen_c_defines(self):
        self.assertEqual(gen_c_defines(self.foo_prot), FOO_DEFINES)

    def test_bit_masks_inside_byte(self):
        prot = Structure("foo_prot", [
            Field("field1", uint8, 6, FMT_BE_MSB),
            Field("field2", uint8, 4, FMT_BE_MSB),
            Field("field3", uint8, 6, FMT_BE_MSB),
            ])

        res = build_bit_masks(prot)
        masks = [("field1", [(0, 8, 2, 6, 0)]),
                 ("field2", [(0, 2, 0, 4, 2), (1, 8, 6, 2, 0)]),
                 ("field3", [(1, 6, 0, 6, 0)]),
        ]
        self.assertEqual(res, masks)

    def test_bit_masks_multibyte(self):
        prot = Structure("prot_multi", [
            Field("field1", uint8, 6, FMT_BE_MSB),
            Field("field2", uint8, 12, FMT_BE_MSB),
            Field("field3", uint8, 16, FMT_BE_MSB),
            ])

        #byte, byte_first_bit, byte_last_bit, first_bit_to_serialize, last_bit_to_serialize
        res = build_bit_masks(prot)
        masks = [("field1", [(0, 8, 2, 6, 0)]),
                 ("field2", [(0, 2, 0, 12, 10), (1, 8, 0, 10, 2), (2, 8, 6, 2, 0)]),
                 ("field3", [(2, 6, 0, 16, 10), (3, 8, 0, 10, 2), (4, 8, 6, 2, 0)])
        ]
        self.assertEqual(res, masks)
        self.maxDiff = None
        self.assertEqual(gen_c_serialize_def(prot), MULTIBYTE_SERIALIZE_DEF)
        self.assertEqual(gen_c_deserialize_def(prot), MULTIBYTE_DESERIALIZE_DEF)

    def test_byte(self):
        byte = Byte()
        self.assertEqual(byte.process_bits(2), (8, 6, 2))
        self.assertEqual(byte.process_bits(2), (6, 4, 2))
        self.assertEqual(byte.process_bits(2), (4, 2, 2))
        self.assertTrue(byte.bits_available)
        self.assertEqual(byte.process_bits(2), (2, 0, 2))
        self.assertFalse(byte.bits_available)

        byte = Byte()
        self.assertEqual(byte.process_bits(2), (8, 6, 2))
        self.assertEqual(byte.process_bits(4), (6, 2, 4))
        self.assertEqual(byte.process_bits(4), (2, 0, 2))

        byte = Byte()
        self.assertTrue(byte.bits_available)
        self.assertEqual(byte.process_bits(10), (8, 0, 8))
        self.assertFalse(byte.bits_available)

    def test_build(self):
        out_file = NamedTemporaryFile(suffix=".c", delete=False)
        out_file.write("#include <stdint.h>\n".encode())
        out_file.write(gen_c_struct_decl(self.foo_prot).encode())
        out_file.write(gen_c_serialize_decl(self.foo_prot).encode())
        out_file.write(gen_c_serialize_def(self.foo_prot).encode())
        out_file.write("void main(void){}".encode())
        out_file.close()

        tmp_out = "/tmp/a.out"

        subprocess.check_call(["gcc", os.path.abspath(out_file.name), "-o", tmp_out])
        os.remove(tmp_out)
        os.remove(out_file.name)

    def test_online_cffi(self):
        from cffi import FFI
        ffi = FFI()
        ffi.cdef(gen_c_struct_decl(self.foo_prot))
        ffi.cdef(gen_c_serialize_decl(self.foo_prot))

        ffi.set_source("_test_online_cffi",
            gen_c_struct_decl(self.foo_prot)+"\n"+
            gen_c_serialize_def(self.foo_prot))
        ffi.compile(tmpdir='tests')

        from _test_online_cffi import lib, ffi as nffi
        buffer_out = nffi.new("uint8_t[]", 100)
        foo_prot = nffi.new("foo_prot_t *", [0b100001, 0b1111, 0b11])
        lib.foo_prot_serialize(foo_prot, buffer_out)
        self.assertEqual(buffer_out[0], (0b100001 << 2) | 0b11 )
        self.assertEqual(buffer_out[1], (0b11 << 6) | 0b11 )

    def test_generate_and_integration(self):
        TESTS_PATH = os.path.dirname(os.path.realpath(__file__))
        protocol_file = os.path.join(TESTS_PATH, "struct_defs.py")
        generate(protocol_file, os.path.join(TESTS_PATH, "foo.h"),
                 os.path.join(TESTS_PATH, "foo.c"),
                 os.path.join(TESTS_PATH, "foo.py"))
        import foo
        in_data = {"field1": 0b100001, "field2":0b1111, "field3":0b11}
        out_buff = foo.foo_prot_serialize(in_data)
        self.assertEqual(out_buff, bytes([(0b100001 << 2) | 0b11, (0b11 << 6) | 0b11]))
        values = foo.foo_prot_deserialize(out_buff)
        self.assertTrue(all([getattr(values, key) == in_data[key] for key in in_data.keys()]))


if __name__ == "__main__":
    unittest.main()
