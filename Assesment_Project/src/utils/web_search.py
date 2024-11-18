from serpapi import GoogleSearch
from typing import Dict, Any
import os

def perform_web_search(query: str, api_key: str) -> Dict[str, Any]:
    """
    Perform a Google search using the SerpAPI service.
    
    Args:
        query: The search query string
        api_key: SerpAPI API key
        
    Returns:
        Dict containing the search results
        
    Raises:
        Exception: If the API request fails
    """
    try:
        search = GoogleSearch({
            "q": query,
            "api_key": api_key
        })
        return search.get_dict()
    except Exception as e:
        raise Exception(f"Search failed: {str(e)}")
