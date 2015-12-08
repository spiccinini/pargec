#ifndef _PROT_
#define _PROT_

{{ defines }}

{% for struct_decl in struct_declarations %}
{{ struct_decl }}
{% endfor %}

{% for declaration in declarations %}
{{ declaration }}
{% endfor %}

#endif
