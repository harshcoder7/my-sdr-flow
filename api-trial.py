import json
import requests
import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# API Configuration
try:
    api_key = os.environ["AGENT_HIVE_API_KEY"]
except KeyError:
    raise ValueError("API_KEY environment variable not found. Please set your API key in the environment variables.")

url = "https://flow.agenthive.tech/api/v1/run/linkedin-posts"  # The complete API endpoint URL for this flow

# data = {"linkedin_url": "https://www.linkedin.com/in/satishhc/", "icp_result": {"product_fit": "Both", "icp_score": 3, "prospect_level": "Low", "engagement_readiness": "Cold", "justification": "Infosys, being a large multinational with over 343,000 employees, does not fit the target ICP of 50-500 employees. They have extensive AI capabilities with platforms like Infosys Nia and Topaz and a comprehensive suite of services across AI, cloud, and digital transformation. However, assuming their internal AI solutions are not up to the mark, QpiAI Pro could enhance their AutoML and MLOps capabilities for faster AI project delivery. Agent Hive could improve their orchestration and integration of AI models into enterprise workflows. Despite this, Infosys's broad and mature AI offerings suggest that they might not have an immediate need for our platforms.", "use_cases": ["QpiAI Pro can be used to enhance Infosys's AI & Data Analytics services by providing advanced AutoML and MLOps capabilities, enabling faster model training and deployment for client projects.", "Agent Hive can improve Infosys's Business Process Management & Automation by integrating sophisticated multi-agent orchestration, enhancing their RPA tools with dynamic memory and tool integration for complex enterprise workflows."]}}

# Request payload configuration
payload = {
    "output_type": "chat",
    "input_type": "chat",
    "input_value": "https://www.linkedin.com/in/shubhamsaboo/",
    "tweaks" : {
        "GoogleGenerativeAIModel-pmAtd" : {
            "model_name" : "gemini-2.5-flash",
        }
    }  # Convert data to JSON string
}

# Request headers
headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key  # Authentication key from environment variable
}

try:
    # Send API request
    response = requests.request("POST", url, json=payload, headers=headers)
    response.raise_for_status()  # Raise exception for bad status codes
    
    # Print response details for debugging
    # print(f"Status Code: {response.status_code}")
    # print(f"Response Headers: {response.headers}")
    print(f"Raw Response: {response.text}")
    
    # # Try to parse JSON if response has content
    # if response.text.strip():
    #     result = response.json()
    #     print("JSON Response:")
    #     print(result)
    # else:
    #     print("Empty response received")

except requests.exceptions.RequestException as e:
    print(f"Error making API request: {e}")

except json.JSONDecodeError as e:
    print(f"Error parsing JSON response: {e}")
    print(f"Raw response content: {response.text}")