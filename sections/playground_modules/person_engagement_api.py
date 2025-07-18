"""
Person Engagement API Playground Module
"""

import streamlit as st
import json
from .base_api_client import PlaygroundAPIClient

# Constants
DEFAULT_TIMEOUT = 120  # 2 minutes
FLOW_NAME = "linkedin-posts"

def validate_linkedin_url(url: str) -> bool:
    """
    Validate if the provided URL is a valid LinkedIn profile URL.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid LinkedIn URL, False otherwise
    """
    if not url:
        return False
    
    # Basic LinkedIn URL patterns
    linkedin_patterns = [
        "linkedin.com/in/",
        "www.linkedin.com/in/",
        "https://linkedin.com/in/",
        "https://www.linkedin.com/in/",
        "http://linkedin.com/in/",
        "http://www.linkedin.com/in/"
    ]
    
    return any(pattern in url.lower() for pattern in linkedin_patterns)

def process_engagement_response(response: dict) -> dict:
    """
    Extract person name and engagement summary from response payload.

    Args:
        response (dict): Full API response with embedded JSON markdown blocks.

    Returns:
        dict: Dictionary with person_name and engagement_signal_summary.
    """
    try:
        outputs = response.get("outputs", [])
        for output in outputs:
            inner_outputs = output.get("outputs", [])
            for item in inner_outputs:
                messages = item.get("messages", [])
                for msg in messages:
                    message_text = msg.get("message", "")
                    if "```json" in message_text:
                        # Extract and parse the JSON block
                        json_block = message_text.split("```json")[1].split("```")[0].strip()
                        parsed = json.loads(json_block)

                        return {
                            "person_name": parsed.get("person_name"),
                            "engagement_signal_summary": parsed.get("engagement_signal_summary")
                        }

        return {
            "status": "no_data_found",
            "error": "No embedded JSON found",
            "session_id": response.get("session_id")
        }

    except Exception as e:
        return {
            "status": "extraction_error",
            "error": str(e),
            "session_id": response.get("session_id"),
            "raw_excerpt": str(response)[:1000]  # truncate for debugging
        }

def show_person_engagement_playground():
    """Display the person engagement API playground"""
    st.subheader("📊 Person Engagement Signal API")
    st.markdown("Analyze LinkedIn posts to identify engagement signals and opportunities")
    
    # Initialize API client
    api_client = PlaygroundAPIClient()
    
    # Input section
    st.markdown("### Input Configuration")
    
    # LinkedIn URL input
    linkedin_url = st.text_input(
        "Enter LinkedIn Profile URL:",
        placeholder="https://www.linkedin.com/in/username/",
        key="linkedin_url_input",
        help="Enter the LinkedIn profile URL of the person you want to analyze"
    )
    
    # Add tweaks for the LinkedIn posts API
    tweaks = {
        "GoogleGenerativeAIModel-pmAtd": {
            "model_name": "gemini-2.5-flash"
        }
    }
    
    if st.button("🔍 Analyze Engagement Signals", key="engagement_api_call", type="primary"):
        if not linkedin_url.strip():
            st.error("Please provide a LinkedIn profile URL")
            return
        
        # Validate LinkedIn URL
        if not validate_linkedin_url(linkedin_url):
            st.error("Please provide a valid LinkedIn profile URL (e.g., https://www.linkedin.com/in/username/)")
            return
        
        # Make API call with custom processing function and timeout
        with st.spinner("Analyzing LinkedIn posts and engagement signals..."):
            response = api_client.make_request(
                FLOW_NAME, 
                linkedin_url, 
                tweaks=tweaks,
                timeout=DEFAULT_TIMEOUT,
                process_fn=process_engagement_response
            )
    
    # Display results
    st.markdown("### API Response")
    
    if 'response' in locals() and response.get("success", False):
            st.success("✅ Engagement signal analysis completed!")

            # Show processing error if any
            if "processing_error" in response:
                st.warning(f"⚠️ Processing error: {response['processing_error']}")
            
            # Display processed data if available
            if "processed_data" in response:
                st.markdown("#### 📊 ICP Analysis Results")
                processed_data = response["processed_data"]
                
                # Display full processed data
                st.json(processed_data)
            else:
                # Extract and display content
                content = api_client.extract_response_content(response)
                
                # Try to parse as JSON for better display
                try:
                    if "```json" in content:
                        json_content = content.split("```json")[1].split("```")[0].strip()
                        parsed_content = json.loads(json_content)
                        
                        # Display full JSON
                        st.json(parsed_content)
                    else:
                        st.text_area("Response Content:", content, height=500)
                except Exception as e:
                    st.text_area("Response Content:", content, height=500)
            
            # Show raw response in expander
            with st.expander("🔍 Raw API Response", expanded=False):
                st.json(response["data"])
                
    elif 'response' in locals():
        st.error(f"❌ API call failed: {response.get('error', 'Unknown error')}")
        
        # Show error details
        if "response_text" in response:
            with st.expander("🔍 Error Details", expanded=False):
                st.text(response["response_text"])
    
    # Help section
    with st.expander("ℹ️ API Information", expanded=False):
        st.markdown("""
        **Endpoint:** `linkedin-posts`
        
        **Purpose:** Analyzes LinkedIn posts and activity to identify:
        - Business pain points and challenges
        - Technology interests and preferences
        - Decision-making signals
        - Engagement opportunities
        - Best times to reach out
        - Sentiment and mood indicators
        - Industry focus areas

        """)
