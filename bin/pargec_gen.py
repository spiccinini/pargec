import os
import imp
import sys
import argparse

from pargec.c_generator import (gen_c_struct_decl, gen_c_serialize_decl,
                                 gen_c_deserialize_decl, gen_c_serialize_def)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('protocol_file', help='path of the proto.py')
    parser.add_argument('output_header')
    parser.add_argument('output_source')
    args = parser.parse_args()


    protocol_file = imp.load_source('protocol_file', args.protocol_file)
    try:
        protocol_file.STRUCTURES
    except AttributeError:
        sys.stderr.write("protocol_file must contain STRUCTURES list")
        sys.exit(1)

    with open(args.output_header, "w") as header:
        declarations = []
        for structure in protocol_file.STRUCTURES:
            declarations.append(gen_c_serialize_decl(structure))
            declarations.append(gen_c_deserialize_decl(structure))

        struct_declarations = [gen_c_struct_decl(structure) for structure in protocol_file.STRUCTURES]
        header.write(header_tpl.render(struct_declarations=struct_declarations,
                                       declarations=declarations))

    with open(args.output_source, "w") as source:
        definitions = []
        for structure in protocol_file.STRUCTURES:
            definitions.append(gen_c_serialize_def(structure))

        source.write(source_tpl.render(header=args.output_header, definitions=definitions))


