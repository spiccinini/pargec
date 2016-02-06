import imp
import math
from collections import defaultdict
from jinja2 import Template, Environment, PackageLoader


jinja_env = Environment(loader=PackageLoader('pargec', 'templates'),
                        trim_blocks=True, lstrip_blocks=True)

serialize_tpl = jinja_env.get_template('serialize_def.tpl')
deserialize_tpl = jinja_env.get_template('deserialize_def.tpl')
header_tpl = jinja_env.get_template('header.tpl')
source_tpl = jinja_env.get_template('source.tpl')
python_tpl = jinja_env.get_template('python_wrapper.tpl')

def gen_c_serialize_decl(structure):
    return "void %s_serialize(%s* in_struct, uint8_t *out_buff);" % (
            structure.name,  structure.c_type)


def gen_c_deserialize_decl(structure):
    return "void %s_deserialize(%s* out_struct, uint8_t *in_buff);" % (
            structure.name,  structure.c_type)

def gen_c_struct_decl(structure):
    out = "typedef struct %s {\n" % structure.name
    for field in structure.fields:
        out += "    %s;\n" % field.get_c_type_str()
    out += "} %s;\n" % structure.c_type
    return out

def _build_arrays(structure):
    # arrays
    arrays = []
    for field in structure.fields:
        if hasattr(field, "ARRAY"):
            first_byte = structure.field_bit_position(field) // 8
            length = field.serialized_n_bits // 8
            arrays.append((field.name, first_byte, length))
    return arrays

def gen_c_serialize_def(structure):
    masks = build_bit_masks(structure)
    out_bytes = []
    last_byte = None
    for field, ranges in masks:
        for range_ in ranges:
            byte, byte_first_bit, byte_last_bit, field_first_bit, field_last_bit = range_
            mask = bin(((1 << (field_first_bit-field_last_bit))-1) << field_last_bit)
            empty = byte != last_byte
            out = (field, byte, byte_first_bit, byte_last_bit, mask, field_last_bit, empty)

            if empty:
                out_bytes.append([out])
            else:
                out_bytes[-1].append(out)

            last_byte = byte

    arrays = _build_arrays(structure)

    out = serialize_tpl.render(name=structure.name, c_type=structure.c_type,
                               out_bytes=out_bytes, arrays=arrays)
    return out

def gen_c_deserialize_def(structure):
    masks = build_bit_masks(structure)
    new_masks = []
    for field, ranges in masks:
        ranges_ = []
        for range_ in ranges:
            byte, byte_first_bit, byte_last_bit, field_first_bit, field_last_bit = range_
            mask = bin(((1 << (byte_first_bit-byte_last_bit))-1))
            out = (byte, byte_first_bit, byte_last_bit, mask, field_last_bit)
            ranges_.append(out)
        new_masks.append((field, ranges_))

    arrays = _build_arrays(structure)

    out = deserialize_tpl.render(name=structure.name, c_type=structure.c_type,
                                 masks=new_masks, arrays=arrays)
    return out

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
        if hasattr(field, "ARRAY"): # skip arrays
            byte += field.serialized_n_bits//8
            continue

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

def gen_c_defines(structure):
    n_bytes = structure.get_serialized_n_bytes()
    return "#define %s_SERIALIZED_N_BYTES %d\n" % (structure.name.upper(), n_bytes)

def generate(protocol_file, output_header, output_source, output_python=None, basename='proto'):
    protocol_file = imp.load_source('protocol_file', protocol_file)
    try:
        protocol_file.STRUCTURES
    except AttributeError:
        sys.stderr.write("protocol_file must contain STRUCTURES list")
        sys.exit(1)

    struct_declarations = [gen_c_struct_decl(structure) for structure in protocol_file.STRUCTURES]
    defines = [gen_c_defines(structure) for structure in protocol_file.STRUCTURES]
    declarations = []
    for structure in protocol_file.STRUCTURES:
        declarations.append(gen_c_serialize_decl(structure))
        declarations.append(gen_c_deserialize_decl(structure))

    definitions = []
    for structure in protocol_file.STRUCTURES:
        definitions.append(gen_c_serialize_def(structure))
        definitions.append(gen_c_deserialize_def(structure))

    with open(output_header, "w") as header:
        header.write(header_tpl.render(struct_declarations=struct_declarations,
                                       declarations=declarations, defines=defines,
                                       basename=basename))

    with open(output_source, "w") as source:
        source.write(source_tpl.render(header=output_header, definitions=definitions))

    if output_python:
        with open(output_python, "w") as python:
            source =  "\n".join(defines) + "\n".join(struct_declarations) + "\n".join(definitions)
            python.write(python_tpl.render(struct_declarations=struct_declarations, name=basename,
                              declarations=declarations, source=source, structures=protocol_file.STRUCTURES))
