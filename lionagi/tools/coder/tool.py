# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import os
from typing import Any, Dict

from lionagi.operatives.action.tool import Tool
from lionagi.tools.base import LionTool

from .session import AiderSessionRegistry
from .types import (
    AiderAction,
    ChatMode,
    CoderRequest,
    CoderResponse,
    SessionState,
)


class CoderTool(LionTool):
    """
    CoderTool provides a programmatic interface to aider's functionality.

    Key features:
    - Session management (create, resume, end sessions)
    - File operations (add, drop files)
    - Code editing in different modes (architect, code, ask)
    - Git integration
    - Testing and linting support

    The tool maintains session state and handles process management
    for persistent aider instances.
    """

    is_lion_system_tool = True
    system_tool_name = "coder_tool"

    def __init__(self):
        super().__init__()
        self.registry = AiderSessionRegistry()
        self._tool = None

    async def handle_request(self, request: CoderRequest) -> CoderResponse:
        """
        Process a coder request and return a response.

        Args:
            request (CoderRequest): The request containing action and parameters

        Returns:
            CoderResponse: Result of the operation
        """
        if isinstance(request, dict):
            request = CoderRequest(**request)

        try:
            # Get or create session
            session = await self.registry.get_or_create(
                session_id=request.session_id,
                working_dir=request.working_dir or os.getcwd(),
                model=request.model,
                git_enabled=request.git_enabled,
            )

            # Execute action with session lock
            async with self.registry.locks[session.session_id]:
                try:
                    result = await self._execute_action(session, request)
                finally:
                    # Always cleanup if not persisting, but don't override operation error
                    if not request.persist_session:
                        await self.registry.cleanup(session.session_id)

            return CoderResponse(
                success=True,
                session_id=session.session_id,
                output=result.get("output"),
                final_diff=result.get("diff"),
                git_status=session.state.git_status,
                session_state=session.state,
            )

        except Exception as e:
            session_id = (
                getattr(session, "session_id", request.session_id)
                if "session" in locals()
                else request.session_id
            )
            return CoderResponse(
                success=False, error=str(e), session_id=session_id
            )

    async def _execute_action(
        self, session: "AiderSession", request: CoderRequest
    ) -> Dict[str, Any]:
        """Execute the requested action in the session."""

        # Update chat mode if specified
        if request.chat_mode:
            await session.execute(f"/chat-mode {request.chat_mode.value}")

        # Process action
        match request.action:
            case AiderAction.START_SESSION:
                return {"success": True, "output": "Session started"}

            case AiderAction.END_SESSION:
                await session.stop()
                return {"success": True, "output": "Session ended"}

            case AiderAction.ADD_FILES:
                if not request.files:
                    raise ValueError(
                        "files parameter required for ADD_FILES action"
                    )
                return await session.execute(f"/add {' '.join(request.files)}")

            case AiderAction.DROP_FILES:
                if not request.files:
                    raise ValueError(
                        "files parameter required for DROP_FILES action"
                    )
                return await session.execute(
                    f"/drop {' '.join(request.files)}"
                )

            case AiderAction.ARCHITECT | AiderAction.CODE | AiderAction.ASK:
                instruction = request.instruction
                if not instruction:
                    raise ValueError(
                        f"instruction required for {request.action.value} action"
                    )

                command = f"/{request.action.value}"
                if request.command:
                    command = request.command

                return await session.execute(f"{command} {instruction}")

            case AiderAction.RUN_COMMAND:
                if not request.command:
                    raise ValueError("command required for RUN_COMMAND action")
                return await session.execute(request.command)

            case AiderAction.RUN_TEST:
                return await session.execute("/test")

            case AiderAction.RUN_LINT:
                return await session.execute("/lint")

            case AiderAction.COMMIT:
                command = "/commit"
                if request.commit_message:
                    command += f" {request.commit_message}"
                return await session.execute(command)

            case AiderAction.SHOW_DIFF:
                return await session.execute("/diff")

            case _:
                raise ValueError(f"Unknown action: {request.action}")

    def to_tool(self) -> Tool:
        """Convert to a Tool instance for use with Branch."""
        if self._tool is None:

            async def coder_tool(**kwargs) -> dict:
                """
                Execute aider operations via CoderTool.

                Args:
                    **kwargs: Arguments matching CoderRequest schema

                Returns:
                    dict: The CoderResponse as a dictionary
                """
                resp = await self.handle_request(CoderRequest(**kwargs))
                return resp.model_dump()

            if self.system_tool_name != "coder_tool":
                coder_tool.__name__ = self.system_tool_name

            self._tool = Tool(
                func_callable=coder_tool, request_options=CoderRequest
            )

        return self._tool
