from serpapi import GoogleSearch
import os

def perform_web_search(query, api_key):
    search = GoogleSearch({
        "q": query,
        "api_key": api_key
    })
    return search.get_dict()
