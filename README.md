# SDR Agent - Modular Structure

A comprehensive Sales Development Representative toolkit built with Streamlit.

## Project Structure

```
sdr-web-ui/
├── main.py                 # Main application entry point
├── config.py              # Configuration file with all constants and settings
├── sections/              # Individual feature modules
│   ├── __init__.py
│   ├── csv_converter.py   # CSV to JSON conversion functionality
│   ├── lead_enrichment.py # Lead enrichment tools (coming soon)
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── ui_components.py   # Reusable UI components
└── README.md              # This file
```

## Features

### ✅ Available
- **CSV to JSON Converter**: Upload CSV files and convert them to structured JSON format grouped by company

## How to Run

```bash
streamlit run main.py
```

## Modular Design Benefits

1. **Easy Maintenance**: Each feature is in its own file
2. **Scalable**: Add new features by creating new modules
3. **Reusable Components**: UI components can be shared across sections
4. **Centralized Configuration**: All settings in one place
5. **Clean Code**: Separation of concerns and single responsibility

## Adding New Features

1. Create a new file in the `sections/` directory
2. Add the section name to `NAVIGATION_SECTIONS` in `config.py`
3. Import and add the routing logic in `main.py`
4. Update feature descriptions in `config.py` if needed

## Configuration

All application settings are centralized in `config.py`:
- App metadata (title, version, etc.)
- Navigation sections
- CSV processing configuration
- UI messages and text

## File Descriptions

- **main.py**: Application entry point with routing logic
- **config.py**: Centralized configuration and constants
- **sections/csv_converter.py**: Complete CSV to JSON conversion functionality
- **sections/lead_enrichment.py**: Placeholder for lead enrichment tools (coming soon)
- **utils/ui_components.py**: Reusable UI components and page setup functions
