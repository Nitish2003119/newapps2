import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Page Configuration
st.set_page_config(page_title="Smart Data Analyzer", page_icon="📊", layout="wide")

st.title("📊 Smart Excel & CSV Analyzer")
st.markdown("Apni Excel ya CSV file upload karein—turant filter, analyze aur download karein.")

# Sidebar for File Upload
st.sidebar.header("1. Upload Data")
uploaded_file = st.sidebar.file_uploader("Excel (.xlsx) ya CSV file chunein", type=["xlsx", "csv"])

if uploaded_file is not None:
    # Load Data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            # Agar multiple sheets hain toh sheet select karne ka option
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_name = st.sidebar.selectbox("Sheet select karein:", excel_file.sheet_names)
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
    except Exception as e:
        st.error(f"File padhne mein error aaya: {e}")
        st.stop()

    # Key Metrics
    st.subheader("📌 Quick Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", len(df))
    col2.metric("Total Columns", len(df.columns))
    col3.metric("Missing Values", int(df.isnull().sum().sum()))

    st.divider()

    # Search & Filter Section
    st.sidebar.header("2. Filter & Search")
    search_query = st.sidebar.text_input("Koi bhi keyword search karein:")
    
    filtered_df = df.copy()
    if search_query:
        mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
        filtered_df = filtered_df[mask]

    # Column Filter
    filter_col = st.sidebar.selectbox("Column ke hisaab se filter karein:", ["None"] + list(df.columns))
    if filter_col != "None":
        unique_vals = filtered_df[filter_col].dropna().unique().tolist()
        selected_vals = st.sidebar.multiselect(f"{filter_col} values chunein:", unique_vals, default=unique_vals[:5] if len(unique_vals) > 5 else unique_vals)
        if selected_vals:
            filtered_df = filtered_df[filtered_df[filter_col].isin(selected_vals)]

    # Data Preview Tab & Chart Tab
    tab1, tab2 = st.tabs(["📋 Data Table", "📈 Visual Chart"])

    with tab1:
        st.dataframe(filtered_df, use_container_width=True)
        
        # Download Filtered Data as Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Filtered_Data')
        
        st.download_button(
            label="📥 Filtered Data Download Karein (Excel)",
            data=buffer.getvalue(),
            file_name="processed_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with tab2:
        numeric_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()
        all_cols = filtered_df.columns.tolist()

        if numeric_cols:
            c1, c2, c3 = st.columns(3)
            x_axis = c1.selectbox("X-Axis chunein:", all_cols)
            y_axis = c2.selectbox("Y-Axis (Numeric) chunein:", numeric_cols)
            chart_type = c3.selectbox("Chart Type:", ["Bar Chart", "Line Chart", "Scatter Plot"])

            if chart_type == "Bar Chart":
                fig = px.bar(filtered_df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
            elif chart_type == "Line Chart":
                fig = px.line(filtered_df, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")
            else:
                fig = px.scatter(filtered_df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chart banane ke liye data mein kam se kam ek numeric column hona chahiye.")

else:
    st.info("👈 Shuru karne ke liye left sidebar se apni Excel ya CSV file upload karein.")
