import math
FMT_BE_MSB = 0

class Structure(object):
    def __init__(self, name, fields, c_type=None):
        self.name = name
        self.fields = fields
        self.c_type = c_type or "%s_t" % name

    def get_serialized_n_bits(self):
        return sum([field.serialized_n_bits for field in self.fields])

    def get_serialized_n_bytes(self):
        return math.ceil(self.get_serialized_n_bits() / 8.)

    def field_bit_position(self, field):
        bits = 0
        for iter_field in self.fields:
            if iter_field is field:
                break
            bits += iter_field.serialized_n_bits
        return bits

class Field(object):
    def __init__(self, name, struct_c_type, serialized_n_bits,
                 serialized_format):
        self.name = name
        self.struct_c_type = struct_c_type
        self.serialized_n_bits = serialized_n_bits
        self.serialized_format = serialized_format

    def get_c_type_str(self):
        return "%s %s" % (self.struct_c_type.c_type, self.name)

class ArrayField(Field):
    ARRAY = True
    def __init__(self, name, struct_c_type, serialized_n_bits,
                 serialized_format):
        self.name = name
        self.struct_c_type = struct_c_type
        self.serialized_n_bits = serialized_n_bits
        self.serialized_format = serialized_format

    def get_c_type_str(self):
        c_type, n_bits = self.struct_c_type.c_type, self.struct_c_type.n_bits
        return "%s %s[%d]" % (c_type, self.name, self.serialized_n_bits/n_bits)

class CType(object):
    def __init__(self, c_type, n_bits):
        self.c_type = c_type
        self.n_bits = n_bits

class CEnum(CType):
    def __init__(self, c_type, n_bits, constants):
        super(self).__init__(c_type, n_bits)
        self.constants = constants

uint8 = CType("uint8_t", 8)
int8 = CType("int8_t", 8)
uint16 = CType("uint16_t", 16)
uint32 = CType("uint32_t", 32)


C_TYPES = [uint8, int8, uint16, uint32]
