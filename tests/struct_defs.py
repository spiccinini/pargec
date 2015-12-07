from pargec.structure import (Structure, Field, uint8, int8,
                               FMT_BE_MSB)

foo = Structure("foo_prot", [
    Field("field1", uint8, 6, FMT_BE_MSB),
    Field("field2", uint8, 4, FMT_BE_MSB),
    Field("field3", uint8, 6, FMT_BE_MSB),
])

STRUCTURES = [foo]
