from typing import Any, Literal

from lion_core.communication.instruction import Instruction
from lion_core.communication.message import MessageFlag


def handle_instruction(
    sender: Any | MessageFlag,
    recipient: Any | MessageFlag,
    instruction: Any | MessageFlag,
    context: Any | MessageFlag,
    guidance: Any | MessageFlag,
    request_fields: dict | MessageFlag,
    images: list | MessageFlag,
    image_detail: Literal["low", "high", "auto"] | MessageFlag,
):
    if isinstance(instruction, Instruction):
        if context:
            instruction.update_context(context)
        if request_fields:
            instruction.update_request_fields(
                request_fields=request_fields,
            )
        if images:
            instruction.update_images(
                images=images,
                image_detail=image_detail,
            )
        if guidance:
            instruction.update_guidance(
                guidance=guidance,
            )
        return instruction

    return Instruction(
        instruction=instruction,
        context=context,
        guidance=guidance,
        images=images,
        sender=sender,
        recipient=recipient,
        request_fields=request_fields,
        image_detail=image_detail,
    )
