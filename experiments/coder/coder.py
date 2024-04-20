from .autogen import get_autogen_coder


class Coder:

    @staticmethod
    def autogen(**kwargs):
        return get_autogen_coder(**kwargs)
