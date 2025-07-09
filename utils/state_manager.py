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
            'has_data': False,
            'enriched_companies': 0,
            'analyzed_companies': 0,
            'intelligence_companies': 0
        }

def validate_json_structure(data: List[Dict]) -> tuple[bool, str]:
    """
    Validate that uploaded JSON has the correct structure
    
    Args:
        data: The JSON data to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        if not isinstance(data, list):
            return False, "JSON must be a list of company objects"
        
        if len(data) == 0:
            return False, "JSON list cannot be empty"
        
        required_fields = ['company', 'people']
        optional_fields = ['enriched_lead', 'icp_analysis', 'market_intelligence', 'enrichment_timestamp', 'icp_analysis_timestamp', 'intelligence_timestamp']
        
        for i, company_obj in enumerate(data):
            if not isinstance(company_obj, dict):
                return False, f"Company object at index {i} must be a dictionary"
            
            # Check required fields
            for field in required_fields:
                if field not in company_obj:
                    return False, f"Missing required field '{field}' in company object at index {i}"
            
            # Validate company field
            if not isinstance(company_obj['company'], dict):
                return False, f"'company' field must be a dictionary at index {i}"
            
            # Validate people field
            if not isinstance(company_obj['people'], list):
                return False, f"'people' field must be a list at index {i}"
            
            # Validate people entries
            for j, person in enumerate(company_obj['people']):
                if not isinstance(person, dict):
                    return False, f"Person at index {j} in company {i} must be a dictionary"
            
            # Validate optional fields if present
            if 'enriched_lead' in company_obj and not isinstance(company_obj['enriched_lead'], dict):
                return False, f"'enriched_lead' field must be a dictionary at index {i}"
            
            if 'icp_analysis' in company_obj and not isinstance(company_obj['icp_analysis'], dict):
                return False, f"'icp_analysis' field must be a dictionary at index {i}"
            
            if 'market_intelligence' in company_obj and not isinstance(company_obj['market_intelligence'], dict):
                return False, f"'market_intelligence' field must be a dictionary at index {i}"
        
        return True, "JSON structure is valid"
    
    except Exception as e:
        return False, f"Error validating JSON structure: {str(e)}"

def load_workflow_from_json(json_data: str) -> bool:
    """
    Load workflow data from JSON string
    
    Args:
        json_data: JSON string containing workflow data
    
    Returns:
        bool: True if load was successful
    """
    try:
        # Parse JSON
        data = json.loads(json_data)
        
        # Validate structure
        is_valid, error_message = validate_json_structure(data)
        if not is_valid:
            st.error(f"❌ Invalid JSON structure: {error_message}")
            return False
        
        # Store the data
        st.session_state.workflow_data = {
            'data': data,
            'source': "JSON Upload",
            'saved_at': datetime.now().isoformat()
        }
        
        # Update metadata
        total_companies = len(data)
        total_records = sum(len(company.get('people', [])) for company in data)
        
        # Count enriched, analyzed, and market intelligence companies
        enriched_count = sum(1 for company in data if 'enriched_lead' in company)
        analyzed_count = sum(1 for company in data if 'icp_analysis' in company)
        intelligence_count = sum(1 for company in data if 'market_intelligence' in company)
        
        st.session_state.workflow_metadata = {
            'last_saved': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_source': "JSON Upload",
            'total_companies': total_companies,
            'total_records': total_records,
            'has_data': True,
            'enriched_companies': enriched_count,
            'analyzed_companies': analyzed_count,
            'intelligence_companies': intelligence_count
        }
        
        return True
        
    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON format: {str(e)}")
        return False
    except Exception as e:
        st.error(f"❌ Error loading JSON data: {str(e)}")
        return False

def show_json_upload_section():
    """Display JSON upload section in sidebar only if no data is loaded"""
    metadata = get_workflow_metadata()
    
    # Only show upload section if no data is loaded
    if not metadata['has_data']:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📤 Upload Session Data")
        
        uploaded_file = st.sidebar.file_uploader(
            "Upload JSON session data",
            type=['json'],
            help="Upload a previously exported session JSON file to restore your workflow data",
            key="json_upload"
        )
    
        if uploaded_file is not None:
            try:
                # Read the file content
                json_content = uploaded_file.read().decode('utf-8')
                
                # Preview section
                with st.sidebar.expander("🔍 Preview uploaded data"):
                    try:
                        preview_data = json.loads(json_content)
                        st.sidebar.write(f"Companies: {len(preview_data)}")
                        if len(preview_data) > 0:
                            # Check for enriched/analyzed/intelligence data
                            enriched_count = sum(1 for c in preview_data if 'enriched_lead' in c)
                            analyzed_count = sum(1 for c in preview_data if 'icp_analysis' in c)
                            intelligence_count = sum(1 for c in preview_data if 'market_intelligence' in c)
                            
                            if enriched_count > 0:
                                st.sidebar.write(f"✅ Enriched: {enriched_count}/{len(preview_data)}")
                            if analyzed_count > 0:
                                st.sidebar.write(f"🎯 Analyzed: {analyzed_count}/{len(preview_data)}")
                            if intelligence_count > 0:
                                st.sidebar.write(f"📊 Intelligence: {intelligence_count}/{len(preview_data)}")
                                
                    except Exception as e:
                        st.sidebar.error(f"Error previewing: {str(e)}")
                
                # Load button
                if st.sidebar.button("🔄 Load Session Data", type="primary", key="load_json"):
                    if load_workflow_from_json(json_content):
                        st.sidebar.success("✅ Session data loaded successfully!")
                        st.sidebar.balloons()
                        # Rerun to update the UI
                        st.rerun()
                    else:
                        st.sidebar.error("❌ Failed to load session data")
                        
            except Exception as e:
                st.sidebar.error(f"❌ Error reading file: {str(e)}")

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
        
        # Count enriched, analyzed, and market intelligence companies
        enriched_count = sum(1 for company in data if 'enriched_lead' in company)
        analyzed_count = sum(1 for company in data if 'icp_analysis' in company)
        intelligence_count = sum(1 for company in data if 'market_intelligence' in company)
        
        st.session_state.workflow_metadata = {
            'last_saved': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_source': source,
            'total_companies': total_companies,
            'total_records': total_records,
            'has_data': True,
            'enriched_companies': enriched_count,
            'analyzed_companies': analyzed_count,
            'intelligence_companies': intelligence_count
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
        'has_data': False,
        'enriched_companies': 0,
        'analyzed_companies': 0,
        'intelligence_companies': 0
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
        # Create a deep copy of the data to avoid modifying the original
        import copy
        export_data = copy.deepcopy(st.session_state.workflow_data['data'])
        
        # Remove numeric timestamp fields from each company
        for company in export_data:
            # Remove numeric timestamp fields if they exist
            company.pop('enrichment_timestamp_numeric', None)
            company.pop('icp_analysis_timestamp_numeric', None)
            company.pop('intelligence_timestamp_numeric', None)
        
        return json.dumps(export_data, indent=2)
    except Exception as e:
        st.error(f"Error exporting data: {str(e)}")
        return None

def export_workflow_to_csv() -> Optional[str]:
    """
    Export workflow data as CSV string with specific headers using pandas
    
    Returns:
        str or None: CSV string of the data if available
    """
    if not st.session_state.workflow_data:
        return None
    
    try:
        import pandas as pd
        
        # Prepare list to store all rows
        rows = []
        
        for company_data in st.session_state.workflow_data['data']:
            # Extract enriched lead data
            enriched = company_data.get('enriched_lead', {})
            given_company = company_data.get('company', {})
            base_row = {
                'Company': enriched.get('Company', '') or given_company.get('Company Name', ''),
                'Overview': enriched.get('Overview', ''),
                'Size': enriched.get('Size', ''),
                'Revenue': enriched.get('Revenue', ''),
                'Domain': enriched.get('Domain', '') or given_company.get('Company Domain', ''),
                'Funding Information': enriched.get('Funding Information', ''),
                'Latest Funding Round': enriched.get('Latest Funding Round', ''),
                'Investors': enriched.get('Investors', ''),
                'LinkedIn URL': enriched.get('LinkedIn URL', ''),
                'sources': enriched.get('Sources', []) or ""
            }
            
            # Extract ICP data
            icp = company_data.get('icp_analysis', {})
            icp_data = {
                'ICP_Product Fit': icp.get('Product Fit', ''),
                'ICP_ICP Score': icp.get('ICP Score', ''),
                'ICP_Prospect Level': icp.get('Prospect Level', ''),
                'ICP_Engagement Readiness': icp.get('Engagement Readiness', ''),
                'ICP_Justification': icp.get('Justification', ''),
                'ICP_Use Case': icp.get('Use Case', '')
            }
            base_row.update(icp_data)
            
            # Extract Market Intelligence data
            market = company_data.get('market_intelligence', {})
            market_data = {
                'Market_Industry': market.get('Industry', ''),
                'Market_Customer Segments': market.get('Customer Segments', ''),
                'Market_Business Model': market.get('Business Model', ''),
                'Market_Geographic Presence': market.get('Geographic Presence', ''),
                'Market_Product Launches': market.get('Product Launches', ''),
                'Market_Press & PR': market.get('Press & PR', ''),
                'Market_Social Media Activity': market.get('Social Media Activity', '')
            }
            base_row.update(market_data)
            
            # Get people data and create a row for each person
            people = company_data.get('people', [])
            if not people:
                # If no people, add one row with just company data
                rows.append(base_row)
            else:
                # Add a row for each person with company data
                for person in people:
                    row = base_row.copy()
                    person_data = {
                        'Person_Name': person.get('Name', ''),
                        'Person_First Name': person.get('First name', ''),
                        'Person_Last Name': person.get('Last name', ''),
                        'Person_Email': person.get('Email', ''),
                        'Person_Title': person.get('Title', ''),
                        'Person_Location': person.get('Location', ''),
                        'Person_LinkedIn_URL': person.get('Linkedin', ''),
                        'Person_Company_Phone': person.get('Company Phone', ''),
                        'Person_Mobile_Phone': person.get('Mobile Number', ''),
                    }
                    row.update(person_data)
                    rows.append(row)
        
        # Create DataFrame and return CSV
        df = pd.DataFrame(rows)
        # Reorder columns to match original order
        columns = [
            # Company and Enriched Lead fields
            'Company', 'Overview', 'Size', 'Revenue', 'Domain', 'Funding Information', 
            'Latest Funding Round', 'Investors', 'LinkedIn URL', 'sources',
            # ICP fields
            'ICP_Product Fit', 'ICP_ICP Score', 'ICP_Prospect Level', 
            'ICP_Engagement Readiness', 'ICP_Justification', 'ICP_Use Case',
            # Market Intelligence fields
            'Market_Industry', 'Market_Customer Segments', 'Market_Business Model',
            'Market_Geographic Presence', 'Market_Product Launches', 
            'Market_Press & PR', 'Market_Social Media Activity',
            # People fields
            'Person_Name', 'Person_First Name', 'Person_Last Name',
            'Person_Email', 'Person_Title', 'Person_Location',
            'Person_LinkedIn_URL', 'Person_Company_Phone', 'Person_Mobile_Phone'
        ]
        df = df[columns]
        return df.to_csv(index=False)
        
    except Exception as e:
        st.error(f"Error exporting CSV data: {str(e)}")
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
        
        # Show enrichment and analysis status if available
        # if 'enriched_companies' in metadata and metadata['enriched_companies'] > 0:
        #     st.sidebar.markdown(f"**✨ Enriched:** {metadata['enriched_companies']}/{metadata['total_companies']}")
        
        # if 'analyzed_companies' in metadata and metadata['analyzed_companies'] > 0:
        #     st.sidebar.markdown(f"**🎯 ICP Analyzed:** {metadata['analyzed_companies']}/{metadata['total_companies']}")
        
        # Export buttons
        col1, col2 = st.sidebar.columns(2)
        
        # JSON Export
        if col1.button("💾 Export JSON", key="export_workflow_json"):
            json_data = export_workflow_data()
            if json_data:
                col1.download_button(
                    label="⬇️ Download JSON",
                    data=json_data,
                    file_name=f"workflow_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key="download_workflow_json"
                )
        
        # CSV Export
        if col2.button("📊 Export CSV", key="export_workflow_csv"):
            csv_data = export_workflow_to_csv()
            if csv_data:
                col2.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"workflow_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_workflow_csv"
                )
        
        # Clear data button
        if st.sidebar.button("🗑️ Clear Data", key="clear_workflow"):
            clear_workflow_data()
            st.sidebar.success("Data cleared!")
            st.rerun()
    else:
        st.sidebar.info("No data saved yet")
    
    # Show upload section only if no data is loaded
    show_json_upload_section()

def show_data_preview():
    """Show a preview of the saved workflow data"""
    data = get_workflow_data()
    if not data:
        st.warning("No workflow data available")
        return
    
    # st.subheader("📊 Saved Workflow Data Preview")
    
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
    
    # Show enrichment/analysis/intelligence status
    if metadata.get('enriched_companies', 0) > 0 or metadata.get('analyzed_companies', 0) > 0 or metadata.get('intelligence_companies', 0) > 0:
        col1, col2, col3, col4 = st.columns([1, 1, 1, 0.2])
        with col1:
            if metadata.get('enriched_companies', 0) > 0:
                st.metric("✨ Enriched", f"{metadata['enriched_companies']}/{metadata['total_companies']}")
        with col2:
            if metadata.get('analyzed_companies', 0) > 0:
                st.metric("🎯 ICP Analyzed", f"{metadata['analyzed_companies']}/{metadata['total_companies']}")
        with col3:
            if metadata.get('intelligence_companies', 0) > 0:
                st.metric("📊 Intelligence", f"{metadata['intelligence_companies']}/{metadata['total_companies']}")
        with col4:
            if st.button("🔄", help="Refresh metrics"):
                update_workflow_metadata()
    
    # Show first few companies
    # with st.expander("👀 Preview Data (First 3 Companies)"):
    #     preview_data = companies_data[:3] if len(companies_data) >= 3 else companies_data
    #     st.code(json.dumps(preview_data, indent=2), language="json")

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

def update_workflow_metadata():
    """Update workflow metadata counters based on current data"""
    if not st.session_state.workflow_data or 'data' not in st.session_state.workflow_data:
        return
    
    data = st.session_state.workflow_data['data']
    
    # Count enriched, analyzed, and market intelligence companies
    enriched_count = sum(1 for company in data if 'enriched_lead' in company)
    analyzed_count = sum(1 for company in data if 'icp_analysis' in company)
    intelligence_count = sum(1 for company in data if 'market_intelligence' in company)
    
    # Update metadata
    st.session_state.workflow_metadata.update({
        'enriched_companies': enriched_count,
        'analyzed_companies': analyzed_count,
        'intelligence_companies': intelligence_count,
        'last_saved': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    st.rerun()  # Rerun to update UI with new metadata
