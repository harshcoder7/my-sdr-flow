import streamlit as st
from config import APP_CONFIG, NAVIGATION_SECTIONS

def setup_page_config():
    """Configure the Streamlit page settings"""
    st.set_page_config(
        page_title=APP_CONFIG["title"], 
        page_icon=APP_CONFIG["icon"], 
        layout=APP_CONFIG["layout"]
    )

def show_header():
    """Display the main application header"""
    st.title(f"{APP_CONFIG['icon']} {APP_CONFIG['title']}")

def show_sidebar():
    """Display the sidebar navigation and return selected section"""
    st.sidebar.title("Navigation")
    section = st.sidebar.radio(
        "Choose a section:",
        NAVIGATION_SECTIONS,
    )
    return section


