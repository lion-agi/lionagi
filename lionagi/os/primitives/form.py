from lion_core.form.form import Form as CoreForm
from lionagi import lionfuncs as ln


class Form(CoreForm):

    def display(self, fields=None):
        """
        Displays the form fields using IPython display.

        Args:
            fields (optional): Specific fields to display. Defaults to None.
        """
        from IPython.display import display, Markdown

        fields = self.display_dict

        if "answer" in fields:
            answer = fields.pop("answer")
            fields["answer"] = answer

        for k, v in fields.items():
            if isinstance(v, dict):
                v = ln.as_readable_json(v)
            if len(str(v)) > 50:
                display(Markdown(f"**{k}**: \n {v}"))
            else:
                display(Markdown(f"**{k}**: {v}"))


__all__ = ["Form"]
