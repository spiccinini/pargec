#ifndef _{{ basename.upper() }}_
#define _{{ basename.upper() }}_

{{ constants }}

{% for struct_decl in struct_declarations %}
{{ struct_decl }}
{% endfor %}

{% for declaration in declarations %}
{{ declaration }}
{% endfor %}

#endif
