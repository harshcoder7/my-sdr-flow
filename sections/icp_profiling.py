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

# Default values for product context and target ICP
DEFAULT_PRODUCT_CONTEXT = """
**QpiAI Pro – No‑Code AI + AutoML + MLOps Platform**
- End‑to‑end visual pipeline builder (data ingestion → annotation → training → deployment → monitoring).
- Auto‑annotation (up to 700× faster), AutoML hyperparameter tuning, SFT/DPO LLM fine‑tuning.
- Production‑ready deployments (REST/gRPC), real‑time dashboards, on‑prem/cloud/VPC options.

**Agent Hive – No‑Code Enterprise Agent Orchestration**
- GUI‑based multi‑agent builder with dynamic memory, RAG, tool integrations, real‑time streams.
- Domain‑specific and Enterprise-level specialist agents + orchestrator, distributed tracing & monitoring.
- Integrate your own AI/ML models (CV, NLP, etc.) as tools inside agents — enabling model-to-action orchestration.
- Quantum-enhanced planning, memory adaptation, human-in-the-loop guardrails, knowledge ingestion from field systems.
"""

DEFAULT_TARGET_ICP = """
- Regulated SMBs/enterprises: Healthcare (imaging, triage), Finance/Legal (contracts, document analysis), Retail/E‑commerce, Manufacturing/Industrial, Robotics, Education, Agritech, Smart Cities.
- Size: 50–500 employees.
- Signals:
  - Manual image/video annotation workflows or in-house dataset creation (↑ Pro fit)
  - CV/LLM PoCs or research projects with no AutoML, MLOps, or fine-tuning infra (↑ Pro fit)
  - AI teams manually managing training, tuning, or deployment pipelines (↑ Pro fit)
  - Vision + Hardware companies doing inspection, maintenance, or robotics (↑ Pro fit)
  - IT services, analytics firms, or consultancies with vision/AI solution engineers (↑ Pro fit)

  - Rule-based bots, single-task chatbots, or RPA tools with no memory, planning, or context (↑ Hive fit)
  - Companies using LangChain/CrewAI-like frameworks but lacking production-grade orchestration (↑ Hive fit)
  - Internal tools or dashboards that *require AI actions* but currently lack automation (↑ Hive fit)
  - Workflows with multiple steps/roles/systems (e.g., supply chain, compliance, support) that could benefit from intelligent agents (↑ Hive fit)
  - Organizations already using LLMs other AI models and now need orchestration, chaining, or tool integration (↑ Hive fit)
  - Companies building domain-specific copilots (HR assistant, legal AI, SOP navigator, etc.) (↑ Hive fit)
"""


def make_icp_api_request(enriched_lead: dict, domain: str, product_context: str, target_icp: str) -> dict:
    """
    Make API request for ICP profiling
    
    Args:
        enriched_lead (dict): Enriched lead data
        domain (str): Company domain
        product_context (str): Product context from user
        target_icp (str): Target ICP from user
    
    Returns:
        dict: API response data
    """
    try:
        # Prepare the data payload
        data = {
            "enriched_lead": enriched_lead,
            "domain": domain,
            "product_context": product_context,
            "target_icp": target_icp
        }
        
        # Request payload configuration
        payload = {
            "output_type": "chat",
            "input_type": "chat",
            "input_value": json.dumps(data),
        }
        
        # Make POST request - you'll need to update this URL with the actual ICP profiling endpoint
        response = requests.post(           
            "https://flow.agenthive.tech/api/v1/run/icp-profiling",  # Update this URL
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


def process_icp_api_response(api_response: dict) -> dict:
    """
    Extract structured ICP-related data from a stringified JSON block in the API response.

    Args:
        api_response (dict): Raw API response data.

    Returns:
        dict: Dictionary with extracted ICP results or error details.
    """
    try:
        outputs = api_response.get("outputs", [])
        for output in outputs:
            output_items = output.get("outputs", [])
            for item in output_items:
                # Try all levels where messages might appear
                messages = item.get("messages", []) or item.get("outputs", {}).get("messages", [])
                for message_item in messages:
                    message_text = message_item.get("message", "")
                    if "```json" in message_text:
                        try:
                            json_block = message_text.split("```json")[1].split("```")[0].strip()
                            icp_data = json.loads(json_block)
                            return icp_data
                        except json.JSONDecodeError as json_err:
                            return {
                                "icp_status": "json_parse_error",
                                "error": f"Could not parse JSON block: {str(json_err)}",
                                "raw_message": message_text
                            }

        # Fallback if no JSON block found in expected structure
        return {
            "icp_status": "no_icp_data_found",
            "error": "No embedded JSON found in messages",
            "raw_response": api_response
        }

    except Exception as e:
        return {
            "enrichment_status": "processing_error",
            "error": f"Failed to process API response: {str(e)}",
            "raw_response": api_response
        }


def show_icp_profiling():
    """Display the ICP Profiling section"""
    st.header("🎯 ICP Profiling")
    st.markdown("Analyze how well your leads fit your Ideal Customer Profile")
    
    # Check if workflow data is available
    metadata = get_workflow_metadata()
    
    if not metadata['has_data']:
        st.info("🔄 No workflow data available. Please convert CSV data first in the CSV Converter section.")
        st.markdown("---")
        st.markdown("**What you can do here once you have data:**")
        st.markdown("- 🎯 Analyze lead fit against your ICP")
        st.markdown("- 📊 Score companies based on ICP criteria") 
        st.markdown("- 🔍 Identify high-potential prospects")
        st.markdown("- 📈 Prioritize outreach efforts")
        return
    
    # Show data preview
    st.success(f"✅ Workflow data loaded from {metadata['data_source']}")
    show_data_preview()
    
    # ICP Configuration Section
    st.markdown("---")
    st.markdown("### ⚙️ ICP Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Product Context**")
        product_context = st.text_area(
            "Describe your product/service:",
            value=DEFAULT_PRODUCT_CONTEXT,
            height=200,
            help="Provide details about your product, its features, benefits, and value proposition"
        )
    
    with col2:
        st.markdown("**Target ICP**")
        target_icp = st.text_area(
            "Define your Ideal Customer Profile:",
            value=DEFAULT_TARGET_ICP,
            height=200,
            help="Describe your ideal customer including company size, industry, pain points, and decision makers"
        )
    
    # Batch Processing Section
    st.markdown("---")
    st.markdown("### 🚀 Batch ICP Analysis")
    
    # Get workflow data directly
    workflow_data = get_workflow_data()
    total_rows = len(workflow_data["data"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_index = st.number_input(
            "Start Index",
            min_value=0,
            max_value=total_rows - 1,
            value=0
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
    
    # Check if enriched data exists for selected range
    has_enriched_data = False
    missing_enrichment_rows = []
    
    for i in range(start_index, end_index + 1):
        if i < total_rows:
            row_data = workflow_data["data"][i]
            if 'enriched_lead' not in row_data.get('company', {}):
                missing_enrichment_rows.append(i)
            else:
                has_enriched_data = True
    
    if missing_enrichment_rows:
        
        if not has_enriched_data:
            st.error("❌ No enriched data found in selected range. Please run Lead Enrichment first.")
            return
        else:
            st.warning(f"⚠️ Some rows ({len(missing_enrichment_rows)}) don't have enriched data. Please run Lead Enrichment first for rows: {', '.join(map(str, missing_enrichment_rows))}")
            return
        
    # Validation for inputs
    if not product_context.strip():
        st.error("❌ Product context is required!")
        return
    
    if not target_icp.strip():
        st.error("❌ Target ICP definition is required!")
        return
    
    if st.button("🎯 Start ICP Analysis", type="primary", disabled=selected_count <= 0):
        batch_icp_analysis(start_index, end_index, product_context, target_icp)
    
    st.markdown("---")


def batch_icp_analysis(start_index: int, end_index: int, product_context: str, target_icp: str):
    """
    Process workflow data rows with ICP analysis and live progress
    
    Args:
        start_index (int): Starting index
        end_index (int): Ending index (inclusive)
        product_context (str): Product context for analysis
        target_icp (str): Target ICP definition
    """
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
        st.markdown("### 📈 ICP Analysis Results")
        results_placeholder = st.empty()
    
    for i, row_data in enumerate(selected_rows):
        current_progress = (i + 1) / total_rows
        actual_index = start_index + i
        
        # Update progress
        progress_bar.progress(current_progress)
        company_name = row_data.get('company', {}).get('Company Name', f'Row {actual_index}')
        status_text.text(f"Analyzing {i + 1}/{total_rows}: {company_name}")
        
        # Check if row has enriched data
        enriched_lead = row_data.get('company', {}).get('enriched_lead')
        if not enriched_lead:
            skipped_analyses += 1
            st.session_state.workflow_data["data"][actual_index]['company']['icp_analysis_error'] = "No enriched data available"
            continue
        
        # Get domain from company data
        domain = (row_data.get('company', {}).get('Company Domain') or 
                 row_data.get('company', {}).get('Company Website') or
                 enriched_lead.get('Domain', ''))
        
        # Make ICP API request
        api_response = make_icp_api_request(enriched_lead, domain, product_context, target_icp)
        
        if "error" not in api_response:
            # Process API response and store processed data in session state
            processed_data = process_icp_api_response(api_response)
            st.session_state.workflow_data["data"][actual_index]['company']['icp_analysis'] = processed_data
            st.session_state.workflow_data["data"][actual_index]['company']['icp_analysis_timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
            # st.session_state.workflow_data["data"][actual_index]['company']['icp_config'] = {
            #     'product_context': product_context,
            #     'target_icp': target_icp
            # }
            successful_analyses += 1
        else:
            # Store error in session state
            st.session_state.workflow_data["data"][actual_index]['company']['icp_analysis_error'] = api_response['error']
            failed_analyses += 1
        
        # Update results display every few iterations or on completion
        if (i + 1) % 3 == 0 or i == total_rows - 1:
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
                        
                        if 'icp_analysis' in row.get('company', {}):
                            st.success(f"✅ Row {row_index}: {company_name} - ICP Analysis Complete")
                        elif 'icp_analysis_error' in row.get('company', {}) and row['company']['icp_analysis_error'] == "No enriched data available":
                            st.warning(f"⏭️ Row {row_index}: {company_name} - Skipped (No enriched data)")
                        else:
                            st.error(f"❌ Row {row_index}: {company_name} - Analysis Failed")
        
        # Small delay to show progress
        time.sleep(0.1)
    
    # Final completion message
    status_text.text(f"✅ ICP analysis completed! {successful_analyses} successful, {failed_analyses} failed, {skipped_analyses} skipped")
    
    if successful_analyses > 0:
        st.success(f"🎉 Successfully analyzed {successful_analyses} companies against your ICP!")
        
        # Show sample of ICP analysis data
        with st.expander("View Sample ICP Analysis Results"):
            sample_count = 0
            for i in range(total_rows):
                row_index = start_index + i
                if (row_index < len(st.session_state.workflow_data["data"]) and 
                    'icp_analysis' in st.session_state.workflow_data["data"][row_index].get('company', {})):
                    
                    company_name = st.session_state.workflow_data["data"][row_index]['company'].get('Company Name', f'Row {row_index}')
                    icp_data = st.session_state.workflow_data["data"][row_index]['company']['icp_analysis']
                    
                    st.markdown(f"**{company_name}:**")
                    if isinstance(icp_data, dict) and 'analysis_type' in icp_data and icp_data['analysis_type'] == 'text_response':
                        st.markdown(icp_data.get('icp_analysis', 'No analysis available'))
                    else:
                        st.json(icp_data)
                    
                    sample_count += 1
                    if sample_count >= 3:
                        break
    
    if skipped_analyses > 0:
        st.warning(f"⚠️ {skipped_analyses} rows were skipped due to missing enriched data. Run Lead Enrichment first for those rows.")
