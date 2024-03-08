class Tool(BaseRelatableNode):

    func: Any
    schema_: dict | None = None
    manual: Any | None = None
    parser: Any | None = None

    @pyd.field_serializer("func")
    def serialize_func(self, func):
        return func.__name__

