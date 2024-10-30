import contextlib
from abc import abstractmethod
from typing import Any, Dict, List

from lionagi.core.collections.abc import Component, Field

from ..collections.util import to_list_type


class BaseForm(Component):
    """
    NOTICE:
        The Form/Report system is inspired by DSPy. (especially in DSPy's usage
        of `Signature` and `Module`)
        https://github.com/stanfordnlp/dspy

        MIT License
        Copyright (c) 2023 Stanford Future Data Systems

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

    REFERENCES:
        @article{khattab2023dspy,
        title={DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines},
        author={Khattab, Omar and Singhvi, Arnav and Maheshwari, Paridhi and Zhang, Zhiyuan and
        Santhanam, Keshav and Vardhamanan, Sri and Haq, Saiful and Sharma, Ashutosh and Joshi,
        Thomas T. and Moazam, Hanna and Miller, Heather and Zaharia, Matei and Potts, Christopher},
        journal={arXiv preprint arXiv:2310.03714},
        year={2023}
        }
        @article{khattab2022demonstrate,
        title={Demonstrate-Search-Predict: Composing Retrieval and Language Models for
        Knowledge-Intensive {NLP}},
        author={Khattab, Omar and Santhanam, Keshav and Li, Xiang Lisa and Hall, David and Liang,
        Percy and Potts, Christopher and Zaharia, Matei},
        journal={arXiv preprint arXiv:2212.14024},
        year={2022}
        }

    LionAGI Modifications:
        - Redesigned focusing on form-based task handling
        - fully integrated with LionAGI's existing collections and components
        - developed report system for multi-step task handling
        - created work system for task execution and management

    Base class for handling form-like structures within an application.
    Manages form components and operations such as filling forms and
    checking their state (filled, workable).

    Attributes:
        assignment (str): The objective of the form specifying input/output fields.
        input_fields (List[str]): Fields required to carry out the objective of the form.
        requested_fields (List[str]): Fields requested to be filled by the user.
        task (Any): The work to be done by the form, including custom instructions.
        validation_kwargs (Dict[str, Dict[str, Any]]): Additional validation constraints for the form fields.
    """

    template_name: str = "default_directive"

    assignment: str | None = Field(
        None,
        description="The objective of the form specifying input/output fields.",
        examples=["input1, input2 -> output"],
    )

    input_fields: list[str] = Field(
        default_factory=list,
        description="Fields required to carry out the objective of the form.",
    )

    requested_fields: list[str] = Field(
        default_factory=list,
        description="Fields requested to be filled by the user.",
    )

    task: Any = Field(
        default_factory=str,
        description="The work to be done by the form, including custom instructions.",
    )

    validation_kwargs: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional validation constraints for the form fields.",
        examples=[{"field": {"config1": "a", "config2": "b"}}],
    )

    @property
    def work_fields(self) -> dict[str, Any]:
        """
        Get the fields relevant to the current task, including input and
        requested fields. Must be implemented by subclasses.

        Returns:
            Dict[str, Any]: The fields relevant to the current task.
        """
        raise NotImplementedError

    @abstractmethod
    def fill(self, *args, **kwargs):
        """
        Fill the form from various sources, including other forms and
        additional fields. Implement this method in subclasses.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        pass

    @abstractmethod
    def is_workable(self) -> bool:
        """
        Check if the form object is ready for work execution. Raise an error
        if the form is not workable. Use with the workable property.

        Returns:
            bool: True if the form is workable, otherwise False.
        """
        pass

    @property
    def filled(self) -> bool:
        """
        Check if the form is filled with all required fields. Uses the
        _is_filled method and suppresses any ValueError raised by it.

        Returns:
            bool: True if the form is filled, otherwise False.
        """
        with contextlib.suppress(ValueError):
            return self._is_filled()
        return False

    @property
    def workable(self) -> bool:
        """
        Check if the form is workable. This property does not raise an error
        and will return True or False.

        Returns:
            bool: True if the form is workable, otherwise False.
        """
        with contextlib.suppress(ValueError):
            return self.is_workable()
        return False

    def _is_filled(self) -> bool:
        """
        Private method to check if all work fields are filled. Raises a
        ValueError if any field is not filled.

        Returns:
            bool: True if all work fields are filled, otherwise raises ValueError.

        Raises:
            ValueError: If any field is not filled.
        """
        for k, value in self.work_fields.items():
            if value is None:
                raise ValueError(f"Field {k} is not filled")
        return True

    def _get_all_fields(
        self, form: list["BaseForm"] = None, **kwargs
    ) -> dict[str, Any]:
        """
        Given a form or collections of forms, and additional fields, gather
        all fields together including self fields with valid value.

        Args:
            form (List[BaseForm], optional): A list of forms to gather fields from.
            **kwargs: Additional fields to include.

        Returns:
            Dict[str, Any]: A dictionary of all gathered fields.
        """
        form: list["BaseForm"] = to_list_type(form) if form else []
        all_fields = self.work_fields.copy()
        all_form_fields = (
            {}
            if not form
            else {
                k: v
                for i in form
                for k, v in i.work_fields.items()
                if v is not None
            }
        )
        all_fields.update({**all_form_fields, **kwargs})
        return all_fields

    def copy(self):
        return self.model_copy()
