# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
from uuid import uuid4

import pytest

from lionagi._errors import TimeoutError
from lionagi.protocols.mail.mail import Mail
from lionagi.protocols.mail.mailbox import Mailbox
from lionagi.protocols.mail.package import Package, PackageCategory


@pytest.mark.asyncio
async def test_await_response_success():
    """Test successful response waiting"""
    mailbox = Mailbox()
    ask_id = str(uuid4())

    # Start waiting for response in background
    wait_task = asyncio.create_task(mailbox.await_response(ask_id, timeout=1))

    # Simulate response arriving
    response_mail = Mail(
        sender="test_sender",
        recipient="test_recipient",
        package=Package(
            category=PackageCategory.MESSAGE,
            item="test response",
            request_source=ask_id,
        ),
    )
    mailbox.append_in(response_mail)

    # Get response
    response = await wait_task
    assert response == "test response"

    # Check cleanup
    assert ask_id not in mailbox._response_events
    assert ask_id not in mailbox._responses


@pytest.mark.asyncio
async def test_await_response_timeout():
    """Test timeout handling"""
    mailbox = Mailbox()
    ask_id = str(uuid4())

    with pytest.raises(TimeoutError):
        await mailbox.await_response(ask_id, timeout=0.1)

    # Check cleanup
    assert ask_id not in mailbox._response_events
    assert ask_id not in mailbox._responses


@pytest.mark.asyncio
async def test_multiple_responses():
    """Test handling multiple concurrent responses"""
    mailbox = Mailbox()
    ask_ids = [str(uuid4()) for _ in range(3)]
    responses = ["response1", "response2", "response3"]

    # Start waiting for all responses
    wait_tasks = [
        asyncio.create_task(mailbox.await_response(ask_id, timeout=1))
        for ask_id in ask_ids
    ]

    # Send responses in reverse order
    for ask_id, response in zip(reversed(ask_ids), reversed(responses)):
        response_mail = Mail(
            sender="test_sender",
            recipient="test_recipient",
            package=Package(
                category=PackageCategory.MESSAGE,
                item=response,
                request_source=ask_id,
            ),
        )
        mailbox.append_in(response_mail)

    # Get all responses
    received = await asyncio.gather(*wait_tasks)
    assert received == responses

    # Check cleanup
    for ask_id in ask_ids:
        assert ask_id not in mailbox._response_events
        assert ask_id not in mailbox._responses
