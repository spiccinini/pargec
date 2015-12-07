
FMT_BE_MSB = 0

class Structure(object):
    def __init__(self, name, fields, c_type=None):
        self.name = name
        self.fields = fields
        self.c_type = c_type or "%s_t" % name


class Field(object):
    def __init__(self, name, struct_c_type, serialized_n_bits,
                 serialized_format):
        self.name = name
        self.struct_c_type = struct_c_type
        self.serialized_n_bits = serialized_n_bits
        self.serialized_format = serialized_format

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


C_TYPES = [uint8, int8, uint16]
