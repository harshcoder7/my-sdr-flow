import streamlit as st
import requests
import time
import json
from utils.state_manager import (
    get_workflow_data, 
    get_workflow_metadata, 
    show_data_preview,
    get_companies_list,
    get_company_data
)
import os
from dotenv import load_dotenv

load_dotenv()


def make_api_request(row_data: dict) -> dict:
    """
    Make API request to enrich company data
    
    Args:
        row_data (dict): Row data from workflow
        api_endpoint (str): API endpoint URL
    
    Returns:
        dict: API response data
    """
    try:
        # Prepare payload from row data
        company_info = row_data.get('company', {})
        payload = {
           "output_type" : "chat",
           "input_type" : "chat",
           "input_value" : json.dumps(company_info)
        }
        
        # Make POST request
        response = requests.post(           
            "https://flow.agenthive.tech/api/v1/run/lead-enrichment",
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': os.getenv('AGENT_HIVE_API_KEY', '')
            },
            timeout=180
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API request failed with status {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

import json

def process_api_response(api_response: dict) -> dict:
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

def show_lead_enrichment():
    """Display the Lead Enrichment section"""
    st.header("🎯 Lead Enrichment")
    st.markdown("Enrich your leads with additional data and insights")
    
    # Check if workflow data is available
    metadata = get_workflow_metadata()
    
    if not metadata['has_data']:
        st.info("🔄 No workflow data available. Please convert CSV data first in the CSV Converter section.")
        st.markdown("---")
        st.markdown("**What you can do here once you have data:**")
        st.markdown("- ✨ Enrich company information")
        st.markdown("- 📧 Generate personalized email templates") 
        st.markdown("- 🔍 Research prospects")
        st.markdown("- 📊 Analyze lead quality")
        return
    
    # Show data preview
    st.success(f"✅ Workflow data loaded from {metadata['data_source']}")
    show_data_preview()
    
    # Lead enrichment options
    st.markdown("---")
    
    # Batch Processing Section
    st.markdown("### 🚀 Batch API Enrichment")
    
    # Get workflow data directly
    workflow_data = get_workflow_data()
    total_rows = len(workflow_data["data"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_index = st.number_input(
            "Start Index",
            min_value=0,
        )
    
    with col2:
        end_index = st.number_input(
            "End Index",
            min_value=start_index,
            max_value=total_rows - 1,
            value=min(start_index + 4, total_rows - 1),
            help="End index is inclusive"
        )
    
    # Show selected range info
    selected_count = end_index - start_index + 1
    st.info(f"📊 Selected range: {start_index} to {end_index} ({selected_count} rows)")
    
    if st.button("🚀 Start Batch Enrichment", type="primary", disabled=selected_count <= 0):
        batch_enrich_workflow_data(start_index, end_index)
    
    st.markdown("---")

def batch_enrich_workflow_data(start_index: int, end_index: int):
    """
    Process workflow data rows with API enrichment and live progress
    
    Args:
        start_index (int): Starting index
        end_index (int): Ending index (inclusive)
    """
    # Get workflow data from session state
    workflow_data = get_workflow_data()["data"]
    selected_rows = workflow_data[start_index:end_index + 1]
    total_rows = len(selected_rows)
    
    # Create progress containers
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    successful_enrichments = 0
    failed_enrichments = 0
    
    with results_container:
        st.markdown("### 📈 Enrichment Results")
        results_placeholder = st.empty()
    
    for i, row_data in enumerate(selected_rows):
        current_progress = (i + 1) / total_rows
        actual_index = start_index + i
        
        # Update progress
        progress_bar.progress(current_progress)
        company_name = row_data.get('company', {}).get('Company Name', f'Row {actual_index}')
        status_text.text(f"Processing {i + 1}/{total_rows}: {company_name}")
        
        # Make API request
        api_response = make_api_request(row_data)
        
        if "error" not in api_response:
            # Process API response and store processed data in session state
            processed_data = process_api_response(api_response)
            st.session_state.workflow_data["data"][actual_index]['company']['enriched_lead'] = processed_data
            st.session_state.workflow_data["data"][actual_index]['company']['enrichment_timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
            successful_enrichments += 1
        else:
            # Store error in session state
            st.session_state.workflow_data["data"][actual_index]['company']['api_enrichment_error'] = api_response['error']
            failed_enrichments += 1
        
        # Update results display every few iterations or on completion
        if (i + 1) % 5 == 0 or i == total_rows - 1:
            with results_placeholder.container():
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("✅ Successful", successful_enrichments)
                
                with col2:
                    st.metric("❌ Failed", failed_enrichments)
                
                with col3:
                    st.metric("📊 Progress", f"{i + 1}/{total_rows}")
                
                # Show recent results
                if i >= 0:  # Show last few processed rows
                    st.markdown("**Recent Processing:**")
                    start_display = max(0, i - 2)
                    for j in range(start_display, i + 1):
                        row_index = start_index + j
                        row = st.session_state.workflow_data["data"][row_index]
                        company_name = row.get('company', {}).get('Company Name', f'Row {row_index}')
                        
                        if 'enriched_lead' in row.get('company', {}):
                            st.success(f"✅ Row {row_index}: {company_name} - Enriched")
                        else:
                            st.error(f"❌ Row {row_index}: {company_name} - Failed")
        
        # Small delay to show progress (remove in production)
        time.sleep(0.1)
    
    # Final completion message
    status_text.text(f"✅ Batch enrichment completed! {successful_enrichments} successful, {failed_enrichments} failed")
    
    if successful_enrichments > 0:
        st.success(f"🎉 Successfully enriched {successful_enrichments} rows!")
        
        # Show sample of enriched data
        with st.expander("View Sample Enriched Data"):
            for i in range(min(3, successful_enrichments)):
                row_index = start_index + i
                if 'api_enrichment' in st.session_state.workflow_data["data"][row_index].get('company', {}):
                    company_name = st.session_state.workflow_data["data"][row_index]['company'].get('Company Name', f'Row {row_index}')
                    enrichment_data = st.session_state.workflow_data["data"][row_index]['company']['api_enrichment']
                    st.markdown(f"**{company_name}:**")
                    st.json(enrichment_data)

    st.write(get_workflow_data()["data"])
