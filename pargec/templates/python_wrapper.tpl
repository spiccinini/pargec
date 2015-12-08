from cffi import FFI

ffi = FFI()
{% for struct_decl in struct_declarations %}
ffi.cdef("""{{ struct_decl }}""")
{% endfor %}

{% for declaration in declarations %}
ffi.cdef("""{{ declaration }}""")
{% endfor %}

ffi.set_source("_{{ name }}", """\
{{ source }}
""")
ffi.compile()

from _{{ name }} import lib, ffi

{% for struct in structures %}
def {{ struct.name }}_serialize(dict_values):
    {{ struct.c_type }} = ffi.new("{{ struct.c_type }} *", dict_values)
    buffer_out = ffi.new("uint8_t[]", {{ struct.get_serialized_n_bytes() }})

    lib.{{ struct.name }}_serialize({{ struct.c_type }}, buffer_out)
    return bytes(ffi.buffer(buffer_out, {{ struct.get_serialized_n_bytes() }}))

def {{ struct.name }}_deserialize(data_bytes):
    {{ struct.c_type }} = ffi.new("{{ struct.c_type }} *")
    buffer_in = ffi.new("uint8_t[]", data_bytes)

    lib.{{ struct.name }}_deserialize({{ struct.c_type }}, buffer_in)
    return {{ struct.c_type }}
{% endfor %}
