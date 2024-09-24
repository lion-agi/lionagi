"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Any, Callable

from lion_core.form.base import BaseForm
from lion_core.rule.rule_processor import RuleProcessor


async def process_rule(
    form: BaseForm,
    rule_processor: RuleProcessor | None = None,  # priority 1
    response_: dict | str = None,
    rulebook: Any = None,
    strict: bool = False,
    structure_str: bool = False,
    fallback_structure: Callable = None,
) -> BaseForm:

    if not rule_processor:
        rule_processor = RuleProcessor(
            strict=strict,
            rulebook=rulebook,
            fallback_structure=fallback_structure,
        )

    return await rule_processor.process(
        form=form,
        response=response_,
        structure_str=structure_str,
        fallback_structure=fallback_structure,
    )
