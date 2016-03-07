{% if structures %}
enum {
    {% for structure in structures %}
    {{prefix}}{{ structure.name.upper() }}_SERIALIZED_N_BYTES = {{ structure.get_serialized_n_bytes() }},
    {% endfor %}
};
{% endif %}