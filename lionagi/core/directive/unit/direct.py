from lionagi.libs.ln_convert import strip_lower
from ..unit import UNIT_DIRECTIVE_MAPPING, UnitDirective


class Direct(UnitDirective):

    async def direct(
        self,
        directive: str,  # examples, "chat", "predict", "act"
        instruction=None,  # additional instruction
        context=None,  # context to perform the instruction on
        **kwargs,
    ):

        directive = strip_lower(directive)

        if directive not in UNIT_DIRECTIVE_MAPPING:
            raise ValueError(f"Directive {directive} not found in DIRECTIVE_MAPPING")

        directive = UNIT_DIRECTIVE_MAPPING[directive](self.branch)

        return await directive.direct(
            context=context,
            instruction=instruction,
            **kwargs,
        )
