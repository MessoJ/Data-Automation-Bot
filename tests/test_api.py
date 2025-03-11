"""
Tests for the API client module.
"""
import unittest
import requests
import json
from unittest.mock import patch, MagicMock
from api.api_client import APIClient
from config import Config

class TestAPIClient(unittest.TestCase):
    """Test cases for the APIClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = {
            'api': {
                'base_url': 'https://api.example.com',
                'api_key': 'test_api_key',
                'timeout': 30,
                'retry_attempts': 3
            }
        }
        
        with patch('data_automation_bot.config.Config.get_config', return_value=self.mock_config):
            self.api_client = APIClient()
    
    @patch('requests.get')
    def test_get_data(self, mock_get):
        """Test the get_data method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': [{'id': 1, 'name': 'Test'}]}
        mock_get.return_value = mock_response
        
        # Call method
        endpoint = '/data'
        result = self.api_client.get_data(endpoint)
        
        # Assertions
        mock_get.assert_called_once_with(
            'https://api.example.com/data',
            headers={'Authorization': 'Bearer test_api_key'},
            params={},
            timeout=30
        )
        self.assertEqual(result, {'data': [{'id': 1, 'name': 'Test'}]})
    
    @patch('requests.post')
    def test_post_data(self, mock_post):
        """Test the post_data method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 1, 'status': 'created'}
        mock_post.return_value = mock_response
        
        # Call method
        endpoint = '/data'
        payload = {'name': 'New Item', 'value': 42}
        result = self.api_client.post_data(endpoint, payload)
        
        # Assertions
        mock_post.assert_called_once_with(
            'https://api.example.com/data',
            headers={'Authorization': 'Bearer test_api_key', 'Content-Type': 'application/json'},
            json=payload,
            timeout=30
        )
        self.assertEqual(result, {'id': 1, 'status': 'created'})
    
    @patch('requests.get')
    def test_get_data_error_handling(self, mock_get):
        """Test error handling in get_data method."""
        # Setup mock to raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Call method and check exception handling
        with self.assertRaises(requests.exceptions.RequestException):
            self.api_client.get_data('/error')
    
    @patch('requests.get')
    def test_get_data_retry_mechanism(self, mock_get):
        """Test the retry mechanism in get_data method."""
        # Setup mock to fail twice then succeed
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {'data': 'success'}
        
        mock_get.side_effect = [
            requests.exceptions.ConnectionError("Connection refused"),
            requests.exceptions.ConnectionError("Connection refused"),
            mock_response_success
        ]
        
        # Configure retry settings
        self.api_client.retry_attempts = 3
        self.api_client.retry_delay = 0  # No delay for testing
        
        # Call method
        result = self.api_client.get_data('/data')
        
        # Assertions
        self.assertEqual(mock_get.call_count, 3)
        self.assertEqual(result, {'data': 'success'})

if __name__ == '__main__':
    unittest.main()
