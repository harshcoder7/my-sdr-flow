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
│   ├── market_intelligence.py # Market research and intelligence gathering
│   ├── playground.py         # API Playground for direct API testing
│   └── playground_modules/   # Modular API testing components
│       ├── __init__.py
│       ├── base_api_client.py    # Base API client for common functionality
│       ├── enrichment_api.py     # Enrichment API playground
│       ├── icp_profiling_api.py  # ICP Profiling API playground
│       ├── market_intelligence_api.py # Market Intelligence API playground
│       ├── champion_scoring_api.py    # Champion Scoring API playground
│       └── person_engagement_api.py   # Person Engagement API playground
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
- **API Playground**: Direct API testing with 5 modular sections for different endpoints
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
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your AGENT_HIVE_API_KEY
   ```

4. **Run the application**:
   ```bash
   streamlit run main.py
   ```

5. **Access the application**:
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
- **playground.py**: API Playground main interface with tabbed sections for different APIs

### API Playground Modules (`sections/playground_modules/`)
- **base_api_client.py**: Shared API client functionality and common request handling
- **enrichment_api.py**: Interactive testing for lead enrichment API endpoints
- **icp_profiling_api.py**: Direct ICP profiling API testing with manual and JSON input
- **market_intelligence_api.py**: Market intelligence API testing with comprehensive analysis options
- **champion_scoring_api.py**: Champion scoring API for evaluating potential champions within accounts
- **person_engagement_api.py**: LinkedIn post analysis for engagement signals and opportunities

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
- ✅ API Playground with 5 interactive testing modules

## API Playground Features

The API Playground provides direct testing capabilities for 5 key API endpoints:

### 🔍 1. Enrichment API
- **Purpose**: Enrich company data with additional information
- **Input**: Company details (name, domain, industry, employee count, etc.)
- **Output**: Enhanced company data with technology stack, financial info, and insights
- **Formats**: Manual form input or JSON input

### 👥 2. ICP Profiling API  
- **Purpose**: Analyze companies against your Ideal Customer Profile
- **Input**: Company information and business context
- **Output**: ICP score (1-5), product fit assessment, prospect level, engagement readiness
- **Features**: Visual metrics display and detailed justification

### 🏢 3. Market Intelligence API
- **Purpose**: Comprehensive market insights and competitive analysis  
- **Input**: Company data with analysis parameters (geographic focus, time period, analysis type)
- **Output**: Market positioning, competitive landscape, growth opportunities
- **Options**: Include competitors, trends, and opportunity analysis

### 🏆 4. Champion Scoring API
- **Purpose**: Score and identify potential champions within target accounts
- **Input**: Person info, company context, and scoring criteria (influence, budget authority, etc.)
- **Output**: Overall champion score (0-100), individual dimension scores, engagement recommendations
- **Features**: Interactive sliders for scoring criteria and priority classification

### 📊 5. Person Engagement Signal API
- **Purpose**: Analyze LinkedIn posts to identify engagement signals and opportunities
- **Input**: LinkedIn profile URL with optional analysis parameters
- **Output**: Engagement score, pain points, interests, best contact timing, conversation starters
- **Features**: Sentiment analysis and personalization insights

### Playground Benefits
- **Instant Testing**: Direct API calls without batch processing
- **Flexible Input**: Both manual forms and JSON input methods
- **Rich Output**: Formatted responses with key metrics highlighted
- **Error Handling**: Clear error messages and debugging information
- **Modular Design**: Easy to modify or extend individual API modules
- **Development Aid**: Perfect for testing new endpoints or debugging API responses

### Roadmap
- 🔄 Enhanced API integrations
- 🔄 Advanced analytics and reporting
- 🔄 Data export capabilities
- 🔄 User authentication and profiles
- 🔄 Automated workflow scheduling
