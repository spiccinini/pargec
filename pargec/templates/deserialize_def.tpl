void {{ name }}_deserialize({{c_type }}* out_struct, uint8_t *in_buff) {
{% for field, ranges in masks %}
    out_struct->{{field}} = 0;
    {% for byte, byte_first_bit, byte_last_bit, mask, field_last_bit in ranges %}
       {% if field_last_bit %}
    out_struct->{{field}} |= (in_buff[{{ byte }}] & {{ mask }}) << {{ field_last_bit }};
       {% else %}
    out_struct->{{field}} |= (in_buff[{{ byte }}] >> {{ byte_last_bit }}) & {{ mask }};
       {% endif %}
    {% endfor %}
{% endfor %}
}
