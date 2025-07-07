import streamlit as st

# Import modular components
from utils.ui_components import setup_page_config, show_sidebar, show_header
from utils.state_manager import initialize_state, get_workflow_data, show_workflow_status
from sections.csv_converter import show_csv_converter
from sections.lead_enrichment import show_lead_enrichment

def main():
    """Main application function"""
    # Setup page configuration
    setup_page_config()
    
    # Initialize application state
    initialize_state()
    
    # Show main header
    show_header()
    
    # Show workflow status in sidebar
    show_workflow_status()
    
    # Show sidebar navigation
    section = show_sidebar()
    
    # Route to appropriate section
    if section == "CSV to JSON Converter":
        show_csv_converter()
    elif section == "Lead Enrichment":
        show_lead_enrichment()
  

if __name__ == "__main__":
    main()