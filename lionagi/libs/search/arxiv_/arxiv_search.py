# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0
#
# Portions derived from  https://github.com/ag2ai/ag2 are under the Apache-2.0 License.
# SPDX-License-Identifier: Apache-2.0


def arxiv_search(query, max_results=10, sortby="relevance"):
    """
    Search for articles on arXiv based on the given query.

    Args:
        query (str): The search query.
        max_results (int, optional): The maximum number of results to retrieve. Defaults to 10.
        sortby (str, optional): The sorting criterion for the search results. Can be 'relevance' or 'submittedDate'. Defaults to 'relevance'.

    Returns:
        list: A list of dictionaries containing information about the search results. Each dictionary contains the following keys:
            - 'title': The title of the article.
            - 'authors': The authors of the article.
            - 'summary': The summary of the article.
            - 'entry_id': The entry ID of the article.
            - 'doi': The DOI of the article (If applicable).
            - 'published': The publication date of the article in the format 'Y-M'.
    """

    from ...imports_utils import check_import

    arxiv = check_import("arxiv")

    def get_author(r):
        return ", ".join(a.name for a in r.authors)

    criterion = {
        "relevance": arxiv.SortCriterion.Relevance,
        "submittedDate": arxiv.SortCriterion.SubmittedDate,
    }[sortby]

    client = arxiv.Client()
    search = arxiv.Search(
        query=query, max_results=max_results, sort_by=criterion
    )
    res = []
    results = client.results(search)
    for r in results:
        print("Entry id:", r.entry_id)
        print("Title:", r.title)
        print("Authors:", get_author(r))
        print("DOI:", r.doi)
        print("Published:", r.published.strftime("%Y-%m"))
        # print("Summary:", r.summary)
        res.append(
            {
                "title": r.title,
                "authors": get_author(r),
                "summary": r.summary,
                "entry_id": r.entry_id,
                "doi": r.doi,
                "published": r.published.strftime("%Y-%m"),
            }
        )
    return res
