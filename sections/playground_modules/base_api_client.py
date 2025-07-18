"""
Base API client for playground modules
Provides common functionality for making API requests
"""

import requests
import json
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv()

class PlaygroundAPIClient:
    """Base API client for playground API calls"""
    
    def __init__(self):
        self.api_key = os.getenv('AGENT_HIVE_API_KEY', '')
        self.base_url = "https://flow.agenthive.tech/api/v1/run"
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }
    
    def make_request(self, endpoint: str, input_data: str, tweaks: Optional[Dict] = None, timeout: int = 300, process_fn: Optional[callable] = None) -> Dict[str, Any]:
        """
        Make API request to specified endpoint
        
        Args:
            endpoint (str): API endpoint path
            input_data (str): Input data as string
            tweaks (dict, optional): Additional tweaks for the API
            timeout (int, optional): Request timeout in seconds. Default is 300
            process_fn (callable): Custom function to process the API response
        
        Returns:
            dict: API response or error information
        """
        if (not input_data) or (input_data == "{}"):
            return {
                "success": False,
                "error": "Input data cannot be empty"
            }
        try:
            # Prepare payload
            payload = {
                "output_type": "chat",
                "input_type": "chat",
                "input_value": input_data
            }
            
            # Add tweaks if provided
            if tweaks:
                payload["tweaks"] = tweaks
            
            # Make request
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                api_response = {
                    "success": True,
                    "data": response.json(),
                    "status_code": response.status_code
                }
                
                # Apply custom processing function if provided
                if process_fn:
                    try:
                        processed_data = process_fn(api_response["data"])
                        api_response["processed_data"] = processed_data
                    except Exception as e:
                        api_response["processing_error"] = f"Error in custom processing: {str(e)}"
                
                return api_response
            else:
                return {
                    "success": False,
                    "error": f"API request failed with status {response.status_code}",
                    "status_code": response.status_code,
                    "response_text": response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def extract_response_content(self, api_response: Dict[str, Any], use_processed: bool = True) -> str:
        """
        Extract the main content from API response
        
        Args:
            api_response (dict): Raw API response
            use_processed (bool): Whether to use processed_data if available
            
        Returns:
            str: Extracted content or error message
        """
        try:
            if not api_response.get("success", False):
                return f"Error: {api_response.get('error', 'Unknown error')}"
            
            # Use processed data if available and requested
            if use_processed and "processed_data" in api_response:
                processed_data = api_response["processed_data"]
                if isinstance(processed_data, dict):
                    return json.dumps(processed_data, indent=2)
                else:
                    return str(processed_data)
            
            data = api_response.get("data", {})
            outputs = data.get("outputs", [])
            
            for output in outputs:
                for item in output.get("outputs", []):
                    messages = item.get("messages", [])
                    for message_item in messages:
                        message_text = message_item.get("message", "")
                        if message_text:
                            return message_text
            
            return "No content found in response"
            
        except Exception as e:
            return f"Error extracting content: {str(e)}"
