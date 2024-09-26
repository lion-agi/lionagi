from lionagi.core.session.branch import Branch
from lionagi.core.unit.unit import Unit


async def chat(
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    branch=None,
    form=None,
    confidence_score=None,
    reason=False,
    **kwargs,
):
    """
    Performs a chat operation using the specified parameters.

    Args:
        instruction (str, optional): The instruction for the chat.
        context (Any, optional): The context to perform the instruction on.
        system (Any, optional): The system context for the chat.
        sender (str, optional): The sender of the instruction.
        recipient (str, optional): The recipient of the instruction.
        branch (Branch, optional): The branch to use for the chat.
        form (Any, optional): The form to create instruction from.
        confidence_score (float, optional): The confidence score for the operation.
        reason (bool, optional): Whether to include a reason for the operation.
        **kwargs: Additional keyword arguments for the chat operation.

    Returns:
        Any: The result of the chat operation.
    """
    branch = branch or Branch()
    unit = Unit(branch)

    return await unit.chat(
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        form=form,
        confidence_score=confidence_score,
        reason=reason,
        branch=branch,
        **kwargs,
    )


async def select(
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    choices=None,
    branch=None,
    form=None,
    confidence_score=None,
    reason=False,
    **kwargs,
):
    """
    Performs a select operation using the specified parameters.

    Args:
        instruction (str, optional): The instruction for the selection.
        context (Any, optional): The context to perform the instruction on.
        system (Any, optional): The system context for the selection.
        sender (str, optional): The sender of the instruction.
        recipient (str, optional): The recipient of the instruction.
        choices (list, optional): The choices for the selection.
        branch (Branch, optional): The branch to use for the selection.
        form (Any, optional): The form to create instruction from.
        confidence_score (float, optional): The confidence score for the operation.
        reason (bool, optional): Whether to include a reason for the operation.
        **kwargs: Additional keyword arguments for the selection operation.

    Returns:
        Any: The result of the selection operation.
    """
    branch = branch or Branch()
    unit = Unit(branch)

    return await unit.select(
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        choices=choices,
        form=form,
        confidence_score=confidence_score,
        reason=reason,
        **kwargs,
    )


async def predict(
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    branch=None,
    form=None,
    confidence_score=None,
    reason=False,
    num_sentences=1,
    **kwargs,
):
    """
    Performs a predict operation using the specified parameters.

    Args:
        instruction (str, optional): The instruction for the prediction.
        context (Any, optional): The context to perform the instruction on.
        system (Any, optional): The system context for the prediction.
        sender (str, optional): The sender of the instruction.
        recipient (str, optional): The recipient of the instruction.
        branch (Branch, optional): The branch to use for the prediction.
        form (Any, optional): The form to create instruction from.
        confidence_score (float, optional): The confidence score for the operation.
        reason (bool, optional): Whether to include a reason for the operation.
        **kwargs: Additional keyword arguments for the prediction operation.

    Returns:
        Any: The result of the prediction operation.
    """
    branch = branch or Branch()
    unit = Unit(branch)

    return await unit.predict(
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        form=form,
        confidence_score=confidence_score,
        reason=reason,
        num_sentences=num_sentences,
        **kwargs,
    )


async def act(
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    branch=None,
    form=None,
    confidence_score=None,
    reason=False,
    **kwargs,
):
    """
    Performs an act operation using the specified parameters.

    Args:
        instruction (str, optional): The instruction for the action.
        context (Any, optional): The context to perform the instruction on.
        system (Any, optional): The system context for the action.
        sender (str, optional): The sender of the instruction.
        recipient (str, optional): The recipient of the instruction.
        branch (Branch, optional): The branch to use for the action.
        form (Any, optional): The form to create instruction from.
        confidence_score (float, optional): The confidence score for the operation.
        reason (bool, optional): Whether to include a reason for the operation.
        **kwargs: Additional keyword arguments for the act operation.

    Returns:
        Any: The result of the act operation.
    """
    branch = branch or Branch()
    unit = Unit(branch)

    return await unit.act(
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        form=form,
        confidence_score=confidence_score,
        reason=reason,
        **kwargs,
    )


async def score(
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    branch=None,
    form=None,
    confidence_score=None,
    reason=False,
    score_range=None,
    include_endpoints=None,
    num_digit=None,
    **kwargs,
):
    """
    Asynchronously performs a scoring task within a given context.

    Args:
        instruction (str, optional): Additional instruction for the scoring task.
        context (Any, optional): Context to perform the scoring task on.
        system (str, optional): System message to use for the scoring task.
        sender (str, optional): Sender of the instruction. Defaults to None.
        recipient (str, optional): Recipient of the instruction. Defaults to None.
        branch (Branch, optional): Branch to perform the task within. Defaults to a new Branch.
        form (Form, optional): Form to create the instruction from. Defaults to None.
        confidence_score (bool, optional): Flag to include a confidence score. Defaults to None.
        reason (bool, optional): Flag to include a reason for the scoring. Defaults to False.
        score_range (tuple, optional): Range for the score. Defaults to None.
        include_endpoints (bool, optional): Flag to include endpoints in the score range. Defaults to None.
        num_digit (int, optional): Number of decimal places for the score. Defaults to None.
        **kwargs: Additional keyword arguments for further customization.

    Returns:
        Any: The result of the scoring task.
    """

    branch = branch or Branch()
    unit = Unit(branch)

    return await unit.score(
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        form=form,
        confidence_score=confidence_score,
        reason=reason,
        score_range=score_range,
        include_endpoints=include_endpoints,
        num_digit=num_digit,
        **kwargs,
    )


async def plan(
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    branch=None,
    form=None,
    confidence_score=None,
    reason=False,
    num_step=3,
    **kwargs,
):
    """
    Asynchronously generates a step-by-step plan within a given context.

    Args:
        instruction (str, optional): Additional instruction for the planning task.
        context (Any, optional): Context to perform the planning task on.
        system (str, optional): System message to use for the planning task.
        sender (str, optional): Sender of the instruction. Defaults to None.
        recipient (str, optional): Recipient of the instruction. Defaults to None.
        branch (Branch, optional): Branch to perform the task within. Defaults to a new Branch.
        form (Form, optional): Form to create the instruction from. Defaults to None.
        confidence_score (bool, optional): Flag to include a confidence score. Defaults to None.
        reason (bool, optional): Flag to include a reason for the plan. Defaults to False.
        num_step (int, optional): Number of steps in the plan. Defaults to 3.
        **kwargs: Additional keyword arguments for further customization.

    Returns:
        Any: The result of the planning task.
    """

    branch = branch or Branch()
    unit = Unit(branch)

    return await unit.plan(
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        form=form,
        confidence_score=confidence_score,
        reason=reason,
        num_step=num_step,
        **kwargs,
    )
