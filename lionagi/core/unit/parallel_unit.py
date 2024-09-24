from typing import Type
from lion_core.abc import BaseProcessor
from lion_core.form.base import BaseForm

from lionagi.core.session.session import Session
from lionagi.core.unit.unit_form import UnitForm

from lionagi.core.unit.process_parallel_chat import process_parallel_chat
from lionagi.core.unit.process_parallel_direct import process_parallel_direct


class ParallelUnit(BaseProcessor):

    default_form: Type[BaseForm] = UnitForm

    def __init__(self, session: Session):
        self.session = session

    async def process_parallel_chat(self, **kwargs):
        return await process_parallel_chat(self.session, **kwargs)

    async def process_parallel_direct(self, **kwargs):
        return await process_parallel_direct(self.session, **kwargs)
