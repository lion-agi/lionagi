import asyncio

from aiocache import cached

from lionagi import Branch, iModel
from lionagi.lions.judge.config import judge_model_config
from lionagi.lions.judge.forms.code_analysis_form import CodeAnalysisForm
from lionagi.lions.judge.rubric import Rubric


@cached(ttl=3600)
async def judge_code(
    code_submission: str,
    rubric: Rubric,
    instruction: str = None,
    context: str = None,
    model_config: dict = None,
    display_message: bool = True,
    verbose: bool = True,
    language: str = "Python",
) -> CodeAnalysisForm:
    branch = Branch(imodel=iModel(**(model_config or judge_model_config)))
    form = CodeAnalysisForm(
        code_submission=code_submission,
        rubric=rubric,
        instruction=instruction,
        context=context,
        language=language,
    )
    if verbose:
        print("Evaluating code submission...")
    form = await branch.chat(form=form)
    if display_message:
        print(form.display_message)
    return form.to_dict()


async def main():
    from ..data.sample_codes import code1
    from ..data.sample_rurbic import code_quality_rubric

    return await judge_code(
        code_submission=code1,
        rubric=code_quality_rubric,
    )


if __name__ == "__main__":
    asyncio.run(main())
