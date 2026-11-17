import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Page Configuration
st.set_page_config(page_title="Smart Data Analyzer", page_icon="📊", layout="wide")

# ==========================================
# 1. CREDENTIALS & AUTHENTICATION SETUP
# ==========================================
USER_CREDENTIALS = {
    "nitish": "7292",
    "user": "11213"
}

# Session state check karne ke liye ki user logged in hai ya nahi
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

def login_page():
    st.title("🔐 Secure Login")
    st.markdown("App access karne ke liye kripya apna User ID aur Password daalein.")
    
    # Login form create kar rahe hain
    with st.form("login_form"):
        username = st.text_input("User ID")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            # Check credentials
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun() # Login successful hone par page refresh karega
            else:
                st.error("❌ Galat User ID ya Password. Kripya dobara check karein!")

# ==========================================
# 2. MAIN APP CONTENT
# ==========================================
def main_app():
    # Sidebar mein Logout ka option
    st.sidebar.success(f"👤 Logged in as: **{st.session_state['username']}**")
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.rerun()
        
    st.sidebar.divider()

    st.title("📊 Smart Excel & CSV Analyzer")
    st.markdown("Apni Excel ya CSV file upload karein—turant filter, analyze aur download karein.")

    # Sidebar for File Upload
    st.sidebar.header("1. Upload Data")
    uploaded_file = st.sidebar.file_uploader("Excel (.xlsx) ya CSV file chunein", type=["xlsx", "csv"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
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

        # Tabs setup
        tab1, tab2 = st.tabs(["📋 Data Table", "📈 Visual Chart"])

        with tab1:
            st.dataframe(filtered_df, use_container_width=True)
            
            # Download Logic
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


# ==========================================
# 3. ROUTING LOGIC (Login Page dikhana hai ya Main App)
# ==========================================
if st
