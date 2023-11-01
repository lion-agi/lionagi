import os
from typing import Any, Dict, List
import requests
from bs4 import BeautifulSoup
from sys_utils import l_call

proxy_curl_api_key = os.getenv('PROXY_CURL_API_KEY')
api_key = os.getenv('GOOGLE_API_KEY')
engine = os.getenv('GOOGLE_CSE_ID')

def _get_url_response(url: str, timeout: tuple = (1, 1), **kwags) -> requests.Response:
    """
    Sends an HTTP GET request to a specified URL and returns the response.

    Args:
        url (str): The URL to send the request to.
        timeout (tuple, optional): A tuple of two integers specifying the connection timeout and read timeout in seconds. Defaults to (1, 1).
        kwargs (dict): Additional keyword arguments to pass to `requests.get()`.

    Returns:
        requests.Response: The HTTP response object.

    Raises:
        TimeoutError: If the request times out.

    Sample Usage:
        >>> _get_url_response("https://www.example.com", timeout=(2, 2))
    """
    try:
        response = requests.get(url, timeout=timeout, **kwags)
        return response
    except requests.exceptions.ConnectTimeout:
        raise TimeoutError(f"Timeout: requesting the url responses took too long (>{timeout[0]}) seconds.")
    except requests.exceptions.ReadTimeout:
        raise TimeoutError(f"Timeout: reading the url responses took too long (>{timeout[1]}) seconds.")
    except Exception as e:
        raise e

def proxycurl_people(url, timeout=(1, 1)):
    headers = {'Authorization': 'Bearer ' + proxy_curl_api_key}
    api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
    params = {
        'linkedin_profile_url': url,
        'extra': 'include',
        'github_profile_id': 'include',
        'facebook_profile_id': 'include',
        'twitter_profile_id': 'include',
        'personal_contact_number': 'include',
        'personal_email': 'include',
        'inferred_salary': 'include',
        'skills': 'include',
        'use_cache': 'if-present',
        'fallback_to_cache': 'on-error',
    }
    response = _get_url_response(api_endpoint, 
                                 timeout=timeout, 
                                 params=params,
                                 headers=headers)
    response = response.json()
    return response

def get_linkedin_company(linkedin_url, timeout=(1, 1)):
    headers = {'Authorization': 'Bearer ' + proxy_curl_api_key}
    api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/company'
    params = {
        'url': linkedin_url,
        'resolve_numeric_id': 'true',
        'categories': 'include',
        'funding_data': 'include',
        'extra': 'include',
        'exit_data': 'include',
        'acquisitions': 'include',
        'use_cache': 'if-present',
    }
    response = _get_url_response(api_endpoint, 
                                 timeout=timeout,
                                 params=params, 
                                 headers=headers)
    response = response.json()
    return response

def _get_search_item_field(item: Dict[str, Any]) -> Dict[str, str]:
    """
    Extracts relevant fields from a Google search item.

    Args:
        item (Dict[str, Any]): The Google search item as a dictionary.

    Returns:
        Dict[str, str]: A dictionary containing the title, snippet, link, and long description.

    """

    try:
        long_description = item["pagemap"]["metatags"][0]["og:description"]
    except KeyError:
        long_description = "N/A"
    
    return {
        "title": item.get("title"),
        "snippet": item.get("snippet"),
        "link": item.get("link"),
        "long_description": long_description
    }

def _get_google_news_field(item: BeautifulSoup) -> Dict[str, str]:
    """
    Extracts relevant fields from a Google news item.

    Args:
        item (BeautifulSoup): The Google news item as a BeautifulSoup object.

    Returns:
        Dict[str, str]: A dictionary containing the title, source, link, and date.

    """
        
    return {
        "title": item.title.text,
        "source": item.source.text,
        "link": item.link.text,
        "date": item.pubDate.text
    }

def google_search(query: str, start: int = 1, timeout: tuple = (1, 1)) -> List[Dict[str, str]]:
    """
    Conducts a Google search and returns the results.

    Args:
        query (str): The search query.
        start (int, optional): The starting index for the search. Defaults to 1.
        timeout (tuple, optional): A tuple specifying the connection and read timeout. Defaults to (1, 1).

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing the search results.

    """
    
    url = ("https://www.googleapis.com/customsearch/v1?key={key}&cx={engine}&q={query}&start={start}")
    url = url.format(key=api_key, 
                     engine=engine, 
                     query=query, 
                     start=start)
    response = _get_url_response(url, timeout=timeout)
    response = response.json()
    items = response.get('items')
    
    return l_call(items, _get_search_item_field)

def google_news_search(query: str, num: int = 10, timeout: tuple = (1, 1)) -> List[Dict[str, str]]:
    """
    Conducts a Google news search and returns the results.

    Args:
        query (str): The search query.
        num (int, optional): The number of news items to return. Defaults to 10.
        timeout (tuple, optional): A tuple specifying the connection and read timeout. Defaults to (1, 1).

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing the news search results.

    """

    url = f'https://news.google.com/rss/search?q={query}'
    response = _get_url_response(url, timeout=timeout)
    soup = BeautifulSoup(response.text, features="xml")
    items = soup.find_all('item')[:num]
    
    return l_call(items, _get_google_news_field)
