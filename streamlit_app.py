import streamlit as st
import pandas as pd
import altair as alt
import os
import random
import io

# ===== Config =====
PASSWORD = "giaovien123"  # change password here
CSV_FILE = "ds_khong_lam_btvn.csv"

# ===== Helper functions =====
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=["Name", "Class", "Date"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# ===== Login =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔒 Teacher Login")
    pwd = st.text_input("Enter password:", type="password")
    if st.button("Login", type="primary"):
        if pwd == PASSWORD:
            st.session_state.logged_in = True
            st.success("✅ Login successful! Welcome teacher 👩‍🏫")
            st.balloons()
        else:
            st.error("❌ Wrong password! Try again.")
            st.warning("⚠️ Please contact admin if you forgot the password.")
    st.stop()

# ===== Main App =====
st.title("📘 Homework Management - Students who did not complete")

# Load data
df = load_data()

# Animated buttons section
st.subheader("✨ Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎉 Celebrate", type="primary"):
        st.balloons()
        st.success("Great job! Keep motivating students.")
with col2:
    if st.button("🔥 Warning", type="secondary"):
        st.warning("Some students need extra attention today!")
        st.snow()
with col3:
    if st.button("💀 Critical", type="secondary"):
        st.error("Too many students skipped homework! 🚨")

# Form input
st.subheader("➕ Add student record")
with st.form("add_student"):
    name = st.text_input("Student name")
    class_name = st.text_input("Class")
    date = st.date_input("Date")
    submitted = st.form_submit_button("Add")
    if submitted:
        if name and class_name:
            new_row = {"Name": name, "Class": class_name, "Date": date}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"✅ Student added: {name}")
            st.snow()
        else:
            st.error("❌ Please fill all required fields (Name, Class)")

# Display table
st.subheader("📋 Student List")
st.dataframe(df, use_container_width=True)
if not df.empty:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="NoHomework")
        writer.close()

    st.download_button(
        label="⬇️ Download Excel",
        data=buffer,
        file_name="students_missing_assignments.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Search & filter
st.subheader("🔎 Search & Filter")
search_name = st.text_input("Search by student name")
filter_class = st.text_input("Filter by class")

filtered_df = df.copy()
if search_name:
    filtered_df = filtered_df[filtered_df["Name"].str.contains(search_name, case=False)]
if filter_class:
    filtered_df = filtered_df[filtered_df["Class"].str.contains(filter_class, case=False)]

st.write("Filtered results:")
st.dataframe(filtered_df, use_container_width=True)

# Statistics
st.subheader("📊 Statistics Dashboard")
if not df.empty:
    stats_class = df["Class"].value_counts().reset_index()
    stats_class.columns = ["Class", "Students"]

    chart = alt.Chart(stats_class).mark_bar().encode(
        x="Class",
        y="Students",
        tooltip=["Class", "Students"]
    ).properties(title="Number of students who did not complete homework per class")

    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No data available yet.")

# Random motivational button
st.subheader("💡 Motivation")
quotes = [
    "Every mistake is a step to success!",
    "Failure is just the opportunity to begin again.",
    "Keep pushing, keep trying. Homework matters!",
    "Discipline is the bridge between goals and accomplishment."
]

if st.button("🎲 Random Quote", type="primary"):
    st.info(random.choice(quotes))

# Export
st.subheader("💾 Export Data")
st.download_button(
    "Download CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="ds_khong_lam_btvn.csv",
    mime="text/csv"
)

# Delete function
st.subheader("🗑️ Remove Student")
if not df.empty:
    selected = st.selectbox("Select a student to remove", df["Name"].unique())
    if st.button("Remove ❌", type="secondary"):
        df = df[df["Name"] != selected]
        save_data(df)
        st.success(f"Student {selected} removed successfully!")
        st.balloons()
else:
    st.info("No students to remove.")
