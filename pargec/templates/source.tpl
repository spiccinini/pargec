#include <stdint.h>
#include <{{ header }}>

{% for definition in definitions %}
{{ definition }}
{% endfor %}
