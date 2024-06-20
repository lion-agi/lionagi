from abc import ABC
from lionagi.os.lib import lcall
from ..abc import ModelLimitExceededError


class PileEmbeddingsMixin(ABC):

    async def embed_pile(
        self, imodel=None, field="content", embed_kwargs={}, verbose=True, **kwargs
    ):
        """
        Embed the items in the pile.

        Args:
            imodel: The embedding model to use.
            field (str): The field to embed. Default is "content".
            embed_kwargs (dict): Additional keyword arguments for the embedding.
            verbose (bool): Whether to print verbose messages. Default is True.
            **kwargs: Additional keyword arguments for the embedding.

        Raises:
            ModelLimitExceededError: If the model limit is exceeded.
        """
        from ....lionagi import iModel

        imodel = imodel or iModel(endpoint="embeddings", **kwargs)

        max_concurrent = kwargs.get("max_concurrent", None) or 100

        async def _embed_item(item):
            try:
                return await imodel.embed_node(item, field=field, **embed_kwargs)
            except ModelLimitExceededError:
                pass
            return None

        await lcall(
            _embed_item,
            list(self),
            retries=3,
            flatten=True,
            dropna=True,
            verbose=False,
            max_concurrent=max_concurrent,
        )

        a = len([i for i in self if "embedding" in i._all_fields])
        if len(self) > a and verbose:
            print(
                f"Successfully embedded {a}/{len(self)} items, Failed to embed {len(self) - a}/{len(self)} items"
            )
            return

        print(f"Successfully embedded all {a}/{a} items")
