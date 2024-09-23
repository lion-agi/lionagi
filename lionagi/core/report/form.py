from lionagi.libs import lionfuncs as ln
from lion_core.form.form import Form as CoreForm


class Form(CoreForm):

    def display(self, fields=None):
        """
        Displays the form fields using IPython display.

        Args:
            fields (optional): Specific fields to display. Defaults to None.
        """
        from IPython.display import display, Markdown

        fields = fields or self.work_fields

        if "answer" in fields:
            answer = fields.pop("answer")
            fields["answer"] = answer

        for k, v in fields.items():
            if isinstance(v, dict):
                v = ln.to_str(v, indent=2)
            if len(str(v)) > 50:
                display(Markdown(f"**{k}**: \n {v}"))
            else:
                display(Markdown(f"**{k}**: {v}"))
