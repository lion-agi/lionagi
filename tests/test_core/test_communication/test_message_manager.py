import pytest
from pydantic import BaseModel

from lionagi.core.communication.message import MessageRole
from lionagi.core.communication.types import (
    ActionRequest,
    ActionResponse,
    AssistantResponse,
    Instruction,
    MessageManager,
    System,
)
from lionagi.core.generic.types import Pile


class RequestModel(BaseModel):
    """Model for testing request fields"""

    name: str
    age: int


@pytest.fixture
def message_manager():
    """Fixture providing a clean MessageManager instance"""
    return MessageManager()


def test_message_manager_initialization():
    """Test basic initialization of MessageManager"""
    manager = MessageManager()
    assert isinstance(manager.messages, Pile)
    assert not manager.messages
    assert manager.save_on_clear


def test_message_manager_with_system():
    """Test MessageManager with system message"""
    system = System(system="Test system")
    manager = MessageManager(system=system)

    assert manager.system == system
    assert system in manager.messages
    assert len(manager.messages) == 1


def test_set_system():
    """Test setting system message"""
    manager = MessageManager()
    system1 = System(system="System 1")
    system2 = System(system="System 2")

    manager.set_system(system1)
    assert manager.system == system1

    manager.set_system(system2)
    assert manager.system == system2
    assert system1 not in manager.messages
    assert system2 in manager.messages


def test_create_instruction():
    """Test creating instruction messages"""
    instruction = MessageManager.create_instruction(
        instruction="Test instruction",
        context={"test": "context"},
        guidance="Test guidance",
        sender="user",
        recipient="assistant",
    )

    assert isinstance(instruction, Instruction)
    assert instruction.instruction == "Test instruction"
    assert instruction.guidance == "Test guidance"
    assert instruction.sender == "user"
    assert instruction.recipient == "assistant"


def test_create_assistant_response():
    """Test creating assistant response messages"""
    response = MessageManager.create_assistant_response(
        assistant_response="Test response",
        sender="assistant",
        recipient="user",
    )

    assert isinstance(response, AssistantResponse)
    assert response.response == "Test response"
    assert response.sender == "assistant"
    assert response.recipient == "user"


def test_create_action_request():
    """Test creating action request messages"""
    request = MessageManager.create_action_request(
        function="test_function",
        arguments={"arg": "value"},
        sender="user",
        recipient="system",
    )

    assert isinstance(request, ActionRequest)
    assert request.function == "test_function"
    assert request.arguments == {"arg": "value"}
    assert request.sender == "user"
    assert request.recipient == "system"


def test_create_action_response():
    """Test creating action response messages"""
    request = ActionRequest(
        function="test", arguments={}, sender="user", recipient="system"
    )
    response = MessageManager.create_action_response(
        action_request=request, action_response={"result": "success"}
    )

    assert isinstance(response, ActionResponse)
    assert response.output == {"result": "success"}
    assert request.is_responded


def test_add_message(message_manager):
    """Test adding different types of messages"""
    # Add instruction
    instruction = message_manager.add_message(
        instruction="Test instruction", sender="user", recipient="assistant"
    )
    assert isinstance(instruction, Instruction)
    assert instruction in message_manager.messages

    # Add assistant response
    response = message_manager.add_message(
        assistant_response="Test response",
        sender="assistant",
        recipient="user",
    )
    assert isinstance(response, AssistantResponse)
    assert response in message_manager.messages

    # Add action request
    request = message_manager.add_message(
        function="test_function",
        arguments={},
        sender="user",
        recipient="system",
        action_request=ActionRequest(
            function="test_function",
            arguments={},
            sender="user",
            recipient="system",
        ),
    )
    assert isinstance(request, ActionRequest)
    assert request in message_manager.messages


def test_clear_messages(message_manager):
    """Test clearing messages"""
    message_manager.add_message(
        instruction="Test", sender="user", recipient="assistant"
    )
    message_manager.add_message(
        assistant_response="Response", sender="assistant", recipient="user"
    )

    assert len(message_manager.messages) == 2
    message_manager.clear_messages()
    assert len(message_manager.messages) == 0


async def test_async_operations(message_manager):
    """Test async operations"""
    await message_manager.a_add_message(
        instruction="Test", sender="user", recipient="assistant"
    )
    assert len(message_manager.messages) == 1

    await message_manager.aclear_messages()
    assert len(message_manager.messages) == 0


def test_message_collections(message_manager):
    """Test message collection properties"""
    # Add various message types
    instruction = message_manager.add_message(
        instruction="Test instruction", sender="user", recipient="assistant"
    )
    response = message_manager.add_message(
        assistant_response="Test response",
        sender="assistant",
        recipient="user",
    )
    request = message_manager.add_message(
        function="test_function",
        arguments={},
        sender="user",
        recipient="system",
        action_request=ActionRequest(
            function="test_function",
            arguments={},
            sender="user",
            recipient="system",
        ),
    )

    # Test collections
    assert instruction in message_manager.instructions
    assert response in message_manager.assistant_responses
    assert isinstance(request, ActionRequest)
    assert request in message_manager.action_requests

    # Test last message getters
    assert message_manager.last_instruction == instruction
    assert message_manager.last_response == response


def test_to_chat_msgs(message_manager):
    """Test conversion to chat messages"""
    message_manager.add_message(
        instruction="Test instruction", sender="user", recipient="assistant"
    )
    message_manager.add_message(
        assistant_response="Test response",
        sender="assistant",
        recipient="user",
    )

    chat_msgs = message_manager.to_chat_msgs()
    assert len(chat_msgs) == 2
    assert all(isinstance(msg, dict) for msg in chat_msgs)
    assert all("role" in msg and "content" in msg for msg in chat_msgs)


def test_message_manager_with_request_model(message_manager):
    """Test message manager with request model"""
    instruction = message_manager.add_message(
        instruction="Test",
        request_model=RequestModel,
        sender="user",
        recipient="assistant",
    )

    assert instruction.request_model == RequestModel
    assert "name" in instruction.request_fields
    assert "age" in instruction.request_fields


def test_message_manager_bool_and_logs(message_manager):
    """Test boolean operations and log checking"""
    assert not bool(message_manager)  # Empty manager
    assert not message_manager.has_logs()

    message_manager.add_message(
        instruction="Test", sender="user", recipient="assistant"
    )
    assert bool(message_manager)  # Non-empty manager
    assert message_manager.has_logs()


def test_invalid_message_combinations(message_manager):
    """Test invalid message combinations"""
    with pytest.raises(ValueError):
        message_manager.add_message(
            instruction="Test",
            assistant_response="Response",  # Can't add both types at once
            sender="user",
            recipient="assistant",
        )


def test_message_manager_progress(message_manager):
    """Test message progression tracking"""
    msg1 = message_manager.add_message(
        instruction="First", sender="user", recipient="assistant"
    )
    msg2 = message_manager.add_message(
        assistant_response="Second", sender="assistant", recipient="user"
    )

    progress = message_manager.progress
    assert list(progress) == [msg1.ln_id, msg2.ln_id]


def test_message_manager_metadata(message_manager):
    """Test message metadata handling"""
    metadata = {"key": "value"}
    msg = message_manager.add_message(
        instruction="Test",
        metadata=metadata,
        sender="user",
        recipient="assistant",
    )

    assert msg.metadata["extra"] == metadata
