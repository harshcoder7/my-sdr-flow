"""
Enrichment API Playground Module
"""

import streamlit as st
import json
from .base_api_client import PlaygroundAPIClient

def json_to_markdown(data, title="Data", max_depth=3, current_depth=0):
    """
    Convert JSON data to simple markdown format.
    
    Args:
        data: JSON data (dict, list, or primitive)
        title: Title for the markdown section
        max_depth: Maximum depth to display nested objects
        current_depth: Current recursion depth
    
    Returns:
        str: Markdown formatted string
    """
    if current_depth > max_depth:
        return "*(nested data truncated)*"
    
    if isinstance(data, dict):
        markdown = f"## {title}\n\n" if current_depth == 0 else f"{'#' * (current_depth + 2)} {title}\n\n"
        
        for key, value in data.items():
            if isinstance(value, (dict, list)) and value:
                if isinstance(value, dict) and len(value) > 0:
                    markdown += json_to_markdown(value, key, max_depth, current_depth + 1)
                elif isinstance(value, list) and len(value) > 0:
                    markdown += f"**{key}:**\n\n"
                    for i, item in enumerate(value[:5]):  # Limit to first 5 items
                        if isinstance(item, dict):
                            markdown += json_to_markdown(item, f"{key} {i+1}", max_depth, current_depth + 1)
                        else:
                            markdown += f"- {item}\n"
                    if len(value) > 5:
                        markdown += f"- *(and {len(value) - 5} more items)*\n"
                    markdown += "\n"
            else:
                # Format the value nicely
                if value is None:
                    formatted_value = "*Not provided*"
                elif isinstance(value, str) and not value.strip():
                    formatted_value = "*Empty*"
                elif isinstance(value, bool):
                    formatted_value = "✅ Yes" if value else "❌ No"
                else:
                    formatted_value = str(value)
                
                markdown += f"**{key}:** {formatted_value}\n\n"
        
        return markdown
    
    elif isinstance(data, list):
        markdown = f"## {title}\n\n" if current_depth == 0 else f"**{title}:**\n\n"
        for i, item in enumerate(data[:10]):  # Limit to first 10 items
            if isinstance(item, dict):
                markdown += json_to_markdown(item, f"Item {i+1}", max_depth, current_depth + 1)
            else:
                markdown += f"{i+1}. {item}\n"
        if len(data) > 10:
            markdown += f"*(and {len(data) - 10} more items)*\n"
        return markdown + "\n"
    
    else:
        return f"## {title}\n\n{data}\n\n"

def display_response_with_copy_buttons(data, data_title="Response Data"):
    """
    Display response data with copy buttons for JSON and markdown text.
    
    Args:
        data: The data to display (dict, list, or any JSON serializable data)
        data_title: Title for the data section
    """
    # Convert to JSON string
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    
    # Convert to markdown
    markdown_str = json_to_markdown(data, data_title)
    
    # Create copy buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Copy as JSON", key=f"copy_json_{hash(json_str)}", help="Copy response as JSON"):
            st.code(json_str, language="json")
            st.success("JSON copied! Use Ctrl+A, Ctrl+C to copy from the code block above.")
    
    with col2:
        if st.button("📄 Copy as Text", key=f"copy_text_{hash(markdown_str)}", help="Copy response as formatted text"):
            st.markdown("**Formatted Text:**")
            st.text_area("Copy this text:", markdown_str, height=200, key=f"text_area_{hash(markdown_str)}")
            st.success("Text ready to copy! Select all and copy from the text area above.")
    
    # Display the formatted markdown
    st.markdown("---")
    st.markdown(markdown_str)
    
    return json_str, markdown_str

# Constants
DEFAULT_TIMEOUT = 300  # 5 minutes
DEFAULT_JSON = {
    "Company Name": "Example Corp",
    "Company Domain": "example.com",
    "Company Employee Count": "250",
    "Company Employee Count Range": "100-500",
    "Company Founded": "2015",
    "Company Industry": "Technology",
    "Company Type": "Private",
    "Company Headquarters": "San Francisco, CA",
    "Company Revenue Range": "$10M-$50M",
    "Company Linkedin Url": "https://linkedin.com/company/example-corp",
    "Company Crunchbase Url": "https://crunchbase.com/organization/example-corp",
    "Company Funding Rounds": "3",
    "Company Last Funding Round Amount": "$5M"
}

def process_enrichment_response(api_response: dict) -> dict:
    """
    Process API response and extract relevant company data from stringified JSON block.

    Args:
        api_response (dict): Raw API response data.

    Returns:
        dict: Processed dictionary with structured company data.
    """
    try:
        # Navigate to messages -> look for stringified JSON in 'message'
        outputs = api_response.get("outputs", [])
        for output in outputs:
            for item in output.get("outputs", []):
                messages = item.get("messages", [])
                for message_item in messages:
                    message_text = message_item.get("message", "")
                    # Try to locate and parse the embedded JSON block
                    if "```json" in message_text:
                        json_block = message_text.split("```json")[1].split("```")[0].strip()
                        company_data = json.loads(json_block)

                        return company_data

        # If no JSON block was found
        return {
            "enrichment_status": "no_company_data_found",
            "error": "No embedded JSON found in messages",
            "raw_response": api_response
        }

    except Exception as e:
        return { 
            "enrichment_status": "processing_error",
            "error": f"Failed to process API response: {str(e)}",
            "raw_response": api_response
        }
    

def show_enrichment_playground():
    """Display the enrichment API playground"""
    st.subheader("🔍 Lead Enrichment API")
    st.markdown("Enrich company data with additional information")
    
    # Initialize API client
    api_client = PlaygroundAPIClient()
    
    # Input section
    st.markdown("### Input Configuration")
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Manual Input", "JSON Input"],
        key="enrichment_input_method"
    )
    
    if input_method == "Manual Input":
        company_name = st.text_input("Company Name", key="enrich_company_name")
        company_domain = st.text_input("Company Domain", key="enrich_company_domain")
        
        # Build input data
        input_data = {
            "Company Name": company_name,
            "Company Domain": company_domain,
        }
        
        # Convert to JSON string for API
        input_json = json.dumps(input_data, indent=2)

        # Show current input only for manual input
        with st.expander("📋 Current Input Data", expanded=False):
            st.code(input_json, language="json")
        
    else:
        # JSON input
        input_json = st.text_area(
            "Enter company data as JSON:",
            height=200,
            placeholder=DEFAULT_JSON,
            value=json.dumps(DEFAULT_JSON, indent=2),
            key="enrichment_json_input"
        )
    
    if st.button("🚀 Enrich Company Data", key="enrichment_api_call", type="primary"):
        if not input_json.strip():
            st.error("Please provide input data")
            return
        
        # Validate JSON format
        try:
            parsed_json = json.loads(input_json)
            
            # Additional validation for JSON input method
            if input_method == "JSON Input":
                # Check if it's a valid object (not array or primitive)
                if not isinstance(parsed_json, dict):
                    st.error("JSON input must be an object (dictionary), not an array or primitive value")
                    return
                
                # Check if it has at least company name or domain
                if not any(key.lower() in ["company name", "name", "company domain", "domain"] for key in parsed_json.keys()):
                    st.warning("For best results, include at least 'Company Name' or 'Company Domain' in your JSON")
                    
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {str(e)}")
            return
        
        # Create placeholder for loading and results
        loading_placeholder = st.empty()
        result_placeholder = st.empty()
        
        # Initialize response variable
        response = None
        
        try:
            # Show loading state
            with loading_placeholder.container():
                st.info("🔄 Enriching company data... This may take a few minutes.")
                st.spinner("Processing...")
            
            # Make API call with custom processing function and default timeout
            response = api_client.make_request(
                "lead-enrichment", 
                input_json, 
                timeout=DEFAULT_TIMEOUT,
                process_fn=process_enrichment_response
            )
            
        except Exception as e:
            # Handle any exceptions during API call
            response = {
                "success": False,
                "error": f"API call failed: {str(e)}"
            }
        finally:
            # Clear loading state
            loading_placeholder.empty()
        
        # Display results in the result placeholder
        with result_placeholder.container():
            st.markdown("### API Response")
            
            if response.get("success", False):
                st.success("✅ API call successful!")
                
                # Show processing error if any
                if "processing_error" in response:
                    st.warning(f"⚠️ Processing error: {response['processing_error']}")
                
                # Display processed data if available
                if "processed_data" in response:
                    st.markdown("#### 📊 Processed Enrichment Data")
                    processed_data = response["processed_data"]
                    
                    # Display full processed data
                    st.json(processed_data)
                else:
                    # Fallback to original content parsing
                    # Extract and display content (will use processed data if available)
                    content = api_client.extract_response_content(response)
                    try:
                        if "```json" in content:
                            json_content = content.split("```json")[1].split("```")[0].strip()
                            parsed_content = json.loads(json_content)
                            st.json(parsed_content)
                        else:
                            st.text_area("Response Content:", content, height=400)
                    except:
                        st.text_area("Response Content:", content, height=400)
                
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
        **Endpoint:** `lead-enrichment`
        
        **Purpose:** Enriches company data with additional information like:
        - Company details and descriptions
        - Industry insights
        - Technology stack
        - Financial information
        - Contact details
        
        **Input Format:** JSON object with company information
        
        **Required Fields:** At minimum, provide Company Name and Domain for best results
        """)
