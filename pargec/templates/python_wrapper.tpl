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
def foo_prot_serialize(dict_values):
    foo_prot = ffi.new("foo_prot_t *", dict_values)
    buffer_out = ffi.new("uint8_t[]", {{ struct.get_serialized_n_bytes() }})

    lib.foo_prot_serialize(foo_prot, buffer_out)
    return bytes(ffi.buffer(buffer_out, {{ struct.get_serialized_n_bytes() }}))
{% endfor %}
