from lionfuncs import to_num
from pydantic import Field

from lionagi import Form
from lionagi.lions.judge.rubric import Rubric


class CodeAnalysisForm(Form):
    """
    A structured form for analyzing code submissions based on a given rubric.
    """

    system_prompt: str = Field(
        """
        You are an AI code reviewer proficient in {language}.
        Evaluate the following code submission based on the criteria below,
        each independently scored from 0 to 100.
        Note that you should be objective and fair in your evaluation, with
        focus around sophistication, usability, and correctness.
        """.strip(
            "        "
        )
    )

    code_submission: str | None = Field(
        default=None,
        description="The code_submission to be analyzed.",
    )

    overall_feedback: str | None = Field(
        None, description="Overall feedback based on the evaluation."
    )

    rubric: Rubric
    language: str = "Python"
    assignment: str = "task, code_submission -> overall_feedback"

    def __init__(
        self,
        code_submission,
        rubric: Rubric,
        instruction=None,
        context=None,
        language: str = "Python",
    ):
        super().__init__(
            code_submission=code_submission, language=language, rubric=rubric
        )
        self.task = (
            "Follow the prompt and provide the necessary output.\n"
            f"- Additional instruction: {str(instruction or 'N/A')}\n"
            f"- Additional context: {str(context or 'N/A')}\n"
        )
        self.system_prompt = self.system_prompt.format(language=language)

        for item_name, item in rubric.items.items():
            description = item.description or ""
            description += item.prompt
            description += (
                "response format: {score: number 0-100, comments: string}"
            )
            self.add_field(
                item_name, value=None, annotation=dict, description=description
            )
            self.append_to_request(item_name)

    @property
    def display_message(self) -> str:
        """
        Generates a human-readable message summarizing the evaluation.
        """

        _dict: dict = self.work_fields
        overall_feedback = _dict.pop("overall_feedback")
        ttl_score = 0
        for i in self.rubric.analysis_types:
            score = to_num(
                _dict[i]["score"], upper_bound=100, lower_bound=0, num_type=int
            )
            weighted_score = score * self.rubric.normalized_weight[i]
            ttl_score += weighted_score

        rubric_msg = ""

        message_lines = [
            f"Evaluation Results ({self.timestamp[:-7]}):\n",
            f"Language: {self.language}\n",
            f"Total Score: {ttl_score:.1f}/100\n",
            "----------------------------------------",
            "",
        ]

        for i in message_lines:
            rubric_msg += f"{i}\n"

        for k, v in _dict.items():
            if k in self.rubric.analysis_types:
                t = k.replace("_", " ").title()
                rubric_msg += f"{t}:\nScore: {v['score']}/100\nCriteria Weight: {self.rubric.normalized_weight[k]*100:.1f}%\nComments: {v['comments']}\n\n"

        if overall_feedback:
            rubric_msg += f"Overall Feedback:\n{overall_feedback}\n\n"

        if ttl_score:
            rubric_msg += f"Total Score: {ttl_score:.1f}/100\n\n"

        if ttl_score:
            if ttl_score < 30:
                rubric_msg += "Baby Steps. Not an AI hacker yet. 😅\n"
            elif ttl_score < 50:
                rubric_msg += "There we go! You are a junior AI hacker! 🥳\n"
            elif ttl_score < 70:
                rubric_msg += "Great Work! You are a graduated AI hacker! 🤩\n"
            elif ttl_score < 88:
                rubric_msg += "A master AI hacker! 🤯\n"
            else:
                rubric_msg += "The Lion King of AI Hacking! 🚀🦁🚀\n"

        message = f"""
{rubric_msg}
----------------------------------------
"""
        return message


__all__ = ["CodeAnalysisForm"]
