"""
ICP Profiling API Playground Module
"""

import streamlit as st
import json
from .base_api_client import PlaygroundAPIClient

# Constants
DEFAULT_TIMEOUT = 180
DEFAULT_JSON =  """{
  "enriched_lead": {
    "Company": "ExampleTech Solutions Pvt Ltd",
    "Overview": "ExampleTech Solutions Pvt Ltd offers IT and business intelligence services, specializing in SQL development, BI dashboards, and enterprise resource planning. Their workforce is proficient in SQL, SSRS, Power BI, and SAP Hana, signaling a strong focus on data infrastructure and analytics solutions.",
    "Size": "51-200 employees",
    "Revenue": "N/A",
    "Domain": "exampletechsolutions.com",
    "Funding Information": "N/A",
    "Latest Funding Round": "N/A",
    "Investors": "N/A",
    "LinkedIn URL": "https://www.linkedin.com/company/exampletech-solutions",
  },
  "domain": "exampletechsolutions.com",
}
"""
FLOW_NAME = "icp-profiling"
TWEAKS = {
    "GoogleGenerativeAIModel-r4iC7" : {
        "model_name" : "gemini-2.5-flash"
    }
}

TO_EXTEND = {
    "product_context": "\n**QpiAI Pro – No‑Code AI + AutoML + MLOps Platform**\n- End‑to‑end visual pipeline builder (data ingestion → annotation → training → deployment → monitoring).\n- Auto‑annotation (up to 700× faster), AutoML hyperparameter tuning, SFT/DPO LLM fine‑tuning.\n- Production‑ready deployments (REST/gRPC), real‑time dashboards, on‑prem/cloud/VPC options.\n\n**Agent Hive – No‑Code Enterprise Agent Orchestration**\n- GUI‑based multi‑agent builder with dynamic memory, RAG, tool integrations, real‑time streams.\n- Domain‑specific and Enterprise-level specialist agents + orchestrator, distributed tracing & monitoring.\n- Integrate your own AI/ML models (CV, NLP, etc.) as tools inside agents — enabling model-to-action orchestration.\n- Quantum-enhanced planning, memory adaptation, human-in-the-loop guardrails, knowledge ingestion from field systems.",
    "target_icp": "\n- Regulated SMBs/enterprises: Healthcare (imaging, triage), Finance/Legal (contracts, document analysis), Retail/E‑commerce, Manufacturing/Industrial, Robotics, Education, Agritech, Smart Cities.\n- Size: 50‑500 employees.\n- Signals:\n  - Manual image/video annotation workflows or in-house dataset creation (↑ Pro fit)\n  - CV/LLM PoCs or research projects with no AutoML, MLOps, or fine-tuning infra (↑ Pro fit)\n  - AI teams manually managing training, tuning, or deployment pipelines (↑ Pro fit)\n  - Vision + Hardware companies doing inspection, maintenance, or robotics (↑ Pro fit)\n  - IT services, analytics firms, or consultancies with vision/AI solution engineers (↑ Pro fit)\n\n  - Rule-based bots, single-task chatbots, or RPA tools with no memory, planning, or context (↑ Hive fit)\n  - Companies using LangChain/CrewAI-like frameworks but lacking production-grade orchestration (↑ Hive fit)\n  - Internal tools or dashboards that *require AI actions* but currently lack automation (↑ Hive fit)\n  - Workflows with multiple steps/roles/systems (e.g., supply chain, compliance, support) that could benefit from intelligent agents (↑ Hive fit)\n  - Organizations already using LLMs or other AI models and now need orchestration, chaining, or tool integration (↑ Hive fit)\n  - Companies building domain-specific copilots (HR assistant, legal AI, SOP navigator, etc.) (↑ Hive fit)"
}

def process_icp_response(api_response: dict) -> dict:
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

def show_icp_profiling_playground():
    """Display the ICP profiling API playground"""
    st.subheader("👥 ICP Profiling API")
    st.markdown("Analyze companies against your Ideal Customer Profile")
    
    # Initialize API client
    api_client = PlaygroundAPIClient()
    
    # Input section
    st.markdown("### Input Configuration")
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Manual Input", "JSON Input"],
        key="icp_input_method"
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
            "Enter company data as JSON:",
            height=400,
            placeholder=DEFAULT_JSON,
            value=DEFAULT_JSON,
            key="icp_json_input"
        )
    
    # Show current input
    with st.expander("📋 Current Input Data", expanded=False):
        st.code(input_json, language="json")
    
    # API call button
    st.markdown("### Make API Call")
    
    if st.button("🎯 Analyze ICP Fit", key="icp_api_call", type="primary"):
        if not input_json.strip():
            st.error("Please provide input data")
            return
        
        # Validate JSON
        try:
            parsed_json = json.loads(input_json)

            parsed_json.update(TO_EXTEND)

            # Additional validation for required fields
            if input_method == "JSON Input":
                required_fields = ["domain", "enriched_lead", "product_context", "target_icp"]
                missing_fields = [field for field in required_fields if not parsed_json.get(field)]
                if missing_fields:
                    st.error(f"Missing required fields: {', '.join(missing_fields)}")
                    return
                input_json = json.dumps(parsed_json)
            
                    
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {str(e)}")
            return
        
        # Make API call with custom processing function and timeout
        with st.spinner("Analyzing ICP fit..."):
            

            response = api_client.make_request(
                FLOW_NAME, 
                input_json,
                tweaks=TWEAKS,
                timeout=DEFAULT_TIMEOUT,
                process_fn=process_icp_response
            )
    
    # Display results
    st.markdown("### API Response")
    
    if 'response' in locals() and response.get("success", False):
            st.success("✅ ICP analysis completed!")
            
            # Show processing error if any
            if "processing_error" in response:
                st.warning(f"⚠️ Processing error: {response['processing_error']}")
            
            # Display processed data if available
            if "processed_data" in response:
                st.markdown("#### 📊 ICP Analysis Results")
                processed_data = response["processed_data"]
                
                # Display key metrics prominently if data is valid
                if isinstance(processed_data, dict) and "icp_status" not in processed_data:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if "icp_score" in processed_data:
                            st.metric("ICP Score", f"{processed_data['icp_score']}/5")
                    
                    with col2:
                        if "product_fit" in processed_data:
                            st.metric("Product Fit", processed_data["product_fit"])
                    
                    with col3:
                        if "prospect_level" in processed_data:
                            st.metric("Prospect Level", processed_data["prospect_level"])
                
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
                        
                        # Display key metrics prominently
                        if isinstance(parsed_content, dict):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if "icp_score" in parsed_content:
                                    st.metric("ICP Score", f"{parsed_content['icp_score']}/5")
                            
                            with col2:
                                if "product_fit" in parsed_content:
                                    st.metric("Product Fit", parsed_content["product_fit"])
                            
                            with col3:
                                if "prospect_level" in parsed_content:
                                    st.metric("Prospect Level", parsed_content["prospect_level"])
                        
                        # Display full JSON
                        st.json(parsed_content)
                    else:
                        st.text_area("Response Content:", content, height=400)
                except Exception as e:
                    st.text_area("Response Content:", content, height=400)
            
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
        **Endpoint:** `icp-profiling`
        
        **Purpose:** Analyzes companies against your Ideal Customer Profile (ICP) to determine:
        - ICP Score (1-10 scale)
        - Product fit assessment
        - Prospect level classification
        - Engagement readiness
        - Detailed justification
        - Potential use cases
        """)
