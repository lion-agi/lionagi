from lionagi.os.lib import CallDecorator as cd


class KnowledgeCatalog:
    """
    A class to represent a Knowledge Catalog to manage entity data.
    """

    @staticmethod
    @cd.cache(maxsize=10000)
    def get_data(candidate_entity):
        """
        Get data for a candidate entity from Wikipedia.

        Args:
            candidate_entity (str): The candidate entity title.

        Returns:
            dict: A dictionary containing information about the candidate entity (title, url, summary).
                  None if the entity does not exist in Wikipedia.
        """
        try:
            from lionagi.os.lib.sys_util import check_import

            check_import("wikipedia")
            import wikipedia
        except Exception as e:
            raise Exception(f"wikipedia package is not installed {e}")

        try:
            page = wikipedia.page(candidate_entity, auto_suggest=False)
            entity_data = {
                "title": page.title,
                "url": page.url,
                "summary": page.summary,
            }
            return entity_data
        except:
            return None
