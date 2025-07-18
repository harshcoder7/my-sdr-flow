import json
import streamlit as st

def json_to_markdown(data, title="Data", max_depth=3, current_depth=0):
    """
    Convert JSON data to simple markdown format.
    
    Args:
        data: JSON data (dict, list, or primitive)
        title: Title for the markdown section
        max_depth: Maximum depth to display nested objects
        current_depth: Current recursion depth
    
    Returns:
        str: Markdown formatted string
    """
    if current_depth > max_depth:
        return "*(nested data truncated)*"
    
    if isinstance(data, dict):
        markdown = f"## {title}\n\n" if current_depth == 0 else f"{'#' * (current_depth + 2)} {title}\n\n"
        
        for key, value in data.items():
            if isinstance(value, (dict, list)) and value:
                if isinstance(value, dict) and len(value) > 0:
                    markdown += json_to_markdown(value, key, max_depth, current_depth + 1)
                elif isinstance(value, list) and len(value) > 0:
                    markdown += f"**{key}:**\n\n"
                    for i, item in enumerate(value[:5]):  # Limit to first 5 items
                        if isinstance(item, dict):
                            markdown += json_to_markdown(item, f"{key} {i+1}", max_depth, current_depth + 1)
                        else:
                            markdown += f"- {item}\n"
                    if len(value) > 5:
                        markdown += f"- *(and {len(value) - 5} more items)*\n"
                    markdown += "\n"
            else:
                # Format the value nicely
                if value is None:
                    formatted_value = "*Not provided*"
                elif isinstance(value, str) and not value.strip():
                    formatted_value = "*Empty*"
                elif isinstance(value, bool):
                    formatted_value = "✅ Yes" if value else "❌ No"
                else:
                    formatted_value = str(value)
                
                markdown += f"**{key}:** {formatted_value}\n\n"
        
        return markdown
    
    elif isinstance(data, list):
        markdown = f"## {title}\n\n" if current_depth == 0 else f"**{title}:**\n\n"
        for i, item in enumerate(data[:10]):  # Limit to first 10 items
            if isinstance(item, dict):
                markdown += json_to_markdown(item, f"Item {i+1}", max_depth, current_depth + 1)
            else:
                markdown += f"{i+1}. {item}\n"
        if len(data) > 10:
            markdown += f"*(and {len(data) - 10} more items)*\n"
        return markdown + "\n"
    
    else:
        return f"## {title}\n\n{data}\n\n"

def display_response_with_copy_buttons(data, data_title="Response Data"):
    """
    Display response data with copy buttons for JSON and markdown text.
    
    Args:
        data: The data to display (dict, list, or any JSON serializable data)
        data_title: Title for the data section
    """
    # Convert to JSON string
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    
    # Convert to markdown
    markdown_str = json_to_markdown(data, data_title)
    
    # Create copy buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Copy as JSON", key=f"copy_json_{hash(json_str)}", help="Copy response as JSON"):
            st.code(json_str, language="json")
            st.success("JSON copied! Use Ctrl+A, Ctrl+C to copy from the code block above.")
    
    with col2:
        if st.button("📄 Copy as Text", key=f"copy_text_{hash(markdown_str)}", help="Copy response as formatted text"):
            st.markdown("**Formatted Text:**")
            st.text_area("Copy this text:", markdown_str, height=200, key=f"text_area_{hash(markdown_str)}")
            st.success("Text ready to copy! Select all and copy from the text area above.")
    
    # Display the formatted markdown
    st.markdown("---")
    st.markdown(markdown_str)
    
    return json_str, markdown_str
    