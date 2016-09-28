{{ header }}

{{ imports }}


public class {{ classname }}: ResponseObjectSerializable {

	{% for var in var_list %}
    public var {{var.property_name}}: {{var.property_type}}?
	{% endfor %}

    public init() {}

    {{ required_init_method }}

    {{ encode_to_json_method }}
}
