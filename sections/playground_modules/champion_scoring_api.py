"""
Champion Scoring API Playground Module
"""

import streamlit as st
import json
from .base_api_client import PlaygroundAPIClient

# Constants
DEFAULT_TIMEOUT = 180  # 3 minutes
DEFAULT_JSON = {
  "linkedin_url": "https://www.linkedin.com/in/sampleexecutive/",
  "icp_result": {
    "product_fit": "Both",
    "icp_score": 3,
    "prospect_level": "Low",
    "engagement_readiness": "Cold",
    "justification": "MegaCorp Inc., being a large multinational with over 300,000 employees, does not fit the target ICP of 50–500 employees. They possess extensive AI infrastructure, including in-house platforms for automation and analytics. While QpiAI Pro could still add value by accelerating their AutoML and MLOps workflows, and Agent Hive could assist with advanced orchestration, their internal AI maturity suggests that they may not have an urgent need for external platforms.",
    "use_cases": [
      "QpiAI Pro can support MegaCorp Inc.'s AI initiatives by providing visual AutoML workflows and faster deployment pipelines, helping internal data science teams accelerate project delivery.",
      "Agent Hive can augment MegaCorp Inc.'s enterprise automation suite with multi-agent orchestration, enhancing their existing RPA or chatbot infrastructure by adding memory, planning, and tool integration capabilities."
    ]
  }
}
FLOW_NAME = "champion-scoring"
TWEAKS = {
    "GoogleGenerativeAIModel-hc9sp" : {
        "model": "gemini-2.5-flash",
    }
}

def extract_champion_score_result(response: dict) -> dict:
    """
    Extract champion scoring result (as JSON) from nested API response.

    Args:
        response (dict): Full API response containing stringified JSON in a markdown-like block.

    Returns:
        dict: Extracted champion score data or error info.
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
                        json_block = message_text.split("```json")[1].split("```")[0].strip()
                        return json.loads(json_block)
        
        # If we reach here, no embedded JSON was found
        return {
            "status": "no_champion_data_found",
            "error": "Could not locate embedded JSON in message blocks.",
            "session_id": response.get("session_id")
        }

    except Exception as e:
        return {
            "status": "extraction_error",
            "error": str(e),
            "session_id": response.get("session_id"),
            "raw_response_excerpt": str(response)[:1000]  # limit large output
        }

def show_champion_scoring_playground():
    """Display the champion scoring API playground"""
    st.subheader("🏆 Champion Scoring API")
    st.markdown("Score and identify potential champions within target accounts")
    
    # Initialize API client
    api_client = PlaygroundAPIClient()
    
    # Input section
    st.markdown("### Input Configuration")
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Manual Input", "JSON Input"],
        key="champion_input_method"
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
            "Enter champion scoring data as JSON:",
            height=400,
            placeholder=DEFAULT_JSON,
            value= json.dumps(DEFAULT_JSON, indent=2),
            key="champion_json_input"
        )
    
    # Show current input
    with st.expander("📋 Current Input Data", expanded=False):
        st.code(input_json, language="json")
    
    # API call button
    st.markdown("### Make API Call")
    
    if st.button("🎯 Calculate Champion Score", key="champion_api_call", type="primary"):
        if not input_json.strip():
            st.error("Please provide input data")
            return
        
        # Validate JSON
        try:
            parsed_json = json.loads(input_json)
            
            # Additional validation for required fields
            if input_method == "JSON Input":
                required_fields = ["linkedin_url", "icp_result"]
                missing_fields = [field for field in required_fields if not parsed_json.get(field)]
                if missing_fields:
                    st.error(f"Missing required fields: {', '.join(missing_fields)}")
                    return
                    
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {str(e)}")
            return
        
        # Make API call
        with st.spinner("Calculating champion score..."):
            response = api_client.make_request(FLOW_NAME, input_json, tweaks=TWEAKS, timeout=DEFAULT_TIMEOUT, process_fn=extract_champion_score_result)

        # Display results
        st.markdown("### API Response")
        
        if response.get("success", False):
            st.success("✅ Champion scoring completed!")

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
                        st.text_area("Response Content:", content, height=400)
                except Exception as e:
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
        **Endpoint:** `champion-scoring`
        
        **Purpose:** Scores potential champions within target accounts based on their linkedin profile and company's ICP analysis result.
        """)
