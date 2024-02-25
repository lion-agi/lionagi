class LangchainBridge:

    @staticmethod
    def to_langchain_document(*args, **kwargs):
        from .documents import to_langchain_document

        return to_langchain_document(*args, **kwargs)

    @staticmethod
    def langchain_loader(*args, **kwargs):
        from .documents import langchain_loader

        return langchain_loader(*args, **kwargs)

    @staticmethod
    def langchain_text_splitter(*args, **kwargs):
        from .documents import langchain_text_splitter

        return langchain_text_splitter(*args, **kwargs)
