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
            "tweaks": {
                "GoogleGenerativeAIModel-r4iC7" : {
                    "model_name" : "gemini-2.5-flash"
                }
            }
        }
        
        # Make POST request - you'll need to update this URL with the actual ICP profiling endpoint
        response = requests.post(           
            "https://flow.agenthive.tech/api/v1/run/icp-profiling",
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': os.getenv('AGENT_HIVE_API_KEY', '')
            },
            timeout=360
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

def product_context_reset():
    st.session_state.product_context_input = DEFAULT_PRODUCT_CONTEXT

def target_icp_reset():
    st.session_state.target_icp_input = DEFAULT_TARGET_ICP

def show_icp_profiling():
    """Display the ICP Profiling section"""
    st.header("ICP Profiling")
    st.markdown("Analyze how well your leads fit your Ideal Customer Profile")
    
    # Check if workflow data is available
    metadata = get_workflow_metadata()
    
    # Initialize session state
    if 'product_context' not in st.session_state:
        st.session_state.product_context = DEFAULT_PRODUCT_CONTEXT
    if 'target_icp' not in st.session_state:
        st.session_state.target_icp = DEFAULT_TARGET_ICP

    
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
    
    with st.expander("📊 View Data Preview", expanded=False):
        show_data_preview()
    
    # ICP Configuration Section
    st.markdown("### ⚙️ ICP Configuration")
    
    st.markdown("**Product Context**")
    product_context = st.text_area(
        "Describe your product/service:",
        value=st.session_state.product_context,
        height=300,
        help="Provide details about your product, its features, benefits, and value proposition",
        key="product_context_input"
    )

    # Reset button
    if st.button("🔄 Reset to Default", type="secondary", on_click=product_context_reset, key="product-reset"):
        pass

    st.markdown("**Target ICP**")
    target_icp = st.text_area(
        "Define your Ideal Customer Profile:",
        value=st.session_state.target_icp,
        height=300,
        help="Describe your ideal customer including company size, industry, pain points, and decision makers",
        key="target_icp_input"
    )
    
    if st.button("🔄 Reset to Default", type="secondary", on_click=target_icp_reset, key="icp-reset"):
        pass
    
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
            help="End index is inclusive"
        )
    
    # Show selected range info
    selected_count = end_index - start_index + 1
    st.info(f"📊 Selected range: {start_index} to {end_index} ({selected_count} rows)")
    
    # Check if enriched data exists and ICP analysis status for selected range
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
                if 'icp_analysis' in row_data:
                    already_analyzed_count += 1
                else:
                    missing_analysis_rows.append(i)
    
    # Check for missing enrichment data
    if missing_enrichment_rows:
        if not has_enriched_data:
            st.error("❌ No enriched data found in selected range. Please run Lead Enrichment first.")
            return
        else:
            st.warning(f"⚠️ Some rows ({len(missing_enrichment_rows)}) don't have enriched data. Please run Lead Enrichment first for rows: {', '.join(map(str, missing_enrichment_rows))}")
            return
    
    # Show ICP analysis status
    button_disabled = False
    button_help = None
    
    if already_analyzed_count > 0:
        if already_analyzed_count == selected_count:
            st.success(f"✅ All {selected_count} rows in the selected range already have ICP analysis!")
            button_disabled = True
            button_help = "All selected rows already have ICP analysis"
        else:
            st.warning(f"⚠️ {already_analyzed_count}/{selected_count} rows already have ICP analysis. Will process remaining {len(missing_analysis_rows)} rows.")
            button_help = f"Will analyze {len(missing_analysis_rows)} remaining rows"
    else:
        st.info(f"🔄 {selected_count} rows ready for ICP analysis")
        
    # Validation for inputs
    if not product_context.strip():
        st.error("❌ Product context is required!")
        return
    
    if not target_icp.strip():
        st.error("❌ Target ICP definition is required!")
        return
    
    if st.button(
        "🎯 Start ICP Analysis", 
        type="primary", 
        disabled=selected_count <= 0 or button_disabled,
        help=button_help
    ):
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
        enriched_lead = row_data.get('enriched_lead')
        if not enriched_lead:
            skipped_analyses += 1
            st.session_state.workflow_data["data"][actual_index]['icp_analysis_error'] = "No enriched data available"
            continue
        
        # Check if already analyzed
        if 'icp_analysis' in row_data:
            skipped_analyses += 1
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
            st.session_state.workflow_data["data"][actual_index]['icp_analysis'] = processed_data
            st.session_state.workflow_data["data"][actual_index]['icp_analysis_timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
            # st.session_state.workflow_data["data"][actual_index]['company']['icp_config'] = {
            #     'product_context': product_context,
            #     'target_icp': target_icp
            # }
            successful_analyses += 1
        else:
            # Store error in session state
            st.session_state.workflow_data["data"][actual_index]['icp_analysis_error'] = api_response['error']
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
                        
                        if 'icp_analysis' in row and j == i:  # Only show status for newly processed
                            st.success(f"✅ Row {row_index}: {company_name} - ICP Analysis Complete")
                        elif 'icp_analysis' in row:
                            st.info(f"⏭️ Row {row_index}: {company_name} - Already analyzed (skipped)")
                        elif 'icp_analysis_error' in row and row['icp_analysis_error'] == "No enriched data available":
                            st.warning(f"⏭️ Row {row_index}: {company_name} - Skipped (No enriched data)")
                        else:
                            st.error(f"❌ Row {row_index}: {company_name} - Analysis Failed ({row.get('icp_analysis_error', 'Unknown error')})")
        
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
                    'icp_analysis' in st.session_state.workflow_data["data"][row_index] and
                    'icp_analysis_timestamp' in st.session_state.workflow_data["data"][row_index]):  # Only show newly analyzed
                    
                    company_name = st.session_state.workflow_data["data"][row_index]['company'].get('Company Name', f'Row {row_index}')
                    icp_data = st.session_state.workflow_data["data"][row_index]['icp_analysis']
                    
                    st.markdown(f"**{company_name}:**")
                    if isinstance(icp_data, dict):
                        st.json(icp_data)
                    
                    sample_count += 1
                    if sample_count >= 3:
                        break
    
    if skipped_analyses > 0:
        # Count different skip reasons
        already_analyzed_skipped = 0
        no_enrichment_skipped = 0
        
        for i in range(total_rows):
            row_index = start_index + i
            if row_index < len(st.session_state.workflow_data["data"]):
                row = st.session_state.workflow_data["data"][row_index]
                if 'icp_analysis' in row and 'icp_analysis_timestamp' not in row:
                    already_analyzed_skipped += 1
                elif 'icp_analysis_error' in row and row['icp_analysis_error'] == "No enriched data available":
                    no_enrichment_skipped += 1
        
        skip_message = f"ℹ️ {skipped_analyses} rows were skipped"
        if already_analyzed_skipped > 0:
            skip_message += f" ({already_analyzed_skipped} already analyzed"
        if no_enrichment_skipped > 0:
            if already_analyzed_skipped > 0:
                skip_message += f", {no_enrichment_skipped} missing enrichment data"
            else:
                skip_message += f" ({no_enrichment_skipped} missing enrichment data"
        if already_analyzed_skipped > 0 or no_enrichment_skipped > 0:
            skip_message += ")"
        
        st.info(skip_message)
