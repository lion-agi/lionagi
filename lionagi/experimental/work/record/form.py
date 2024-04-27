from abc import ABC, abstractmethod
from lionagi.core.generic.component import BaseComponent
from ._util import get_input_output_fields, system_fields


class Record(BaseComponent, ABC):
    """
    Abstract base class for records in the system, defining a template for records
    that hold input and output fields based on their assignment.

    Attributes:
        assignment (Optional[str]): The specific task or role of the record.
        input_fields (List[str]): Fields expected to be provided as input.
        output_fields (List[str]): Fields expected to be output after processing.
    """

    assignment: str | None = None
    input_fields: list[str] = []
    output_fields: list[str] = []

    @abstractmethod
    def fill(self, *args, **kwargs):
        """
        Abstract method to be implemented by subclasses to fill record fields.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        pass
    
    
class Form(Record):
    """
    Concrete implementation of a Record, representing a form that can be filled with
    data. Forms handle validation to ensure they are correctly filled before processing.

    Methods:
        fill(form, **kwargs): Fills the form with provided data.
        check_workable(): Validates the form's readiness based on filled data.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new form, setting up input and output fields based on the assignment,
        and initializing all fields to None.

        Args:
            **kwargs: Arbitrary keyword arguments passed to the base class initializer.
        """
        super().__init__(**kwargs)
        if not self.assignment:
            self.input_fields, self.output_fields = [], []
        else:
            self.input_fields, self.output_fields = get_input_output_fields(
                self.assignment
            )
        for i in self.input_fields + self.output_fields:
            if i not in self._all_fields:
                self._add_field(i, value=None)


    def check_workable(self):
        """
        Checks if all required input fields are filled, raising an error if any are missing.

        Raises:
            ValueError: If the form is already filled or if input fields are missing.

        Returns:
            bool: True if the form is workable.
        """
        if self.filled:
            raise ValueError(f"Form {self.id_} is already filled")

        if len(
            non_fields := [
                i for i in self.input_fields if getattr(self, i, None) is None
            ]
        ) > 0:
            raise ValueError(f"Form {self.id_} is missing input fields: {non_fields}")

        return True

    def fill(self, form: "Form" = None, **kwargs):
        """
        Fills the form with data provided either directly or from another form.

        Args:
            form (Form, optional): Another form to take data from.
            **kwargs: Field values to fill into the form.

        Raises:
            ValueError: If the form is already filled or if invalid fields are provided.
        """
        if self.filled:
            raise ValueError(f"Form {self.id_} is already filled")

        fields = form.work_fields if form else {}
        kwargs = {**fields, **kwargs}

        for k, v in kwargs.items():
            if k not in self.work_fields:
                raise ValueError(
                    f"Form {self.id_}: Field {k} is not a valid work field"
                )
            setattr(self, k, v)

    @property
    def workable(self) -> bool:
        """
        Property to check if the form is workable without raising exceptions.

        Returns:
            bool: True if the form is workable, otherwise False.
        """
        try:
            self.check_workable()
            return True
        except Exception:
            return False

    @property
    def work_fields(self) -> dict:
        """
        Retrieves the work-related fields that are not part of the system fields.

        Returns:
            dict: Dictionary of work-related fields.
        """
        dict_ = self.to_dict()
        return {
            k: v for k, v in dict_.items()
            if k not in system_fields and k in self.input_fields + self.output_fields
        }

    @property
    def filled(self) -> bool:
        """
        Checks if all fields in the form are filled.

        Returns:
            bool: True if all work-related fields have values other than None.
        """
        return all([value is not None for _, value in self.work_fields.items()])
