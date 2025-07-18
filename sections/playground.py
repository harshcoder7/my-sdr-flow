"""
Playground section for direct API testing
Contains 5 modular sections for different API endpoints
"""

import streamlit as st
from sections.playground_modules.enrichment_api import show_enrichment_playground
from sections.playground_modules.icp_profiling_api import show_icp_profiling_playground
from sections.playground_modules.market_intelligence_api import show_market_intelligence_playground
from sections.playground_modules.champion_scoring_api import show_champion_scoring_playground
from sections.playground_modules.person_engagement_api import show_person_engagement_playground

def show_playground():
    """Display the Playground section with 5 API testing modules"""
    st.header("🧪 API Playground")
    st.markdown("Test individual APIs with direct input and get immediate results")
    
    # Create tabs for each playground section
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Enrichment",
        "👥 ICP Profiling", 
        "🏢 Market Intelligence",
        "🏆 Champion Scoring",
        "📊 Person Engagement"
    ])
    
    with tab1:
        show_enrichment_playground()
    
    with tab2:
        # show_icp_profiling_playground()
        pass
    
    with tab3:
        # show_market_intelligence_playground()
        pass
    
    with tab4:
        # show_champion_scoring_playground()
        pass

    with tab5:
        # show_person_engagement_playground()
        pass
