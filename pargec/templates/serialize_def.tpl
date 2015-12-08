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
}
