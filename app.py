import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="Cloud Production Entry Portal", page_icon="🌐", layout="centered")
st.title("🌐 Cloud Production Entry Portal")
st.markdown("All entries made here sync instantly with your **Google Shared Sheet**.")
st.markdown("---")

# --- INITIALIZE GOOGLE SHEETS CONNECTION ---
try:
    # Connects using the URL provided in .streamlit/secrets.toml
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Failed to connect to Google Sheets: {e}")

# --- FORM FOR SUPERVISOR ENTRY ---
st.subheader("📋 Enter Shift Details")

with st.form(key="production_entry_form", clear_on_submit=True):
    # Supervisor Dropdown
    supervisor = st.selectbox(
        "Supervisor Name", 
        options=["Dharmendra", "Pappu", "Vishal", "Patarbhai"]
    )
    
    # Date (Defaults to today)
    date_val = st.date_input("Date", datetime.date.today())
    formatted_date = date_val.strftime("%d-%m-%y")
    
    # Form fields matching your exact sheet columns
    project_code = st.text_input("Project Code", placeholder="e.g., PRJ-01")
    equipment_code = st.text_input("Equipment Code", value="E6-1")
    equipment_name = st.text_input("Equipment Name", value="APH-1")
    fitter_contractor = st.text_input("Fitter / Contractor Name")
    total_manpower = st.number_input("Total Manpower Deployed", min_value=0, step=1, value=0)
    constraints = st.text_area("Constraints / Operational Blockers", placeholder="Enter any delays or issues...")
    
    # Submit button
    submit_button = st.form_submit_button(label="🚀 Sync & Save to Google Sheet")

# --- PUSH DATA ON SUBMIT ---
if submit_button:
    # 1. Fetch current data from the sheet to prevent overwriting anything
    try:
        existing_data = conn.read(ttl=0) # ttl=0 ensures we bypass cache and get fresh data
    except Exception:
        # If the sheet is completely blank, create an empty DataFrame
        existing_data = pd.DataFrame()

    # 2. Create a row from the new input fields
    new_entry = pd.DataFrame([{
        "Date": formatted_date,
        "Project code": project_code,
        "equipment code": equipment_code,
        "equipment name": equipment_name,
        "fitter/contractor": fitter_contractor,
        "total manpower": total_manpower,
        "constraints:": constraints,
        "Supervisor Name": supervisor # Tracks accountability
    }])
    
    # 3. Combine old data with the new entry row
    updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
    
    # 4. Write back the complete updated dataset to the cloud
    try:
        conn.update(data=updated_df)
        st.success(f"✅ Success! Data successfully written to the Google Shared Sheet for **{supervisor}**.")
        st.balloons()
    except Exception as e:
        st.error(f"❌ Failed to save data to cloud: {e}")

# --- LIVE PREVIEW ---
st.markdown("---")
st.subheader("🔍 Live Cloud Data Preview (Latest Logs)")
if 'conn' in locals():
    try:
        # Re-fetch data to show the supervisor what was just uploaded
        live_data = conn.read(ttl=0)
        st.dataframe(live_data.tail(5), use_container_width=True)
    except Exception:
        st.caption("Unable to fetch fresh preview. Check your sheet access rights.")
