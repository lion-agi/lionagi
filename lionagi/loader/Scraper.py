import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
import feedparser
from lionagi.session.Session import Session
from lionagi.utils.log_utils import source_logger

proxy_curl_api_key = os.getenv('PROXY_CURL_API_KEY')
sourcelog = source_logger()

def get_linkedin_person(linkedin_url):
    headers = {'Authorization': 'Bearer ' + proxy_curl_api_key}
    api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
    params = {
        'linkedin_profile_url': linkedin_url,
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
    response = requests.get(api_endpoint,
                            params=params,
                            headers=headers)
    response = response.json()
    entry = {
        "id": response['public_identifier'],
        "type": {
            "main":"source",
            "subtype": "PeopleLinkedIn"},
        "data": response    
    }
    sourcelog(entry)
    return response

def get_linkedin_company(linkedin_url):
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
    response = requests.get(api_endpoint,
                            params=params,
                            headers=headers)
    response = response.json()
    entry = {
        "id": linkedin_url,
        "type": {
            "main":"source",
            "subtype": "CompanyLinkedIn"},
        "data": response
    }
    sourcelog(entry)
    return response
    
# Fetch bs4 soup from URL with multi-stage timeout
def _get_soup(url, timeout=(1.5, 1.5)):
    try:
        response = requests.get(url, timeout=timeout)
        soup = BeautifulSoup(response.text, 'html.parser')
        return (response.text, soup)
    except requests.exceptions.ConnectTimeout:
        pass
    except requests.exceptions.ReadTimeout:
        pass
    except Exception as e:
        pass

# General HTML inspector
def _info_from_link(url, timeout=(1.5, 1.5)):
    try:
        text, soup = _get_soup(url, timeout=timeout)
        title = soup.find("meta", property="og:title")
        description = soup.find("meta", property="og:description")
        link_url = soup.find("meta", property="og:url")
        info = {
            "link_title": title['content'] if title else None,
            "link_description": description['content'] if description else None,
            "link_url": link_url['content'] if link_url else None,
        }
        entry = {
            "id": url,
            "type": {
                "main":"source",
                "subtype": "url"},
            "data": {
                "info": info, 
                "text": text}
            }
        sourcelog(entry)
        return info
    except:
        pass

def get_news_articles(query, context, num_articles, system_NewsFilter, Filter_News, temperature=0.5, model="gpt-3.5-turbo"):
    newsFilter = Session(system_NewsFilter)
    url = f'https://news.google.com/rss/search?q={query}'
    feed = feedparser.parse(url)
    judges, index, news = [], [], []
    for link in feed.entries[:num_articles]:
        info = _info_from_link(link.link)
        news.append(info)
        context['news'] = info
        judgement = newsFilter.initiate(
            context=context,
            instruction=Filter_News,
            model= model, 
            temperature=temperature).lower().strip()
        index.append(True if "yes" in judgement else False)
        judges.append(judgement)
        
    df = pd.DataFrame(news)
    df = df[index].reset_index(drop=True)
    return (df, judges)