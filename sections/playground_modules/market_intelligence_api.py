"""
Market Intelligence API Playground Module
"""

import streamlit as st
import json
from .base_api_client import PlaygroundAPIClient

# Constants
DEFAULT_TIMEOUT = 300  # 5 minutes
DEFAULT_JSON = """{
    "Company": "ExampleTech Solutions Pvt Ltd",
    "Overview": "ExampleTech Solutions Pvt Ltd offers IT and business intelligence services, specializing in SQL development, BI dashboards, and enterprise resource planning. Their workforce is proficient in SQL, SSRS, Power BI, and SAP Hana, signaling a strong focus on data infrastructure and analytics solutions.",
    "Size": "51-200 employees",
    "Revenue": "N/A",
    "Domain": "exampletechsolutions.com",
    "Funding Information": "N/A",
    "Latest Funding Round": "N/A",
    "Investors": "N/A",
    "LinkedIn URL": "https://www.linkedin.com/company/exampletech-solutions",
    "Sources": "- [EXAMPLETECH SOLUTIONS - LinkedIn](https://in.linkedin.com/company/exampletech-solutions)\\n- [Jane Doe - Director - ExampleTech Solutions](https://in.linkedin.com/in/jane-doe-123456)\\n- [John Smith - SQL Developer - ExampleTech Solutions](https://in.linkedin.com/in/john-smith-789012)"
}"""
FLOW_NAME = "market-intelligence"

def process_api_response(api_response: dict) -> dict:
    """
    Extracts structured market intelligence data from a stringified JSON block
    embedded in the 'message' field of the API response.

    Args:
        api_response (dict): Raw API response.

    Returns:
        dict: Parsed market intelligence data, or error metadata if extraction fails.
    """
    try:
        outputs = api_response.get("outputs", [])

        for output in outputs:
            inner_outputs = output.get("outputs", [])
            for item in inner_outputs:
                messages = item.get("messages", [])
                for message_item in messages:
                    message_text = message_item.get("message", "")

                    if "```json" in message_text:
                        try:
                            # Extract and clean the JSON block
                            json_block = message_text.split("```json")[1].split("```")[0].strip()
                            market_intelligence = json.loads(json_block)
                            return market_intelligence
                        except json.JSONDecodeError as decode_error:
                            return {
                                "enrichment_status": "json_parse_error",
                                "error": f"Failed to parse JSON: {str(decode_error)}",
                                "raw_json_block": json_block,
                                "raw_response": api_response
                            }

        # No valid JSON found
        return {
            "enrichment_status": "no_market_intelligence_found",
            "error": "No embedded JSON found in messages",
            "raw_response": api_response
        }

    except Exception as e:
        return {
            "enrichment_status": "processing_error",
            "error": f"Unexpected failure: {str(e)}",
            "raw_response": api_response
        }

def show_market_intelligence_playground():
    """Display the market intelligence API playground"""
    st.subheader("🏢 Market Intelligence API")
    st.markdown("Get comprehensive market insights and competitive analysis")
    
    # Initialize API client
    api_client = PlaygroundAPIClient()
    
    # Input section
    st.markdown("### Input Configuration")
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Manual Input", "JSON Input"],
        key="market_input_method"
    )
    
    if input_method == "Manual Input":
        st.info("🚧 Coming soon...")
        st.markdown("Manual input interface is currently under development. Please use JSON input for now.")
        
        # Build empty input data for now
        input_data = {}
        input_json = json.dumps(input_data, indent=2)
        
    else:
        # JSON input
        input_json = st.text_area(
            "Enter market intelligence request as JSON:",
            height=300,
            placeholder=DEFAULT_JSON,
            value=DEFAULT_JSON,
            key="market_json_input"
        )
    
    # Show current input
    with st.expander("📋 Current Input Data", expanded=False):
        st.code(input_json, language="json")
    
    # API call button
    st.markdown("### Make API Call")
    
    if st.button("📊 Generate Market Intelligence", key="market_api_call", type="primary"):
        if not input_json.strip():
            st.error("Please provide input data")
            return
        
        # Validate JSON
        try:
            parsed_json = json.loads(input_json)

            # # Additional validation for required fields
            # if input_method == "JSON Input":
            #     required_fields = ["company_name", "industry"]
            #     missing_fields = [field for field in required_fields if not parsed_json.get(field)]
            #     if missing_fields:
            #         st.error(f"Missing required fields: {', '.join(missing_fields)}")
            #         return
                    
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {str(e)}")
            return
        
        # Make API call
        with st.spinner("Generating market intelligence report..."):
            response = api_client.make_request(
                FLOW_NAME, 
                input_json, 
                timeout=DEFAULT_TIMEOUT,
                process_fn=process_api_response,
            )
        
        # Display results
        st.markdown("### API Response")
        
        if response.get("success", False):
            st.success("✅ Market intelligence report generated!")

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
                
        else:
            st.error(f"❌ API call failed: {response.get('error', 'Unknown error')}")
            
            # Show error details
            if "response_text" in response:
                with st.expander("🔍 Error Details", expanded=False):
                    st.text(response["response_text"])
    
    # Help section
    with st.expander("ℹ️ API Information", expanded=False):
        st.markdown("""
        **Endpoint:** `market-intelligence`\n
        **Description:** This API provides detailed market intelligence reports, including company profiles, industry analysis, and any latest news about the company.
        """)
