import requests
import os
import dotenv
import pandas as pd
import time
from typing import Optional, Dict

# Constants for processing
START_INDEX = 0  # Change this to start from a specific row
END_INDEX = 0   # Change this to end at a specific row
INPUT_CSV_PATH = "/Users/adithyankrishnan/Downloads/QPIAI_Xencia_GTM Accounts List.csv"  # Change this to your input CSV path
OUTPUT_CSV_PATH = "companies_with_domains.csv"  # Change this to your desired output path
DELAY_BETWEEN_REQUESTS = 1  # Delay in seconds between API calls to avoid rate limiting

# Load environment variables from .env file
dotenv.load_dotenv()

# API Configuration
try:
    api_key = os.environ["AGENT_HIVE_API_KEY"]
except KeyError:
    raise ValueError("API_KEY environment variable not found. Please set your API key in the environment variables.")

url = "https://flow.agenthive.tech/api/v1/run/fd0c696d-df59-41d3-b4a9-866c8313c67e"  # The complete API endpoint URL for this flow

# Request payload configuration
payload = {
    "output_type": "chat",
    "input_type": "chat",
    # "input_value": "blabla"
}

# Request headers
headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key  # Authentication key from environment variable
}

import json
import re

def process_response(response_json):
    """
    Parses the company domain from the response JSON structure.
    
    Args:
        response_json (dict or str): The response JSON from the API
        
    Returns:
        str: The company domain if found, None otherwise
    """
    try:
        # Handle string input by parsing to dict
        if isinstance(response_json, str):
            response_data = json.loads(response_json)
        else:
            response_data = response_json
        
        # Navigate through the JSON structure to find the AI's text response
        outputs = response_data.get("outputs", [])
        
        for output in outputs:
            # Check multiple possible paths for the text content
            text_content = None
            
            # Path 1: outputs -> outputs -> results -> message -> text
            if "outputs" in output:
                for sub_output in output["outputs"]:
                    if "results" in sub_output and "message" in sub_output["results"]:
                        text_content = sub_output["results"]["message"].get("text")
                        break
            
            # Path 2: artifacts -> message
            if not text_content and "artifacts" in output:
                text_content = output["artifacts"].get("message")
            
            # Path 3: outputs -> message -> message
            if not text_content and "outputs" in output and "message" in output["outputs"]:
                text_content = output["outputs"]["message"].get("message")
            
            # If we found text content, try to extract the domain
            if text_content:
                domain = extract_domain_from_text(text_content)
                if domain:
                    return domain
        
        return None
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error parsing response: {e}")
        return None

def extract_domain_from_text(text):
    """
    Extracts the company domain from the AI's text response.
    
    Args:
        text (str): The AI's response text containing JSON
        
    Returns:
        str: The company domain if found, None otherwise
    """
    try:
        # Look for JSON blocks in the text (between ```json and ```)
        json_pattern = r'```json\s*\n(.*?)\n```'
        json_matches = re.findall(json_pattern, text, re.DOTALL)
        
        for json_match in json_matches:
            try:
                # Parse the JSON content
                json_data = json.loads(json_match)
                
                # Look for company domain in various possible keys
                possible_keys = [
                    "Company Domain",
                    "company_domain", 
                    "domain",
                    "website",
                    "url"
                ]
                
                for key in possible_keys:
                    if key in json_data:
                        return json_data[key]
                        
            except json.JSONDecodeError:
                continue
        
        # If no JSON blocks found, try to find domain directly in text
        # Look for domain patterns (e.g., "convin.ai", "example.com")
        domain_pattern = r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}'
        domain_matches = re.findall(domain_pattern, text)
        
        # Return the first domain that looks like a company domain
        for domain in domain_matches:
            if not domain.startswith('www.') and '.' in domain:
                return domain
                
        return None
        
    except Exception as e:
        print(f"Error extracting domain from text: {e}")
        return None

def process_companies_csv() -> None:
    """
    Process companies from a CSV file, get their domains via API, and save results.
    Uses START_INDEX and END_INDEX to process a specific range of companies.
    """
    try:
        # Read the input CSV
        df = pd.read_csv(INPUT_CSV_PATH)
        if 'Company Name' not in df.columns:
            raise ValueError("CSV must contain a 'Company Name' column")

        # Create results dictionary to store domains
        results: Dict[str, Optional[str]] = {}
        
        # Process only the specified range
        end_idx = min(END_INDEX, len(df)) if END_INDEX > 0 else len(df)
        companies_to_process = df['Company Name'][START_INDEX:end_idx]
        
        print(f"Processing companies from index {START_INDEX} to {end_idx}")
        
        for idx, company_name in enumerate(companies_to_process, start=START_INDEX):
            print(f"Processing {idx + 1}/{end_idx}: {company_name}")
            
            # Update payload with company name
            payload["input_value"] = company_name
            
            try:
                # Send API request
                response = requests.request("POST", url, json=payload, headers=headers)
                response.raise_for_status()
                
                # Process response and store result
                domain = process_response(response.json())
                results[company_name] = domain
                
                print(f"Found domain for {company_name}: {domain}")
                
                # Add delay between requests
                time.sleep(DELAY_BETWEEN_REQUESTS)
                
            except requests.exceptions.RequestException as e:
                print(f"Error processing {company_name}: {e}")
                results[company_name] = None
                
        # Create results DataFrame
        results_df = pd.DataFrame(
            [(company, domain) for company, domain in results.items()],
            columns=['company_name', 'domain']
        )
        
        # Save results to CSV
        results_df.to_csv(OUTPUT_CSV_PATH, index=False)
        print(f"\nResults saved to {OUTPUT_CSV_PATH}")
        print(f"Processed {len(results)} companies. Success rate: {(len([d for d in results.values() if d is not None]) / len(results)) * 100:.2f}%")
        
    except Exception as e:
        print(f"Error processing CSV: {e}")

if __name__ == "__main__":
    try:
        process_companies_csv()
    except Exception as e:
        print(f"Fatal error: {e}")