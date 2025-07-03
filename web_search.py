import os
from dataclasses import dataclass
from typing import List, Optional
from googleapiclient.discovery import build

@dataclass
class SearchResult:
    title: str
    link: str
    snippet: str

class GoogleSearch:
    """Google Custom Search API wrapper"""
    
    def __init__(self, api_key: str, cse_id: str):
        self.api_key = api_key
        self.cse_id = cse_id
        self.service = build("customsearch", "v1", developerKey=api_key)
    
    def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """Perform search using Google Custom Search API"""
        try:
            res = self.service.cse().list(
                q=query,
                cx=self.cse_id,
                num=num_results
            ).execute()
            
            return [
                SearchResult(
                    title=item.get('title', 'No title'),
                    link=item.get('link', '#'),
                    snippet=item.get('snippet', 'No description')
                )
                for item in res.get('items', [])
            ]
        except Exception as e:
            raise RuntimeError(f"Google Search failed: {str(e)}")
