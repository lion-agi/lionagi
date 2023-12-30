class ToolManager:
    def __init__(self):
        self.registry: Dict[str, BaseTool] = {}

    def _name_exists(self, name: str) -> bool:
        return name in self.registry

    def _register_tool(self, tool: BaseTool, name: Optional[str] = None, update: bool = False,
                       new: bool = False, prefix: Optional[str] = None, postfix: Optional[int] = None):
        name = name or tool.func.__name__
        original_name = name

        if self._name_exists(name):
            if update and new:
                raise ValueError("Cannot both update and create new registry for existing function.")
            if new:
                idx = 1
                while self._name_exists(f"{prefix or ''}{name}{postfix or ''}{idx}"):
                    idx += 1
                name = f"{prefix or ''}{name}{postfix or ''}{idx}"
            else:
                self.registry.pop(original_name, None)

        self.registry[name] = tool

    async def invoke(self, name: str, kwargs: Dict) -> Any:
        if not self._name_exists(name):
            raise ValueError(f"Function {name} is not registered.")

        tool = self.registry[name]
        func = tool.func
        parser = tool.parser

        try:
            result = await func(**kwargs) if asyncio.iscoroutinefunction(func) else func(**kwargs)
            return await parser(result) if parser and asyncio.iscoroutinefunction(parser) else parser(result) if parser else result
        except Exception as e:
            raise ValueError(f"Error invoking function {name}: {str(e)}")

    @staticmethod
    def parse_function_call(response: str) -> Tuple[str, Dict]:
        out = json.loads(response)
        func = out.get('function', '').lstrip('call_')
        args = json.loads(out.get('arguments', '{}'))
        return func, args

    def register_tools(self, tools: List[BaseTool], update: bool = False, new: bool = False,
                       prefix: Optional[str] = None, postfix: Optional[int] = None):
        for tool in tools:
            self._register_tool(tool, update=update, new=new, prefix=prefix, postfix=postfix)