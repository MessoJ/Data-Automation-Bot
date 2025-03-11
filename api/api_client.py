import os
import requests
import json
import pandas as pd
import logging
import time
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class APIClient:
    """
    Class for handling API interactions.
    Provides methods for fetching, posting and processing API data.
    """
    
    def __init__(self, base_url=None, api_key=None, api_secret=None):
        """
        Initialize the APIClient with connection parameters.
        
        If parameters are not provided, attempts to load from environment variables.
        
        Args:
            base_url (str, optional): Base URL for the API.
            api_key (str, optional): API key for authentication.
            api_secret (str, optional): API secret for authentication.
        """
        load_dotenv()
        
        self.base_url = base_url or os.getenv("API_BASE_URL")
        self.api_key = api_key or os.getenv("API_KEY")
        self.api_secret = api_secret or os.getenv("API_SECRET")
        
        if not self.base_url:
            raise ValueError("API base URL not provided or found in environment variables")
        
        self.session = requests.Session()
        
        # Set up authentication if credentials are provided
        if self.api_key and self.api_secret:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "x-api-secret": self.api_secret,
                "Content-Type": "application/json",
                "Accept": "application/json"
            })
        
        # Default rate limiting settings
        self.rate_limit = 60  # requests per minute
        self.request_count = 0
        self.last_request_time = time.time()
        
        logger.info("APIClient initialized")
    
    def get(self, endpoint, params=None, timeout=30, rate_limit=True):
        """
        Make a GET request to the API.
        
        Args:
            endpoint (str): API endpoint to request.
            params (dict, optional): Query parameters for the request.
            timeout (int, optional): Request timeout in seconds.
            rate_limit (bool, optional): Whether to apply rate limiting.
        
        Returns:
            dict: JSON response from the API.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Apply rate limiting if enabled
        if rate_limit:
            self._apply_rate_limiting()
        
        try:
            logger.info(f"Making GET request to {url}")
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            raise
    
    def post(self, endpoint, data, timeout=30, rate_limit=True):
        """
        Make a POST request to the API.
        
        Args:
            endpoint (str): API endpoint to request.
            data (dict): Data to send in the request body.
            timeout (int, optional): Request timeout in seconds.
            rate_limit (bool, optional): Whether to apply rate limiting.
        
        Returns:
            dict: JSON response from the API.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Apply rate limiting if enabled
        if rate_limit:
            self._apply_rate_limiting()
        
        try:
            logger.info(f"Making POST request to {url}")
            response = self.session.post(url, json=data, timeout=timeout)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            raise
    
    def _apply_rate_limiting(self):
        """
        Apply rate limiting to prevent exceeding API limits.
        
        This method keeps track of requests and adds delays when necessary
        to stay within the configured rate limit.
        """
        current_time = time.time()
        time_passed = current_time - self.last_request_time
        
        # If we've made a request recently, check if we need to throttle
        if self.request_count > 0:
            # Reset counter if a minute has passed
            if time_passed > 60:
                self.request_count = 0
                self.last_request_time = current_time
            # If we're approaching the rate limit, add a delay
            elif self.request_count >= self.rate_limit:
                sleep_time = 60 - time_passed
                if sleep_time > 0:
                    logger.info(f"Rate limit approached. Sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
                    self.request_count = 0
                    self.last_request_time = time.time()
        
        # Increment the request counter
        self.request_count += 1
    
    def fetch_data_to_dataframe(self, endpoint, params=None, data_path=None):
        """
        Fetch data from the API and convert it to a pandas DataFrame.
        
        Args:
            endpoint (str): API endpoint to request.
            params (dict, optional): Query parameters for the request.
            data_path (str, optional): JSON path to the data array in the response.
                For example, 'data.items' would extract response['data']['items'].
        
        Returns:
            pd.DataFrame: DataFrame containing the API data.
        """
        try:
            response_data = self.get(endpoint, params=params)
            
            # Extract data from the specified path if provided
            if data_path:
                data = response_data
                for key in data_path.split('.'):
                    data = data.get(key, {})
                
                if not data:
                    logger.warning(f"No data found at path '{data_path}' in API response")
                    return pd.DataFrame()
            else:
                data = response_data
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                # If it's not a list, try to convert it to a DataFrame with a single row
                df = pd.DataFrame([data])
            
            logger.info(f"Successfully converted API data to DataFrame with shape {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error converting API data to DataFrame: {str(e)}")
            raise
    
    def paginated_fetch(self, endpoint, params=None, data_path=None, 
                        page_param='page', limit_param='limit', limit=100, 
                        max_pages=None):
        """
        Fetch paginated data from the API and combine into a single DataFrame.
        
        Args:
            endpoint (str): API endpoint to request.
            params (dict, optional): Query parameters for the request.
            data_path (str, optional): JSON path to the data array in the response.
            page_param (str, optional): Name of the pagination parameter.
            limit_param (str, optional): Name of the limit parameter.
            limit (int, optional): Number of items per page.
            max_pages (int, optional): Maximum number of pages to fetch.
        
        Returns:
            pd.DataFrame: Combined DataFrame containing all paginated data.
        """
        all_data = []
        page = 1
        
        # Initialize params if None
        params = params or {}
        
        while True:
            # Update pagination parameters
            current_params = params.copy()
            current_params[page_param] = page
            current_params[limit_param] = limit
            
            try:
                logger.info(f"Fetching page {page} from API")
                response_data = self.get(endpoint, params=current_params)
                
                # Extract data from the specified path if provided
                if data_path:
                    data = response_data
                    for key in data_path.split('.'):
                        data = data.get(key, {})
                else:
                    data = response_data
                
                # If we get an empty result or not a list, break the loop
                if not data or not isinstance(data, list) or len(data) == 0:
                    break
                
                all_data.extend(data)
                logger.info(f"Retrieved {len(data)} items from page {page}")
                
                # Break if we received fewer items than the limit (last page)
                if len(data) < limit:
                    break
                
                # Break if we've reached the maximum number of pages
                if max_pages and page >= max_pages:
                    logger.info(f"Reached maximum number of pages ({max_pages})")
                    break
                
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {str(e)}")
                break
        
        # Convert combined data to DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            logger.info(f"Successfully combined {len(all_data)} items into DataFrame")
            return df
        else:
            logger.warning("No data retrieved from paginated API requests")
            return pd.DataFrame()
