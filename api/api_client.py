"""
API Client for interacting with external data sources.

This module handles authentication, request formation, 
data fetching, and error handling when communicating with APIs.
"""

import logging
import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

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
    
    def _is_demo_mode(self) -> bool:
        """Return True when external API isn't configured for real usage."""
        if not self.base_url:
            return True
        if "api.example.com" in self.base_url:
            return True
        if not self.api_key:
            return True
        return False

    def _generate_synthetic_data(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate deterministic synthetic records for local dev/demo."""
        now = datetime.now()
        data: List[Dict[str, Any]] = []
        for i in range(count):
            data.append({
                "id": i + 1,
                "type": "revenue" if i % 3 == 0 else ("inventory" if i % 3 == 1 else "general"),
                "value": round(100 + (i * 7.3) % 250, 2),
                "timestamp": (now - timedelta(minutes=i * 10)).isoformat(),
                "source_id": f"synthetic_{(i % 5) + 1}",
                "category": "demo",
            })
        return data
    
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
        params = params or {}
        # Safe local/demo fallback
        if self._is_demo_mode():
            logging.warning("API not fully configured; using synthetic demo data instead of external call")
            return self._generate_synthetic_data(count=int(params.get("limit", 100) or 100))

        url = f"{self.base_url}{endpoint}"
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
        # Safe local/demo fallback
        if self._is_demo_mode():
            logging.warning("API not fully configured; simulating POST success locally")
            return {"success": True, "echo": data}

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
        
        # Safe local/demo fallback
        if self._is_demo_mode():
            return self._generate_synthetic_data(count=page_size)

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
