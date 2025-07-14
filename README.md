# SDR Agent - Modular Structure

A comprehensive Sales Development Representative toolkit built with Streamlit, designed to streamline and automate various aspects of the sales development process.

## Project Structure

```
sdr-web-ui/
├── main.py                    # Main application entry point
├── config.py                  # Configuration file with all constants and settings
├── api-trial.py              # API integration trials and testing
├── api-trial copy.py         # API integration backup/testing
├── sections/                 # Individual feature modules
│   ├── __init__.py
│   ├── csv_converter.py      # CSV to JSON conversion functionality
│   ├── lead_enrichment.py    # Lead enrichment and data enhancement tools
│   ├── icp_profiling.py      # Ideal Customer Profile analysis
│   └── market_intelligence.py # Market research and intelligence gathering
├── utils/                    # Utility functions and components
│   ├── __init__.py
│   ├── ui_components.py      # Reusable UI components
│   └── state_manager.py      # Application state management
└── README.md                 # This file
```

## Features

### ✅ Available
- **CSV to JSON Converter**: Upload CSV files and convert them to structured JSON format grouped by company
- **Lead Enrichment**: Advanced tools for enriching lead data and contact information
- **ICP Profiling**: Ideal Customer Profile analysis and segmentation
- **Market Intelligence**: Market research and competitive intelligence gathering
- **Workflow State Management**: Persistent state management across different sections

## How to Run

### Prerequisites
- Python 3.8 or higher
- Streamlit

### Installation & Setup

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd sdr-web-ui
   ```

2. **Install required dependencies**:
   ```bash
   pip install streamlit pandas
   # Add other dependencies as needed
   ```

3. **Run the application**:
   ```bash
   streamlit run main.py
   ```

4. **Access the application**:
   Open your browser and navigate to `http://localhost:8501`

## Modular Design Benefits

1. **Easy Maintenance**: Each feature is in its own dedicated module
2. **Scalable Architecture**: Add new features by creating new modules in the sections directory
3. **Reusable Components**: UI components and utilities can be shared across sections
4. **Centralized Configuration**: All settings and constants managed in one place
5. **Clean Code Structure**: Clear separation of concerns and single responsibility principle
6. **State Management**: Persistent workflow state across different sections
7. **Extensible**: Easy to integrate new APIs and data sources

## Adding New Features

1. **Create a new module**: Add a new file in the `sections/` directory (e.g., `new_feature.py`)
2. **Update configuration**: Add the section name to `NAVIGATION_SECTIONS` in `config.py`
3. **Implement routing**: Import and add the routing logic in `main.py`
4. **Configure settings**: Update feature-specific settings in `config.py` if needed
5. **Add utilities**: Create reusable components in `utils/` if needed

Example structure for a new feature:
```python
# sections/new_feature.py
def show_new_feature():
    """Display the new feature interface"""
    st.header("New Feature")
    # Feature implementation here
```

## Configuration

All application settings are centralized in `config.py`:

- **App Metadata**: Title, version, layout configuration, and last updated date
- **Navigation Sections**: Available feature modules and routing
- **CSV Processing**: Column mappings, required fields, and output configuration
- **UI Messages**: User-facing messages, success/error notifications
- **Feature Settings**: Module-specific configuration options

### Key Configuration Sections:
- `APP_CONFIG`: Application metadata and display settings
- `NAVIGATION_SECTIONS`: Available features in the sidebar
- `CSV_CONFIG`: CSV processing rules and column mappings
- `MESSAGES`: User interface text and notifications

## File Descriptions

### Core Files
- **main.py**: Application entry point with routing logic and section coordination
- **config.py**: Centralized configuration, constants, and application settings

### Feature Modules (`sections/`)
- **csv_converter.py**: Complete CSV to JSON conversion functionality with company grouping
- **lead_enrichment.py**: Lead data enhancement and enrichment tools
- **icp_profiling.py**: Ideal Customer Profile analysis and segmentation tools
- **market_intelligence.py**: Market research and competitive intelligence features

### Utilities (`utils/`)
- **ui_components.py**: Reusable UI components, page setup, and common interface elements
- **state_manager.py**: Application state management and workflow persistence

### API Integration
- **api-trial.py**: Main API integration and testing functionality
- **api-trial copy.py**: Backup/alternative API integration approaches

## Development Status

**Current Version**: 1.0.0  
**Last Updated**: July 2025

### Recent Updates
- ✅ Modular architecture implementation
- ✅ State management system
- ✅ Enhanced UI components
- ✅ Multiple feature modules
- ✅ API integration capabilities

### Roadmap
- 🔄 Enhanced API integrations
- 🔄 Advanced analytics and reporting
- 🔄 Data export capabilities
- 🔄 User authentication and profiles
- 🔄 Automated workflow scheduling
