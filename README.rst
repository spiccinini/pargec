==========================================
pargec generates C binary/protocol parsers
==========================================

pargec generates C code for parsing binary structures (eg: protocol headers) from
a Structure declaration like the following::

    foo = Structure("foo_prot", [
        Field("field1", uint8, 6, FMT_BE_MSB),
        Field("field2", uint8, 4, FMT_BE_MSB),
        Field("field3", uint8, 6, FMT_BE_MSB),
    ])

Also pargec generates a python wrapper of the C code.
