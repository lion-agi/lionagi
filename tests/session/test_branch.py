import pandas as pd
import pytest
from pydantic import BaseModel

from lionagi.operatives.action.request_response_model import (
    ActionResponseModel,
)
from lionagi.operatives.types import Instruct, Operative
from lionagi.protocols.types import (
    ActionRequest,
    AssistantResponse,
    Instruction,
    LogManagerConfig,
    MessageRole,
    PackageCategory,
    RoledMessage,
)
from lionagi.service.manager import iModel
from lionagi.session.branch import Branch


@pytest.fixture
def branch_with_mock_imodel() -> Branch:
    """
    Creates a strongly-typed Branch with a mock chat_model & parse_model
    whose .invoke(...) always returns a MagicMock with .response = 'mocked_response'.
    """
    # 1) Create the Branch with minimal needed arguments
    branch = Branch(
        user="user",
        name="TestBranch",
        log_config=LogManagerConfig(),
    )

    # 2) Create a MagicMock simulating iModel
    mock_model = iModel(
        provider="groq",
        model="llama-3.3-70b-versatile",
    )

    async def invoke(*args, **kwargs):
        a = mock_model.create_api_calling()
        a.response = """{"foo": "mocked_response", "bar": 123}"""
        return a

    mock_model.invoke = invoke

    # 3) Inject it into the branch's iModelManager
    branch.mdls.register_imodel("chat", mock_model)
    branch.mdls.register_imodel("parse", mock_model)

    return branch


def test_branch_init_basic():
    """
    Ensures Branch can be created with typed user, name,
    and internal managers default to an empty state.
    """
    branch = Branch(user="tester", name="MyBranch")
    assert branch.user == "tester"
    assert branch.name == "MyBranch"
    assert branch.msgs is not None
    assert branch.acts is not None
    assert branch.mdls is not None
    assert branch.logs is not None
    assert branch.mailbox is not None


def test_branch_init_system_message():
    """
    If we pass system=some_string,
    a system message is automatically added to the message manager.
    """
    branch = Branch(system="System online!")
    assert branch.system is not None
    assert "System online!" in branch.system.rendered
    assert len(branch.messages) == 1
    assert branch.messages[0].role == MessageRole.SYSTEM


@pytest.mark.asyncio
async def test_invoke_chat_basic(branch_with_mock_imodel: Branch):
    """
    Checks that the mock iModel returns 'mocked_response' with no errors
    and doesn't automatically store any messages.
    """
    ins, res = await branch_with_mock_imodel.chat(
        instruction="Hello model!", return_ins_res_message=True
    )
    assert isinstance(ins, Instruction)
    assert isinstance(res, AssistantResponse)
    assert res.response == """{"foo": "mocked_response", "bar": 123}"""
    # By default, we don't store these messages
    assert len(branch_with_mock_imodel.messages) == 0


@pytest.mark.asyncio
async def test_communicate_no_validation(branch_with_mock_imodel: Branch):
    """
    If skip_validation=True, returns raw 'mocked_response' from the model
    and DOES store user+assistant messages in Branch.messages.
    """
    result = await branch_with_mock_imodel.communicate(
        instruction="Hello from user", skip_validation=True
    )
    assert result == """{"foo": "mocked_response", "bar": 123}"""
    # Now we should have user + assistant messages
    assert len(branch_with_mock_imodel.messages) == 2
    assert branch_with_mock_imodel.messages[0].role == MessageRole.USER
    assert branch_with_mock_imodel.messages[1].role == MessageRole.ASSISTANT


@pytest.mark.asyncio
async def test_communicate_with_request_model(branch_with_mock_imodel: Branch):
    """
    If request_model is provided,
    branch tries to parse the final response => we can mock `branch.parse` to simulate success.
    """

    class MyModel(BaseModel):
        foo: str = "bar"

    result = await branch_with_mock_imodel.communicate(
        instruction="We want typed output",
        request_model=MyModel,
    )
    assert result.foo == "mocked_response"
    # user + assistant stored
    msgs = branch_with_mock_imodel.messages
    assert len(msgs) == 2
    assert msgs[0].role == MessageRole.USER
    assert msgs[1].role == MessageRole.ASSISTANT


@pytest.mark.asyncio
async def test_operate_basic_flow_no_actions(branch_with_mock_imodel: Branch):
    """
    With invoke_actions=False and skip_validation=True =>
    operate returns the raw 'mocked_response'
    and stores user+assistant messages.
    """
    final = await branch_with_mock_imodel.operate(
        instruction="No tools needed",
        invoke_actions=False,
        skip_validation=True,
    )
    assert final == """{"foo": "mocked_response", "bar": 123}"""
    # user + assistant stored
    assert len(branch_with_mock_imodel.messages) == 2


@pytest.mark.asyncio
async def test_operate_with_validation(branch_with_mock_imodel: Branch):
    """
    If skip_validation=False, we call parse(...) to produce a typed result.
    We'll override parse with a stub.
    """

    class SomeResp(BaseModel):
        bar: int = 123

    final = await branch_with_mock_imodel.operate(
        instruction="Get typed result",
        invoke_actions=False,
        response_format=SomeResp,
    )
    assert final.bar == 123
    # user + assistant stored
    msgs = branch_with_mock_imodel.messages
    assert len(msgs) == 2


@pytest.mark.asyncio
async def test_operate_return_operative(branch_with_mock_imodel: Branch):
    """
    If return_operative=True, we get the entire Operative instead of the final model/string.
    """
    final = await branch_with_mock_imodel.operate(
        instruction="Testing return_operative",
        invoke_actions=False,
        skip_validation=True,
        return_operative=True,
    )
    assert isinstance(final, Operative)
    # user + assistant stored
    assert len(branch_with_mock_imodel.messages) == 2


@pytest.mark.asyncio
async def test_parse_exceeds_retries_returns_value(
    branch_with_mock_imodel: Branch,
):
    """
    If parse never yields a BaseModel within max_retries, handle_validation='return_value' => we return 'mocked_response'.
    """
    from pydantic import BaseModel

    class BasicModel(BaseModel):
        bar: int
        foo: str

    # .invoke is already mocked => always "mocked_response" => won't parse => returns that string
    val = await branch_with_mock_imodel.parse(
        text="""{"foo": "mocked_response", "bar": 123}""",
        request_type=BasicModel,
        max_retries=2,
        handle_validation="return_value",
    )
    assert val == BasicModel(bar=123, foo="mocked_response")


@pytest.mark.asyncio
async def test_invoke_action_no_tools(branch_with_mock_imodel: Branch):
    """
    If we pass an ActionRequest referencing an unregistered tool,
    we expect None + a Log error about 'not registered'.
    """
    req = ActionRequest.create(
        function="unregistered_tool", arguments={"x": 1}
    )
    resp = await branch_with_mock_imodel.act(req)
    assert resp == []
    # logs => check the last entry for 'not registered'
    assert len(branch_with_mock_imodel.logs) == 1
    assert "not registered" in (
        branch_with_mock_imodel.logs[-1].content["error"] or ""
    )


@pytest.mark.asyncio
async def test_invoke_action_ok(branch_with_mock_imodel: Branch):
    """
    Register a valid tool => call invoke_action => expect ActionResponseModel with correct output.
    """

    def echo_tool(text: str) -> str:
        return f"ECHO: {text}"

    # register the tool
    branch_with_mock_imodel.acts.register_tool(echo_tool)

    req = ActionRequest.create(
        function="echo_tool", arguments={"text": "hello"}
    )
    resp = await branch_with_mock_imodel.act(req)
    # Should get ActionResponseModel with output = "ECHO: hello"
    assert resp is not None
    assert resp[0].output == "ECHO: hello"
    # 2 messages => action_request + action_output
    assert len(branch_with_mock_imodel.messages) == 2
    assert branch_with_mock_imodel.messages[1].output == "ECHO: hello"


@pytest.mark.asyncio
async def test_invoke_action_suppress_errors(branch_with_mock_imodel: Branch):
    """
    If the tool raises an error but suppress_errors=True => we log it => return None.
    """

    def fail_tool(**kwargs):
        raise RuntimeError("Tool error")

    branch_with_mock_imodel.acts.register_tool(fail_tool)
    req = ActionRequest.create(function="fail_tool", arguments={})

    result = await branch_with_mock_imodel.act(req, suppress_errors=True)
    assert result == [
        ActionResponseModel(function="fail_tool", arguments={}, output=None)
    ]
    logs = branch_with_mock_imodel.logs
    assert len(logs) == 1
    assert logs[-1].content["execution"]["response"] is None


def test_clone_with_id_sender(branch_with_mock_imodel: Branch):
    """
    If clone requires an ID for 'sender', pass an actual ID.
    All messages in the clone have new 'sender' and the clone's id as 'recipient'.
    """
    from lionagi.protocols.types import ID

    # add a roled message
    msg = RoledMessage(
        role=MessageRole.USER,
        content={"text": "Hello original"},
        sender=branch_with_mock_imodel.user,
        recipient=branch_with_mock_imodel.id,
    )
    branch_with_mock_imodel.messages.include(msg)

    cloned = branch_with_mock_imodel.clone(sender=msg.id)
    # cloned => has the same messages
    assert len(cloned.messages) == 1
    cm = cloned.messages[0]
    assert cm.sender == msg.id
    assert cm.recipient == cloned.id


@pytest.mark.asyncio
async def test_aclone(branch_with_mock_imodel: Branch):
    """
    aclone(...) => same as clone, but async context lock on messages.
    """
    from lionagi.protocols.types import ID

    msg = RoledMessage(
        role=MessageRole.USER,
        content={"text": "Async test"},
        sender=branch_with_mock_imodel.user,
        recipient=branch_with_mock_imodel.id,
    )
    branch_with_mock_imodel.messages.include(msg)

    cloned = await branch_with_mock_imodel.aclone()
    assert len(cloned.messages) == 1
    cmsg = cloned.messages[0]
    assert cmsg.recipient == cloned.id


def test_send_and_receive_sync(branch_with_mock_imodel: Branch):
    """
    send(...) => place in out_queue. We simulate transferring to a target's mailbox => target calls receive(...).
    """
    target_branch = Branch(user="target", name="ReceiverBranch")

    msg = Instruction(
        role=MessageRole.USER,
        content={"text": "Message from outside"},
        sender=branch_with_mock_imodel.user,
        recipient=branch_with_mock_imodel.id,
    )

    branch_with_mock_imodel.send(
        recipient=target_branch.id,
        category=PackageCategory.MESSAGE,
        item=msg,
    )
    # Mail in out_queue
    assert len(branch_with_mock_imodel.mailbox.pending_outs) == 1
    mail_id = branch_with_mock_imodel.mailbox.pending_outs[0]
    mail_obj = branch_with_mock_imodel.mailbox.pile_[mail_id]

    # Transfer mail to target mailbox
    target_branch.mailbox.pile_[mail_id] = mail_obj
    target_branch.mailbox.append_in(mail_obj)

    # Now target receives
    target_branch.receive(sender=branch_with_mock_imodel, message=True)
    assert len(target_branch.messages) == 1
    rm = target_branch.messages[0]
    assert rm.content["text"] == "Message from outside"
    assert rm.sender == branch_with_mock_imodel.id


def test_to_dict_from_dict(branch_with_mock_imodel: Branch):
    """
    Round-trip with to_dict, from_dict => confirm logs, messages, models are restored.
    """
    msg = RoledMessage(
        role=MessageRole.USER,
        content={"text": "hello user"},
        sender=branch_with_mock_imodel.user,
        recipient=branch_with_mock_imodel.id,
    )
    branch_with_mock_imodel.messages.include(msg)

    d = branch_with_mock_imodel.to_dict()
    assert "messages" in d
    assert "logs" in d
    assert "chat_model" in d
    assert "parse_model" in d

    new_branch = Branch.from_dict(d)
    assert len(new_branch.messages) == 1
    nm = new_branch.messages[0]
    assert nm.content["text"] == "hello user"


def test_branch_to_df(branch_with_mock_imodel: Branch):
    """
    Add a couple messages, ensure to_df() yields a Pandas DataFrame with expected columns/rows.
    """
    msg1 = RoledMessage(
        role=MessageRole.USER,
        content={"text": "User says hi"},
        sender=branch_with_mock_imodel.user,
        recipient=branch_with_mock_imodel.id,
    )
    msg2 = RoledMessage(
        role=MessageRole.ASSISTANT,
        content={"text": "Assistant replies"},
        sender=branch_with_mock_imodel.id,
        recipient=branch_with_mock_imodel.user,
    )
    branch_with_mock_imodel.messages.include(msg1)
    branch_with_mock_imodel.messages.include(msg2)

    df = branch_with_mock_imodel.to_df()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    for col in ["role", "content", "sender", "recipient"]:
        assert col in df.columns


@pytest.mark.asyncio
async def test_instruct_calls_communicate_when_no_actions(
    branch_with_mock_imodel: Branch,
):
    """
    If Instruct has no 'actions', _instruct => communicate => returns 'mocked_response' by default.
    """
    instruct = Instruct(instruction="No actions needed")
    await branch_with_mock_imodel.instruct(instruct)
    # user + assistant in messages
    assert len(branch_with_mock_imodel.messages) == 2


@pytest.mark.asyncio
async def test_instruct_calls_operate_when_actions_true(
    branch_with_mock_imodel: Branch,
):
    """
    If instruct.actions=True, instruct => operate => returns 'mocked_response' unless skip_validation or parse is customized.
    """
    instruct = Instruct(instruction="Need actions", actions=True)
    result = await branch_with_mock_imodel.instruct(
        instruct, skip_validation=True
    )
    assert result == """{"foo": "mocked_response", "bar": 123}"""
    assert len(branch_with_mock_imodel.messages) == 2
