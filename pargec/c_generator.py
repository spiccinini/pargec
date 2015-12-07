from collections import defaultdict
from jinja2 import Template, Environment


jinja_env = Template("").environment
jinja_env.trim_blocks = True
jinja_env.lstrip_blocks = True
serialize_tpl = Template("""\
void {{ name }}_serialize({{c_type }}* in_struct, uint8_t *out_buff) {
{% for byte in out_bytes %}{% set outer_loop = loop %}
    out_buff[{{ loop.index0 }}] = 0;
    {% for field, first, last, mask, field_last_bit in byte %}
       {% if field_last_bit %}
    out_buff[{{ outer_loop.index0 }}] |= (in_struct->{{field}} & {{ mask }}) >> {{ field_last_bit }};
       {% else %}
    out_buff[{{ outer_loop.index0 }}] |= (in_struct->{{field}} & {{ mask }}) << {{ last }};
       {% endif %}
    {% endfor %}
{% endfor %}
}""")


def gen_c_serialize_decl(structure):
    return "void %s_serialize(%s* in_struct, uint8_t *out_buff);" % (
            structure.name,  structure.c_type)


def gen_c_deserialize_decl(structure):
    return "void %s_deserialize(%s* out_struct, uint8_t *in_buff);" % (
            structure.name,  structure.c_type)

def gen_c_struct_decl(structure):
    out = "typedef struct %s {\n" % structure.name
    for field in structure.fields:
        out += "    %s %s;\n" % (field.struct_c_type.c_type, field.name)
    out += "} %s;\n" % structure.c_type
    return out

def gen_c_serialize_def(structure):
    masks = build_bit_masks(structure)
    out_bytes = []
    for field, ranges in masks:
        for range_ in ranges:
            byte, byte_first_bit, byte_last_bit, field_first_bit, field_last_bit = range_
            mask = bin(((1 << (field_first_bit-field_last_bit))-1) << field_last_bit)
            out = (field, byte_first_bit, byte_last_bit, mask, field_last_bit)
            if len(out_bytes) == byte:
                out_bytes.append([out])
            else:
                out_bytes[byte].append(out)

    out = serialize_tpl.render(name=structure.name, c_type=structure.c_type,
                                 out_bytes=out_bytes)
    return out

def gen_c_deserialize_def(structure):
    pass

def gen_c_decl(structure):
    return (self.gen_c_serialize_decl(structure) +
            self.gen_c_deserialize_decl(structure))

def gen_c_def(structure):
    return (self.gen_c_serialize_def(structure) +
             self.gen_c_deserialize_def(structure))

class Byte(object):
    TOTAL_BITS = 8
    def __init__(self):
        self.current_bit = 8
        self.bits_available = True

    def process_bits(self, bits):
        first_bit = self.current_bit
        total_bits = self.current_bit - bits
        if total_bits < 1:
            processed = self.current_bit
            self.current_bit = 0
        else:
            self.current_bit -= bits
            processed = bits

        self.bits_available = self.current_bit != 0

        return first_bit, self.current_bit, processed

def build_bit_masks(structure):
    byte = 0
    current_byte = Byte()
    result = []
    for field in structure.fields:
        field_bits_to_serialize = field.serialized_n_bits
        field_bits = []
        while field_bits_to_serialize > 0:
            byte_first_bit, byte_last_bit, processed = current_byte.process_bits(field_bits_to_serialize)
            field_first_bit = field_bits_to_serialize
            field_bits_to_serialize -= processed
            field_last_bit = field_bits_to_serialize

            field_bits.append((byte, byte_first_bit, byte_last_bit, field_first_bit, field_last_bit))
            if not current_byte.bits_available:
                current_byte = Byte()
                byte += 1
        result.append((field.name, field_bits))
    return result

