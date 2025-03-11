"""
API Client for interacting with external data sources.

This module handles authentication, request formation, 
data fetching, and error handling when communicating with APIs.
"""

import logging
import requests
import time
from typing import Dict, List, Optional, Any

import config as config
from utils.helpers import handle_exceptions

class APIClient:
    """Client for interacting with the data source API."""
    
    def __init__(self, base_url: str = None, api_key: str = None, timeout: int = None):
        """
        Initialize the API client.
        
        Args:
            base_url: The base URL for the API. Defaults to config value.
            api_key: The API key for authentication. Defaults to config value.
            timeout: Request timeout in seconds. Defaults to config value.
        """
        self.base_url = base_url or config.API_BASE_URL
        self.api_key = api_key or config.API_KEY
        self.timeout = timeout or config.API_TIMEOUT
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        logging.debug(f"Initialized API client with base URL: {self.base_url}")
    
    @handle_exceptions
    def fetch_data(self, endpoint: str = "/data", params: Dict = None) -> List[Dict]:
        """
        Fetch data from the API endpoint.
        
        Args:
            endpoint: API endpoint path. Defaults to "/data".
            params: Query parameters for the request.
            
        Returns:
            List of data records as dictionaries.
        """
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        
        logging.info(f"Fetching data from {url}")
        logging.debug(f"Request parameters: {params}")
        
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        
        data = response.json()
        logging.info(f"Successfully fetched {len(data)} records")
        
        return data
    
    @handle_exceptions
    def post_data(self, endpoint: str, data: Dict) -> Dict:
        """
        Post data to the API endpoint.
        
        Args:
            endpoint: API endpoint path.
            data: Data to send in the request body.
            
        Returns:
            Response data as dictionary.
        """
        url = f"{self.base_url}{endpoint}"
        
        logging.info(f"Posting data to {url}")
        response = self.session.post(url, json=data, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    @handle_exceptions
    def paginated_fetch(self, endpoint: str, page_size: int = 100) -> List[Dict]:
        """
        Fetch data from paginated API endpoints.
        
        Args:
            endpoint: API endpoint path.
            page_size: Number of records per page.
            
        Returns:
            List of all data records across pages.
        """
        all_data = []
        page = 1
        has_more = True
        
        while has_more:
            params = {
                "page": page,
                "limit": page_size
            }
            
            response = self.session.get(
                f"{self.base_url}{endpoint}", 
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            records = data.get("data", [])
            all_data.extend(records)
            
            # Check if we need to fetch more pages
            has_more = data.get("has_more", False)
            page += 1
            
            # Avoid hitting rate limits
            if has_more:
                time.sleep(0.5)
        
        logging.info(f"Fetched {len(all_data)} total records across {page-1} pages")
        return all_data
