# frontend.py
# This file handles the user interface using Streamlit.
# It imports functions from the backend to interact with the database.

import streamlit as st
import pandas as pd
import backend
from datetime import date

# Set up the database tables on first run
backend.setup_database()

# --- Page Title and Layout ---
st.set_page_config(layout="wide")
st.title("🛡️ Aadhaar Management System")
st.markdown("### A Dynamic Dashboard for System Administrators")

# --- Dashboard & Metrics Section ---
st.markdown("---")
st.subheader("📊 System Overview Dashboard")
insights = backend.get_business_insights()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Enrolled Citizens", value=insights.get("total_enrolled", 0))
with col2:
    st.metric(label="Total Auth Attempts", value=insights.get("total_auth_attempts", 0))
with col3:
    st.metric(label="Successful Authentications", value=insights.get("successful_auths", 0))
with col4:
    st.metric(label="De-duplication Conflicts", value=insights.get("dedup_conflicts", 0))

# --- Alerts Section ---
if insights.get("failed_auths", 0) > 10: # Example alert threshold
    st.warning("⚠️ **ALERT:** A high number of failed authentication attempts has been detected. Investigate potential security issues.")
if insights.get("dedup_conflicts", 0) > 0:
    st.info("ℹ️ **ALERT:** The de-duplication process has flagged potential duplicate records. Manual review is required.")

st.markdown("---")

# --- Main App Sections ---
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Enrollment Management", "Authentication & Verification", "Reporting & Analytics"])

# --- 1. Enrollment Management ---
if page == "Enrollment Management":
    st.header("👤 Enrollment Management (CRUD)")
    operation = st.selectbox("Select Operation", ["Create", "Read", "Update", "Delete"])
    
    if operation == "Create":
        st.subheader("Create New Enrollment")
        with st.form("create_form"):
            aadhaar_id = st.text_input("Aadhaar ID (12 digits)", max_chars=12)
            name = st.text_input("Full Name")
            dob = st.date_input("Date of Birth", value=date(1990, 1, 1))
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            address = st.text_area("Address")
            biometric_hash = st.text_input("Simulated Biometric ID (Hash)") # Simulating unique hash
            
            submitted = st.form_submit_button("Submit Enrollment")
            
            if submitted:
                if backend.check_deduplication(biometric_hash):
                    st.error("❌ De-duplication check failed: Biometric ID already exists!")
                else:
                    success, message = backend.create_citizen(aadhaar_id, name, dob, gender, address, biometric_hash)
                    if success:
                        st.success(f"✅ {message}")
                    else:
            
                        st.error(f"❌ {message}")

    elif operation == "Read":
        st.subheader("Read Citizen Record")
        search_id = st.text_input("Enter Aadhaar ID to read")
        if st.button("Search"):
            record = backend.read_citizen(search_id)
            if record:
                st.write(f"**Aadhaar ID:** {record[0]}")
                st.write(f"**Name:** {record[1]}")
                st.write(f"**Date of Birth:** {record[2]}")
                st.write(f"**Gender:** {record[3]}")
                st.write(f"**Address:** {record[4]}")
                st.write(f"**Enrollment Date:** {record[6].strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.warning("No record found for this Aadhaar ID.")

    elif operation == "Update":
        st.subheader("Update Citizen Record")
        update_id = st.text_input("Enter Aadhaar ID to update")
        if update_id:
            current_record = backend.read_citizen(update_id)
            if current_record:
                with st.form("update_form"):
                    new_name = st.text_input("New Name", value=current_record[1])
                    new_dob = st.date_input("New Date of Birth", value=current_record[2])
                    new_gender = st.selectbox("New Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(current_record[3]))
                    new_address = st.text_area("New Address", value=current_record[4])
                    
                    if st.form_submit_button("Update Record"):
                        success, message = backend.update_citizen(update_id, new_name, new_dob, new_gender, new_address)
                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")
            else:
                st.warning("Aadhaar ID not found.")

    elif operation == "Delete":
        st.subheader("Delete Citizen Record")
        delete_id = st.text_input("Enter Aadhaar ID to delete")
        if st.button("Delete Record", type="primary"):
            success, message = backend.delete_citizen(delete_id)
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")

# --- 2. Authentication & Verification ---
elif page == "Authentication & Verification":
    st.header("🔑 Authentication & Verification")
    auth_id = st.text_input("Enter Aadhaar ID for Authentication")
    auth_biometric = st.text_input("Simulated Biometric ID")
    
    if st.button("Authenticate"):
        if backend.authenticate(auth_id, auth_biometric):
            st.success("✅ **Authentication Successful!**")
            # Simulated eKYC
            st.subheader("eKYC Data Retrieval")
            citizen_data = backend.read_citizen(auth_id)
            if citizen_data:
                df = pd.DataFrame([citizen_data], columns=["Aadhaar ID", "Name", "DOB", "Gender", "Address", "Biometric Hash", "Enrollment Date"])
                st.dataframe(df.drop("Biometric Hash", axis=1)) # Hide hash for eKYC
        else:
            st.error("❌ **Authentication Failed.** Biometric or Aadhaar ID is incorrect.")

# --- 3. Reporting & Analytics ---
elif page == "Reporting & Analytics":
    st.header("📈 Reporting & Analytics")
    st.subheader("Enrollment History")
    citizens, columns = backend.read_all_citizens()
    if citizens:
        df = pd.DataFrame(citizens, columns=columns)
        st.dataframe(df)
    else:
        st.info("No citizens enrolled yet.")

    st.subheader("Authentication Log")
    conn = backend.create_connection()
    if conn:
        auth_df = pd.read_sql_query("SELECT * FROM auth_log ORDER BY attempt_date DESC", conn)
        conn.close()
        st.dataframe(auth_df)
    
    st.subheader("De-duplication Conflicts")
    conn = backend.create_connection()
    if conn:
        conflict_df = pd.read_sql_query("SELECT * FROM deduplication_conflicts ORDER BY attempt_date DESC", conn)
        conn.close()
        st.dataframe(conflict_df)
    else:
        st.warning("Could not connect to database to fetch conflict data.")
        