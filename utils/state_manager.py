"""
State management for SDR Agent application
Handles workflow data storage and access across sections
"""

import streamlit as st
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

def initialize_state():
    """Initialize the application state variables"""
    if 'workflow_data' not in st.session_state:
        st.session_state.workflow_data = {}
    
    if 'workflow_metadata' not in st.session_state:
        st.session_state.workflow_metadata = {
            'last_saved': None,
            'data_source': None,
            'total_companies': 0,
            'total_records': 0,
            'has_data': False
        }

def save_workflow_data(data: List[Dict], source: str = "CSV Converter") -> bool:
    """
    Save converted JSON data to workflow state
    
    Args:
        data: The converted JSON data (list of company/people objects)
        source: The source section that generated the data
    
    Returns:
        bool: True if save was successful
    """
    try:
        # Store the data
        st.session_state.workflow_data = {
            'data': data,
            'source': source,
            'saved_at': datetime.now().isoformat()
        }
        
        # Update metadata
        total_companies = len(data)
        total_records = sum(len(company.get('people', [])) for company in data)
        
        st.session_state.workflow_metadata = {
            'last_saved': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_source': source,
            'total_companies': total_companies,
            'total_records': total_records,
            'has_data': True
        }
        
        return True
    except Exception as e:
        st.error(f"Error saving workflow data: {str(e)}")
        return False

def get_workflow_data() -> Optional[Dict]:
    """
    Get the current workflow data
    
    Returns:
        Dict or None: The workflow data if available
    """
    return st.session_state.workflow_data if st.session_state.workflow_data else None

def get_workflow_metadata() -> Dict:
    """
    Get workflow metadata
    
    Returns:
        Dict: Metadata about the current workflow
    """
    return st.session_state.workflow_metadata

def clear_workflow_data():
    """Clear all workflow data"""
    st.session_state.workflow_data = {}
    st.session_state.workflow_metadata = {
        'last_saved': None,
        'data_source': None,
        'total_companies': 0,
        'total_records': 0,
        'has_data': False
    }

def export_workflow_data() -> Optional[str]:
    """
    Export workflow data as JSON string
    
    Returns:
        str or None: JSON string of the data if available
    """
    if not st.session_state.workflow_data:
        return None
    
    try:
        return json.dumps(st.session_state.workflow_data['data'], indent=2)
    except Exception as e:
        st.error(f"Error exporting data: {str(e)}")
        return None

def show_workflow_status():
    """Display workflow status in sidebar"""
    st.sidebar.subheader("🔄 Data Status")
    
    metadata = get_workflow_metadata()
    
    if metadata['has_data']:
        st.sidebar.success("✅ Data loaded")
        st.sidebar.markdown(f"**Source:** {metadata['data_source']}")
        st.sidebar.markdown(f"**Companies:** {metadata['total_companies']}")
        st.sidebar.markdown(f"**Records:** {metadata['total_records']}")
        st.sidebar.markdown(f"**Last saved:** {metadata['last_saved']}")
        
        # Export button
        if st.sidebar.button("💾 Export Data", key="export_workflow"):
            json_data = export_workflow_data()
            if json_data:
                st.sidebar.download_button(
                    label="⬇️ Download JSON",
                    data=json_data,
                    file_name=f"workflow_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key="download_workflow"
                )
        
        # Clear data button
        if st.sidebar.button("🗑️ Clear Data", key="clear_workflow"):
            clear_workflow_data()
            st.sidebar.success("Data cleared!")
    else:
        st.sidebar.info("No data saved yet")

def show_data_preview():
    """Show a preview of the saved workflow data"""
    data = get_workflow_data()
    if not data:
        st.warning("No workflow data available")
        return
    
    st.subheader("📊 Saved Workflow Data Preview")
    
    companies_data = data['data']
    metadata = get_workflow_metadata()
    
    # Show summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Companies", metadata['total_companies'])
    with col2:
        st.metric("Total Records", metadata['total_records'])
    with col3:
        st.metric("Source", metadata['data_source'])
    
    # Show first few companies
    with st.expander("👀 Preview Data (First 3 Companies)"):
        preview_data = companies_data[:3] if len(companies_data) >= 3 else companies_data
        st.code(json.dumps(preview_data, indent=2), language="json")

def get_companies_list() -> List[str]:
    """
    Get list of company names from workflow data
    
    Returns:
        List[str]: List of company names
    """
    data = get_workflow_data()
    if not data:
        return []
    
    return [company['company'].get('Company Name', 'Unknown') 
            for company in data['data']]

def get_company_data(company_name: str) -> Optional[Dict]:
    """
    Get data for a specific company
    
    Args:
        company_name: Name of the company to retrieve
    
    Returns:
        Dict or None: Company data if found
    """
    data = get_workflow_data()
    if not data:
        return None
    
    for company in data['data']:
        if company['company'].get('Company Name') == company_name:
            return company
    
    return None
    return None
