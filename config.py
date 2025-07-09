"""
Configuration file for SDR Agent application
Contains all constants, settings, and configuration options
"""

# Application Configuration
APP_CONFIG = {
    "title": "SDR Agent",
    "icon": "🎯",
    "layout": "wide",
    "version": "1.0.0",
    "last_updated": "July 2025"
}

# Navigation Sections
NAVIGATION_SECTIONS = [
    "CSV to JSON Converter",
    "Lead Enrichment",
    "ICP Profiling",
    "Market Intelligence",
]

# CSV Converter Configuration
CSV_CONFIG = {
    "company_columns": [
        "Company Name", "Company Domain", "Company Website", "Company Employee Count",
        "Company Employee Count Range", "Company Founded", "Company Industry",
        "Company Type", "Company Headquarters", "Company Revenue Range",
        "Company Linkedin Url", "Company Crunchbase Url", "Company Funding Rounds",
        "Company Last Funding Round Amount"
    ],
    "person_columns": [
        "Name", "First name", "Last name", "Email", "Mobile Number",
        "Company Phone", "Title", "Linkedin", "Location"
    ],
    "required_columns": ["Company Name", "Company Domain", "Name", "Email", "Linkedin"],
    "output_filename": "converted_data.json"
}

# UI Messages
MESSAGES = {
    "csv_success": "✅ CSV file loaded successfully! ({} rows)",
    "csv_error": "❌ Error processing file: {}",
    "csv_upload_prompt": "👆 Please upload a CSV file to get started",
    "processing_complete": "✅ Processing complete! Total companies processed: {}",
    "missing_required": "❌ '{}' column is required but not found in the CSV!",
    "format_hint": "💡 Please make sure your CSV file is properly formatted and contains the required columns."
}
