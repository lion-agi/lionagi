from abc import ABC

from lionagi import iModel, pile, Branch, to_list

from lionagi.core.manual.guide import OperationGuide
from lionagi.core.manual.manual import OperationManual
from lionagi.core.expert.expert_form import ExpertForm
from lionagi.core.expert.utils import save_to_jsonl


class Expert(ABC):
    """Base class for Expert agents in the AutoOS system."""

    manual: OperationManual
    form_template: type[ExpertForm] = ExpertForm

    def __init__(
        self,
        verbose: bool = True,
        imodel: iModel | None = None,
        name: str = "ExpertOne",
        persist_path="/data/experts/",
    ):
        self.branches = pile()
        self.forms: dict[str, list[ExpertForm]] = {}
        self.verbose = verbose
        self.imodel = imodel
        self.name = name
        self.persist_path = persist_path

    async def work(
        self,
        operation: OperationGuide | None = None,
        name=None,
        assignment=None,
        thinking_style=None,
        instruction=None,
        guidance=None,
        context=None,
        branch: Branch | None = None,
        return_branch: bool = False,
        **kwargs,
    ) -> ExpertForm | tuple[ExpertForm, Branch]:

        if not operation and not assignment:
            raise ValueError("Either operation or assignment must be provided")

        form: ExpertForm = self.form_template(
            operation=operation,
            name=name,
            assignment=assignment,
            thinking_style=thinking_style,
            instruction=instruction,
            guidance=guidance,
            context=context,
            **kwargs,
        )
        if self.verbose:
            print(
                f"********** Working on: {form.operation_name or 'unnamed'} **********"
            )
        form, branch = await self.predict(form, branch=branch)
        form.metadata["branch_id"] = branch.ln_id

        self.forms.setdefault(form.assignment, []).append(form)
        if branch not in self.branches:
            self.branches.include(branch)
        if return_branch:
            return form, branch
        return form

    async def predict(
        self,
        form: ExpertForm,
        branch: Branch | None = None,
        imodel: iModel | None = None,
    ) -> tuple[ExpertForm, Branch]:
        """Interact with the AI model to process the form.

        Args:
            form: The form to process.
            branch: The AI conversation branch to use.
            imodel: The AI model instance to use.

        Returns:
            A tuple containing the processed form and branch.
        """
        if branch is None:
            branch = Branch(imodel=imodel or self.imodel)
        await branch.chat(form=form)
        form.chatted = True
        if self.verbose:
            print(
                "********** Successfully communicated with "
                f"AI model ({self.imodel.iModel_name}) **********"
            )
        return form, branch

    def save_messages(self, filename: str = "expert"):
        msgs = [j.to_dict() for i in self.branches for j in i.messages]
        msgs = to_list(msgs, flatten=True, dropna=True)
        save_to_jsonl(msgs, f"{self.persist_path+filename}_messages.jsonl")

    def save_forms(self, filename: str = "expert"):
        forms = [j.to_dict() for i in self.forms.values() for j in i]
        extension_forms = [
            j.to_dict() for i in forms for j in i.extension_forms if i.extension_forms
        ]
        msgs = to_list(forms + extension_forms, flatten=True, dropna=True)
        filename = filename or self.name
        filename.replace(" ", "_")
        save_to_jsonl(msgs, f"{self.persist_path+filename}_forms.jsonl")
