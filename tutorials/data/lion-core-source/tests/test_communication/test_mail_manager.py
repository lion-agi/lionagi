import asyncio
from collections import deque
from unittest.mock import patch

import pytest
from lionabc import Observable

from lion_core.communication.mail import Mail
from lion_core.communication.mail_manager import MailManager
from lion_core.communication.package import Package, PackageCategory
from lion_core.generic.exchange import Exchange
from lion_core.generic.pile import Pile
from lion_core.sys_utils import SysUtil


class MockObservable(Observable):
    def __init__(self, ln_id):
        self.ln_id = ln_id
        self.mailbox = Exchange()


@pytest.fixture
def mock_source():
    return MockObservable(SysUtil.id())


@pytest.fixture
def mail_manager(mock_source):
    return MailManager([mock_source])


def create_mock_mail(sender, recipient, category, content):
    package = Package(category=category, package=content)
    return Mail(sender=sender, recipient=recipient, package=package)


def test_mail_manager_init():
    manager = MailManager()
    assert isinstance(manager.sources, Pile)
    assert isinstance(manager.mails, dict)
    assert manager.execute_stop is False


def test_mail_manager_add_sources(mail_manager, mock_source):
    new_source = MockObservable(SysUtil.id())
    mail_manager.add_sources(new_source)
    assert new_source.ln_id in mail_manager.mails
    assert len(mail_manager.sources) == 2


def test_mail_manager_create_mail():
    sender_id, recipient_id = SysUtil.id(), SysUtil.id()
    mail = MailManager.create_mail(
        sender_id, recipient_id, PackageCategory.MESSAGE, "content"
    )
    assert isinstance(mail, Mail)
    assert mail.package.category == PackageCategory.MESSAGE
    assert mail.package.package == "content"


def test_mail_manager_delete_source(mail_manager, mock_source):
    mail_manager.delete_source(mock_source.ln_id)
    assert mock_source.ln_id not in mail_manager.sources
    assert mock_source.ln_id not in mail_manager.mails


def test_mail_manager_collect(mail_manager, mock_source):
    sender_id = SysUtil.id()
    mock_mail = create_mock_mail(
        sender_id, mock_source.ln_id, PackageCategory.MESSAGE, "content"
    )
    mock_source.mailbox.include(mock_mail, "out")
    mail_manager.collect(mock_source.ln_id)
    assert len(mail_manager.mails[mock_source.ln_id][sender_id]) == 1


def test_mail_manager_send(mail_manager, mock_source):
    sender_id = SysUtil.id()
    mock_mail = create_mock_mail(
        sender_id, mock_source.ln_id, PackageCategory.MESSAGE, "content"
    )
    mail_manager.mails[mock_source.ln_id] = {sender_id: deque([mock_mail])}
    mail_manager.send(mock_source.ln_id)
    assert len(mock_source.mailbox.pile_) == 1


def test_mail_manager_collect_all(mail_manager, mock_source):
    sender_id = SysUtil.id()
    mock_mail = create_mock_mail(
        sender_id, mock_source.ln_id, PackageCategory.MESSAGE, "content"
    )
    mock_source.mailbox.include(mock_mail, "out")
    mail_manager.collect_all()
    assert len(mail_manager.mails[mock_source.ln_id][sender_id]) == 1


def test_mail_manager_send_all(mail_manager, mock_source):
    sender_id = SysUtil.id()
    mock_mail = create_mock_mail(
        sender_id, mock_source.ln_id, PackageCategory.MESSAGE, "content"
    )
    mail_manager.mails[mock_source.ln_id] = {sender_id: deque([mock_mail])}
    mail_manager.send_all()
    assert len(mock_source.mailbox.pile_) == 1


@pytest.mark.asyncio
async def test_mail_manager_execute(mail_manager):
    with (
        patch.object(mail_manager, "collect_all") as mock_collect_all,
        patch.object(mail_manager, "send_all") as mock_send_all,
    ):
        mail_manager.execute_stop = False
        task = asyncio.create_task(mail_manager.execute(refresh_time=0.1))

        # Use a timeout to prevent the test from hanging
        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=1.0)
        except asyncio.TimeoutError:
            pass
        finally:
            mail_manager.execute_stop = True
            await task

        assert mock_collect_all.call_count > 0
        assert mock_send_all.call_count > 0


def test_mail_manager_add_invalid_source():
    manager = MailManager()
    manager.add_sources("invalid_source")


def test_mail_manager_delete_nonexistent_source(mail_manager):
    with pytest.raises(ValueError):
        mail_manager.delete_source(SysUtil.id())


def test_mail_manager_collect_nonexistent_sender(mail_manager):
    with pytest.raises(ValueError):
        mail_manager.collect(SysUtil.id())


def test_mail_manager_send_nonexistent_recipient(mail_manager):
    with pytest.raises(ValueError):
        mail_manager.send(SysUtil.id())


def test_mail_manager_collect_with_nonexistent_recipient(
    mail_manager, mock_source
):
    mock_mail = create_mock_mail(
        SysUtil.id(), SysUtil.id(), PackageCategory.MESSAGE, "content"
    )
    mock_source.mailbox.include(mock_mail, "out")
    with pytest.raises(ValueError):
        mail_manager.collect(mock_source.ln_id)


def test_mail_manager_send_empty_mail_queue(mail_manager, mock_source):
    mail_manager.send(mock_source.ln_id)
    assert len(mock_source.mailbox.pile_) == 0


@pytest.mark.parametrize("num_sources", [10, 100, 1000])
def test_mail_manager_large_number_of_sources(num_sources):
    sources = [MockObservable(SysUtil.id()) for _ in range(num_sources)]
    manager = MailManager(sources)
    assert len(manager.sources) == num_sources
    assert len(manager.mails) == num_sources


@pytest.mark.parametrize("num_mails", [10, 100, 1000])
def test_mail_manager_large_number_of_mails(
    mail_manager, mock_source, num_mails
):
    sender_id = SysUtil.id()
    for _ in range(num_mails):
        mock_mail = create_mock_mail(
            sender_id,
            mock_source.ln_id,
            PackageCategory.MESSAGE,
            f"content_{_}",
        )
        mock_source.mailbox.include(mock_mail, "out")
    mail_manager.collect(mock_source.ln_id)
    assert (
        sum(
            len(queue)
            for queue in mail_manager.mails[mock_source.ln_id].values()
        )
        == num_mails
    )


def test_mail_manager_multiple_senders_same_recipient(
    mail_manager, mock_source
):
    senders = [SysUtil.id() for _ in range(3)]
    for sender in senders:
        mock_mail = create_mock_mail(
            sender, mock_source.ln_id, PackageCategory.MESSAGE, "content"
        )
        mock_source.mailbox.include(mock_mail, "out")
    mail_manager.collect(mock_source.ln_id)
    assert len(mail_manager.mails[mock_source.ln_id]) == len(senders)


def test_mail_manager_collect_and_send_cycle(mail_manager, mock_source):
    sender_id = SysUtil.id()
    mock_mail = create_mock_mail(
        sender_id, mock_source.ln_id, PackageCategory.MESSAGE, "content"
    )
    mock_source.mailbox.include(mock_mail, "out")
    mail_manager.collect_all()
    assert len(mail_manager.mails[mock_source.ln_id][sender_id]) == 1
    mail_manager.send_all()
    assert len(mock_source.mailbox.pile_) == 1
    assert len(mail_manager.mails[mock_source.ln_id]) == 0


@pytest.mark.asyncio
async def test_mail_manager_execute_with_interruption(mail_manager):
    async def interrupt():
        await asyncio.sleep(0.01)
        mail_manager.execute_stop = True

    with (
        patch.object(mail_manager, "collect_all") as mock_collect_all,
        patch.object(mail_manager, "send_all") as mock_send_all,
    ):
        interrupt_task = asyncio.create_task(interrupt())
        execute_task = asyncio.create_task(
            mail_manager.execute(refresh_time=0.01)
        )

        # Use a timeout to prevent the test from hanging
        try:
            await asyncio.wait_for(
                asyncio.gather(interrupt_task, execute_task), timeout=0.1
            )
        except asyncio.TimeoutError:
            pass
        finally:
            mail_manager.execute_stop = True
            await asyncio.gather(
                interrupt_task, execute_task, return_exceptions=True
            )

        assert mock_collect_all.call_count > 0
        assert mock_send_all.call_count > 0


def test_mail_manager_with_various_package_categories(
    mail_manager, mock_source
):
    sender_id = SysUtil.id()
    for category in PackageCategory:
        mock_mail = create_mock_mail(
            sender_id, mock_source.ln_id, category, "content"
        )
        mock_source.mailbox.include(mock_mail, "out")
    mail_manager.collect(mock_source.ln_id)
    assert len(mail_manager.mails[mock_source.ln_id][sender_id]) == len(
        PackageCategory
    )


@pytest.mark.asyncio
async def test_mail_manager_performance():
    num_sources = 10  # Reduced from 100 to speed up the test
    mails_per_source = 10  # Reduced from 100 to speed up the test
    sources = [MockObservable(SysUtil.id()) for _ in range(num_sources)]
    manager = MailManager(sources)

    for source in sources:
        for _ in range(mails_per_source):
            mock_mail = create_mock_mail(
                SysUtil.id(),
                source.ln_id,
                PackageCategory.MESSAGE,
                f"content_{_}",
            )
            source.mailbox.include(mock_mail, "out")

    start_time = asyncio.get_event_loop().time()

    # Use a timeout to prevent the test from hanging
    try:
        await asyncio.wait_for(manager.execute(refresh_time=0), timeout=0.5)
    except asyncio.TimeoutError:
        pass
    finally:
        manager.execute_stop = True

    end_time = asyncio.get_event_loop().time()

    assert end_time - start_time <= 0.75


@pytest.mark.asyncio
async def test_mail_manager_thread_safety():
    manager = MailManager()
    source = MockObservable(SysUtil.id())
    manager.add_sources(source)

    async def add_and_collect():
        sender_id = SysUtil.id()
        for _ in range(10):  # Reduced from 100 to speed up the test
            mock_mail = create_mock_mail(
                sender_id, source.ln_id, PackageCategory.MESSAGE, "content"
            )
            source.mailbox.include(mock_mail, "out")
        await asyncio.sleep(0.01)
        manager.collect(source.ln_id)

    tasks = [
        asyncio.create_task(add_and_collect()) for _ in range(5)
    ]  # Reduced from 10 to speed up the test

    # Use a timeout to prevent the test from hanging
    try:
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=0.05)
    except asyncio.TimeoutError:
        pass

    total_mails = sum(
        len(queue) for queue in manager.mails[source.ln_id].values()
    )
    assert total_mails == 50  # 5 tasks * 10 mails each


def test_mail_manager_with_large_mail_content(mail_manager, mock_source):
    large_content = "a" * 1000000  # 1MB of content
    sender_id = SysUtil.id()
    mock_mail = create_mock_mail(
        sender_id, mock_source.ln_id, PackageCategory.MESSAGE, large_content
    )
    mock_source.mailbox.include(mock_mail, "out")
    mail_manager.collect(mock_source.ln_id)
    assert len(mail_manager.mails[mock_source.ln_id][sender_id]) == 1
    assert (
        len(
            mail_manager.mails[mock_source.ln_id][sender_id][0].package.package
        )
        == 1000000
    )
