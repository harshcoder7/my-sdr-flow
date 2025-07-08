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
    st.header("Lead Enrichment")
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
    
    with st.expander("📊 View Data Preview", expanded=False):
        show_data_preview()
             
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
            help="End index is inclusive"
        )
    
    # Show selected range info
    selected_count = end_index - start_index + 1
    st.info(f"📊 Selected range: {start_index} to {end_index} ({selected_count} rows)")
    
    # Check if selected rows are already enriched
    already_enriched_count = 0
    missing_enrichment_rows = []
    
    for i in range(start_index, end_index + 1):
        if i < total_rows:
            row_data = workflow_data["data"][i]
            if 'enriched_lead' in row_data:
                already_enriched_count += 1
            else:
                missing_enrichment_rows.append(i)
    
    # Show enrichment status
    if already_enriched_count > 0:
        if already_enriched_count == selected_count:
            st.success(f"✅ All {selected_count} rows in the selected range are already enriched!")
            button_disabled = True
            button_help = "All selected rows are already enriched"
        else:
            st.warning(f"⚠️ {already_enriched_count}/{selected_count} rows are already enriched. Will process remaining {len(missing_enrichment_rows)} rows.")
            button_disabled = False
            button_help = f"Will enrich {len(missing_enrichment_rows)} remaining rows"
    else:
        st.info(f"🔄 {selected_count} rows ready for enrichment")
        button_disabled = False
        button_help = None
    
    if st.button(
        "🚀 Start Batch Enrichment", 
        type="primary", 
        disabled=selected_count <= 0 or button_disabled,
        help=button_help
    ):
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
    skipped_enrichments = 0
    
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
        
        # Check if already enriched
        if 'enriched_lead' in row_data:
            skipped_enrichments += 1
            continue
        
        # Make API request
        api_response = make_api_request(row_data)
        
        if "error" not in api_response:
            # Process API response and store processed data in session state
            processed_data = process_api_response(api_response)
            st.session_state.workflow_data["data"][actual_index]['enriched_lead'] = processed_data
            st.session_state.workflow_data["data"][actual_index]['enrichment_timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
            successful_enrichments += 1
        else:
            # Store error in session state
            st.session_state.workflow_data["data"][actual_index]['api_enrichment_error'] = api_response['error']
            failed_enrichments += 1
        
        # Update results display every few iterations or on completion
        if (i + 1) % 5 == 0 or i == total_rows - 1:
            with results_placeholder.container():
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("✅ Successful", successful_enrichments)
                
                with col2:
                    st.metric("❌ Failed", failed_enrichments)
                
                with col3:
                    st.metric("⏭️ Skipped", skipped_enrichments)
                
                with col4:
                    st.metric("📊 Progress", f"{i + 1}/{total_rows}")
                
                # Show recent results
                if i >= 0:  # Show last few processed rows
                    st.markdown("**Recent Processing:**")
                    start_display = max(0, i - 2)
                    for j in range(start_display, i + 1):
                        row_index = start_index + j
                        row = st.session_state.workflow_data["data"][row_index]
                        company_name = row.get('company', {}).get('Company Name', f'Row {row_index}')
                        
                        if 'enriched_lead' in row and j == i:  # Only show status for newly processed
                            st.success(f"✅ Row {row_index}: {company_name} - Enriched")
                        elif 'enriched_lead' in row:
                            st.info(f"⏭️ Row {row_index}: {company_name} - Already enriched (skipped)")
                        elif 'api_enrichment_error' in row:
                            st.error(f"❌ Row {row_index}: {company_name} - Failed")
        
        # # Small delay to show progress (remove in production)
        # time.sleep(0.1)
    
    # Final completion message
    status_text.text(f"✅ Batch enrichment completed! {successful_enrichments} successful, {failed_enrichments} failed, {skipped_enrichments} skipped")
    
    if successful_enrichments > 0:
        st.success(f"🎉 Successfully enriched {successful_enrichments} rows!")
        
        # Show sample of enriched data
        with st.expander("View Sample Enriched Data"):
            sample_count = 0
            for i in range(total_rows):
                row_index = start_index + i
                if (row_index < len(st.session_state.workflow_data["data"]) and 
                    'enriched_lead' in st.session_state.workflow_data["data"][row_index] and
                    'enrichment_timestamp' in st.session_state.workflow_data["data"][row_index]):  # Only show newly enriched
                    
                    enrichment_data = st.session_state.workflow_data["data"][row_index]['enriched_lead']
                    company_name = enrichment_data.get('Company', f'Row {row_index}')
                    st.markdown(f"**{company_name}:**")
                    st.json(enrichment_data)
                    
                    sample_count += 1
                    if sample_count >= 3:
                        break
    
    if skipped_enrichments > 0:
        st.info(f"ℹ️ {skipped_enrichments} rows were skipped as they were already enriched.")
