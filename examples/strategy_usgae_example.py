import asyncio

from lionagi.operations.session import Branch, Session
from lionagi.operations.strategies.controller import ExecutionController
from lionagi.operations.strategies.types import StrategyParams
from lionagi.protocols.operatives.tasks import Task


async def main():
    # Create an operative that has `instruct_models` as a list of tasks
    operative = type("Operative", (), {})()
    operative.instruct_models = [
        Task(ln_id="task-1", payload={"data": "First"}),
        Task(ln_id="task-2", payload={"data": "Second"}),
    ]

    # Create a session and branch
    session = Session()
    branch = Branch()

    # Initialize controller
    controller = ExecutionController()

    # Execute
    result = await controller.execute_with_strategy(
        operative=operative,
        session=session,
        branch=branch,
        strategy_params=StrategyParams(concurrency_limit=2, chunk_size=1),
    )

    print("Execution Result:", result)
    print("Final Metrics:", controller.get_metrics())


if __name__ == "__main__":
    asyncio.run(main())
