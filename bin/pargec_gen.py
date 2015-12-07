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
        header.write("#ifndef _PROT_\n")
        header.write("#define _PROT_\n\n")
        header.write("#include <stdint.h>\n\n")
        for structure in protocol_file.STRUCTURES:
            header.write(gen_c_struct_decl(structure))
            header.write("\n")

        for structure in protocol_file.STRUCTURES:
            header.write(gen_c_serialize_decl(structure))
            header.write("\n")
            header.write(gen_c_deserialize_decl(structure))
        header.write("\n\n#endif\n")
        header.close()

    with open(args.output_source, "w") as source:
        source.write("#include <stdint.h>\n")
        source.write("#include <%s>\n\n" % args.output_header)

        for structure in protocol_file.STRUCTURES:
            source.write(gen_c_serialize_def(structure))
            source.write("\n")


