required public init?(response: NSHTTPURLResponse, representation: AnyObject) {
    {% for var in var_list %}
        {{ var.if_block() }} {
            {{ var.then_block() }}
        }
    {% endfor %}
    }
