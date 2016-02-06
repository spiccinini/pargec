void {{ name }}_serialize({{c_type }}* in_struct, uint8_t *out_buff) {
{% for byte_ in out_bytes %}
    {% for field, byte, first, last, mask, field_last_bit, empty in byte_ %}
       {% if empty %}
    out_buff[{{ byte_[0][1] }}] = 0;
       {% endif %}
       {% if field_last_bit %}
    out_buff[{{ byte }}] |= (in_struct->{{field}} & {{ mask }}) >> {{ field_last_bit }};
       {% else %}
    out_buff[{{ byte }}] |= (in_struct->{{field}} & {{ mask }}) << {{ last }};
       {% endif %}
    {% endfor %}
{% endfor %}
{% for field, first_byte, length in arrays %}
    for(int i = 0; i < {{ length }}; ++i){out_buff[{{ first_byte }}+i] = in_struct->{{ field }}[i];}
{% endfor %}
}
