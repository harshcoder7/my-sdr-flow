import streamlit as st
import requests
import time
import json
from utils.state_manager import (
    get_workflow_data, 
    get_workflow_metadata, 
    show_data_preview,
    get_companies_list,
    get_company_data,
    update_workflow_metadata
)
import os
from dotenv import load_dotenv

load_dotenv()


def make_api_request(row_data: dict) -> dict:
    """
    Make API request to get market intelligence and engagement signals
    
    Args:
        row_data (dict): Row data from workflow (must include enriched_lead)
    
    Returns:
        dict: API response data
    """
    try:
        # Check if enriched lead data exists
        enriched_lead = row_data.get('enriched_lead')
        if not enriched_lead:
            return {"error": "No enriched lead data available"}
        
        # make a copy and remove sources from enriched_lead before sending to API
        enriched_lead = enriched_lead.copy()
        if 'Sources' in enriched_lead:
            enriched_lead.pop('Sources', None)
        
        payload = {
           "output_type" : "chat",
           "input_type" : "chat",
           "input_value" : json.dumps(enriched_lead)
        }
        
        # Make POST request
        response = requests.post(           
            "https://flow.agenthive.tech/api/v1/run/market-intelligence",
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

def show_market_intelligence():
    """Display the Market Intelligence section"""
    st.header("Market Intelligence & Engagement Signals")
    st.markdown("Analyze market trends and engagement opportunities for your leads")
    
    # Check if workflow data is available
    metadata = get_workflow_metadata()
    
    if not metadata['has_data']:
        st.info("🔄 No workflow data available. Please convert CSV data first in the CSV Converter section.")
        return
    
    # Show data preview
    st.success(f"✅ Workflow data loaded from {metadata['data_source']}")
    
    with st.expander("📊 View Saved Data Preview", expanded=False):
        show_data_preview()
             
    # Batch Processing Section
    st.markdown("### 🚀 Batch Market Intelligence Analysis")
    
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
    
    # Check if selected rows already have market intelligence and enriched data
    has_enriched_data = False
    missing_enrichment_rows = []
    already_analyzed_count = 0
    missing_analysis_rows = []
    
    for i in range(start_index, end_index + 1):
        if i < total_rows:
            row_data = workflow_data["data"][i]
            if 'enriched_lead' not in row_data:
                missing_enrichment_rows.append(i)
            else:
                has_enriched_data = True
                if 'market_intelligence' in row_data:
                    already_analyzed_count += 1
                else:
                    missing_analysis_rows.append(i)
    
    # Check for missing enrichment data
    if selected_count <= 0:
        button_disabled = True
        button_help = "Please select a valid range"
    elif missing_enrichment_rows:
        if not has_enriched_data:
            st.error("❌ No enriched data found in selected range. Please run Lead Enrichment first.")
            button_disabled = True
            button_help = "Missing enriched lead data for all selected rows"
        else:
            st.warning(f"⚠️ Some rows ({len(missing_enrichment_rows)}) don't have enriched data. Please run Lead Enrichment first for rows: {', '.join(map(str, missing_enrichment_rows))}")
            button_disabled = True
            button_help = f"Missing enriched lead data for rows: {', '.join(map(str, missing_enrichment_rows))}"
    else:
        # Show analysis status
        if already_analyzed_count > 0:
            if already_analyzed_count == selected_count:
                st.success(f"✅ All {selected_count} rows in the selected range already have market intelligence!")
                button_disabled = True
                button_help = "All selected rows already have market intelligence"
            else:
                st.warning(f"⚠️ {already_analyzed_count}/{selected_count} rows already have market intelligence. Will process remaining {len(missing_analysis_rows)} rows.")
                button_disabled = False
                button_help = f"Will analyze {len(missing_analysis_rows)} remaining rows"
        else:
            st.info(f"🔄 {selected_count} rows ready for market intelligence analysis")
            button_disabled = False
            button_help = None
    
    if st.button(
        "🚀 Start Market Intelligence Analysis", 
        type="primary", 
        disabled=button_disabled,
        help=button_help
    ):
        # Only proceed if we have enriched data for all selected rows
        if not missing_enrichment_rows:
            batch_analyze_market_intelligence(start_index, end_index)
    
    st.markdown("---")

def batch_analyze_market_intelligence(start_index: int, end_index: int):
    """
    Process workflow data rows with market intelligence analysis and live progress
    
    Args:
        start_index (int): Starting index
        end_index (int): Ending index (inclusive)
    """
    # Record batch start time for filtering newly processed data
    batch_start_time = time.time()
    
    # Get workflow data from session state
    workflow_data = get_workflow_data()["data"]
    selected_rows = workflow_data[start_index:end_index + 1]
    total_rows = len(selected_rows)
    
    # Create progress containers
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    successful_analyses = 0
    failed_analyses = 0
    skipped_analyses = 0
    
    with results_container:
        st.markdown("### 📈 Market Intelligence Analysis Results")
        results_placeholder = st.empty()
    
    for i, row_data in enumerate(selected_rows):
        current_progress = (i + 1) / total_rows
        actual_index = start_index + i
        
        # Update progress
        progress_bar.progress(current_progress)
        company_name = row_data.get('company', {}).get('Company Name', f'Row {actual_index}')
        status_text.text(f"Analyzing {i + 1}/{total_rows}: {company_name}")
        
        # Check if row has enriched data
        enriched_lead = row_data.get('enriched_lead')
        if not enriched_lead:
            skipped_analyses += 1
            st.session_state.workflow_data["data"][actual_index]['market_intelligence_error'] = "No enriched data available"
            continue
        
        # Check if already analyzed
        if 'market_intelligence' in row_data:
            skipped_analyses += 1
            continue
        
        # Make API request
        api_response = make_api_request(row_data)
        
        if "error" not in api_response:
            # Process API response and store processed data in session state
            processed_data = process_api_response(api_response)
            st.session_state.workflow_data["data"][actual_index]['market_intelligence'] = processed_data
            st.session_state.workflow_data["data"][actual_index]['intelligence_timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.workflow_data["data"][actual_index]['intelligence_timestamp_numeric'] = time.time()
            successful_analyses += 1
        else:
            # Store error in session state
            st.session_state.workflow_data["data"][actual_index]['market_intelligence_error'] = api_response['error']
            failed_analyses += 1
        
        # Update results display every few iterations or on completion
        if (i + 1) % 5 == 0 or i == total_rows - 1:
            with results_placeholder.container():
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("✅ Successful", successful_analyses)
                
                with col2:
                    st.metric("❌ Failed", failed_analyses)
                
                with col3:
                    st.metric("⏭️ Skipped", skipped_analyses)
                
                with col4:
                    st.metric("📊 Progress", f"{i + 1}/{total_rows}")
                
                # Show recent results
                if i >= 0:  # Show last few processed rows
                    st.markdown("**Recent Analysis:**")
                    start_display = max(0, i - 2)
                    for j in range(start_display, i + 1):
                        row_index = start_index + j
                        row = st.session_state.workflow_data["data"][row_index]
                        company_name = row.get('company', {}).get('Company Name', f'Row {row_index}')
                        
                        # Check if row was analyzed in this batch using timestamp
                        is_newly_analyzed = (
                            'market_intelligence' in row and 
                            'intelligence_timestamp_numeric' in row and 
                            row['intelligence_timestamp_numeric'] > batch_start_time
                        )
                        
                        if is_newly_analyzed:
                            st.success(f"✅ Row {row_index}: {company_name} - Analysis complete")
                        elif 'market_intelligence' in row:
                            st.info(f"⏭️ Row {row_index}: {company_name} - Already analyzed (skipped)")
                        elif 'market_intelligence_error' in row:
                            st.error(f"❌ Row {row_index}: {company_name} - Analysis failed")
    
    # Final completion message
    status_text.text(f"✅ Market intelligence analysis completed! {successful_analyses} successful, {failed_analyses} failed, {skipped_analyses} skipped")
    
    # Update metadata counters
    # update_workflow_metadata()
    
    if successful_analyses > 0:
        st.success(f"🎉 Successfully analyzed {successful_analyses} rows!")
        
        # Show sample of analyzed data
        with st.expander("View Sample Market Intelligence Data"):
            sample_count = 0
            for i in range(total_rows):
                row_index = start_index + i
                if (row_index < len(st.session_state.workflow_data["data"]) and 
                    'market_intelligence' in st.session_state.workflow_data["data"][row_index] and
                    'intelligence_timestamp_numeric' in st.session_state.workflow_data["data"][row_index] and
                    st.session_state.workflow_data["data"][row_index]['intelligence_timestamp_numeric'] > batch_start_time):  # Only show newly analyzed
                    
                    intelligence_data = st.session_state.workflow_data["data"][row_index]['market_intelligence']
                    company_name = intelligence_data.get('Company', row_data.get('company', {}).get('Company Name', f'Row {row_index}'))
                    st.markdown(f"**{company_name}:**")
                    st.json(intelligence_data)
                    
                    sample_count += 1
                    if sample_count >= 3:
                        break
    
    if skipped_analyses > 0:
        st.info(f"ℹ️ {skipped_analyses} rows were skipped as they already had market intelligence analysis.")
