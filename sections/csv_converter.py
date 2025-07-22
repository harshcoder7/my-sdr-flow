import streamlit as st
import pandas as pd
import json
from config import CSV_CONFIG, MESSAGES
from utils.state_manager import save_workflow_data


def show_csv_converter():
    """Display the CSV to JSON converter section"""
    st.header("CSV to JSON Converter")
    st.markdown(
        "Upload a CSV file and convert it to structured JSON format grouped by Company Name"
    )

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            # Load CSV
            df = pd.read_csv(uploaded_file)

            # Create a unique key for this file to detect changes
            file_key = f"{uploaded_file.name}_{uploaded_file.size}"

            # Check if we have processed data for this file
            if (
                "csv_file_key" not in st.session_state
                or st.session_state.csv_file_key != file_key
            ):
                # New file or file changed, process it
                st.session_state.csv_file_key = file_key
                st.session_state.csv_dataframe = df
                st.session_state.csv_result = None

            st.success(MESSAGES["csv_success"].format(len(df)))

            # Show preview of the data
            with st.expander("📋 Preview Data (First 5 rows)"):
                st.dataframe(df.head())

            # Fill NaN values
            df = df.fillna("")

            # Get column mappings
            company_columns, person_columns = get_column_mappings()

            # Check which columns are available
            available_company_cols = [
                col for col in company_columns if col in df.columns
            ]
            available_person_cols = [col for col in person_columns if col in df.columns]

            st.info(
                f"📊 Available company columns: {len(available_company_cols)}/{len(company_columns)}"
            )
            st.info(
                f"👥 Available person columns: {len(available_person_cols)}/{len(person_columns)}"
            )

            # Check for required columns
            missing_required = [
                col for col in CSV_CONFIG["required_columns"] if col not in df.columns
            ]
            if missing_required:
                for col in missing_required:
                    st.error(MESSAGES["missing_required"].format(col))
            else:
                # Process button
                if st.button("🔄 Convert to JSON", type="primary"):
                    result = process_csv_to_json(
                        df, available_company_cols, available_person_cols
                    )
                    st.session_state.csv_result = result

                # Display results if we have processed data
                if (
                    "csv_result" in st.session_state
                    and st.session_state.csv_result is not None
                ):
                    display_results(df, st.session_state.csv_result)

        except Exception as e:
            st.error(MESSAGES["csv_error"].format(str(e)))
            st.info(MESSAGES["format_hint"])

    else:
        # Clear session state when no file is uploaded
        if "csv_result" in st.session_state:
            del st.session_state.csv_result
        if "csv_file_key" in st.session_state:
            del st.session_state.csv_file_key
        if "csv_dataframe" in st.session_state:
            del st.session_state.csv_dataframe

        st.info(MESSAGES["csv_upload_prompt"])
        show_expected_format()


def get_column_mappings():
    """Return the expected column mappings for company and person data"""
    return CSV_CONFIG["company_columns"], CSV_CONFIG["person_columns"]


def process_csv_to_json(df, available_company_cols, available_person_cols):
    """Process the CSV data and convert it to JSON format"""
    with st.spinner("Processing data..."):
        # Group by "Company Name"
        grouped = df.groupby("Company Name", dropna=False)

        # Build the final JSON structure
        result = []
        for company_name, group in grouped:
            # Take the first row as the base for company fields
            company_data = group.iloc[0][available_company_cols].to_dict()

            # Get all people for this company
            people_data = []
            for _, person_row in group.iterrows():
                person_info = person_row[available_person_cols].to_dict()
                people_data.append(person_info)

            # Combine company and people data
            company_entry = {"company": company_data, "people": people_data}
            result.append(company_entry)

        st.success(MESSAGES["processing_complete"].format(len(result)))
        return result


def display_results(df, result):
    """Display the processing results and download options"""
    # Display results
    st.subheader("📈 Summary")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Companies", len(result))

    with col2:
        st.metric("Total Records", len(df))

    # Show company distribution in a scrollable text area
    company_counts = df.groupby("Company Name").size().sort_values(ascending=False)
    st.subheader("🏢 Records per Company")

    # Create text content
    company_text = []
    for company, count in company_counts.items():
        company_text.append(f"- {company} : {count}")

    # Display in a scrollable text area
    st.text_area(
        "Company Distribution", "\n".join(company_text), height=200, disabled=True
    )

    # Action buttons section
    st.subheader("📁 Actions")
    col1, col2 = st.columns(2)

    with col1:
        # Save to workflow button
        if st.button("💾 Save Data for Workflow", type="primary", key="save_workflow"):
            if save_workflow_data(result, "CSV Converter"):
                st.success(
                    "✅ Data saved to workflow! You can now access it from other sections."
                )
            else:
                st.error("❌ Failed to save data to workflow.")

    with col2:
        # Create download button
        json_string = json.dumps(result, indent=2)
        st.download_button(
            label="⬇️ Download JSON File",
            data=json_string,
            file_name=CSV_CONFIG["output_filename"],
            mime="application/json",
            key="download_json",
        )

    # Show top 5 JSON elements in expandable section
    with st.expander("📄 View Top 5 JSON Elements"):
        top_5_result = result[:5] if len(result) >= 5 else result
        st.code(json.dumps(top_5_result, indent=2), language="json")


def show_expected_format():
    """Display the expected CSV format information"""
    company_columns, person_columns = get_column_mappings()

    with st.expander("ℹ️ Expected CSV Format"):
        st.markdown("**Company Columns:**")
        for col in company_columns:
            required_marker = (
                " (Required)" if col in CSV_CONFIG["required_columns"] else ""
            )
            st.markdown(f"- {col}{required_marker}")

        st.markdown("\n**Person Columns:**")
        for col in person_columns:
            required_marker = (
                " (Required)" if col in CSV_CONFIG["required_columns"] else ""
            )
            st.markdown(f"- {col}{required_marker}")
