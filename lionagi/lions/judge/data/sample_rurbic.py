from lionagi.lions.judge.rubric import Rubric, RubricItem

functionality = RubricItem(
    name="functionality",
    prompt="Assess how well the code meets the functional requirements.",
    weight=2.7,
)

readability = RubricItem(
    name="readability",
    prompt="Evaluate the readability and clarity of the code.",
    weight=1,
)

efficiency = RubricItem(
    name="efficiency",
    prompt="Examine the efficiency of the algorithms used.",
    weight=1.5,
)

style_compliance = RubricItem(
    name="style_compliance",
    prompt="Check adherence to coding style guidelines.",
    weight=0.5,
)

error_handling = RubricItem(
    name="error_handling",
    prompt="Analyze the robustness of error handling mechanisms.",
    weight=1,
)

code_quality_rubric = Rubric(
    name="code_quality_rubric",
    description="Used for assessing code submissions in programming challenges.",
    items={
        i.name: i
        for i in [
            functionality,
            readability,
            efficiency,
            style_compliance,
            error_handling,
        ]
    },
)

__all__ = ["code_quality_rubric"]
